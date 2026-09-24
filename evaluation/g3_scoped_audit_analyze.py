"""Deterministic, selected-evidence G3 audit projection for the frozen cohort.

This script reads only the frozen novel_dev run and emits IDs/receipts, never
copies question text, answers, or full evidence into the audit result.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from panda_agent.qa import _evidence_source_types, _is_public_claim_citation_eligible


ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "evaluation/G3_SCOPED_AUDIT_COHORT.json"
AUTH = ROOT / "evaluation/G3_SCOPED_AUDIT_EXECUTION_AUTHORIZATION.json"
REVIEW = ROOT / "evaluation/G3_SCOPED_AUDIT_REVIEW_OVERLAY.json"
OUT = ROOT / "evaluation/G3_SCOPED_AUDIT_EXECUTION_RESULT.json"
REASONS = (
    "DIRECTLY_CITATION_ELIGIBLE", "RESOLVED_EXACT_BACKING", "INVALID_LOCATOR",
    "CONTENT_RELATION_NOT_ESTABLISHED", "BOUND_EXCEEDED", "LOOKUP_FAILED",
    "VERSION_MISMATCH", "AMBIGUOUS_BACKING", "NO_VALID_BACKING",
)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def event(trace: dict, stage: str, round_: int | None = None) -> dict | None:
    for item in trace.get("events", []):
        if item.get("stage") == stage and (round_ is None or item.get("round") == round_):
            return item
    return None


def resolved_items(items: list, registry: dict) -> list[dict]:
    result = []
    for item in items:
        if isinstance(item, dict) and "evidence_projection_ref" in item:
            value = registry.get(item["evidence_projection_ref"])
            if isinstance(value, dict):
                result.append(value)
        elif isinstance(item, dict):
            result.append(item)
    return result


def metric(n: int | None, d: int, unknown: int, *, not_applicable: int = 0) -> dict:
    return {"numerator": n if d else None, "denominator": d,
            "rate": n / d if d and n is not None else None,
            "unknown_questions": unknown, "not_applicable_questions": not_applicable}


def main() -> None:
    cohort, auth = read(COHORT), read(AUTH)
    review = read(REVIEW)
    ids = cohort["selected_question_ids"]
    assert len(ids) == len(set(ids)) == 28
    assert auth["audit_id"] == cohort["audit_id"]
    assert auth["cohort_selection_changed"] is False
    assert review["audit_id"] == cohort["audit_id"]
    assert set(review["targeted_question_ids"]) <= set(ids)
    sidecar = yaml.safe_load((ROOT / cohort["novel_dev_dataset"]["curation_metadata_path"]).read_text(encoding="utf-8"))
    classes = {x["question_id"]: x["representativeness"]["class"] for x in sidecar["records"]}
    assert all(qid in classes for qid in ids)
    run = ROOT / "data/evaluation/runs" / cohort["audit_id"]
    manifest = read(run / "manifest.json")
    assert manifest["mode"] == "qa" and manifest["split"] == "novel_dev"
    assert manifest["official"] is False and not manifest.get("candidate_id")
    assert manifest["capture_stage_trace"] is True
    assert manifest["case_ids"] == ids
    assert manifest["gold_dataset_hash"] == cohort["novel_dev_dataset"]["dataset_sha256"]
    assert manifest["prompt_hash"] == cohort["prompt_fingerprint"]
    assert manifest["max_model_calls"] is None and manifest["max_token_usage"] is None
    assert manifest["repository_identity"]["commit"] == "16dad6f52e266de88f9a218938f236d3ef6cd936"
    assert not manifest["repository_identity"]["dirty"]

    questions, evidence_records, semantic_links = [], [], []
    reason_counts = Counter()
    source_counts = defaultdict(Counter)
    admission_question_ids, rejection_question_ids = set(), set()
    qualified_questions, no_a0_questions, unknown_questions = set(), set(), set()
    tier1_questions, tier0_questions = set(), set()
    a1_exposed = a1_admitted = a1_questions = 0
    named_states, ordinary_states = Counter(), Counter()
    g2_point_states = Counter()
    valid_visible_only, traceable_visible_only = 0, 0
    trace_completeness = Counter()
    stage_counts = {f"S{i}": Counter() for i in range(9)}

    for qid in ids:
        path = run / "records" / f"{qid}.json"
        q = {"question_id": qid, "representativeness_class": classes[qid],
             "record_ref": str(path.relative_to(ROOT)).replace("\\", "/"),
             "retrieval_trace_ref": f"data/evaluation/runs/{cohort['audit_id']}/traces/{qid}.json",
             "stage_status": {}, "artifact_status": None, "qa_status": None,
             "selected_count": None, "admission_denominator_eligible": False,
             "tier0": False, "tier1": False, "primary_root_cause": None}
        if not path.exists():
            q["artifact_status"] = "NOT_OBSERVABLE"
            q["limitation"] = "CASE_RECORD_MISSING"
            q["stage_status"] = {f"S{i}": "NOT_OBSERVABLE" for i in range(9)}
            unknown_questions.add(qid)
            trace_completeness["NOT_OBSERVABLE"] += 1
            questions.append(q)
            continue
        rec = read(path)
        if rec.get("exception"):
            q["artifact_status"] = "NOT_OBSERVABLE"
            q["exception"] = rec["exception"]
            q["stage_status"] = {f"S{i}": "NOT_OBSERVABLE" for i in range(9)}
            unknown_questions.add(qid)
            trace_completeness["NOT_OBSERVABLE"] += 1
            questions.append(q)
            continue
        diag = rec.get("diagnostics") or {}
        qa_trace = diag.get("qa_stage_trace") or {}
        retrieval_path = ROOT / q["retrieval_trace_ref"]
        retrieval = read(retrieval_path) if retrieval_path.is_file() else None
        q["qa_status"] = (rec.get("result") or {}).get("status")
        q["capture_status"] = qa_trace.get("capture_status")
        q["selected_count"] = len(diag.get("selected_evidence") or [])
        if not qa_trace or not retrieval:
            q["artifact_status"] = "NOT_OBSERVABLE"
            q["limitation"] = "REQUIRED_TRACE_MISSING"
            q["stage_status"] = {f"S{i}": "NOT_OBSERVABLE" for i in range(9)}
            unknown_questions.add(qid)
            trace_completeness["NOT_OBSERVABLE"] += 1
            questions.append(q)
            continue
        assert retrieval["run_id"] == cohort["audit_id"] and retrieval["question_id"] == qid
        selected = diag.get("selected_evidence") or []
        assert [x["evidence_id"] for x in selected] == list(diag.get("selected_evidence_ids") or [])
        assert {x["evidence_id"] for x in selected} == {x["evidence_id"] for x in retrieval["final_evidence"]}
        registry = qa_trace.get("evidence_registry") or {}
        ea0 = event(qa_trace, "EA_ADMISSION", 0)
        v1in, v2in = event(qa_trace, "V1_INPUT"), event(qa_trace, "V2_INPUT")
        v1out, v2out = event(qa_trace, "V1_OUTPUT"), event(qa_trace, "V2_OUTPUT")
        required = [ea0, v1in, v1out]
        if v2in and v2in.get("status") == "CAPTURED":
            required.append(v2out)
        good = qa_trace.get("capture_status") == "COMPLETE" and all(
            x and x.get("status") in {"CAPTURED", "NOT_EXECUTED"} for x in required
        )
        q["artifact_status"] = "COMPLETE" if good else "PARTIAL"
        trace_completeness[q["artifact_status"]] += 1
        q["stage_event_status"] = {f"{x['stage']}.{x['round']}": x["status"] for x in qa_trace.get("events", [])}
        if not good:
            unknown_questions.add(qid)

        ea_payload = ea0.get("payload") or {} if ea0 else {}
        ea_captured = bool(ea0 and ea0.get("status") == "CAPTURED")
        decision_map = {}
        admitted_ids = set()
        if ea_captured:
            decisions = ea_payload.get("decisions") or []
            selected_ids = [x["evidence_id"] for x in selected]
            if (ea_payload.get("selected_evidence_ids") == selected_ids
                    and len(decisions) == len(selected_ids)
                    and [x.get("evidence_id") for x in decisions] == selected_ids
                    and all(x.get("reason_code") in REASONS for x in decisions)):
                decision_map = {x["evidence_id"]: x for x in decisions}
                admitted_ids = set(ea_payload.get("admitted_evidence_ids") or [])
                qualified_questions.add(qid)
                q["admission_denominator_eligible"] = True
            else:
                q["admission_limitation"] = "EA_DECISION_ALIGNMENT_INCOMPLETE"
                unknown_questions.add(qid)
        elif ea0 and ea0.get("status") == "NOT_EXECUTED":
            no_a0_questions.add(qid)
        else:
            unknown_questions.add(qid)

        channel_ids = {c.get("object_id") for rows in retrieval.get("channel_candidates", {}).values() for c in rows}
        ranked_ids = {c.get("object_id") for k in ("fused_candidates", "reranked_candidates") for c in retrieval.get(k, [])}
        ranked_ids.update(diag.get("ranked_object_ids") or [])
        object_types = {c.get("object_id"): c.get("object_type") for rows in retrieval.get("channel_candidates", {}).values() for c in rows}
        visible_ids = set()
        verifier_admitted_ids = set()
        verifier_executed = False
        for ve in (v1in, v2in):
            if ve and ve.get("status") == "CAPTURED":
                verifier_executed = True
                payload = ve.get("payload", {}).get("model_input") or {}
                visible_ids.update(x.get("evidence_id") for x in resolved_items(payload.get("untrusted_evidence") or [], registry))
                verifier_admitted_ids.update(payload.get("admitted_evidence_ids") or [])

        final_audit = diag.get("answer_point_audit") or {}
        validation = final_audit.get("coverage_validation") or {}
        valid_results = {x.get("answer_point_id"): x for x in validation.get("point_results") or []}
        g2_point_states.update(x.get("state", "UNKNOWN") for x in valid_results.values())
        claim_mappings = {x.get("claim_id"): x for x in final_audit.get("claim_mappings") or []}
        final_round = "V2" if v2out and v2out.get("status") == "CAPTURED" else "V1" if v1out and v1out.get("status") == "CAPTURED" else None
        final_coverage = final_audit.get("answer_point_coverage") or []
        semantic_authoritative = bool(final_round and validation.get("status") in {"VALID", "PARTIAL"}
                                      and final_coverage)
        q["semantic_authoritative"] = semantic_authoritative
        q["verification_rounds"] = {}
        for label, ve in (("V1", v1out), ("V2", v2out)):
            status = ve.get("status") if ve else "MISSING"
            q["verification_rounds"][label] = {
                "event_status": status,
                "raw_validation_status": (ve.get("payload") or {}).get("validation", {}).get("status") if ve else None,
                "semantic_authority": "FINAL_G2_AUDIT" if semantic_authoritative and final_round == label
                                      else "NOT_OBSERVABLE" if status == "CAPTURED" else "NOT_APPLICABLE" if status == "NOT_EXECUTED" else "NOT_OBSERVABLE",
            }
        if final_round and not semantic_authoritative:
            q["semantic_limitation"] = "PER_ROUND_VALID_DISPOSITIONS_NOT_OBSERVABLE"
        basis_by_id = defaultdict(list)
        if semantic_authoritative:
            for point in final_coverage:
                pid = point.get("answer_point_id")
                state = valid_results.get(pid, {}).get("state")
                if state != "VALID":
                    continue
                named = point.get("required_relation_checks") or []
                ordinary = point.get("relationship_checks") or []
                relation_states = {x.get("relation_id"): x.get("state") for x in valid_results.get(pid, {}).get("relations") or []}
                for kind, checks in (("named_relation", named), ("ordinary_check", ordinary)):
                    for ordinal, check in enumerate(checks):
                        if kind == "named_relation" and relation_states.get(check.get("relation_id")) != "VALID":
                            continue
                        state_name = check.get("admission_state")
                        if not isinstance(state_name, str):
                            continue
                        link = {"question_id": qid, "verify_round": final_round,
                                "answer_point_id": pid, "kind": kind,
                                "relation_id": check.get("relation_id") if kind == "named_relation" else None,
                                "ordinary_check_ordinal": ordinal if kind == "ordinary_check" else None,
                                "validation_state": "VALID", "admission_state": state_name,
                                "basis_evidence_ids": [x.get("evidence_id") for x in check.get("basis") or []],
                                "supporting_claim_ids": check.get("supporting_claim_ids") or [],
                                "satisfied": check.get("satisfied"), "point_complete": point.get("complete") is True}
                        link["supported_claim_ids"] = [cid for cid in link["supporting_claim_ids"]
                            if claim_mappings.get(cid, {}).get("supported") is True]
                        link["rendered_claim_ids"] = [cid for cid in link["supported_claim_ids"]
                            if claim_mappings.get(cid, {}).get("rendered") is True]
                        link["mapped_to_answer_point"] = any(
                            pid in claim_mappings.get(cid, {}).get("verified_answer_point_ids", [])
                            for cid in link["supported_claim_ids"])
                        link["required_relation_satisfied"] = kind == "named_relation" and check.get("satisfied") is True
                        link["ordinary_check_complete"] = kind == "ordinary_check" and check.get("satisfied") is True
                        semantic_links.append(link)
                        (named_states if kind == "named_relation" else ordinary_states)[state_name] += 1
                        if state_name == "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING":
                            valid_visible_only += 1
                        for eid in link["basis_evidence_ids"]:
                            basis_by_id[eid].append(link)

        q_evidence = []
        for item in selected:
            eid, oid = item["evidence_id"], item.get("object_id")
            decision = decision_map.get(eid)
            reason = decision.get("reason_code") if decision else None
            direct = _is_public_claim_citation_eligible(item)
            backing = decision.get("backing_evidence_id") if decision else None
            admission_success = reason in {"DIRECTLY_CITATION_ELIGIBLE", "RESOLVED_EXACT_BACKING"}
            if decision:
                assert direct == (reason == "DIRECTLY_CITATION_ELIGIBLE")
                assert (eid if direct else backing) in admitted_ids if admission_success else True
                reason_counts[reason] += 1
                for source_type in _evidence_source_types(item):
                    source_counts[source_type][reason] += 1
                if admission_success:
                    admission_question_ids.add(qid)
                else:
                    rejection_question_ids.add(qid)
                    tier0_questions.add(qid)
            locator = item.get("locator") or {}
            resolution_applicable = not direct and bool(oid and locator.get("url") and locator.get("snapshot_date") and not locator.get("section_path"))
            links = [*basis_by_id.get(eid, []), *basis_by_id.get(backing, [])] if backing else basis_by_id.get(eid, [])
            tier1 = bool(decision and not admission_success and any(
                x["admission_state"] == "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING" for x in links))
            if tier1:
                tier1_questions.add(qid)
            authorization = {
                "supported_claim": any(x["supported_claim_ids"] for x in links),
                "satisfied_required_relation": any(x["required_relation_satisfied"] for x in links),
                "complete_ordinary_check": any(x["ordinary_check_complete"] for x in links),
                "complete_answer_point": any(x["point_complete"] and x["satisfied"] for x in links),
            }
            stages = {
                "S0": "YES" if oid in channel_ids else "NOT_OBSERVABLE",
                "S1": "YES" if oid in ranked_ids else "NOT_OBSERVABLE",
                "S2": "YES",
                "S3": "YES" if direct else "NO",
                "S4": "NOT_APPLICABLE" if direct else "YES" if resolution_applicable else "NO",
                "S5": "YES" if admission_success else "NO" if decision else "NOT_APPLICABLE" if qid in no_a0_questions else "NOT_OBSERVABLE",
                "S6": "YES" if eid in visible_ids or (backing and backing in visible_ids) else "NO" if verifier_executed else "NOT_APPLICABLE",
                "S7": "YES" if links else "NO" if semantic_authoritative else "NOT_APPLICABLE" if not final_round else "NOT_OBSERVABLE",
                "S8": "YES" if any(authorization.values()) else "NO" if semantic_authoritative else "NOT_OBSERVABLE" if final_round else "NOT_APPLICABLE",
            }
            for stage, value in stages.items():
                stage_counts[stage][value] += 1
            source_type_set = sorted(_evidence_source_types(item))
            er = {"question_id": qid, "phase": "A0", "selected_evidence_id": eid,
                  "selected_object_id": oid, "source_id": item.get("source_id"),
                  "source_version_id": item.get("source_version_id"),
                  "source_types": source_type_set, "object_type": object_types.get(oid) or "UNKNOWN",
                  "admission_reason_code": reason, "admission_route": "DIRECT" if reason == "DIRECTLY_CITATION_ELIGIBLE" else "EXACT_BACKING" if reason == "RESOLVED_EXACT_BACKING" else "REJECTED" if decision else "NOT_APPLICABLE" if qid in no_a0_questions else "NOT_OBSERVABLE",
                  "backing_evidence_id": backing, "resolution_applicable": resolution_applicable,
                  "resolution_attempted": "YES" if reason in {"RESOLVED_EXACT_BACKING", "VERSION_MISMATCH", "AMBIGUOUS_BACKING", "NO_VALID_BACKING", "CONTENT_RELATION_NOT_ESTABLISHED"} and resolution_applicable else "NOT_OBSERVABLE" if resolution_applicable else "NOT_APPLICABLE",
                  "verifier_visible": eid in visible_ids or bool(backing and backing in visible_ids),
                  "verifier_admitted": eid in verifier_admitted_ids or bool(backing and backing in verifier_admitted_ids),
                  "authorization": authorization, "stage_status": stages,
                  "tier0": bool(decision and not admission_success),
                  "tier1": tier1, "semantic_link_count": len(links)}
            q_evidence.append(er)
            evidence_records.append(er)
        rejected_selected = {x["selected_evidence_id"] for x in q_evidence if x["admission_route"] == "REJECTED"}
        traceable_visible_only += sum(
            x["admission_state"] == "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING"
            and bool(set(x["basis_evidence_ids"]) & rejected_selected)
            for x in semantic_links if x["question_id"] == qid
        )
        q["tier0"], q["tier1"] = qid in tier0_questions, qid in tier1_questions
        q["selected_count"] = len(q_evidence)
        for stage in (f"S{i}" for i in range(9)):
            values = {x["stage_status"][stage] for x in q_evidence}
            q["stage_status"][stage] = (
                "YES" if "YES" in values else
                "NOT_OBSERVABLE" if "NOT_OBSERVABLE" in values else
                "NO" if "NO" in values else "NOT_APPLICABLE"
            )
        q["final_verify_round"] = final_round
        q["coverage_validation_status"] = validation.get("status")
        q["final_point_complete_count"] = sum(x.get("complete") is True for x in final_coverage)
        q["final_point_count"] = len(final_audit.get("answer_points") or [])
        q["primary_root_cause"] = "UNRESOLVED" if q["qa_status"] != "answered" else "NOT_APPLICABLE"
        if qid in no_a0_questions:
            q["primary_root_cause"] = "UNRESOLVED"
        if qid in tier1_questions:
            q["primary_root_cause"] = "UNRESOLVED"
        if final_round and not semantic_authoritative:
            q["primary_root_cause"] = "OBSERVABILITY_LIMITATION"
        if qid in qualified_questions:
            a1 = event(qa_trace, "A1_INPUT")
            if a1 and a1.get("status") == "CAPTURED":
                a1_questions += 1
                inputs = a1.get("payload", {}).get("model_input") or {}
                a1_ids = {x.get("evidence_id") for x in resolved_items(inputs.get("untrusted_evidence") or [], registry)}
                a1_exposed += len(a1_ids & admitted_ids)
                a1_admitted += len(admitted_ids)
        questions.append(q)

    attempts_path = run / "attempts.jsonl"
    attempts = [json.loads(line) for line in attempts_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    attempts = [x for x in attempts if x.get("id") in ids]
    usage = {k: sum((x.get("model_call_breakdown") or {}).get("runtime", {}).get(k, 0) for x in attempts)
             for k in ("generation_calls", "embedding_calls")}
    usage["model_calls"] = sum(x.get("model_calls", 0) for x in attempts)
    usage["token_usage"] = sum(x.get("token_usage", 0) for x in attempts)
    completed = sum(q["qa_status"] is not None for q in questions)
    incomplete = len(ids) - completed
    denom_evidence = sum(reason_counts.values())
    unknown_admission = len(ids) - len(qualified_questions) - len(no_a0_questions)
    valid_final_questions = {q["question_id"] for q in questions if q.get("semantic_authoritative") and q["admission_denominator_eligible"]}
    adjudicated_primary_questions = sum(q["primary_root_cause"] not in (None, "UNRESOLVED") for q in questions)
    tier1_incomplete = sum(q["question_id"] in tier1_questions and q["final_point_complete_count"] < q["final_point_count"] for q in questions if q["question_id"] in valid_final_questions)
    metrics = {
        "a0_admission": metric(reason_counts["DIRECTLY_CITATION_ELIGIBLE"] + reason_counts["RESOLVED_EXACT_BACKING"], denom_evidence, unknown_admission, not_applicable=len(no_a0_questions)),
        "a0_rejection": metric(denom_evidence - reason_counts["DIRECTLY_CITATION_ELIGIBLE"] - reason_counts["RESOLVED_EXACT_BACKING"], denom_evidence, unknown_admission, not_applicable=len(no_a0_questions)),
        "selected_but_unadmitted_questions": metric(len(rejection_question_ids), len(qualified_questions), unknown_admission, not_applicable=len(no_a0_questions)),
        "a1_target_exposure": metric(a1_exposed, a1_admitted, len(unknown_questions),
                                      not_applicable=len(ids) - a1_questions - len(unknown_questions)),
        "traceable_visible_only_linkage": metric(traceable_visible_only, valid_visible_only, len(ids) - len(valid_final_questions)),
        "tier1_incomplete_question_incidence": metric(tier1_incomplete, len(valid_final_questions), len(ids) - len(valid_final_questions)),
        "tier2_candidate_incidence": metric(0, len(valid_final_questions), len(ids) - len(valid_final_questions)),
        "admission_policy_primary_incidence": metric(0, adjudicated_primary_questions,
                                                    len(ids) - adjudicated_primary_questions),
        "admission_outcomes": {reason: metric(reason_counts[reason], denom_evidence, unknown_admission, not_applicable=len(no_a0_questions)) for reason in REASONS},
        "named_relation_states": {state: metric(count, sum(named_states.values()), len(ids) - len(valid_final_questions)) for state, count in named_states.items()},
        "ordinary_check_states": {state: metric(count, sum(ordinary_states.values()), len(ids) - len(valid_final_questions)) for state, count in ordinary_states.items()},
    }
    root_counts = Counter(q["primary_root_cause"] for q in questions if q["primary_root_cause"])
    assert review["tier1_reviewed"] == 0 if not tier1_questions else review["tier1_reviewed"] <= len(tier1_questions)
    assert review["tier2_candidates"] == 0 if not tier1_questions else review["tier2_candidates"] >= 0
    metrics["primary_root_cause_distribution"] = {
        cause: metric(root_counts[cause], len(ids) - len(unknown_questions), len(unknown_questions))
        for cause in ("ADMISSION_POLICY", "ADMISSION_DATA_INTEGRITY", "RETRIEVAL_SELECTION",
                      "SEMANTIC_INSUFFICIENCY", "VERIFIER_FALSE_REJECTION",
                      "CLAIM_MAPPING_OR_SUPPORT", "GENERATION_OR_REVISION",
                      "QUESTION_DECOMPOSITION", "INFRASTRUCTURE", "OBSERVABILITY_LIMITATION",
                      "NOT_APPLICABLE", "UNRESOLVED")
    }
    strata = {}
    for class_name in ("representative", "exploratory"):
        qids = {q for q in ids if classes[q] == class_name}
        qualified = qids & qualified_questions
        ev = [x for x in evidence_records if x["question_id"] in qualified and x["admission_reason_code"]]
        admitted = sum(x["admission_route"] in {"DIRECT", "EXACT_BACKING"} for x in ev)
        strata[class_name] = {"frozen_questions": len(qids), "admission_auditable_questions": len(qualified),
                              "unknown_admission_questions": len(qids - qualified - no_a0_questions),
                              "selected_evidence": len(ev), "admitted_selected_evidence": admitted,
                              "admission_rate": admitted / len(ev) if ev else None,
                              "tier1_questions": len(qids & tier1_questions)}
    result = {
        "schema_version": "g3-scoped-audit-execution-result-v1",
        "audit_id": cohort["audit_id"], "run_id": cohort["audit_id"],
        "frozen_cohort_commit": auth["frozen_cohort_commit"],
        "execution_authorization_commit": manifest["repository_identity"]["commit"],
        "prior_budget_stop_result": "evaluation/G3_SCOPED_AUDIT_RESULT.json",
        "cohort_selection_changed": False, "product_behavior_lineage": cohort["product_behavior_lineage"],
        "run_manifest_ref": str((run / "manifest.json").relative_to(ROOT)).replace("\\", "/"),
        "run_identity": {k: manifest.get(k) for k in ("mode", "split", "official", "capture_stage_trace", "gold_dataset_hash", "source_manifest_hash", "index_identity", "prompt_hash", "prompt_version", "repository_identity", "generation_model_id", "runtime_generation_model_id", "embedding_model_id", "evaluation_judge_model_id", "max_model_calls", "max_token_usage")},
        "frozen_cohort_size": len(ids), "artifact_reuse_cases": 0,
        "fresh_capture_required": len(ids), "fresh_capture_attempted": len({x["id"] for x in attempts}),
        "fresh_capture_completed": completed, "fresh_capture_incomplete": incomplete,
        "qa_execution_attempts": len(attempts), "qa_cases_completed": completed,
        "scientific_usage": {**usage, "external_judge_calls": 0},
        "trace_completeness": {k: trace_completeness[k] for k in ("COMPLETE", "PARTIAL", "NOT_OBSERVABLE")},
        "stage_status_counts": {k: dict(v) for k, v in stage_counts.items()},
        "question_summaries": questions, "evidence_opportunities": evidence_records,
        "relation_check_links": semantic_links,
        "admission_outcome_counts": {k: reason_counts[k] for k in REASONS},
        "g2_point_validation_states": dict(g2_point_states),
        "source_type_admission_counts": {k: dict(v) for k, v in source_counts.items()},
        "metrics": metrics, "root_cause_counts": dict(root_counts),
        "representativeness_strata": strata,
        "tiers": {"tier0_questions": len(tier0_questions), "tier1_questions": len(tier1_questions),
                  "tier2_candidates": review["tier2_candidates"]},
        "manual_review": {k: review[k] for k in ("reviewer", "method", "tier1_reviewed",
                           "targeted_ambiguous_classification_reviewed", "targeted_question_ids",
                           "targeted_finding", "tier2_candidates", "tier2_independent_review_completed",
                           "tier2_independent_review_pending")},
        "review_overlay_ref": str(REVIEW.relative_to(ROOT)).replace("\\", "/"),
        "primary_decision": review["primary_decision"],
        "decision_basis": review["decision_basis"],
        "next_task_recommendation": review["next_task_recommendation"],
        "next_task_execution_authorized": review["next_task_execution_authorized"],
        "materiality": {"source_change": False, "product_source_change": False,
                        "material_product_change": False, "product_behavior_change": False,
                        "audit_execution_authorization_change": True, "audit_artifact_change": True,
                        "status_doc_change": True, "prompt_change": False, "schema_change": False,
                        "trace_schema_change": False, "manifest_schema_change": False,
                        "retrieval_behavior_change": False, "admission_behavior_change": False,
                        "g1_g2_behavior_change": False, "evaluator_scoring_change": False,
                        "gold_change": False, "calibration_change": False,
                        "empirical_audit_executed": True, "empirical_admission_gap_established": False},
        "data_access": {"novel_dev_case_content_access": len(ids), "novel_dev_outcome_access": len(ids),
                        "novel_validation_content_access": 0, "novel_validation_outcome_access": 0,
                        "holdout_content_access": 0, "holdout_outcome_access": 0, "protected_leakage": 0},
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"completed": completed, "incomplete": incomplete,
                      "trace_completeness": result["trace_completeness"],
                      "selected_evidence": len(evidence_records),
                      "admission_decisions": denom_evidence,
                      "tier1_questions": len(tier1_questions), "usage": usage}))


if __name__ == "__main__":
    main()

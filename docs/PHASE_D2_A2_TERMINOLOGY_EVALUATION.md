# PANDA Agent — Phase D2-A2: Terminology/Paraphrase Evaluation Report

> Status: `D2-A2 = COMPLETE / MIXED_RESULTS` (A2R1:
> `COMPLETE / EVALUATION_SEMANTICS_REPAIRED`; A2R2:
> `COMPLETE / TARGET_SCOPED_ACCOUNTING_REPAIRED`, 2026-08-30). Frozen evaluation
> executed correctly against a current D1-compatible structured state. The
> mixed outcome is recorded honestly; the resolver was not modified during or
> after the evaluation. D2-A3 owns the role decision.
>
> All headline numbers in this document are mechanically reproduced from the
> structured result artifact `evaluation/d2_a2_results.json`
> (`metric_consistency_problems = []`); they are not manually transcribed.

BEGIN_D2_A2_METRICS
```json
{
 "run_provenance": {
  "head": "2c095ebd68b571f3cf3d093e9b9d1e28dd2867cc",
  "baseline_commit": "67eff2b",
  "case_artifact_path": "evaluation\\d2_a2_terminology_cases.yaml",
  "state_type": "deterministic_in_memory_d1_compatible",
  "state_valid": true,
  "timestamp_utc": "2026-08-30T13:11:18.756612+00:00",
  "case_count": 22
 },
 "state_validation": {
  "state_type": "deterministic_in_memory_d1_compatible",
  "object_count": 32,
  "expected_object_count": 32,
  "object_count_ok": true,
  "seed_object_count": 24,
  "declared_source_native_count": 8,
  "duplicate_object_ids": [],
  "no_duplicate_object_ids": true,
  "required_canonical_ids": {
   "concept.luminosityfit.luminosity_fit_model": 1,
   "workflow.restgas.first_pass_poca": 1,
   "data_product.restgas.pid_final_root": 1,
   "configuration.restgas_profile": 1
  },
  "required_canonical_ids_ok": true,
  "identity_role_values": [
   "canonical",
   "source_native"
  ],
  "identity_roles_valid": true,
  "accepted_alias_count": 2,
  "expected_accepted_alias_count": 2,
  "corrective_alias_present": true,
  "true_identity_alias_present": true,
  "alias_targets_missing": [],
  "no_missing_alias_targets": true,
  "accepted_relation_count": 16,
  "expected_accepted_relation_count": 16,
  "pending_relation_count": 0,
  "workflow_step_count": 1,
  "expected_workflow_step_count": 1,
  "first_pass_poca_features": [
   "CONSUMES data_product.restgas.pid_root",
   "*_pid.root",
   "PRODUCES data_product.restgas.boost_root",
   "*_boost.root"
  ],
  "first_pass_poca_features_ok": true,
  "resolver_probe_question": "Where is *_pid_final.root produced?",
  "resolver_probe_ok": true,
  "resolver_probe_error": null,
  "read_only_statements": 8,
  "valid": true
 },
 "metrics": {
  "case_counts": {
   "total": 22,
   "valid": 20,
   "invalid": 2,
   "invalid_case_ids": [
    "C10",
    "C14"
   ],
   "not_applicable": 0,
   "correct": 16
  },
  "failure_taxonomy_counts": {
   "COMPETITION_AMBIGUITY": 3,
   "WRONG_CONFIDENT_RESOLUTION": 1
  },
  "decision_accounting": {
   "correct_resolve": 9,
   "wrong_resolve": 1,
   "correct_abstain": 5,
   "wrong_abstain": 0,
   "correct_ambiguous": 2,
   "wrong_ambiguous": 3,
   "not_applicable": 0
  },
  "case_validity": {
   "numerator": 20,
   "denominator": 22,
   "value": 0.9090909090909091
  },
  "category_natural_applicability": {
   "numerator": 14,
   "denominator": 16,
   "value": 0.875,
   "categories_requiring_accounting": 16,
   "not_available_categories": [
    "resolved_multiple",
    "same_as"
   ],
   "represented_categories": [
    "accepted_alias",
    "ambiguous_terminology",
    "corrective_term",
    "data_product_description",
    "descriptive_domain_paraphrase",
    "documentation_vs_concept",
    "exact_canonical_terminology",
    "exact_technical_identifier",
    "multi_mention_isolation",
    "path_reference",
    "query_expansion_negative_control",
    "related_but_not_identical",
    "source_native_symbol",
    "unsupported_expression",
    "version_sensitive_identifier",
    "workflow_description"
   ]
  },
  "execution_coverage": {
   "numerator": 22,
   "denominator": 22,
   "value": 1.0
  },
  "resolution_accuracy": {
   "numerator": 9,
   "denominator": 12,
   "value": 0.75
  },
  "canonical_identity_accuracy": {
   "numerator": 6,
   "denominator": 9,
   "value": 0.6666666666666666
  },
  "explicit_canonicalization_accuracy": {
   "numerator": 1,
   "denominator": 1,
   "value": 1.0
  },
  "source_native_noncanonicalization_accuracy": {
   "numerator": 3,
   "denominator": 3,
   "value": 1.0
  },
  "abstention_accuracy": {
   "numerator": 5,
   "denominator": 6,
   "value": 0.8333333333333334
  },
  "ambiguity_accuracy": {
   "numerator": 2,
   "denominator": 2,
   "value": 1.0
  },
  "false_positive_resolution_rate": {
   "numerator": 1,
   "denominator": 8,
   "value": 0.125
  },
  "evidence_validity": {
   "numerator": 10,
   "denominator": 10,
   "value": 1.0,
   "evidence_checked_cases": 10,
   "evidence_valid_cases": 10,
   "evidence_invalid_cases": 0
  },
  "positive_resolution_coverage": {
   "numerator": 9,
   "denominator": 12,
   "value": 0.75
  },
  "correct_positive_resolution_coverage": {
   "numerator": 9,
   "denominator": 12,
   "value": 0.75
  },
  "descriptive_resolution_summary": {
   "descriptive_positive_cases": 6,
   "descriptive_correctly_resolved": 3,
   "descriptive_ambiguous": 3,
   "descriptive_unresolved": 0,
   "descriptive_wrong_confident": 0
  },
  "corrective_handling_correct": 1,
  "corrective_handling_incorrect": 0
 },
 "failure_taxonomy_counts": {
  "COMPETITION_AMBIGUITY": 3,
  "WRONG_CONFIDENT_RESOLUTION": 1
 },
 "category_summaries": {
  "accepted_alias": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_resolve": 1
   },
   "failure_types": {}
  },
  "ambiguous_terminology": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_ambiguous": 1
   },
   "failure_types": {}
  },
  "corrective_term": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_abstain": 1
   },
   "failure_types": {}
  },
  "data_product_description": {
   "cases": 1,
   "applicable": 1,
   "correct": 0,
   "incorrect": 1,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "wrong_ambiguous": 1
   },
   "failure_types": {
    "COMPETITION_AMBIGUITY": 1
   }
  },
  "descriptive_domain_paraphrase": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_resolve": 1
   },
   "failure_types": {}
  },
  "documentation_vs_concept": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_resolve": 1
   },
   "failure_types": {}
  },
  "exact_canonical_terminology": {
   "cases": 2,
   "applicable": 2,
   "correct": 1,
   "incorrect": 1,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_resolve": 1,
    "wrong_ambiguous": 1
   },
   "failure_types": {
    "COMPETITION_AMBIGUITY": 1
   }
  },
  "exact_technical_identifier": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_ambiguous": 1
   },
   "failure_types": {}
  },
  "implementation_description_paraphrase": {
   "cases": 1,
   "applicable": 0,
   "correct": 0,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 1,
   "false_positive_resolutions": 0,
   "decisions": {
    "not_applicable": 1
   },
   "failure_types": {
    "CASE_INVALID": 1
   }
  },
  "multi_mention_isolation": {
   "cases": 1,
   "applicable": 1,
   "correct": 0,
   "incorrect": 1,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "wrong_ambiguous": 1
   },
   "failure_types": {
    "COMPETITION_AMBIGUITY": 1
   }
  },
  "path_reference": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_resolve": 1
   },
   "failure_types": {}
  },
  "query_expansion_negative_control": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_abstain": 1
   },
   "failure_types": {}
  },
  "related_but_not_identical": {
   "cases": 2,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 1,
   "false_positive_resolutions": 0,
   "decisions": {
    "not_applicable": 1,
    "correct_resolve": 1
   },
   "failure_types": {
    "CASE_INVALID": 1
   }
  },
  "source_native_symbol": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_resolve": 1
   },
   "failure_types": {}
  },
  "unsupported_expression": {
   "cases": 2,
   "applicable": 2,
   "correct": 2,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_abstain": 2
   },
   "failure_types": {}
  },
  "version_sensitive_identifier": {
   "cases": 3,
   "applicable": 3,
   "correct": 2,
   "incorrect": 1,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 1,
   "decisions": {
    "correct_resolve": 1,
    "wrong_resolve": 1,
    "correct_abstain": 1
   },
   "failure_types": {
    "WRONG_CONFIDENT_RESOLUTION": 1
   }
  },
  "workflow_description": {
   "cases": 1,
   "applicable": 1,
   "correct": 1,
   "incorrect": 0,
   "not_applicable": 0,
   "case_invalid": 0,
   "false_positive_resolutions": 0,
   "decisions": {
    "correct_resolve": 1
   },
   "failure_types": {}
  }
 },
 "per_case_results": [
  {
   "case_id": "C01",
   "category": "exact_canonical_terminology",
   "question": "What does concept.luminosityfit.luminosity_fit_model describe?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "expected_canonical_object_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "expected_resolution_kind": "true_identity",
   "expected_evidence_tier": "G",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot",
     "restgas_determination",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "concept.luminosityfit.luminosity_fit_model",
       "mention_kind": "governed_id",
       "support_span": "concept.luminosityfit.luminosity_fit_model",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "concept.luminosityfit.luminosity_fit_model",
       "canonical_object_id": "concept.luminosityfit.luminosity_fit_model",
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "G",
         "kind": "canonical_object_id",
         "matched_value": "concept.luminosityfit.luminosity_fit_model",
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "detail": "governed object id stated verbatim in the question"
        }
       ],
       "candidates": [],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "concept.luminosityfit.luminosity_fit_model"
     ],
     "fallback_required": false
    },
    "statuses": [
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "resolved"
  },
  {
   "case_id": "C02",
   "category": "exact_canonical_terminology",
   "question": "How is the luminosity fit model used?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "expected_canonical_object_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "expected_resolution_kind": "descriptive_inferential",
   "expected_evidence_tier": "D",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": false,
   "decision": "wrong_ambiguous",
   "primary_failure_type": "COMPETITION_AMBIGUITY",
   "failure_detail": "no resolution satisfied expected status RESOLVED_UNIQUE with the expected identity targets",
   "evidence_valid": null,
   "has_confident_resolve": false,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot",
     "restgas_determination",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": [
       {
        "value": "luminosity fit model",
        "support_spans": [
         "luminosity fit model"
        ]
       }
      ]
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "luminosity fit model",
       "mention_kind": "descriptive",
       "support_span": "luminosity fit model",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.li_2026.restgas_effective_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "paper.pflueger_2017.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 3 candidates at 3 features",
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "luminosity fit model"
     ],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "AMBIGUOUS"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "ambiguous"
  },
  {
   "case_id": "C03",
   "category": "exact_technical_identifier",
   "question": "How does PndLmdTrackQ work?",
   "expected_status": "AMBIGUOUS",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "none",
   "expected_evidence_tier": "none",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_ambiguous",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": null,
   "has_confident_resolve": false,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot",
     "restgas_determination",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PndLmdTrackQ",
       "mention_kind": "explicit_identifier",
       "support_span": "PndLmdTrackQ",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "object.11268c4b6743544a8c5494e6",
         "source_id": "pandaroot",
         "source_version_id": "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdTrackQ",
         "tier": "S",
         "status": "PROMOTED",
         "reason": "unique exact exact_symbol match within scope"
        },
        {
         "object_id": "object.b786907743079aff236b65b8",
         "source_id": "restgas_determination",
         "source_version_id": "restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdTrackQ",
         "tier": "S",
         "status": "PROMOTED",
         "reason": "unique exact exact_symbol match within scope"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "multiple distinct objects share the exact match",
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "PndLmdTrackQ"
     ],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "AMBIGUOUS"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C04",
   "category": "version_sensitive_identifier",
   "question": "How does PndLmdTrackQ work?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "object.11268c4b6743544a8c5494e6"
   ],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "structural",
   "expected_evidence_tier": "S",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot"
    ],
    "resolved_versions": {
     "pandaroot": "18c09e91100db27867ded30e708b4dae95bd8357"
    },
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PndLmdTrackQ",
       "mention_kind": "explicit_identifier",
       "support_span": "PndLmdTrackQ",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "object.11268c4b6743544a8c5494e6",
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "S",
         "kind": "exact_symbol",
         "matched_value": "PndLmdTrackQ",
         "object_id": "object.11268c4b6743544a8c5494e6",
         "detail": "unique exact_symbol match within locked scope"
        }
       ],
       "candidates": [
        {
         "object_id": "object.11268c4b6743544a8c5494e6",
         "source_id": "pandaroot",
         "source_version_id": "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdTrackQ",
         "tier": "S",
         "status": "PROMOTED",
         "reason": "unique exact exact_symbol match within scope"
        },
        {
         "object_id": "object.b786907743079aff236b65b8",
         "source_id": "restgas_determination",
         "source_version_id": "restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdTrackQ",
         "tier": "S",
         "status": "REJECTED_SCOPE",
         "reason": "rejected by source-scope safety"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {
         "pandaroot": "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357"
        }
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": [
         {
          "object_id": "object.b786907743079aff236b65b8",
          "reason": "REJECTED_SCOPE"
         }
        ]
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "object.11268c4b6743544a8c5494e6"
     ],
     "fallback_required": false
    },
    "statuses": [
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "object.11268c4b6743544a8c5494e6"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "resolved"
  },
  {
   "case_id": "C05",
   "category": "source_native_symbol",
   "question": "How does PndLmdCombinedDataReader work?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "object.c60a8a86eb1b0578b83a8fa2"
   ],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "structural",
   "expected_evidence_tier": "S",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PndLmdCombinedDataReader",
       "mention_kind": "explicit_identifier",
       "support_span": "PndLmdCombinedDataReader",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "object.c60a8a86eb1b0578b83a8fa2",
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "S",
         "kind": "exact_symbol",
         "matched_value": "PndLmdCombinedDataReader",
         "object_id": "object.c60a8a86eb1b0578b83a8fa2",
         "detail": "unique exact_symbol match within locked scope"
        }
       ],
       "candidates": [
        {
         "object_id": "object.c60a8a86eb1b0578b83a8fa2",
         "source_id": "luminosityfit",
         "source_version_id": "luminosityfit@ddd83dcd1a74093bf48ef259a2849a67f9413f32",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdCombinedDataReader",
         "tier": "S",
         "status": "PROMOTED",
         "reason": "unique exact exact_symbol match within scope"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "object.c60a8a86eb1b0578b83a8fa2"
     ],
     "fallback_required": false
    },
    "statuses": [
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "object.c60a8a86eb1b0578b83a8fa2"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "resolved"
  },
  {
   "case_id": "C06",
   "category": "path_reference",
   "question": "Where is detectors/lmd/LmdQA/PndLmdTrackQ.cxx defined?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "object.91b3e79331a311bb259f6a04"
   ],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "structural",
   "expected_evidence_tier": "S",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
       "mention_kind": "explicit_identifier",
       "support_span": "detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "object.91b3e79331a311bb259f6a04",
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "S",
         "kind": "exact_title",
         "matched_value": "detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
         "object_id": "object.91b3e79331a311bb259f6a04",
         "detail": "unique exact_title match within locked scope"
        }
       ],
       "candidates": [
        {
         "object_id": "object.91b3e79331a311bb259f6a04",
         "source_id": "pandaroot",
         "source_version_id": "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
         "match_kind": "exact_title",
         "matched_value": "detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
         "tier": "S",
         "status": "PROMOTED",
         "reason": "unique exact exact_title match within scope"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "object.91b3e79331a311bb259f6a04"
     ],
     "fallback_required": false
    },
    "statuses": [
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "object.91b3e79331a311bb259f6a04"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "resolved"
  },
  {
   "case_id": "C07",
   "category": "accepted_alias",
   "question": "Which output file is *_pid_final.root?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "data_product.restgas.pid_final_root"
   ],
   "expected_canonical_object_ids": [
    "data_product.restgas.pid_final_root"
   ],
   "expected_resolution_kind": "true_identity",
   "expected_evidence_tier": "G",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "restgas_determination"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "*_pid_final.root",
       "mention_kind": "accepted_alias",
       "support_span": "*_pid_final.root",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "data_product.restgas.pid_final_root",
       "canonical_object_id": "data_product.restgas.pid_final_root",
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "G",
         "kind": "true_alias",
         "matched_value": "*_pid_final.root",
         "object_id": "data_product.restgas.pid_final_root",
         "detail": "accepted true-identity alias maps the mention to its governed target"
        }
       ],
       "candidates": [
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "accepted_alias",
         "matched_value": "*_pid_final.root",
         "tier": "G",
         "status": "PROMOTED",
         "reason": "accepted alias resolves one validated target"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "_pid_final.root",
       "mention_kind": "explicit_identifier",
       "support_span": "_pid_final.root",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "_pid_final.root",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 2 candidates at 3 features",
        "abstention_reason": null,
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "Which output file is *_pid_final.root?",
       "mention_kind": "descriptive",
       "support_span": "Which output file is *_pid_final.root?",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "configuration.restgas_profile",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "file_pattern.restgas_profile_input",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "Which output file is *_pid_final.root?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 2 candidates at 4 features",
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "_pid_final.root",
      "Which output file is *_pid_final.root?"
     ],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "data_product.restgas.pid_final_root"
     ],
     "fallback_required": true
    },
    "statuses": [
     "RESOLVED_UNIQUE",
     "AMBIGUOUS",
     "AMBIGUOUS"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "data_product.restgas.pid_final_root"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": true,
   "explicit_canonicalization_valid": true,
   "primary_target_outcome": "resolved"
  },
  {
   "case_id": "C08",
   "category": "corrective_term",
   "question": "Where is restgas_profile.txt read?",
   "expected_status": "UNRESOLVED",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "corrective",
   "expected_evidence_tier": "corrective",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_abstain",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": false,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "restgas_determination"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "restgas_profile.txt",
       "mention_kind": "accepted_alias",
       "support_span": "restgas_profile.txt",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "corrective",
         "kind": "corrective_term",
         "matched_value": "restgas_profile.txt",
         "object_id": "configuration.restgas_profile",
         "detail": "The locked corpus contains no literal file named restgas_profile.txt; it uses the restgas_profile configuration key and concrete restgas_16012024_*.txt profile files."
        }
       ],
       "candidates": [
        {
         "object_id": "configuration.restgas_profile",
         "source_id": "",
         "source_version_id": "",
         "match_kind": "corrective_term",
         "matched_value": "restgas_profile.txt",
         "tier": "corrective",
         "status": "CANDIDATE_ONLY",
         "reason": "corrective term generates a candidate without identity authority"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": true,
        "correction_message": "The locked corpus contains no literal file named restgas_profile.txt; it uses the restgas_profile configuration key and concrete restgas_16012024_*.txt profile files.",
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "corrective term requires user-facing correction; not identity evidence",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [
      {
       "surface_term": "restgas_profile.txt",
       "target_candidate": "configuration.restgas_profile",
       "correction_message": "The locked corpus contains no literal file named restgas_profile.txt; it uses the restgas_profile configuration key and concrete restgas_16012024_*.txt profile files.",
       "identity_authority": false
      }
     ],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "UNRESOLVED"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C09",
   "category": "descriptive_domain_paraphrase",
   "question": "How is the model used to extract luminosity from the LMD angular distribution defined?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "expected_canonical_object_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "expected_resolution_kind": "descriptive_inferential",
   "expected_evidence_tier": "D",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot",
     "restgas_determination",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": [
       {
        "value": "the model used to extract luminosity from the LMD angular distribution",
        "support_spans": [
         "the model used to extract luminosity from the LMD angular distribution"
        ]
       }
      ]
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "LMD",
       "mention_kind": "explicit_identifier",
       "support_span": "LMD",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LMD",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LMD",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LMD",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LMD",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LMD",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "the model used to extract luminosity from the LMD angular distribution",
       "mention_kind": "descriptive",
       "support_span": "the model used to extract luminosity from the LMD angular distribution",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "concept.luminosityfit.luminosity_fit_model",
       "canonical_object_id": "concept.luminosityfit.luminosity_fit_model",
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "D",
         "kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "detail": "governed descriptive-evidence bundle satisfied; features=4; matched=['angular', 'distribution', 'luminosity', 'model']"
        }
       ],
       "candidates": [
        {
         "object_id": "concept.li_2026.restgas_effective_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.pflueger_2017.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model used to extract luminosity from the LMD angular distribution",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": true,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [
      "LMD"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "concept.luminosityfit.luminosity_fit_model"
     ],
     "fallback_required": true
    },
    "statuses": [
     "UNRESOLVED",
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "resolved"
  },
  {
   "case_id": "C10",
   "category": "implementation_description_paraphrase",
   "question": "Where is the model-and-fit subsystem of the LuminosityFit framework implemented?",
   "expected_status": "AMBIGUOUS",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "none",
   "expected_evidence_tier": "none",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": true,
   "correct": false,
   "decision": "not_applicable",
   "primary_failure_type": "CASE_INVALID",
   "failure_detail": "Source-first Gold violation recorded after the first measured run: the expected AMBIGUOUS status was influenced by the frozen resolver's lexical competition behavior rather than being determined purely from source semantics. The raw receipt is preserved as qualitative RELATED_ENTITY_OVERRESOLUTION evidence for D2-A3; the case is excluded from quantitative metrics.",
   "evidence_valid": null,
   "has_confident_resolve": true,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot",
     "restgas_determination",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": [
       {
        "value": "the model-and-fit subsystem of the LuminosityFit framework",
        "support_spans": [
         "the model-and-fit subsystem of the LuminosityFit framework"
        ]
       }
      ]
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "LuminosityFit",
       "mention_kind": "explicit_identifier",
       "support_span": "LuminosityFit",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.li_2026.restgas_effective_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "paper.pflueger_2017.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "LuminosityFit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 5 candidates at 2 features",
        "abstention_reason": null,
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "model-and-fit",
       "mention_kind": "explicit_identifier",
       "support_span": "model-and-fit",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "model-and-fit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "model-and-fit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.pflueger_2017.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "model-and-fit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "model-and-fit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "model-and-fit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "model-and-fit",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 3 candidates at 2 features",
        "abstention_reason": null,
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "the model-and-fit subsystem of the LuminosityFit framework",
       "mention_kind": "descriptive",
       "support_span": "the model-and-fit subsystem of the LuminosityFit framework",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "concept.luminosityfit.luminosity_fit_model",
       "canonical_object_id": "concept.luminosityfit.luminosity_fit_model",
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "D",
         "kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "detail": "governed descriptive-evidence bundle satisfied; features=5; matched=['fit', 'framework', 'luminosity', 'model', 'subsystem']"
        }
       ],
       "candidates": [
        {
         "object_id": "concept.li_2026.restgas_effective_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=5"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "paper.pflueger_2017.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the model-and-fit subsystem of the LuminosityFit framework",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": true,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "LuminosityFit",
      "model-and-fit"
     ],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "concept.luminosityfit.luminosity_fit_model"
     ],
     "fallback_required": true
    },
    "statuses": [
     "AMBIGUOUS",
     "AMBIGUOUS",
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [
    "concept.luminosityfit.luminosity_fit_model"
   ],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C11",
   "category": "workflow_description",
   "question": "Which step is the step that reads the first PID output and writes the boost ROOT file?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "workflow.restgas.first_pass_poca"
   ],
   "expected_canonical_object_ids": [
    "workflow.restgas.first_pass_poca"
   ],
   "expected_resolution_kind": "descriptive_inferential",
   "expected_evidence_tier": "D",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "restgas_determination",
     "pandaroot"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": [
       {
        "value": "the step that reads the first PID output and writes the boost ROOT file",
        "support_spans": [
         "the step that reads the first PID output and writes the boost ROOT file"
        ]
       }
      ]
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PID",
       "mention_kind": "explicit_identifier",
       "support_span": "PID",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "ROOT",
       "mention_kind": "explicit_identifier",
       "support_span": "ROOT",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "the step that reads the first PID output and writes the boost ROOT file",
       "mention_kind": "descriptive",
       "support_span": "the step that reads the first PID output and writes the boost ROOT file",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "workflow.restgas.first_pass_poca",
       "canonical_object_id": "workflow.restgas.first_pass_poca",
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "D",
         "kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "object_id": "workflow.restgas.first_pass_poca",
         "detail": "governed descriptive-evidence bundle satisfied; features=6; matched=['boost', 'first', 'output', 'pid', 'root', 'writes']"
        }
       ],
       "candidates": [
        {
         "object_id": "configuration.restgas_profile",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "file_pattern.restgas_profile_input",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=6"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=5; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the step that reads the first PID output and writes the boost ROOT file",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": true,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [
      "PID",
      "ROOT"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "workflow.restgas.first_pass_poca"
     ],
     "fallback_required": true
    },
    "statuses": [
     "UNRESOLVED",
     "UNRESOLVED",
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "workflow.restgas.first_pass_poca"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "resolved"
  },
  {
   "case_id": "C12",
   "category": "data_product_description",
   "question": "Where is the boost ROOT output that contains the event_poca tree written?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "data_product.restgas.boost_root"
   ],
   "expected_canonical_object_ids": [
    "data_product.restgas.boost_root"
   ],
   "expected_resolution_kind": "descriptive_inferential",
   "expected_evidence_tier": "D",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": false,
   "decision": "wrong_ambiguous",
   "primary_failure_type": "COMPETITION_AMBIGUITY",
   "failure_detail": "no resolution satisfied expected status RESOLVED_UNIQUE with the expected identity targets",
   "evidence_valid": null,
   "has_confident_resolve": true,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "restgas_determination"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": [
       {
        "value": "the boost ROOT output that contains the event_poca tree",
        "support_spans": [
         "the boost ROOT output that contains the event_poca tree"
        ]
       }
      ]
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "event_poca",
       "mention_kind": "explicit_identifier",
       "support_span": "event_poca",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "data_product.restgas.event_poca",
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "S",
         "kind": "exact_title",
         "matched_value": "event_poca",
         "object_id": "data_product.restgas.event_poca",
         "detail": "unique exact_title match within locked scope"
        }
       ],
       "candidates": [
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "exact_title",
         "matched_value": "event_poca",
         "tier": "S",
         "status": "PROMOTED",
         "reason": "unique exact exact_title match within scope"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "ROOT",
       "mention_kind": "explicit_identifier",
       "support_span": "ROOT",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "ROOT",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "the boost ROOT output that contains the event_poca tree",
       "mention_kind": "descriptive",
       "support_span": "the boost ROOT output that contains the event_poca tree",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=6; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=6; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the boost ROOT output that contains the event_poca tree",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 2 candidates at 6 features",
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "the boost ROOT output that contains the event_poca tree"
     ],
     "unresolved_mentions": [
      "ROOT"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "data_product.restgas.event_poca"
     ],
     "fallback_required": true
    },
    "statuses": [
     "RESOLVED_UNIQUE",
     "UNRESOLVED",
     "AMBIGUOUS"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [
    "data_product.restgas.event_poca"
   ],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [
    "data_product.restgas.event_poca"
   ],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "ambiguous"
  },
  {
   "case_id": "C13",
   "category": "ambiguous_terminology",
   "question": "Where is the PID data product?",
   "expected_status": "AMBIGUOUS",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "none",
   "expected_evidence_tier": "none",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_ambiguous",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": null,
   "has_confident_resolve": false,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "restgas_determination"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": [
       {
        "value": "the PID data product",
        "support_spans": [
         "the PID data product"
        ]
       }
      ]
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PID",
       "mention_kind": "explicit_identifier",
       "support_span": "PID",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PID",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "the PID data product",
       "mention_kind": "descriptive",
       "support_span": "the PID data product",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.restgas_longitudinal_efficiency",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.reconstructed_restgas_profile",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "the PID data product",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 5 candidates at 3 features",
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "the PID data product"
     ],
     "unresolved_mentions": [
      "PID"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "UNRESOLVED",
     "AMBIGUOUS"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C14",
   "category": "related_but_not_identical",
   "question": "What does PndLmdModelFactory do?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "object.ceb44bd02a5e3a790cf2dfad"
   ],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "structural",
   "expected_evidence_tier": "S",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": true,
   "correct": false,
   "decision": "not_applicable",
   "primary_failure_type": "CASE_INVALID",
   "failure_detail": "Curation inventory error recorded after the first measured run: the authoritative symbol-bearing record for PndLmdModelFactory is the function row object.c08459387c6fd0c77a717960, while the frozen expectation declared the source_file row object.ceb44bd02a5e3a790cf2dfad. Recorded INVALID_CASE per the D2-A2 freeze discipline; not replaced.",
   "evidence_valid": null,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PndLmdModelFactory",
       "mention_kind": "explicit_identifier",
       "support_span": "PndLmdModelFactory",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "object.c08459387c6fd0c77a717960",
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "S",
         "kind": "exact_symbol",
         "matched_value": "PndLmdModelFactory",
         "object_id": "object.c08459387c6fd0c77a717960",
         "detail": "unique exact_symbol match within locked scope"
        }
       ],
       "candidates": [
        {
         "object_id": "object.c08459387c6fd0c77a717960",
         "source_id": "luminosityfit",
         "source_version_id": "luminosityfit@ddd83dcd1a74093bf48ef259a2849a67f9413f32",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdModelFactory",
         "tier": "S",
         "status": "PROMOTED",
         "reason": "unique exact exact_symbol match within scope"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "object.c08459387c6fd0c77a717960"
     ],
     "fallback_required": false
    },
    "statuses": [
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [
    "object.c08459387c6fd0c77a717960"
   ],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "unresolved"
  },
  {
   "case_id": "C15",
   "category": "related_but_not_identical",
   "question": "What is event_poca?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "data_product.restgas.event_poca"
   ],
   "expected_canonical_object_ids": [
    "data_product.restgas.event_poca"
   ],
   "expected_resolution_kind": "structural",
   "expected_evidence_tier": "S",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "restgas_determination"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "event_poca",
       "mention_kind": "explicit_identifier",
       "support_span": "event_poca",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "data_product.restgas.event_poca",
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "S",
         "kind": "exact_title",
         "matched_value": "event_poca",
         "object_id": "data_product.restgas.event_poca",
         "detail": "unique exact_title match within locked scope"
        }
       ],
       "candidates": [
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "exact_title",
         "matched_value": "event_poca",
         "tier": "S",
         "status": "PROMOTED",
         "reason": "unique exact exact_title match within scope"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "data_product.restgas.event_poca"
     ],
     "fallback_required": false
    },
    "statuses": [
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "data_product.restgas.event_poca"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "resolved"
  },
  {
   "case_id": "C16",
   "category": "version_sensitive_identifier",
   "question": "How does PndLmdTrackQ work?",
   "expected_status": "REJECTED_VERSION",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "none",
   "expected_evidence_tier": "none",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": false,
   "decision": "wrong_resolve",
   "primary_failure_type": "WRONG_CONFIDENT_RESOLUTION",
   "failure_detail": "resolution 'How does PndLmdTrackQ work?' confidently resolved workflow.pandaroot.lmd_reconstruction in a case expecting REJECTED_VERSION",
   "evidence_valid": null,
   "has_confident_resolve": true,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot"
    ],
    "resolved_versions": {
     "pandaroot": "0000000000000000000000000000000000000000"
    },
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PndLmdTrackQ",
       "mention_kind": "explicit_identifier",
       "support_span": "PndLmdTrackQ",
       "status": "REJECTED_VERSION",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "object.b786907743079aff236b65b8",
         "source_id": "restgas_determination",
         "source_version_id": "restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdTrackQ",
         "tier": "S",
         "status": "REJECTED_SCOPE",
         "reason": "rejected by source-scope safety"
        },
        {
         "object_id": "object.11268c4b6743544a8c5494e6",
         "source_id": "pandaroot",
         "source_version_id": "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdTrackQ",
         "tier": "S",
         "status": "REJECTED_VERSION",
         "reason": "rejected by locked-version safety"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {
         "pandaroot": "pandaroot@0000000000000000000000000000000000000000"
        }
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": [
         {
          "object_id": "object.11268c4b6743544a8c5494e6",
          "reason": "REJECTED_VERSION"
         },
         {
          "object_id": "object.b786907743079aff236b65b8",
          "reason": "REJECTED_SCOPE"
         }
        ]
       }
      },
      {
       "mention_text": "How does PndLmdTrackQ work?",
       "mention_kind": "descriptive",
       "support_span": "How does PndLmdTrackQ work?",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "workflow.pandaroot.lmd_reconstruction",
       "canonical_object_id": "workflow.pandaroot.lmd_reconstruction",
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "D",
         "kind": "descriptive_inference",
         "matched_value": "How does PndLmdTrackQ work?",
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "detail": "governed descriptive-evidence bundle satisfied; features=2; matched=['lmd', 'track']"
        }
       ],
       "candidates": [
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdTrackQ work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdTrackQ work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdTrackQ work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdTrackQ work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdTrackQ work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdTrackQ work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {
         "pandaroot": "pandaroot@0000000000000000000000000000000000000000"
        }
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": true,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [
      "PndLmdTrackQ"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "workflow.pandaroot.lmd_reconstruction"
     ],
     "fallback_required": true
    },
    "statuses": [
     "REJECTED_VERSION",
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [
    "workflow.pandaroot.lmd_reconstruction"
   ],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C17",
   "category": "version_sensitive_identifier",
   "question": "How does PndLmdCombinedDataReader work?",
   "expected_status": "REJECTED_SCOPE",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "none",
   "expected_evidence_tier": "none",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_abstain",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": null,
   "has_confident_resolve": false,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PndLmdCombinedDataReader",
       "mention_kind": "explicit_identifier",
       "support_span": "PndLmdCombinedDataReader",
       "status": "REJECTED_SCOPE",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "object.c60a8a86eb1b0578b83a8fa2",
         "source_id": "luminosityfit",
         "source_version_id": "luminosityfit@ddd83dcd1a74093bf48ef259a2849a67f9413f32",
         "match_kind": "exact_symbol",
         "matched_value": "PndLmdCombinedDataReader",
         "tier": "S",
         "status": "REJECTED_SCOPE",
         "reason": "rejected by source-scope safety"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": null,
        "rejection_reasons": [
         {
          "object_id": "object.c60a8a86eb1b0578b83a8fa2",
          "reason": "REJECTED_SCOPE"
         }
        ]
       }
      },
      {
       "mention_text": "How does PndLmdCombinedDataReader work?",
       "mention_kind": "descriptive",
       "support_span": "How does PndLmdCombinedDataReader work?",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.restgas_longitudinal_efficiency",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.reconstructed_restgas_profile",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How does PndLmdCombinedDataReader work?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 3 candidates at 2 features",
        "abstention_reason": null,
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "How does PndLmdCombinedDataReader work?"
     ],
     "unresolved_mentions": [
      "PndLmdCombinedDataReader"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "REJECTED_SCOPE",
     "AMBIGUOUS"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C18",
   "category": "unsupported_expression",
   "question": "What is the unrelated nonexistent calibration concept?",
   "expected_status": "UNRESOLVED",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "none",
   "expected_evidence_tier": "none",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_abstain",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": null,
   "has_confident_resolve": false,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot",
     "restgas_determination",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "What is the unrelated nonexistent calibration concept?",
       "mention_kind": "descriptive",
       "support_span": "What is the unrelated nonexistent calibration concept?",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.li_2026.restgas_effective_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the unrelated nonexistent calibration concept?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the unrelated nonexistent calibration concept?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "concept.restgas_longitudinal_efficiency",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the unrelated nonexistent calibration concept?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.reconstructed_restgas_profile",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the unrelated nonexistent calibration concept?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.pflueger_2017.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the unrelated nonexistent calibration concept?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the unrelated nonexistent calibration concept?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the unrelated nonexistent calibration concept?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [
      "What is the unrelated nonexistent calibration concept?"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "UNRESOLVED"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C19",
   "category": "unsupported_expression",
   "question": "How is the model configured?",
   "expected_status": "UNRESOLVED",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "none",
   "expected_evidence_tier": "none",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_abstain",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": null,
   "has_confident_resolve": false,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot",
     "restgas_determination",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "How is the model configured?",
       "mention_kind": "descriptive",
       "support_span": "How is the model configured?",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How is the model configured?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.pflueger_2017.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How is the model configured?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "How is the model configured?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [
      "How is the model configured?"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "UNRESOLVED"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C20",
   "category": "query_expansion_negative_control",
   "question": "What is the acceptance class?",
   "expected_status": "UNRESOLVED",
   "expected_object_ids": [],
   "expected_canonical_object_ids": [],
   "expected_resolution_kind": "none",
   "expected_evidence_tier": "none",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_abstain",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": null,
   "has_confident_resolve": false,
   "has_ambiguous": false,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "restgas_determination",
     "pandaroot",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": []
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "What is the acceptance class?",
       "mention_kind": "descriptive",
       "support_span": "What is the acceptance class?",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.li_2026.restgas_effective_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the acceptance class?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the acceptance class?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the acceptance class?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the acceptance class?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "What is the acceptance class?",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "restgas_determination",
         "pandaroot",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [],
     "unresolved_mentions": [
      "What is the acceptance class?"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "UNRESOLVED"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null
  },
  {
   "case_id": "C21",
   "category": "multi_mention_isolation",
   "question": "How does the luminosity fit model relate to the first-pass POCA workflow?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "concept.luminosityfit.luminosity_fit_model",
    "workflow.restgas.first_pass_poca"
   ],
   "expected_canonical_object_ids": [
    "concept.luminosityfit.luminosity_fit_model",
    "workflow.restgas.first_pass_poca"
   ],
   "expected_resolution_kind": "descriptive_inferential",
   "expected_evidence_tier": "D",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": false,
   "decision": "wrong_ambiguous",
   "primary_failure_type": "COMPETITION_AMBIGUITY",
   "failure_detail": "no resolution satisfied expected status RESOLVED_UNIQUE with the expected identity targets",
   "evidence_valid": null,
   "has_confident_resolve": false,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot",
     "restgas_determination",
     "luminosityfit"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": [
       {
        "value": "luminosity fit model",
        "support_spans": [
         "luminosity fit model"
        ]
       },
       {
        "value": "first-pass POCA workflow",
        "support_spans": [
         "first-pass POCA workflow"
        ]
       }
      ]
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "first-pass",
       "mention_kind": "explicit_identifier",
       "support_span": "first-pass",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 4 candidates at 2 features",
        "abstention_reason": null,
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "POCA",
       "mention_kind": "explicit_identifier",
       "support_span": "POCA",
       "status": "UNRESOLVED",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "POCA",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "POCA",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "POCA",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "POCA",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "POCA",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "POCA",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": null,
        "abstention_reason": "single_feature",
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "first-pass POCA workflow",
       "mention_kind": "descriptive",
       "support_span": "first-pass POCA workflow",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.li_2026.restgas_effective_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "configuration.restgas_profile",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "file_pattern.restgas_profile_input",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "first-pass POCA workflow",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 4 candidates at 4 features",
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "luminosity fit model",
       "mention_kind": "descriptive",
       "support_span": "luminosity fit model",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "concept.li_2026.restgas_effective_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "concept.luminosityfit.luminosity_fit_model",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "paper.pflueger_2017.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.model_and_fit",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_aware_luminosity_acceptance",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas_profile_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "luminosity fit model",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "restgas_determination",
         "luminosityfit",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 3 candidates at 3 features",
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "first-pass",
      "first-pass POCA workflow",
      "luminosity fit model"
     ],
     "unresolved_mentions": [
      "POCA"
     ],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [],
     "fallback_required": true
    },
    "statuses": [
     "AMBIGUOUS",
     "UNRESOLVED",
     "AMBIGUOUS",
     "AMBIGUOUS"
    ]
   },
   "target_match_mode": "ALL",
   "expected_target_count": 2,
   "resolved_expected_targets": [],
   "missing_expected_targets": [
    "concept.luminosityfit.luminosity_fit_model",
    "workflow.restgas.first_pass_poca"
   ],
   "mention_isolation_valid": true,
   "isolation_details": [
    "no cross-mention token leakage observed"
   ],
   "confident_required_target_ids": [],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "ambiguous"
  },
  {
   "case_id": "C22",
   "category": "documentation_vs_concept",
   "question": "Where is the PandaRoot Sphinx documentation?",
   "expected_status": "RESOLVED_UNIQUE",
   "expected_object_ids": [
    "document.pandaroot_sphinx_2023_08_25_dev"
   ],
   "expected_canonical_object_ids": [
    "document.pandaroot_sphinx_2023_08_25_dev"
   ],
   "expected_resolution_kind": "descriptive_inferential",
   "expected_evidence_tier": "D",
   "applicability": "AVAILABLE",
   "not_applicable": false,
   "case_invalid": false,
   "correct": true,
   "decision": "correct_resolve",
   "primary_failure_type": null,
   "failure_detail": null,
   "evidence_valid": true,
   "has_confident_resolve": true,
   "has_ambiguous": true,
   "plan": {
    "intent": "terminology_resolution",
    "target_repositories": [
     "pandaroot"
    ],
    "resolved_versions": {},
    "resolved_aliases": {},
    "symbols": [],
    "concepts": [],
    "analysis_diagnostics": {
     "analyzer_accepted_semantic_delta": {
      "symbols": [],
      "concepts": [
       {
        "value": "PandaRoot Sphinx documentation",
        "support_spans": [
         "PandaRoot Sphinx documentation"
        ]
       }
      ]
     }
    }
   },
   "actual": {
    "receipt": {
     "identity_relation_support": "ACTIVE_SHADOW",
     "resolutions": [
      {
       "mention_text": "PandaRoot",
       "mention_kind": "explicit_identifier",
       "support_span": "PandaRoot",
       "status": "AMBIGUOUS",
       "matched_object_id": null,
       "canonical_object_id": null,
       "selected_object_ids": [],
       "evidence": [],
       "candidates": [
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": false,
        "corrective": false,
        "correction_message": null,
        "identity_authority": false,
        "ambiguity_reason": "descriptive evidence ties between 6 candidates at 2 features",
        "abstention_reason": null,
        "rejection_reasons": []
       }
      },
      {
       "mention_text": "PandaRoot Sphinx documentation",
       "mention_kind": "descriptive",
       "support_span": "PandaRoot Sphinx documentation",
       "status": "RESOLVED_UNIQUE",
       "matched_object_id": "document.pandaroot_sphinx_2023_08_25_dev",
       "canonical_object_id": "document.pandaroot_sphinx_2023_08_25_dev",
       "selected_object_ids": [],
       "evidence": [
        {
         "tier": "D",
         "kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "detail": "governed descriptive-evidence bundle satisfied; features=4; matched=['documentation', 'panda', 'root', 'sphinx']"
        }
       ],
       "candidates": [
        {
         "object_id": "data_product.pandaroot.lumi_trks_qa",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "data_product.restgas.boost_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.event_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_final_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "data_product.restgas.pid_root",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "document.pandaroot_sphinx_2023_08_25_dev",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=4"
        },
        {
         "object_id": "paper.karavdina_2015.chapter_4",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "subsystem.luminosityfit.panda_data_io",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.generic",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=3; tied_with_competitor"
        },
        {
         "object_id": "workflow.pandaroot.lmd_reconstruction",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=True; features=2; tied_with_competitor"
        },
        {
         "object_id": "workflow.restgas.first_pass_poca",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        },
        {
         "object_id": "workflow.restgas.second_pass_pid",
         "source_id": "curated_panda_domain",
         "source_version_id": "curated_panda_domain@1.0",
         "match_kind": "descriptive_inference",
         "matched_value": "PandaRoot Sphinx documentation",
         "tier": "D",
         "status": "PROMOTED",
         "reason": "descriptive bundle eligible=False; features=1; single_feature"
        }
       ],
       "version_scope": {
        "allowed_sources": [
         "pandaroot",
         "curated_panda_domain"
        ],
        "locked_versions": {}
       },
       "diagnostics": {
        "canonicalization": false,
        "descriptive_inference": true,
        "corrective": false,
        "correction_message": null,
        "identity_authority": true,
        "ambiguity_reason": null,
        "abstention_reason": "descriptive mention awaits governed descriptive evaluation",
        "rejection_reasons": []
       }
      }
     ],
     "ambiguous_mentions": [
      "PandaRoot"
     ],
     "unresolved_mentions": [],
     "multi_entity_results": [],
     "corrective_mentions": [],
     "resolved_object_ids": [
      "document.pandaroot_sphinx_2023_08_25_dev"
     ],
     "fallback_required": true
    },
    "statuses": [
     "AMBIGUOUS",
     "RESOLVED_UNIQUE"
    ]
   },
   "target_match_mode": "ANY",
   "expected_target_count": null,
   "resolved_expected_targets": [],
   "missing_expected_targets": [],
   "mention_isolation_valid": null,
   "isolation_details": [],
   "confident_required_target_ids": [
    "document.pandaroot_sphinx_2023_08_25_dev"
   ],
   "confident_allowed_context_ids": [],
   "confident_unexpected_ids": [],
   "allowed_context_object_ids": [],
   "expects_explicit_canonicalization": false,
   "explicit_canonicalization_valid": null,
   "primary_target_outcome": "resolved"
  }
 ],
 "not_applicable_records": [
  {
   "category": "resolved_multiple",
   "reason": "No natural A1 mechanism promotes RESOLVED_MULTIPLE (trailing-s promotion removed in D2-A1R1); natural applicability = 0. Schema support remains representable."
  },
  {
   "category": "same_as",
   "reason": "Current D1 state contains no accepted SAME_AS edges; manufacturing one would violate the D1 co-reference contract. Shadow SAME_AS traversal is separately covered by focused T0 tests."
  }
 ],
 "metric_consistency_problems": [],
 "receipt_consistency_vs_ae7b281": {
  "baseline_commit": "ae7b281",
  "baseline_artifact": "C:\\Users\\JINXIN~1.DES\\AppData\\Local\\Temp\\d2_a2_results_ae7b281.json",
  "compared_cases": 20,
  "identical_receipts": 20,
  "mismatched_case_ids": [],
  "skipped_invalid_cases": [
   "C10",
   "C14"
  ],
  "resolver_behavior_unchanged": true
 }
}
```
END_D2_A2_METRICS


---

## 1. Objective

Evaluate the frozen D2-A1 shadow resolver (baseline `67eff2b`) against a
preregistered, source-grounded terminology/paraphrase case set: how accurately
and conservatively does it map genuine user terminology, technical
identifiers, aliases, descriptive paraphrases, ambiguous expressions,
corrective expressions, and unsupported expressions to the D1-governed entity
space?

## 2. Baseline and provenance

- Resolver implementation baseline: `67eff2b` — verified unchanged: `git diff
  67eff2b HEAD` over `entity_resolution.py` / `descriptive_resolution.py` /
  `retrieval.py` is empty.
- Case artifact: `evaluation/d2_a2_terminology_cases.yaml` (frozen before
  execution; authorized post-freeze amendments limited to C14/C10 invalid
  markers, the C16 encoding repair, and C21 evaluation metadata — no question
  or expected-identity changes).
- Results artifact: `evaluation/d2_a2_results.json`.
- Runner/state: `evaluation/scripts/d2_a2_runner.py` +
  `evaluation/scripts/d2_a2_state.py`; executed with `--receipt-baseline`
  pointing at the `ae7b281` results for the §19 consistency check.
- No model/Vertex/LLM calls; no Qdrant; no production DB writes.

## 3. Evaluation-state construction

Deterministic in-memory D1-compatible fixture state (the A0-acceptable
alternative to a reingested isolated database), materialized via the
PRODUCTION loaders — `seed_knowledge_objects`, `materialize_seed_relations`,
`seed_workflow_steps`, `seed_knowledge_aliases` — plus 8 declared real-corpus
source-native rows (ids/versions/locators verified against
`data/normalized/9925ec31…/knowledge_objects.jsonl`, including the
symbol-bearing `PndLmdTrackQ` class records in both pandaroot and
restgas_determination and the `PndLmdModelFactory` function record added by
the documented state correction in §14). The stale live PostgreSQL state
(133,075 objects predating D1-A2) was deliberately NOT used: missing D1-A2
representative entities there must not be counted as resolver failures.

## 4. Evaluation-state validation gate

All green before execution (`valid = true`): 32 objects, zero duplicate IDs;
the four required representative canonical IDs
(`concept.luminosityfit.luminosity_fit_model`,
`workflow.restgas.first_pass_poca`, `data_product.restgas.pid_final_root`,
`configuration.restgas_profile`) each present exactly once; identity roles ⊆
{canonical, source_native} on all seeds; 2 accepted aliases (1 corrective, 1
true identity); 16 accepted relations; 1 curated WorkflowStep; POCA structured
facts present; resolver probe executed read-only.

## 5. Case curation method and distribution

Source-first per the A0 preregistration: governed entities/conditions selected
from current D1 configs and verified corpus rows → terminology/paraphrases
determined from source semantics → expected status/targets assigned from the
frozen contract → frozen → only then executed. No Gold wording mining; no
pseudo-Gold; no protected data. 22 concrete cases + 2 recorded
NOT_APPLICABLE categories (`RESOLVED_MULTIPLE` natural applicability = 0 —
the trailing-`s` mechanism was removed in D2-A1R1; `SAME_AS` — no accepted
`SAME_AS` edges exist in the current D1 state, and manufacturing one would
violate the D1 co-reference contract). Both are separately covered by focused
T0 tests.

Category coverage: exact canonical terminology (2), exact technical
identifier (1), source-native symbol (1), path reference (1), accepted alias
(1), corrective term (1), descriptive domain paraphrase (1), implementation
description (1), workflow description (1), data-product description (1),
ambiguous terminology (1), related-but-not-identical (2), version-sensitive
(2), unsupported/generic (2), query-expansion negative control (1),
multi-mention isolation (1), documentation-vs-concept (1).

## 6. Exposure policy

Development-visible and source-grounded only. No `novel_holdout`, no
protected holdout, no hidden benchmark content, no T5/release data.

## 7. Case counts and validity

```text
case_counts:
  total = 22          valid = 20
  case_invalid = 2    not_applicable = 0
  correct = 16
case_validity: 20/22 = 0.9091
```

Invalid cases (both recorded with reasons in the case artifact, never
replaced): **C10** — expected status was implementation-informed rather than
source-first (the frozen resolver's lexical tie behavior shaped the expected
AMBIGUOUS); **C14** — curation inventory error (the expected target declared
the source_file row while the authoritative symbol-bearing record is the
function row `object.c08459387c6fd0c77a717960`).

## 8. Decision accounting (valid cases)

```text
correct_resolve   = 9
wrong_resolve     = 1   (C16)
correct_abstain   = 5   (C08, C17, C18, C19, C20)
wrong_abstain     = 0
correct_ambiguous = 2   (C03, C13)
wrong_ambiguous   = 3   (C02, C12, C21)
not_applicable    = 0
```

The accounting sums to the 20 valid cases; `metric_consistency_problems = []`.
C10/C14 are `case_invalid`, not `not_applicable` (Section 7); A2R2 also
reclassified C12 as `wrong_ambiguous` — the boost_root AMBIGUOUS outcome plus
the allowed-context event_poca resolution is a competition-ambiguity failure,
not a wrong identity.

## 9. Preregistered metrics (numerator/denominator/value)

| Metric | Num | Den | Value |
| --- | --- | --- | --- |
| resolution_accuracy (expected RESOLVED_UNIQUE, valid) | 9 | 12 | 0.75 |
| canonical_identity_accuracy (expected-canonical, valid) | 6 | 9 | 0.6667 |
| explicit_canonicalization_accuracy (true-identity alias) | 1 | 1 | 1.0 |
| source_native_noncanonicalization_accuracy | 3 | 3 | 1.0 |
| abstention_accuracy | 5 | 6 | 0.8333 |
| ambiguity_accuracy | 2 | 2 | 1.0 |
| false_positive_resolution_rate (valid negative/control) | 1 | 8 | 0.125 |
| case_validity | 20 | 22 | 0.9091 |
| category_natural_applicability | 14 | 16 | 0.875 |
| execution_coverage | 22 | 22 | 1.0 |
| evidence_validity | 10 | 10 | 1.0 |
| positive_resolution_coverage | 9 | 12 | 0.75 |

`canonical_identity_accuracy` counts cases expecting a canonical identity
(direct canonical match with `canonical_object_id = null`, or valid Tier G
canonicalization). `explicit_canonicalization_accuracy` counts only the
true-identity alias case, where a noncanonical surface form is expected to
canonicalize. `source_native_noncanonicalization_accuracy` counts cases where
`canonical_object_id` must remain null — all three held.

## 10. Corrective-term analysis

C08 (`restgas_profile.txt`): correction surfaced, `identity_authority = false`,
status UNRESOLVED — `corrective_handling_correct = 1`,
`corrective_handling_incorrect = 0`. The corrective term never carried Tier G
authority and was never sent through Tier D.

## 11. Descriptive Tier D summary

```text
descriptive_positive_cases       = 6  (C02, C09, C11, C12, C21, C22; C10 invalid and excluded)
descriptive_correctly_resolved   = 3  (C09, C11, C22)
descriptive_ambiguous            = 3  (C02, C12, C21)
descriptive_unresolved           = 0
descriptive_wrong_confident      = 0
```

## 12. Strong identity (Tier G/S) analysis

All strong-identity cases correct: governed ID (C01), true alias
canonicalization (C07), exact symbol (C05), exact path (C06), and the
scoped/natural collisions (C03 AMBIGUOUS, C04 version-scoped unique). Zero
false cross-record canonicalizations: `PndLmdModelFactory` resolves to its own
function record with `canonical_object_id = null` despite the `IMPLEMENTS`
relation (C14 qualitative receipt), and `event_poca` resolves to itself
despite containment by `boost_root` (C15).

## 13. False-positive resolution analysis

The only formal false positive is **C16**: after the identifier was correctly
`REJECTED_VERSION`, the whole-question fallback confidently resolved to
`workflow.pandaroot.lmd_reconstruction` (2 features). This is the
fallback-granularity finding of Section 15. C10's related-entity
over-resolution is qualitative only (Section 15).

## 14. Multi-mention isolation

C21 verified the A1R1 evidence-isolation repair independently: each mention's
descriptive evidence excludes the other mention's distinctive tokens
(`mention_isolation_valid = true`, no leakage). The C21 failures are the
lexical sibling ties of Section 11, not evidence leakage.

## 15. Qualitative findings from invalidated cases

- **C10** — CASE_INVALID for quantitative scoring because the Gold
  expectation was implementation-informed. The raw receipt still shows: an
  explicit subsystem description produced a **confident resolution to
  `concept.luminosityfit.luminosity_fit_model`** — qualitative
  RELATED_ENTITY_OVERRESOLUTION evidence: the whole-question fallback span
  aggregates tokens and can dominate where mention-level evidence ties. A3
  should review the fallback-span granularity.
- **C14** — CASE_INVALID (curation inventory error); its re-executed receipt
  demonstrates the corrected state resolving the symbol to the function
  record.

## 16. Version/scope analysis

C04 (locked-version unique resolution), C16 (wrong-version rejection), and
C17 (source-scope rejection) behaved per contract; descriptive inference never
bypassed scope/version checks.

## 17. Query-expansion boundary

C20: the QE-only concept never became a mention; the fallback abstention is
retained and `fallback_required = true`. Query expansion helped planning but
did not establish identity.

## 18. Failure taxonomy

```text
COMPETITION_AMBIGUITY        = 3  (C02, C12, C21)
WRONG_CONFIDENT_RESOLUTION   = 1  (C16)
CASE_INVALID                 = 2  (C10, C14 — excluded from formal failure accounting)
```

## 19. Receipt consistency versus the frozen resolver

`receipt_consistency_vs_ae7b281`: 20 unchanged valid cases compared across
statuses/mention texts/matched/canonical/evidence tier+kind/candidate IDs —
**20/20 identical** (C10/C14 skipped as invalid; C14's difference is the
documented §41 state-row correction, not resolver behavior).
`resolver_behavior_unchanged = true`: **evaluation semantics changed; resolver
behavior did not.**

## 20. Limitations

Small targeted set (22 cases) — proves contract behavior, not statistical
quality; the descriptive mechanism is deliberately lexical-only in A1 (frozen
shadow isolation forbade resolver-time model calls); the evaluation state is
a deterministic fixture of the D1 representative space plus 8 real corpus
rows, not the full 133k corpus (the resolver's exact-match layer is value-
driven, so un-declared corpus identifiers are out of scope rather than
missed); C14 was invalidated by a curation inventory error and C10 by a
source-first Gold violation.

## 21. Implications for D2-A3 (evidence package; no role decision here)

D2-A3 must review: (1) strong identity (Tier G/S) is fully reliable — zero
false canonicalizations; (2) corrective terms and abstention are safely
non-authoritative with correct accounting; (3) descriptive Tier D is useful
(3/6 correct) but lexically conservative — sibling/container ties produce
AMBIGUOUS instead of resolution (C02/C12/C21); (4) the whole-question fallback
can over-resolve (C10 qualitative, C16 formal); (5) natural applicability is
meaningful for identity/descriptive/ambiguous/corrective categories and zero
for MULTIPLE/SAME_AS; (6) failures are systematic (two mechanisms), not
scattered. Candidate A3 considerations: narrowing the fallback-span scope,
sibling-aware descriptive features, or KEEP_SHADOW — the role decision belongs
to D2-A3.

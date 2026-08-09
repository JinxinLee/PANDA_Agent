"""Build the initial M6 benchmark annotation draft.

This script is deliberately one-shot: it refuses to overwrite an existing
dataset unless ``--force`` is supplied.  Human review happens in the generated
YAML and is never automated by this script.
"""

from __future__ import annotations

import argparse
import copy
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


LOCKED_VERSIONS = [
    "luminosityfit@ddd83dcd1a74093bf48ef259a2849a67f9413f32",
    "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
    "restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
    "li_2026@9930dfd79c74b9d1dadc6d1eb6c093ac10ccb45e12f641887bcdc8b823b8690a",
    "karavdina_2015@422421852c5a046c24e894a77b9380988ec8172914e9b30b055a100145c07a2b",
    "pflueger_2017@1b6ec987fc1430be085f2a7ba631d634f6580115ff0a90dff090dfcba5e990f3",
    "pandaroot_sphinx_2023_08_25_dev@5bff86c0f3a1102c80f3466a8ca0a63db48c0c7d8f142a78a0849219d7844f87",
    "curated_panda_domain@1.0",
]

DEV_COUNTS = {
    "installation": 8,
    "usage": 9,
    "api": 11,
    "algorithm_theory": 11,
    "algorithm_implementation": 13,
    "data_flow": 12,
    "module_structure": 8,
    "troubleshooting": 8,
}
DEFAULT_SOURCES = {
    "installation": ["documentation"],
    "usage": ["documentation", "code"],
    "api": ["code"],
    "algorithm_theory": ["paper"],
    "algorithm_implementation": ["paper", "code"],
    "data_flow": ["workflow", "code"],
    "module_structure": ["code", "graph"],
    "troubleshooting": ["documentation", "code"],
}
INSUFFICIENT_IDS = {7, 25, 41, 57, 77, 95, 107, 117, 118, 119}
VERSION_CONFLICT_IDS = {12, 26, 42, 58, 78, 96, 108, 120}


def selector(**values: Any) -> dict[str, Any]:
    return values


def doc(title: str) -> dict[str, Any]:
    return selector(
        source_id="pandaroot_sphinx_2023_08_25_dev", title_contains=title
    )


def code(source: str, path: str, symbol: str | None = None) -> dict[str, Any]:
    values: dict[str, Any] = {"source_id": source, "path": path}
    if symbol:
        values["symbol"] = symbol
    return selector(**values)


def paper(source: str, *pages: int) -> list[dict[str, Any]]:
    return [selector(source_id=source, pdf_page=page) for page in pages]


DOC_INSTALL = doc("Installation —")
DOC_INSTALL_RUN = doc("Installing & running PandaRoot")
DOC_DEVELOPER = doc("Installation of PandaRoot for Developers")
DOC_CVMFS = doc("CernVM-FS installation")
DOC_DOCKER = doc("Docker Containers")
DOC_DOCKER_DEV = doc("Development inside Docker")
DOC_RUNNING = doc("Running PandaRoot")
DOC_SEQUENCE = doc("Running Sequence")
DOC_MACROS = doc("PandaRoot Macros")
DOC_MASTER = doc("MasterTasks")
DOC_MASTER_SIM = doc("PndMasterRunSim")
DOC_MASTER_RECO = doc("PndMasterRecoTask")
DOC_MASTER_PID = doc("PndMasterMultiPidTask")
DOC_GENERATORS = doc("Event Generators")
DOC_DPM = doc("DPMGenerator")
DOC_RHO = doc("Simulation and Analysis in PandaRoot with RHO")
DOC_DATA_ACCESS = doc("Data Access")
DOC_PID = doc("Particle Identification")
DOC_FITTING = doc("Fitting")
DOC_TASK = doc("Analysis in a Task")
DOC_JUPYTER = doc("Jupyter Notebooks")

LF_README = code("luminosityfit", "README.md")
LF_CREATE = code("luminosityfit", "apps/createLmdFitData.cxx")
LF_CREATE_DOC = code("luminosityfit", "docs/apps/createLmdFitData.md")
LF_RUN = code("luminosityfit", "apps/runLmdFit.cxx")
LF_EXTRACT = code("luminosityfit", "apps/extractLuminosityValues.cxx")
LF_READER = code("luminosityfit", "data/PndLmdCombinedDataReader.cxx")
LF_ACCEPTANCE = code("luminosityfit", "data/PndLmdAcceptance.cxx")
LF_DATA_READER = code("luminosityfit", "data/PndLmdDataReader.cxx")
LF_FACTORY = code("luminosityfit", "model/PndLmdModelFactory.cxx")
LF_DPM_1D = code("luminosityfit", "model/PndLmdDPMAngModel1D.cxx")
LF_DPM_2D = code("luminosityfit", "model/PndLmdDPMAngModel2D.cxx")
LF_DIVERGENCE = code(
    "luminosityfit", "model/PndLmdDivergenceSmearingModel2D.cxx"
)
LF_SMEARING = code(
    "luminosityfit", "model/PndLmdSmearingConvolutionModel2D.cxx"
)

RG_README = code("restgas_determination", "macro/target/README.md")
RG_SIM = code("restgas_determination", "macro/target/prod_sim_hvmaps.C")
RG_RECO = code("restgas_determination", "macro/target/reco_complete.C")
RG_PID = code("restgas_determination", "macro/target/pid_complete.C")
RG_POCA = code("restgas_determination", "macro/target/ana_dpm.C")
RG_SECOND = code("restgas_determination", "macro/target/prod_aod_complete.C")
RG_FINAL = code("restgas_determination", "macro/target/ana_complete.C")
RG_EFF = code(
    "restgas_determination", "macro/target/correction/efficiency_correction_2.C"
)
RG_EFF_STEPS = code(
    "restgas_determination", "macro/target/correction/efficiency_correction_steps.C"
)
RG_RUNNER = code("restgas_determination", "macro/target/runall_prod_hvmaps.py")
RG_TARGET = code(
    "restgas_determination", "pgenerators/Target/PndTargetGenerator.cxx"
)
RG_PID_CORR = code(
    "restgas_determination", "pid/PidCorr/PndPidCorrelator.cxx"
)
RG_APOLLONIUS = code(
    "restgas_determination",
    "tracking/PndApolloniusTripletTrackFinder/PndApolloniusTripletTrackFinderTask.cxx",
)
RG_PZ = code(
    "restgas_determination", "tracking/PzFinder/PndSttSkewStrawPzFinderTask.cxx"
)

PR_TARGET = code("pandaroot", "pgenerators/Target/PndTargetGenerator.cxx")
PR_PID_CORR = code("pandaroot", "pid/PidCorr/PndPidCorrelator.cxx")
PR_MASTER_SIM = code("pandaroot", "tools/MasterTasks/PndMasterRunSim.cxx")
PR_LMD_GEANE = code("pandaroot", "detectors/lmd/LmdTrack/PndLmdGeaneTask.cxx")
PR_LMD_TRACK_Q = code("pandaroot", "detectors/lmd/LmdQA/PndLmdTrackQ.cxx")
PR_LMD_FINDER = code(
    "pandaroot", "detectors/lmd/LmdTrack/PndLmdTrackFinderCATask.cxx"
)

CASES: list[dict[str, Any]] = []
intent_seen: Counter[str] = Counter()


def add(
    intent: str,
    query: str,
    evidence: list[dict[str, Any] | list[dict[str, Any]]],
    answer_points: list[str],
    *,
    identifiers: list[str] | None = None,
    source_types: list[str] | None = None,
    scopes: dict[str, str] | None = None,
    forbidden: list[dict[str, Any]] | None = None,
) -> None:
    number = len(CASES) + 1
    intent_seen[intent] += 1
    status = "answered"
    if number in INSUFFICIENT_IDS:
        status = "insufficient_evidence"
    elif number in VERSION_CONFLICT_IDS:
        status = "version_conflict"
    groups = []
    for group_number, candidates in enumerate(evidence, start=1):
        any_of = candidates if isinstance(candidates, list) else [candidates]
        groups.append(
            {
                "group_id": f"g{number:03d}.e{group_number}",
                "any_of": copy.deepcopy(any_of),
            }
        )
    CASES.append(
        {
            "id": f"g{number:03d}",
            "split": "dev"
            if intent_seen[intent] <= DEV_COUNTS[intent]
            else "acceptance",
            "language": "en" if number <= 60 else "zh" if number <= 100 else "mixed",
            "intent": intent,
            "query": query,
            "expected_status": status,
            "allowed_source_versions": list(LOCKED_VERSIONS),
            "required_evidence_groups": groups,
            "required_source_types": list(
                source_types if source_types is not None else DEFAULT_SOURCES[intent]
            ),
            "required_answer_points": answer_points,
            "required_identifiers": list(identifiers or []),
            "forbidden_evidence": copy.deepcopy(forbidden or []),
            "concept_scopes": dict(scopes or {}),
            "review_status": "draft",
            "reviewer": None,
            "reviewed_at": None,
        }
    )


# g001-g012: installation (8 dev, 4 acceptance)
add("installation", "How do I install the locked PandaRoot development snapshot?", [DOC_INSTALL, DOC_DEVELOPER], ["Use the locked 2023-dev installation documentation and state that repository behavior is commit-specific."])
add("installation", "What are the documented prerequisites before building PandaRoot?", [DOC_INSTALL_RUN], ["List only prerequisites explicitly documented by the locked Sphinx page."])
add("installation", "How can I use CernVM-FS for a PandaRoot environment?", [DOC_CVMFS], ["Explain the documented CVMFS route and its operating assumptions."])
add("installation", "How do I start PandaRoot with its documented Docker containers?", [DOC_DOCKER], ["Describe the local documented container workflow without inventing image tags."])
add("installation", "How is a PandaRoot developer environment used inside Docker?", [DOC_DOCKER_DEV], ["Distinguish developing inside the container from merely running an image."])
add("installation", "Which setup step makes PandaRoot commands available in a shell?", [DOC_INSTALL_RUN], ["Cite the documented environment setup step and avoid guessing host-specific paths."])
add("installation", "What exact minimum GPU memory is required to install PandaRoot?", [DOC_INSTALL], ["State that the locked corpus does not establish an exact minimum GPU-memory requirement."])
add("installation", "How can I verify that the PandaRoot environment is ready before running a macro?", [DOC_INSTALL_RUN, DOC_RUNNING], ["Use documented environment and run instructions as the readiness evidence."])
add("installation", "Which installation page should a source-code contributor read?", [DOC_DEVELOPER], ["Point to the developer installation instructions rather than the generic runtime tutorial."])
add("installation", "Is a Jupyter-based PandaRoot workflow documented, and where?", [DOC_JUPYTER], ["Identify the Jupyter documentation page and keep installation claims scoped to it."])
add("installation", "What is the difference between the native and container setup paths in the locked documentation?", [[DOC_INSTALL_RUN, DOC_DEVELOPER], DOC_DOCKER], ["Compare only the documented setup boundaries."])
add("installation", "Install PandaRoot from commit deadbeef instead of the locked corpus commit.", [DOC_INSTALL, PR_MASTER_SIM], ["Reject the requested commit because it conflicts with the locked PandaRoot version."])

# g013-g026: usage (9 dev, 5 acceptance)
add("usage", "How do I run a ROOT macro in PandaRoot?", [DOC_MACROS, PR_MASTER_SIM], ["Explain the documented macro entry pattern and how a run task participates."])
add("usage", "What is the documented PandaRoot simulation-to-analysis sequence?", [DOC_SEQUENCE, DOC_MASTER], ["Preserve the simulation, digitization, reconstruction, PID, and analysis ordering."])
add("usage", "How is PndMasterRunSim used to configure a simulation?", [DOC_MASTER_SIM, PR_MASTER_SIM], ["Connect the operational documentation to the implementation class."], identifiers=["PndMasterRunSim"])
add("usage", "How do I select a DPM event generator in PandaRoot?", [DOC_DPM, DOC_GENERATORS], ["Use the generator documentation and do not substitute a different generator."], identifiers=["DPMGenerator"])
add("usage", "How should createLmdFitData be invoked and what categories can it create?", [LF_CREATE_DOC, LF_CREATE], ["Describe the CLI from current code and identify angular, efficiency, resolution, and vertex data modes."], identifiers=["createLmdFitData"])
add("usage", "How do I run a luminosity fit after preparing fit data?", [LF_RUN, LF_README], ["Identify the fit executable and the prepared input it consumes."], identifiers=["runLmdFit"])
add("usage", "How do I extract luminosity values from completed fit results?", [LF_EXTRACT, LF_README], ["Describe the extraction executable using current repository behavior."], identifiers=["extractLuminosityValues"])
add("usage", "How is the restgas two-pass reconstruction workflow run?", [RG_README, RG_RUNNER], ["Describe both PID passes and the POCA handoff in workflow order."], identifiers=["event_poca", "POCA_VERTEX_FILE"])
add("usage", "How is restgas_profile supplied to distributed-target simulation?", [RG_SIM, RG_TARGET], ["Explain how the profile becomes generator input without inventing a new class."], identifiers=["PndTargetGenerator"])
add("usage", "Which documented RHO pages cover data access and particle identification?", [DOC_DATA_ACCESS, DOC_PID], ["Point to the data-access and PID tutorial stages."])
add("usage", "How do I use PndMasterRecoTask in the generic workflow?", [DOC_MASTER_RECO, DOC_SEQUENCE], ["Place reconstruction after digitization and before PID."], identifiers=["PndMasterRecoTask"])
add("usage", "How do I perform analysis inside a FairTask-style task?", [DOC_TASK], ["Use only the analysis-in-a-task instructions from the locked documentation."])
add("usage", "What exact SHA-256 checksum will the next runLmdFit output ROOT file have?", [LF_RUN], ["Refuse because output content and checksum cannot be determined from the locked source alone."])
add("usage", "Run LuminosityFit from requested commit cafebabe rather than the locked master snapshot.", [LF_RUN, LF_README], ["Reject the requested LuminosityFit commit as a version conflict."])

# g027-g042: API (11 dev, 5 acceptance)
add("api", "Where is PndTargetGenerator defined?", [[PR_TARGET, RG_TARGET]], ["Give the real source path and distinguish the PandaRoot snapshot from the RestgasDetermination fork."], identifiers=["PndTargetGenerator"])
add("api", "Where is PndPidCorrelator implemented?", [[PR_PID_CORR, RG_PID_CORR]], ["Give the implementation path and the version scope."], identifiers=["PndPidCorrelator"])
add("api", "Where is PndLmdCombinedDataReader defined and what data boundary does it implement?", [LF_READER], ["Locate the class and explain that it adapts PandaRoot LMD products into LuminosityFit."], identifiers=["PndLmdCombinedDataReader"])
add("api", "Which class represents angular acceptance in LuminosityFit?", [LF_ACCEPTANCE], ["Identify the class and avoid calling it longitudinal profile efficiency."], identifiers=["PndLmdAcceptance"], scopes={"efficiency": "angular_acceptance"}, forbidden=[RG_EFF])
add("api", "Where does PndLmdModelFactory assemble the fit model?", [LF_FACTORY], ["Locate the factory and identify model assembly as its responsibility."], identifiers=["PndLmdModelFactory"])
add("api", "Which source implements the 1D DPM angular model?", [LF_DPM_1D], ["Return the exact current path and class identifier."], identifiers=["PndLmdDPMAngModel1D"])
add("api", "Which source implements the 2D DPM angular model?", [LF_DPM_2D], ["Return the exact current path and class identifier."], identifiers=["PndLmdDPMAngModel2D"])
add("api", "Where is detector-resolution convolution implemented in LuminosityFit?", [LF_SMEARING], ["Locate the smearing-convolution implementation."], identifiers=["PndLmdSmearingConvolutionModel2D"])
add("api", "Where is beam-divergence smearing implemented?", [LF_DIVERGENCE], ["Locate the divergence-smearing implementation."], identifiers=["PndLmdDivergenceSmearingModel2D"])
add("api", "Which macro produces event_poca?", [RG_POCA], ["Identify the exact target macro and the event_poca product."], identifiers=["ana_dpm.C", "event_poca"])
add("api", "Which macro consumes POCA_VERTEX_FILE for the second pass?", [RG_SECOND], ["Locate the second-pass macro and name the environment variable."], identifiers=["prod_aod_complete.C", "POCA_VERTEX_FILE"])
add("api", "Where is the final restgas vertex analysis implemented?", [RG_FINAL], ["Locate the final analysis macro and keep it distinct from the POCA-producing pass."], identifiers=["ana_complete.C"])
add("api", "Where is longitudinal restgas efficiency correction implemented?", [RG_EFF], ["Locate the profile-correction macro and distinguish it from PndLmdAcceptance."], identifiers=["efficiency_correction_2.C"], scopes={"efficiency": "longitudinal_profile"}, forbidden=[LF_ACCEPTANCE])
add("api", "Where is the displaced-track Apollonius task implemented in the restgas fork?", [RG_APOLLONIUS], ["Return the exact implementation path and class name."], identifiers=["PndApolloniusTripletTrackFinderTask"])
add("api", "What is the exact signature of PndPidCorrelator::SetMagicRestgasSeed?", [RG_PID_CORR], ["State that the requested method is not established by the indexed source and do not invent a signature."], identifiers=[])
add("api", "Show PndTargetGenerator from PandaRoot commit 0123456789abcdef instead of the locked snapshot.", [PR_TARGET], ["Reject the requested commit because it is not the locked PandaRoot version."], identifiers=["PndTargetGenerator"])

# g043-g058: algorithm_theory (11 dev, 5 acceptance)
add("algorithm_theory", "Explain the luminosity-extraction equation with cross section, acceptance, and resolution.", [paper("karavdina_2015", 60, 65, 71)], ["Explain how luminosity scales the reconstructed angular distribution and how acceptance and resolution enter."])
add("algorithm_theory", "Why is angular acceptance needed in a luminosity fit?", [paper("pflueger_2017", 57, 58, 62)], ["Explain the efficiency/acceptance factor using the thesis, not source-code inference."], scopes={"efficiency": "angular_acceptance"})
add("algorithm_theory", "Why is detector resolution represented by a smearing or convolution?", [paper("pflueger_2017", 65, 70, 71)], ["Explain reconstructed-angle migration from the theoretical distribution."])
add("algorithm_theory", "What role does beam divergence play in the luminosity model?", [paper("pflueger_2017", 74, 78, 84)], ["Explain the physical smearing caused by the incident-beam angular distribution."])
add("algorithm_theory", "What is the theoretical purpose of the DPM elastic-scattering model?", [paper("pflueger_2017", 51, 52, 54)], ["Relate the elastic differential cross section to luminosity extraction."])
add("algorithm_theory", "Why are LMD tracks propagated back toward an interaction point?", [paper("karavdina_2015", 94, 100, 104)], ["Explain recovery of scattering kinematics at the interaction region."], scopes={"back_propagation": "lmd_to_ip"}, forbidden=[RG_POCA])
add("algorithm_theory", "Why does the restgas method use an event-by-event POCA?", [paper("li_2026", 127, 131, 138)], ["Explain event-vertex estimation for displaced target interactions."], scopes={"back_propagation": "target_track_to_event_poca"}, forbidden=[PR_LMD_GEANE])
add("algorithm_theory", "Why is restgas longitudinal reconstruction efficiency profile dependent?", [paper("li_2026", 138, 142, 147)], ["Explain how generated profile and reconstruction response affect epsilon(z)."], scopes={"efficiency": "longitudinal_profile"})
add("algorithm_theory", "How does point-like angular acceptance differ from restgas effective acceptance?", [paper("pflueger_2017", 57, 62), paper("li_2026", 83, 86, 89)], ["Contrast compact-IP acceptance with profile- and cut-dependent effective acceptance."], scopes={"acceptance": "point_like_vs_restgas_effective"})
add("algorithm_theory", "Why does a reconstructed restgas profile feed back into effective acceptance?", [paper("li_2026", 141, 149, 151)], ["Explain the self-consistent profile-to-MC-to-acceptance loop."])
add("algorithm_theory", "What detector property makes HV-MAPS relevant for longitudinal vertex resolution?", [paper("li_2026", 103, 109, 123)], ["Relate material budget and hit resolution to vertex performance."])
add("algorithm_theory", "How should the two meanings of back propagation be distinguished?", [paper("karavdina_2015", 94, 100), paper("li_2026", 127, 131)], ["Distinguish LMD-to-IP propagation from target-track-to-event-POCA propagation."], scopes={"back_propagation": "lmd_to_ip_vs_target_track_to_event_poca"})
add("algorithm_theory", "How should angular acceptance be distinguished from longitudinal efficiency?", [paper("pflueger_2017", 57, 62), paper("li_2026", 142, 147)], ["State the variables, purpose, and downstream product of each efficiency concept."], scopes={"efficiency": "angular_acceptance_vs_longitudinal_profile"})
add("algorithm_theory", "What is the conceptual role of detector-coordinate transformations in LuminosityFit?", [paper("pflueger_2017", 53, 54, 55)], ["Explain why the elastic model is expressed in detector-relevant angular coordinates."])
add("algorithm_theory", "Prove from the corpus that the efficiency iteration converges for every possible gas profile.", [paper("li_2026", 149, 150, 151)], ["Refuse the universal proof because the thesis validation does not establish every possible profile."])
add("algorithm_theory", "Explain the theory for PandaRoot commit abcdef0123456789 rather than the locked snapshot.", [paper("karavdina_2015", 94), PR_LMD_GEANE], ["Reject the requested PandaRoot commit as a version conflict."])

# g059-g078: algorithm_implementation (13 dev, 7 acceptance)
add("algorithm_implementation", "How is detector-resolution smearing implemented in LuminosityFit?", [paper("pflueger_2017", 65, 70), LF_SMEARING, LF_FACTORY], ["Connect the thesis resolution model to the smearing-convolution class and model factory."], identifiers=["PndLmdSmearingConvolutionModel2D", "PndLmdModelFactory"])
add("algorithm_implementation", "How is beam-divergence smearing implemented in LuminosityFit?", [paper("pflueger_2017", 74, 78), LF_DIVERGENCE, LF_FACTORY], ["Connect the beam-divergence model to its implementation and factory composition."], identifiers=["PndLmdDivergenceSmearingModel2D"])
add("algorithm_implementation", "LMD 轨迹如何回传到 interaction point？", [paper("karavdina_2015", 94, 100, 104), PR_LMD_GEANE], ["把论文中的 LMD 回传目的与 PandaRoot LMD GEANE task 对应起来。"], identifiers=["PndLmdGeaneTask"], scopes={"back_propagation": "lmd_to_ip"}, forbidden=[RG_POCA])
add("algorithm_implementation", "Target Spectrometer 轨迹如何回传到 event POCA？", [paper("li_2026", 127, 131), RG_POCA, RG_SECOND], ["说明第一遍生成 event_poca，第二遍按该顶点传播。"], identifiers=["event_poca", "POCA_VERTEX_FILE"], scopes={"back_propagation": "target_track_to_event_poca"}, forbidden=[PR_LMD_GEANE])
add("algorithm_implementation", "Restgas effective acceptance 在代码中如何实现？", [paper("li_2026", 83, 86, 89), RG_SIM, LF_ACCEPTANCE, LF_FACTORY], ["说明它是 profile MC、LMD reconstruction、selection 与普通 acceptance 对象组成的 pipeline，而非独立类。"], identifiers=["PndLmdAcceptance", "PndLmdModelFactory"], scopes={"acceptance": "restgas_effective"})
add("algorithm_implementation", "PndLmdModelFactory 如何组合 DPM、acceptance 和 resolution？", [paper("pflueger_2017", 51, 57, 65), LF_FACTORY], ["按模型构造顺序说明理论模型、acceptance 乘法与 resolution convolution。"], identifiers=["PndLmdModelFactory"])
add("algorithm_implementation", "PndLmdDataReader 如何形成 accepted/generated angular efficiency？", [paper("pflueger_2017", 57, 62), LF_DATA_READER, LF_ACCEPTANCE], ["说明 selector 后的 accepted/generated 填充逻辑。"], identifiers=["PndLmdDataReader", "PndLmdAcceptance"], scopes={"efficiency": "angular_acceptance"})
add("algorithm_implementation", "DPM 1D 与 2D angular model 分别在哪里实现？", [paper("pflueger_2017", 51, 54), LF_DPM_1D, LF_DPM_2D], ["列出两个真实类及源文件，并说明维度差异。"], identifiers=["PndLmdDPMAngModel1D", "PndLmdDPMAngModel2D"])
add("algorithm_implementation", "Restgas longitudinal efficiency correction 如何实现？", [paper("li_2026", 142, 147), RG_EFF, RG_EFF_STEPS], ["说明 reconstructed z 分布如何除以 profile-dependent efficiency。"], identifiers=["efficiency_correction_2.C"], scopes={"efficiency": "longitudinal_profile"}, forbidden=[LF_ACCEPTANCE])
add("algorithm_implementation", "displaced tracking 中 Apollonius task 与 skew-straw pz finder 如何配合？", [paper("li_2026", 127, 131), RG_APOLLONIUS, RG_PZ, RG_RECO], ["把 transverse track finding、longitudinal pz 与 reconstruction macro 连接起来。"], identifiers=["PndApolloniusTripletTrackFinderTask", "PndSttSkewStrawPzFinderTask"])
add("algorithm_implementation", "PndTargetGenerator 如何用于分布式 restgas target？", [paper("li_2026", 128, 132), RG_TARGET, RG_SIM], ["说明 generator 与 profile-driven simulation macro 的实现关系。"], identifiers=["PndTargetGenerator"])
add("algorithm_implementation", "event_poca 是如何写出并按事件重新读入的？", [paper("li_2026", 131, 138), RG_POCA, RG_SECOND], ["说明 event_poca tree、事件对应关系和 POCA_VERTEX_FILE handoff。"], identifiers=["event_poca", "POCA_VERTEX_FILE"])
add("algorithm_implementation", "最终 vertex fit 与原始 POCA pass 的实现边界是什么？", [paper("li_2026", 131, 138), RG_POCA, RG_FINAL], ["区分 ana_dpm.C 的 POCA 产物与 ana_complete.C 的最终顶点结果。"], identifiers=["ana_dpm.C", "ana_complete.C"])
add("algorithm_implementation", "如何在实现层面区分 angular acceptance 与 epsilon_reco(z)？", [paper("pflueger_2017", 57, 62), paper("li_2026", 142, 147), LF_ACCEPTANCE, RG_EFF], ["分别给出两个对象的变量、代码路径和用途。"], identifiers=["PndLmdAcceptance", "efficiency_correction_2.C"], scopes={"efficiency": "angular_acceptance_vs_longitudinal_profile"})
add("algorithm_implementation", "为什么 Restgas effective acceptance 不是一个独立 C++ class？", [paper("li_2026", 83, 86), RG_SIM, LF_ACCEPTANCE, LF_FACTORY], ["用真实 pipeline 证据说明物理语义来自输入 profile 与 selection。"], identifiers=["PndLmdAcceptance"])
add("algorithm_implementation", "PndLmdCombinedDataReader 如何连接 LMDTrackQ 与 fit data？", [paper("pflueger_2017", 65, 70), LF_READER, PR_LMD_TRACK_Q], ["说明 PandaRoot QA data product 到 LuminosityFit adapter 的边界。"], identifiers=["PndLmdCombinedDataReader", "PndLmdTrackQ"])
add("algorithm_implementation", "两遍 PID workflow 为什么不能与 LMD-to-IP propagation 合并？", [paper("karavdina_2015", 94, 100), paper("li_2026", 127, 131), PR_LMD_GEANE, RG_SECOND], ["从 detector scope、vertex scope 和 workflow product 三方面消歧。"], scopes={"back_propagation": "lmd_to_ip_vs_target_track_to_event_poca"})
add("algorithm_implementation", "请给出代码中不存在的 PndUniversalRestgasDeconvolver 实现细节。", [paper("li_2026", 142, 147), RG_EFF], ["拒绝虚构不存在的类，并指出现有实现是效率修正 macro。"])
add("algorithm_implementation", "RestgasDetermination commit fedcba9876543210 中如何实现 event_poca？", [RG_POCA, RG_SECOND], ["拒绝请求的非锁定 RestgasDetermination commit。"], identifiers=["event_poca"])
add("algorithm_implementation", "PndLmdAcceptance 如何被 model factory 转换为可参与 fit 的模型组件？", [paper("pflueger_2017", 57, 62), LF_ACCEPTANCE, LF_FACTORY], ["把论文中的 acceptance correction 与 data object、factory 组合逻辑对应起来。"], identifiers=["PndLmdAcceptance", "PndLmdModelFactory"], scopes={"efficiency": "angular_acceptance"})

# g079-g096: data_flow (12 dev, 6 acceptance)
add("data_flow", "追踪 Lumi_TrksQA 到 LuminosityFit 最终 luminosity result。", [PR_LMD_TRACK_Q, LF_READER, LF_CREATE, LF_RUN, LF_EXTRACT], ["给出 PandaRoot QA product、reader、fit-data creation、fit 和 extraction 的顺序。"], identifiers=["PndLmdTrackQ", "PndLmdCombinedDataReader", "runLmdFit"])
add("data_flow", "追踪 restgas_profile 到 corrected rho(z)。", [RG_SIM, RG_TARGET, RG_RECO, RG_FINAL, RG_EFF], ["给出 profile simulation、reconstruction、vertex output 与 efficiency correction 顺序。"], identifiers=["PndTargetGenerator", "efficiency_correction_2.C"])
add("data_flow", "谁产生 event_poca，谁消费它？", [RG_POCA, RG_SECOND], ["明确 ana_dpm.C 产生，prod_aod_complete.C 经 POCA_VERTEX_FILE 消费。"], identifiers=["event_poca", "POCA_VERTEX_FILE"])
add("data_flow", "追踪 *_pid.root 到 *_pid_final.root。", [RG_PID, RG_POCA, RG_SECOND], ["说明 first PID、POCA derivation 与 second-pass PID output。"], identifiers=["event_poca"])
add("data_flow", "追踪 *_pid_final.root 到最终 pvz 分布。", [RG_SECOND, RG_FINAL], ["说明 final PID product 被 final analysis 读取并形成 vertex branches。"], identifiers=["pvz"])
add("data_flow", "追踪 generated z profile 到 epsilon_reco(z)。", [RG_SIM, RG_FINAL, RG_EFF], ["说明 generated truth 与 reconstructed vertex histogram 如何形成效率。"], scopes={"efficiency": "longitudinal_profile"})
add("data_flow", "追踪 reconstructed rho(z) 到 restgas effective acceptance。", [paper("li_2026", 141, 149, 151), RG_SIM, LF_ACCEPTANCE], ["说明 profile 更新、重新生成 MC、LMD reconstruction 与 acceptance creation。"], identifiers=["PndLmdAcceptance"])
add("data_flow", "createLmdFitData 的 a/e/r/v 数据流分别是什么？", [LF_CREATE_DOC, LF_CREATE], ["解释 angular、efficiency、resolution、vertex 四类输出。"], identifiers=["createLmdFitData"])
add("data_flow", "PndLmdTrackQ 如何进入 PndLmdCombinedDataReader？", [PR_LMD_TRACK_Q, LF_READER], ["明确 ROOT data product 与 adapter read boundary。"], identifiers=["PndLmdTrackQ", "PndLmdCombinedDataReader"])
add("data_flow", "PndLmdAcceptance 如何进入 PndLmdModelFactory？", [LF_ACCEPTANCE, LF_FACTORY], ["说明 acceptance data object 被 factory 取用并组合到模型。"], identifiers=["PndLmdAcceptance", "PndLmdModelFactory"])
add("data_flow", "PndMasterRunSim 与 PndTargetGenerator 的数据流关系是什么？", [DOC_MASTER_SIM, PR_MASTER_SIM, PR_TARGET], ["说明 master simulation orchestration 与 generator input 的边界。"], identifiers=["PndMasterRunSim", "PndTargetGenerator"])
add("data_flow", "两次 PID 之间的 event ID 对齐为什么重要？", [RG_README, RG_POCA, RG_SECOND], ["说明 event-specific POCA 必须与 second-pass event 对应。"], identifiers=["event_poca"])
add("data_flow", "最终 luminosity fit 中 cross section、divergence、acceptance 和 resolution 的顺序是什么？", [paper("pflueger_2017", 51, 57, 65, 78), LF_FACTORY], ["按模型数据流说明各组件组合关系。"], identifiers=["PndLmdModelFactory"])
add("data_flow", "restgas runner 如何串联 sim、reco、PID、POCA 与 final analysis？", [RG_RUNNER, RG_SIM, RG_RECO, RG_PID, RG_POCA, RG_SECOND, RG_FINAL], ["按 runner 的真实 entrypoint 顺序描述各阶段。"], identifiers=["runall_prod_hvmaps.py"])
add("data_flow", "profile iteration 中 rho_0 到 rho_1 的一次更新包含哪些数据产物？", [paper("li_2026", 142, 149, 151), RG_EFF], ["说明一次 efficiency estimation、data correction 和 profile update。"])
add("data_flow", "网页 Running Sequence 与 restgas custom workflow 的关系是什么？", [DOC_SEQUENCE, RG_README], ["区分通用 PandaRoot 顺序与 oct19 fork 的定制两遍流程。"])
add("data_flow", "从当前语料给出 event_poca ROOT tree 的未来文件 checksum。", [RG_POCA], ["拒绝，因为未来运行产物的 checksum 不在锁定语料中。"], identifiers=["event_poca"])
add("data_flow", "追踪 LuminosityFit commit aaaaaaaaaaaaaaaa 的数据流。", [LF_CREATE, LF_RUN], ["拒绝非锁定 LuminosityFit commit 的实现结论。"])

# g097-g108: module_structure (8 dev, 4 acceptance)
add("module_structure", "LuminosityFit 的 model layer 由哪些核心模块组成？", [LF_DPM_2D, LF_DIVERGENCE, LF_SMEARING, LF_FACTORY], ["列出 DPM、divergence、resolution convolution 与 factory 的职责边界。"])
add("module_structure", "PandaRoot 与 LuminosityFit 的依赖边界在哪里？", [PR_LMD_TRACK_Q, LF_READER, LF_FACTORY], ["区分 PandaRoot data production/adapter 与独立 fit-model layer。"])
add("module_structure", "RestgasDetermination 如何扩展 PandaRoot？", [RG_TARGET, RG_APOLLONIUS, RG_PZ, RG_PID_CORR], ["指出 generator、displaced tracking、PID/POCA 相关扩展位于 fork 中。"])
add("module_structure", "macro/target 的模块如何按 workflow 分组？", [RG_SIM, RG_RECO, RG_PID, RG_POCA, RG_SECOND, RG_FINAL, RG_EFF], ["按 simulation、reconstruction、two-pass PID、analysis、correction 分组。"])
add("module_structure", "Sphinx documentation 在知识架构中负责什么？", [DOC_RUNNING, DOC_INSTALL, DOC_MASTER], ["说明其操作性权威边界，不把它当 restgas 算法论文。"])
add("module_structure", "PndLmdModelFactory 与 data objects 的结构关系是什么？", [LF_ACCEPTANCE, LF_FACTORY], ["说明 factory 消费 acceptance/resolution 等 data objects 构造 model。"], identifiers=["PndLmdModelFactory", "PndLmdAcceptance"])
add("module_structure", "off-IP tracking 由哪些结构化模块支持？", [RG_APOLLONIUS, RG_PZ, RG_RECO], ["列出 transverse finder、longitudinal pz finder 与 orchestration macro。"])
add("module_structure", "LMD reconstruction 模块如何连接到 LMD QA output？", [PR_LMD_FINDER, PR_LMD_GEANE, PR_LMD_TRACK_Q], ["说明 track finding、propagation 与 QA data object 的结构连接。"])
add("module_structure", "Map model/ vs data/ vs apps/ in LuminosityFit with PndLmdModelFactory and createLmdFitData.", [LF_FACTORY, LF_ACCEPTANCE, LF_CREATE], ["Explain the model, data-object, and executable boundaries."], identifiers=["PndLmdModelFactory", "createLmdFitData"])
add("module_structure", "Compare generic MasterTasks vs custom macro/target workflow modules.", [DOC_MASTER, RG_README], ["Separate generic documented orchestration from repository-specific target macros."])
add("module_structure", "Describe the internal module named RestgasQuantumGPUOptimizer.", [RG_README], ["State that this module is not established by the locked repository and do not fabricate it."])
add("module_structure", "Describe PandaRoot commit bbbbbbbbbbbbbbbb module boundaries instead of the locked snapshot.", [PR_MASTER_SIM, PR_LMD_TRACK_Q], ["Reject the non-locked PandaRoot commit."])

# g109-g120: troubleshooting (8 dev, 4 acceptance)
add("troubleshooting", "Why can Sphinx 2023-dev docs disagree with RestgasDetermination/oct19-derived code?", [DOC_RUNNING, RG_README], ["Explain the source-version boundary and choose the target commit for current behavior."])
add("troubleshooting", "event_poca is missing: what should I inspect first?", [RG_POCA, RG_README], ["Check the first-pass POCA output, expected tree/product, and upstream PID input."], identifiers=["event_poca"])
add("troubleshooting", "POCA_VERTEX_FILE is set but second-pass PID does not use it; what should I check?", [RG_SECOND, RG_PID_CORR], ["Check environment visibility, file readability, event alignment, and the actual second-pass code path."], identifiers=["POCA_VERTEX_FILE"])
add("troubleshooting", "createLmdFitData returns no acceptance: which code and input assumptions should I inspect?", [LF_CREATE_DOC, LF_CREATE, LF_DATA_READER], ["Check requested data mode, input LMD QA data, selections, and accepted/generated filling."], identifiers=["createLmdFitData"])
add("troubleshooting", "runLmdFit cannot find prepared data; how do I trace the mismatch?", [LF_CREATE, LF_RUN, LF_README], ["Compare create and fit paths/options using current repository entrypoints."], identifiers=["runLmdFit"])
add("troubleshooting", "Why might restgas efficiency correction have empty bins?", [RG_EFF, RG_EFF_STEPS], ["Check generated/reconstructed histogram support and guard against division with no efficiency evidence."], scopes={"efficiency": "longitudinal_profile"})
add("troubleshooting", "Why might LMD angular acceptance be confused with pvz efficiency?", [LF_ACCEPTANCE, RG_EFF], ["Diagnose variable/domain confusion and point to the separate implementations."], scopes={"efficiency": "angular_acceptance_vs_longitudinal_profile"})
add("troubleshooting", "Why can a class name match the query but still be the wrong implementation?", [RG_APOLLONIUS, PR_LMD_FINDER], ["Use detector scope, call/workflow context, source version, and path rather than name alone."])
add("troubleshooting", "What exact runtime stack trace will a future failed ROOT job produce?", [RG_RUNNER], ["Refuse because a future stack trace cannot be inferred from source alone."])
add("troubleshooting", "Which undocumented cluster quota caused my production job to fail?", [RG_RUNNER], ["State that the locked corpus and question provide no cluster log or quota evidence."])
add("troubleshooting", "Recover the deleted event_poca file contents from source code only.", [RG_POCA], ["Refuse because source code cannot reconstruct a deleted runtime data product."], identifiers=["event_poca"])
add("troubleshooting", "Debug RestgasDetermination at commit cccccccccccccccc rather than the locked commit.", [RG_README, RG_SECOND], ["Reject the requested non-locked RestgasDetermination commit."])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("gold_questions.yaml"),
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite existing review dataset: {args.output}")
    if len(CASES) != 120:
        raise RuntimeError(f"expected 120 questions, built {len(CASES)}")
    payload = {
        "schema_version": "1.0",
        "benchmark_version": "m6-draft-1",
        "questions": CASES,
    }
    args.output.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
        newline="\n",
    )
    print(args.output)


if __name__ == "__main__":
    main()

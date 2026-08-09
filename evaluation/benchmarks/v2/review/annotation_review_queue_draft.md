# Benchmark v2 annotation review queue

> This draft is not release-eligible. All 120 questions require human approval after schema and split changes.

- Questions: `120`
- Knowledge clusters: `76`
- Broad selectors shown below: `30`
- Karavdina selectors require page/section spot checks because that PDF used PyMuPDF fallback.

## Broad selector queue

| Case | Group | Role | Matches | Selector |
|---|---|---|---:|---|
| `g014` | `g014.e2` | `g014.e2` | 67 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "MasterTasks"}` |
| `g101` | `g101.e3` | `g101.e3` | 67 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "MasterTasks"}` |
| `g106` | `g106.e1` | `g106.e1` | 67 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "MasterTasks"}` |
| `g087` | `g087.e1` | `pandaroot_data_product_definition` | 58 | `{"source_id": "pandaroot", "path": "detectors/lmd/LmdQA/PndLmdTrackQ.h"}` |
| `g016` | `g016.e2` | `g016.e2` | 43 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "Event Generators"}` |
| `g015` | `g015.e1` | `g015.e1` | 41 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "PndMasterRunSim"}` |
| `g022` | `g022.e2` | `g022.e2` | 41 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "Particle Identification"}` |
| `g089` | `g089.e1` | `g089.e1` | 41 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "PndMasterRunSim"}` |
| `g008` | `g008.e2` | `g008.e2` | 33 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "Running PandaRoot"}` |
| `g101` | `g101.e1` | `g101.e1` | 33 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "Running PandaRoot"}` |
| `g109` | `g109.e1` | `g109.e1` | 33 | `{"source_id": "pandaroot_sphinx_2023_08_25_dev", "title_contains": "Running PandaRoot"}` |
| `g012` | `g012.e2` | `g012.e2` | 30 | `{"source_id": "pandaroot", "path": "tools/MasterTasks/PndMasterRunSim.cxx"}` |
| `g013` | `g013.e2` | `g013.e2` | 30 | `{"source_id": "pandaroot", "path": "tools/MasterTasks/PndMasterRunSim.cxx"}` |
| `g015` | `g015.e2` | `g015.e2` | 30 | `{"source_id": "pandaroot", "path": "tools/MasterTasks/PndMasterRunSim.cxx"}` |
| `g089` | `g089.e2` | `g089.e2` | 30 | `{"source_id": "pandaroot", "path": "tools/MasterTasks/PndMasterRunSim.cxx"}` |
| `g108` | `g108.e1` | `g108.e1` | 30 | `{"source_id": "pandaroot", "path": "tools/MasterTasks/PndMasterRunSim.cxx"}` |
| `g028` | `g028.e1` | `g028.e1` | 29 | `{"source_id": "pandaroot", "path": "pid/PidCorr/PndPidCorrelator.cxx"}` |
| `g020` | `g020.e1` | `g020.e1` | 28 | `{"source_id": "restgas_determination", "path": "macro/target/README.md"}` |
| `g090` | `g090.e1` | `g090.e1` | 28 | `{"source_id": "restgas_determination", "path": "macro/target/README.md"}` |
| `g094` | `g094.e2` | `g094.e2` | 28 | `{"source_id": "restgas_determination", "path": "macro/target/README.md"}` |
| `g106` | `g106.e2` | `g106.e2` | 28 | `{"source_id": "restgas_determination", "path": "macro/target/README.md"}` |
| `g107` | `g107.e1` | `g107.e1` | 28 | `{"source_id": "restgas_determination", "path": "macro/target/README.md"}` |
| `g109` | `g109.e2` | `g109.e2` | 28 | `{"source_id": "restgas_determination", "path": "macro/target/README.md"}` |
| `g110` | `g110.e2` | `g110.e2` | 28 | `{"source_id": "restgas_determination", "path": "macro/target/README.md"}` |
| `g120` | `g120.e1` | `g120.e1` | 28 | `{"source_id": "restgas_determination", "path": "macro/target/README.md"}` |
| `g026` | `g026.e2` | `g026.e2` | 27 | `{"source_id": "luminosityfit", "path": "README.md"}` |
| `g028` | `g028.e1` | `g028.e1` | 27 | `{"source_id": "restgas_determination", "path": "pid/PidCorr/PndPidCorrelator.cxx"}` |
| `g041` | `g041.e1` | `g041.e1` | 27 | `{"source_id": "restgas_determination", "path": "pid/PidCorr/PndPidCorrelator.cxx"}` |
| `g099` | `g099.e4` | `g099.e4` | 27 | `{"source_id": "restgas_determination", "path": "pid/PidCorr/PndPidCorrelator.cxx"}` |
| `g111` | `g111.e2` | `g111.e2` | 27 | `{"source_id": "restgas_determination", "path": "pid/PidCorr/PndPidCorrelator.cxx"}` |

## Full 120-question approval queue

> Review the YAML for full selectors and answer-point text. Fill reviewer/status in the YAML; this table is a navigation checklist.

| Case | Split | Cluster | Intent | Status | Query | Evidence roles | Points | Decision |
|---|---|---|---|---|---|---|---:|---|
| `g001` | `dev` | `cluster-g001` | `installation` | `answered` | How do I install the locked PandaRoot development snapshot? | locked_developer_installation | 1 | pending |
| `g002` | `dev` | `cluster-g002` | `installation` | `answered` | What are the documented prerequisites before building PandaRoot? | g002.e1 | 1 | pending |
| `g003` | `dev` | `cluster-g003` | `installation` | `answered` | How can I use CernVM-FS for a PandaRoot environment? | g003.e1 | 1 | pending |
| `g004` | `dev` | `cluster-g004` | `installation` | `answered` | How do I start PandaRoot with its documented Docker containers? | g004.e1 | 1 | pending |
| `g005` | `dev` | `cluster-g005` | `installation` | `answered` | How is a PandaRoot developer environment used inside Docker? | g005.e1 | 1 | pending |
| `g006` | `dev` | `cluster-g002` | `installation` | `answered` | Which setup step makes PandaRoot commands available in a shell? | g006.e1 | 1 | pending |
| `g007` | `dev` | `cluster-g007` | `installation` | `insufficient_evidence` | What exact minimum GPU memory is required to install PandaRoot? | g007.e1 | 1 | pending |
| `g008` | `dev` | `cluster-g008` | `installation` | `answered` | How can I verify that the PandaRoot environment is ready before running a macro? | g008.e1, g008.e2 | 1 | pending |
| `g009` | `dev` | `cluster-g009` | `installation` | `answered` | Which installation page should a source-code contributor read? | g009.e1 | 1 | pending |
| `g010` | `dev` | `cluster-g010` | `installation` | `answered` | Is a Jupyter-based PandaRoot workflow documented, and where? | g010.e1 | 1 | pending |
| `g011` | `dev` | `cluster-g011` | `installation` | `answered` | What is the difference between the native and container setup paths in the locked documentation? | g011.e1, g011.e2 | 1 | pending |
| `g012` | `dev` | `cluster-g012` | `installation` | `version_conflict` | Install PandaRoot from commit deadbeef instead of the locked corpus commit. | g012.e1, g012.e2 | 1 | pending |
| `g013` | `dev` | `cluster-g013` | `usage` | `answered` | How do I set up the terminal and run a ROOT simulation macro in PandaRoot, and how does the master run task participate in the lifecycle? | g013.e1, g013.e2 | 3 | pending |
| `g014` | `dev` | `cluster-g014` | `usage` | `answered` | What is the documented PandaRoot simulation-to-analysis sequence? | g014.e1, g014.e2 | 1 | pending |
| `g015` | `dev` | `cluster-g015` | `usage` | `answered` | How is PndMasterRunSim used to configure a simulation? | g015.e1, g015.e2 | 1 | pending |
| `g016` | `dev` | `cluster-g016` | `usage` | `answered` | How do I select a DPM event generator in PandaRoot? | g016.e1, g016.e2 | 1 | pending |
| `g017` | `dev` | `cluster-g017` | `usage` | `answered` | How should createLmdFitData be invoked and what categories can it create? | g017.e1, g017.e2 | 1 | pending |
| `g018` | `dev` | `cluster-g018` | `usage` | `answered` | How do I run a luminosity fit after preparing fit data? | g018.e1 | 1 | pending |
| `g019` | `dev` | `cluster-g019` | `usage` | `answered` | How do I extract luminosity values from completed fit results? | g019.e1 | 1 | pending |
| `g020` | `dev` | `cluster-g020` | `usage` | `answered` | How is the restgas two-pass reconstruction workflow run? | g020.e1, g020.e2 | 1 | pending |
| `g021` | `dev` | `cluster-g021` | `usage` | `answered` | How is restgas_profile supplied to distributed-target simulation? | g021.e1, g021.e2 | 1 | pending |
| `g022` | `dev` | `cluster-g022` | `usage` | `answered` | Which documented RHO pages cover data access and particle identification? | g022.e1, g022.e2 | 1 | pending |
| `g023` | `dev` | `cluster-g023` | `usage` | `answered` | How do I use PndMasterRecoTask in the generic workflow? | g023.e1, g023.e2 | 1 | pending |
| `g024` | `dev` | `cluster-g024` | `usage` | `answered` | How do I perform analysis inside a FairTask-style task? | g024.e1 | 1 | pending |
| `g025` | `dev` | `cluster-g018` | `usage` | `insufficient_evidence` | What exact SHA-256 checksum will the next runLmdFit output ROOT file have? | g025.e1 | 1 | pending |
| `g026` | `dev` | `cluster-g018` | `usage` | `version_conflict` | Run LuminosityFit from requested commit cafebabe rather than the locked master snapshot. | g026.e1, g026.e2 | 1 | pending |
| `g027` | `dev` | `cluster-g015` | `api` | `answered` | Where is PndTargetGenerator defined in the locked PandaRoot snapshot and the RestgasDetermination fork, and why does version scope matter? | upstream_snapshot_definition, fork_definition | 3 | pending |
| `g028` | `dev` | `cluster-g028` | `api` | `answered` | Where is PndPidCorrelator implemented? | g028.e1 | 1 | pending |
| `g029` | `dev` | `cluster-g029` | `api` | `answered` | Where is PndLmdCombinedDataReader defined and what data boundary does it implement? | g029.e1 | 1 | pending |
| `g030` | `dev` | `cluster-g030` | `api` | `answered` | Which class represents angular acceptance in LuminosityFit? | g030.e1 | 1 | pending |
| `g031` | `dev` | `cluster-g031` | `api` | `answered` | Where does PndLmdModelFactory assemble the fit model? | g031.e1 | 1 | pending |
| `g032` | `dev` | `cluster-g032` | `api` | `answered` | Which source implements the 1D DPM angular model? | g032.e1 | 1 | pending |
| `g033` | `dev` | `cluster-g032` | `api` | `answered` | Which source implements the 2D DPM angular model? | g033.e1 | 1 | pending |
| `g034` | `dev` | `cluster-g034` | `api` | `answered` | Where is detector-resolution convolution implemented in LuminosityFit? | g034.e1 | 1 | pending |
| `g035` | `dev` | `cluster-g035` | `api` | `answered` | Where is beam-divergence smearing implemented? | g035.e1 | 1 | pending |
| `g036` | `dev` | `cluster-g036` | `api` | `answered` | Which macro produces event_poca? | g036.e1 | 1 | pending |
| `g037` | `dev` | `cluster-g037` | `api` | `answered` | Which macro consumes POCA_VERTEX_FILE for the second pass? | g037.e1 | 1 | pending |
| `g038` | `challenge` | `cluster-g038` | `api` | `answered` | Where is the final restgas vertex analysis implemented? | g038.e1 | 1 | pending |
| `g039` | `dev` | `cluster-g030` | `api` | `answered` | Where is longitudinal restgas efficiency correction implemented? | g039.e1 | 1 | pending |
| `g040` | `dev` | `cluster-g040` | `api` | `answered` | Where is the displaced-track Apollonius task implemented in the restgas fork? | g040.e1 | 1 | pending |
| `g041` | `dev` | `cluster-g041` | `api` | `insufficient_evidence` | What is the exact signature of PndPidCorrelator::SetMagicRestgasSeed? | g041.e1 | 1 | pending |
| `g042` | `dev` | `cluster-g042` | `api` | `version_conflict` | Show PndTargetGenerator from PandaRoot commit 0123456789abcdef instead of the locked snapshot. | g042.e1 | 1 | pending |
| `g043` | `challenge` | `cluster-g043` | `algorithm_theory` | `answered` | Explain the luminosity-extraction equation with cross section, acceptance, and resolution. | g043.e1 | 1 | pending |
| `g044` | `dev` | `cluster-g030` | `algorithm_theory` | `answered` | Why is angular acceptance needed in a luminosity fit? | g044.e1 | 1 | pending |
| `g045` | `challenge` | `cluster-g045` | `algorithm_theory` | `answered` | Why is detector resolution represented by a smearing or convolution? | g045.e1 | 1 | pending |
| `g046` | `challenge` | `cluster-g046` | `algorithm_theory` | `answered` | What role does beam divergence play in the luminosity model? | g046.e1 | 1 | pending |
| `g047` | `dev` | `cluster-g032` | `algorithm_theory` | `answered` | What is the theoretical purpose of the DPM elastic-scattering model? | g047.e1 | 1 | pending |
| `g048` | `challenge` | `cluster-g048` | `algorithm_theory` | `answered` | Why are LMD tracks propagated back toward an interaction point? | g048.e1 | 1 | pending |
| `g049` | `challenge` | `cluster-g049` | `algorithm_theory` | `answered` | Why does the restgas method use an event-by-event POCA? | g049.e1 | 1 | pending |
| `g050` | `dev` | `cluster-g030` | `algorithm_theory` | `answered` | Why is restgas longitudinal reconstruction efficiency profile dependent? | g050.e1 | 1 | pending |
| `g051` | `dev` | `cluster-g030` | `algorithm_theory` | `answered` | How does point-like angular acceptance differ from restgas effective acceptance? | g051.e1, g051.e2 | 1 | pending |
| `g052` | `dev` | `cluster-g030` | `algorithm_theory` | `answered` | Why does a reconstructed restgas profile feed back into effective acceptance? | g052.e1 | 1 | pending |
| `g053` | `challenge` | `cluster-g053` | `algorithm_theory` | `answered` | What detector property makes HV-MAPS relevant for longitudinal vertex resolution? | g053.e1 | 1 | pending |
| `g054` | `challenge` | `cluster-g054` | `algorithm_theory` | `answered` | How should the two meanings of back propagation be distinguished? | g054.e1, g054.e2 | 1 | pending |
| `g055` | `dev` | `cluster-g030` | `algorithm_theory` | `answered` | How should angular acceptance be distinguished from longitudinal efficiency? | g055.e1, g055.e2 | 1 | pending |
| `g056` | `challenge` | `cluster-g056` | `algorithm_theory` | `answered` | What is the conceptual role of detector-coordinate transformations in LuminosityFit? | g056.e1 | 1 | pending |
| `g057` | `dev` | `cluster-g057` | `algorithm_theory` | `insufficient_evidence` | Prove from the corpus that the efficiency iteration converges for every possible gas profile. | g057.e1 | 1 | pending |
| `g058` | `dev` | `cluster-g058` | `algorithm_theory` | `version_conflict` | Explain the theory for PandaRoot commit abcdef0123456789 rather than the locked snapshot. | g058.e1, g058.e2 | 1 | pending |
| `g059` | `dev` | `cluster-g034` | `algorithm_implementation` | `answered` | How is detector-resolution smearing implemented in LuminosityFit? | g059.e1, g059.e2, g059.e3 | 1 | pending |
| `g060` | `dev` | `cluster-g035` | `algorithm_implementation` | `answered` | How is beam-divergence smearing implemented in LuminosityFit? | g060.e1, g060.e2, g060.e3 | 1 | pending |
| `g061` | `challenge` | `cluster-g048` | `algorithm_implementation` | `answered` | LMD 轨迹如何回传到 interaction point？ | g061.e1, g061.e2 | 1 | pending |
| `g062` | `challenge` | `cluster-g062` | `algorithm_implementation` | `answered` | Target Spectrometer 轨迹如何回传到 event POCA？ | g062.e1, g062.e2, g062.e3 | 1 | pending |
| `g063` | `dev` | `cluster-g030` | `algorithm_implementation` | `answered` | Restgas effective acceptance 在代码中如何实现？ | g063.e1, g063.e2, g063.e3, g063.e4 | 1 | pending |
| `g064` | `challenge` | `cluster-g064` | `algorithm_implementation` | `answered` | PndLmdModelFactory 如何组合 DPM、acceptance 和 resolution？ | g064.e1, g064.e2 | 1 | pending |
| `g065` | `challenge` | `cluster-g065` | `algorithm_implementation` | `answered` | PndLmdDataReader 如何形成 accepted/generated angular efficiency？ | g065.e1, g065.e2, g065.e3 | 1 | pending |
| `g066` | `dev` | `cluster-g032` | `algorithm_implementation` | `answered` | DPM 1D 与 2D angular model 分别在哪里实现？ | g066.e1, g066.e2, g066.e3 | 1 | pending |
| `g067` | `dev` | `cluster-g030` | `algorithm_implementation` | `answered` | Restgas longitudinal efficiency correction 如何实现？ | g067.e1, g067.e2, g067.e3 | 1 | pending |
| `g068` | `dev` | `cluster-g040` | `algorithm_implementation` | `answered` | displaced tracking 中 Apollonius task 与 skew-straw pz finder 如何配合？ | g068.e1, g068.e2, g068.e3, g068.e4 | 1 | pending |
| `g069` | `dev` | `cluster-g015` | `algorithm_implementation` | `answered` | PndTargetGenerator 如何用于分布式 restgas target？ | g069.e1, g069.e2, g069.e3 | 1 | pending |
| `g070` | `dev` | `cluster-g036` | `algorithm_implementation` | `answered` | event_poca 是如何写出并按事件重新读入的？ | g070.e1, g070.e2, g070.e3 | 1 | pending |
| `g071` | `challenge` | `cluster-g071` | `algorithm_implementation` | `answered` | 最终 vertex fit 与原始 POCA pass 的实现边界是什么？ | g071.e1, g071.e2, g071.e3 | 1 | pending |
| `g072` | `dev` | `cluster-g030` | `algorithm_implementation` | `answered` | 如何在实现层面区分 angular acceptance 与 epsilon_reco(z)？ | g072.e1, g072.e2, g072.e3, g072.e4 | 1 | pending |
| `g073` | `dev` | `cluster-g030` | `algorithm_implementation` | `answered` | 为什么 Restgas effective acceptance 不是一个独立 C++ class？ | g073.e1, g073.e2, g073.e3, g073.e4 | 1 | pending |
| `g074` | `dev` | `cluster-g029` | `algorithm_implementation` | `answered` | PndLmdCombinedDataReader 如何连接 LMDTrackQ 与 fit data？ | g074.e1, g074.e2, g074.e3 | 1 | pending |
| `g075` | `challenge` | `cluster-g075` | `algorithm_implementation` | `answered` | 两遍 PID workflow 为什么不能与 LMD-to-IP propagation 合并？ | g075.e1, g075.e2, g075.e3, g075.e4 | 1 | pending |
| `g076` | `dev` | `cluster-g076` | `algorithm_implementation` | `insufficient_evidence` | 请给出代码中不存在的 PndUniversalRestgasDeconvolver 实现细节。 | g076.e1, g076.e2 | 1 | pending |
| `g077` | `dev` | `cluster-g036` | `algorithm_implementation` | `version_conflict` | RestgasDetermination commit fedcba9876543210 中如何实现 event_poca？ | g077.e1, g077.e2 | 1 | pending |
| `g078` | `dev` | `cluster-g031` | `algorithm_implementation` | `answered` | PndLmdAcceptance 如何被 model factory 转换为可参与 fit 的模型组件？ | g078.e1, g078.e2, g078.e3 | 1 | pending |
| `g079` | `dev` | `cluster-g079` | `data_flow` | `answered` | 追踪 Lumi_TrksQA 到 LuminosityFit 最终 luminosity result。 | g079.e1, g079.e2, g079.e3, g079.e4, g079.e5 | 1 | pending |
| `g080` | `challenge` | `cluster-g080` | `data_flow` | `answered` | 追踪 restgas_profile 到 corrected rho(z)。 | g080.e1, g080.e2, g080.e3, g080.e4, g080.e5 | 1 | pending |
| `g081` | `dev` | `cluster-g036` | `data_flow` | `answered` | 谁产生 event_poca，谁消费它？ | g081.e1, g081.e2 | 1 | pending |
| `g082` | `challenge` | `cluster-g082` | `data_flow` | `answered` | 追踪 *_pid.root 到 *_pid_final.root。 | g082.e1, g082.e2, g082.e3 | 1 | pending |
| `g083` | `challenge` | `cluster-g083` | `data_flow` | `answered` | 追踪 *_pid_final.root 到最终 pvz 分布。 | g083.e1, g083.e2 | 1 | pending |
| `g084` | `challenge` | `cluster-g084` | `data_flow` | `answered` | 追踪 generated z profile 到 epsilon_reco(z)。 | g084.e1, g084.e2, g084.e3 | 1 | pending |
| `g085` | `dev` | `cluster-g030` | `data_flow` | `answered` | 追踪 reconstructed rho(z) 到 restgas effective acceptance。 | profile_feedback_theory, g085.e2, g085.e3 | 1 | pending |
| `g086` | `dev` | `cluster-g017` | `data_flow` | `answered` | createLmdFitData 的 a/e/r/v 数据流分别是什么？ | g086.e1, g086.e2 | 1 | pending |
| `g087` | `regression` | `cluster-g087` | `data_flow` | `answered` | PndLmdTrackQ 如何进入 PndLmdCombinedDataReader？ | pandaroot_data_product_definition, adapter_read_boundary | 1 | pending |
| `g088` | `dev` | `cluster-g031` | `data_flow` | `answered` | PndLmdAcceptance 如何进入 PndLmdModelFactory？ | g088.e1, g088.e2 | 1 | pending |
| `g089` | `dev` | `cluster-g015` | `data_flow` | `answered` | PndMasterRunSim 与 PndTargetGenerator 的数据流关系是什么？ | g089.e1, g089.e2, target_generator_interface_or_sampling | 1 | pending |
| `g090` | `regression` | `cluster-g090` | `data_flow` | `answered` | 两次 PID 之间的 event ID 对齐为什么重要？ | g090.e1, g090.e2, g090.e3 | 1 | pending |
| `g091` | `challenge` | `cluster-g064` | `data_flow` | `answered` | 最终 luminosity fit 中 cross section、divergence、acceptance 和 resolution 的顺序是什么？ | g091.e1, g091.e2 | 1 | pending |
| `g092` | `regression` | `cluster-g092` | `data_flow` | `answered` | restgas runner 如何串联 sim、reco、PID、POCA 与 final analysis？ | g092.e1, g092.e2, g092.e3, g092.e4, g092.e5, g092.e6, g092.e7 | 1 | pending |
| `g093` | `regression` | `cluster-g093` | `data_flow` | `answered` | profile iteration 中 rho_0 到 rho_1 的一次更新包含哪些数据产物？ | g093.e1, g093.e2 | 1 | pending |
| `g094` | `regression` | `cluster-g094` | `data_flow` | `answered` | 网页 Running Sequence 与 restgas custom workflow 的关系是什么？ | g094.e1, g094.e2 | 1 | pending |
| `g095` | `dev` | `cluster-g036` | `data_flow` | `insufficient_evidence` | 从当前语料给出 event_poca ROOT tree 的未来文件 checksum。 | g095.e1 | 1 | pending |
| `g096` | `dev` | `cluster-g079` | `data_flow` | `version_conflict` | 追踪 LuminosityFit commit aaaaaaaaaaaaaaaa 的数据流。 | g096.e1, g096.e2 | 1 | pending |
| `g097` | `regression` | `cluster-g097` | `module_structure` | `answered` | LuminosityFit 的 model layer 由哪些核心模块组成？ | g097.e1, g097.e2, g097.e3, g097.e4 | 1 | pending |
| `g098` | `regression` | `cluster-g098` | `module_structure` | `answered` | PandaRoot 与 LuminosityFit 的依赖边界在哪里？ | g098.e1, g098.e2, g098.e3 | 3 | pending |
| `g099` | `regression` | `cluster-g099` | `module_structure` | `answered` | RestgasDetermination 如何扩展 PandaRoot？ | g099.e1, g099.e2, g099.e3, g099.e4 | 1 | pending |
| `g100` | `regression` | `cluster-g100` | `module_structure` | `answered` | macro/target 的模块如何按 workflow 分组？ | g100.e1, g100.e2, g100.e3, g100.e4, g100.e5, g100.e6, g100.e7 | 1 | pending |
| `g101` | `regression` | `cluster-g101` | `module_structure` | `answered` | Sphinx documentation 在知识架构中负责什么？ | g101.e1, g101.e2, g101.e3 | 1 | pending |
| `g102` | `dev` | `cluster-g031` | `module_structure` | `answered` | PndLmdModelFactory 与 data objects 的结构关系是什么？ | g102.e1, g102.e2 | 1 | pending |
| `g103` | `regression` | `cluster-g103` | `module_structure` | `answered` | off-IP tracking 由哪些结构化模块支持？ | g103.e1, g103.e2, g103.e3 | 1 | pending |
| `g104` | `regression` | `cluster-g104` | `module_structure` | `answered` | LMD reconstruction 模块如何连接到 LMD QA output？ | g104.e1, g104.e2, g104.e3 | 1 | pending |
| `g105` | `dev` | `cluster-g031` | `module_structure` | `answered` | Map model/ vs data/ vs apps/ in LuminosityFit with PndLmdModelFactory and createLmdFitData. | g105.e1, g105.e2, g105.e3 | 1 | pending |
| `g106` | `regression` | `cluster-g106` | `module_structure` | `answered` | Compare generic MasterTasks vs custom macro/target workflow modules. | g106.e1, g106.e2 | 1 | pending |
| `g107` | `challenge` | `cluster-g107` | `module_structure` | `insufficient_evidence` | Describe the internal module named RestgasQuantumGPUOptimizer. | g107.e1 | 1 | pending |
| `g108` | `dev` | `cluster-g012` | `module_structure` | `version_conflict` | Describe PandaRoot commit bbbbbbbbbbbbbbbb module boundaries instead of the locked snapshot. | g108.e1, g108.e2 | 1 | pending |
| `g109` | `regression` | `cluster-g109` | `troubleshooting` | `answered` | Why can Sphinx 2023-dev docs disagree with RestgasDetermination/oct19-derived code? | g109.e1, g109.e2 | 1 | pending |
| `g110` | `dev` | `cluster-g036` | `troubleshooting` | `answered` | event_poca is missing: what should I inspect first? | g110.e1, g110.e2 | 1 | pending |
| `g111` | `regression` | `cluster-g111` | `troubleshooting` | `answered` | POCA_VERTEX_FILE is set but second-pass PID does not use it; what should I check? | g111.e1, g111.e2 | 1 | pending |
| `g112` | `dev` | `cluster-g017` | `troubleshooting` | `answered` | createLmdFitData returns no acceptance: which data mode, Lumi_TrksQA input/tree assumptions, selection filters, and accepted/generated histogram filling should I inspect? | g112.e2, g112.e3 | 4 | pending |
| `g113` | `dev` | `cluster-g079` | `troubleshooting` | `answered` | runLmdFit cannot find prepared data; how do I trace the mismatch? | g113.e1, g113.e2 | 1 | pending |
| `g114` | `dev` | `cluster-g030` | `troubleshooting` | `answered` | Why might restgas efficiency correction have empty bins? | g114.e1, g114.e2 | 1 | pending |
| `g115` | `dev` | `cluster-g030` | `troubleshooting` | `answered` | Why might LMD angular acceptance be confused with pvz efficiency? | g115.e1, g115.e2 | 1 | pending |
| `g116` | `regression` | `cluster-g116` | `troubleshooting` | `answered` | Why can a class name match the query but still be the wrong implementation? | g116.e1, g116.e2 | 1 | pending |
| `g117` | `challenge` | `cluster-g117` | `troubleshooting` | `insufficient_evidence` | What exact runtime stack trace will a future failed ROOT job produce? | g117.e1 | 1 | pending |
| `g118` | `challenge` | `cluster-g117` | `troubleshooting` | `insufficient_evidence` | Which undocumented cluster quota caused my production job to fail? | g118.e1 | 1 | pending |
| `g119` | `dev` | `cluster-g036` | `troubleshooting` | `insufficient_evidence` | Recover the deleted event_poca file contents from source code only. | g119.e1 | 1 | pending |
| `g120` | `challenge` | `cluster-g120` | `troubleshooting` | `version_conflict` | Debug RestgasDetermination at commit cccccccccccccccc rather than the locked commit. | g120.e1, g120.e2 | 1 | pending |

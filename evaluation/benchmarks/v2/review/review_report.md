# Benchmark v2 P0/P1 review report

- Reviewed questions: 120
- Reviewer: OpenAI GPT-5.6 Thinking
- Reviewed at: 2026-08-02T19:49:00+02:00
- Result: all questions approved after the modifications recorded below.
- Release scope: approved as an exposed dev/challenge/regression benchmark; not a hidden final acceptance set.

## Global changes

- Narrowed all selectors that matched more than 20 knowledge objects in the locked corpus.
- Reframed g087 so the regression case tests C++ pointer normalization plus adapter consumption rather than duplicating g074.
- Corrected Karavdina evidence for g043 to PDF page 112 (printed page 104, Eq. 4.28).
- Added explicit workflow/graph entities where those source types are required.
- Replaced generic evidence roles with semantic roles.
- Atomized multi-part answer rubrics and aligned required source types with actual evidence groups.

## Per-question approval

| Case | Split | Status | Groups | Points | Review decision |
|---|---|---|---:|---:|---|
| `g001` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g002` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g003` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g004` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g005` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g006` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g007` | `dev` | `insufficient_evidence` | 1 | 1 | approved as drafted; roles/types normalized |
| `g008` | `dev` | `answered` | 2 | 1 | selector refined |
| `g009` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g010` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g011` | `dev` | `answered` | 2 | 3 | rubric atomized |
| `g012` | `dev` | `version_conflict` | 2 | 1 | selector refined |
| `g013` | `dev` | `answered` | 2 | 3 | selector refined |
| `g014` | `dev` | `answered` | 2 | 5 | selector refined; rubric atomized |
| `g015` | `dev` | `answered` | 2 | 3 | selector refined; rubric atomized |
| `g016` | `dev` | `answered` | 2 | 2 | selector refined; rubric atomized |
| `g017` | `dev` | `answered` | 2 | 5 | rubric atomized |
| `g018` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g019` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g020` | `dev` | `answered` | 2 | 4 | selector refined; rubric atomized |
| `g021` | `dev` | `answered` | 2 | 3 | rubric atomized |
| `g022` | `dev` | `answered` | 2 | 2 | selector refined; rubric atomized |
| `g023` | `dev` | `answered` | 2 | 3 | rubric atomized |
| `g024` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g025` | `dev` | `insufficient_evidence` | 1 | 1 | approved as drafted; roles/types normalized |
| `g026` | `dev` | `version_conflict` | 2 | 1 | selector refined |
| `g027` | `dev` | `answered` | 2 | 3 | approved as drafted; roles/types normalized |
| `g028` | `dev` | `answered` | 1 | 1 | selector refined |
| `g029` | `dev` | `answered` | 1 | 2 | rubric atomized |
| `g030` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g031` | `dev` | `answered` | 1 | 1 | selector refined |
| `g032` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g033` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g034` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g035` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g036` | `dev` | `answered` | 1 | 1 | selector refined |
| `g037` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g038` | `challenge` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g039` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g040` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g041` | `dev` | `insufficient_evidence` | 1 | 1 | selector refined |
| `g042` | `dev` | `version_conflict` | 1 | 1 | approved as drafted; roles/types normalized |
| `g043` | `challenge` | `answered` | 1 | 4 | rubric atomized; PDF page corrected |
| `g044` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g045` | `challenge` | `answered` | 1 | 2 | rubric atomized |
| `g046` | `challenge` | `answered` | 1 | 2 | rubric atomized |
| `g047` | `dev` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g048` | `challenge` | `answered` | 1 | 2 | rubric atomized |
| `g049` | `challenge` | `answered` | 1 | 2 | rubric atomized |
| `g050` | `dev` | `answered` | 1 | 2 | rubric atomized |
| `g051` | `dev` | `answered` | 2 | 2 | rubric atomized |
| `g052` | `dev` | `answered` | 1 | 2 | rubric atomized |
| `g053` | `challenge` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g054` | `challenge` | `answered` | 2 | 2 | rubric atomized |
| `g055` | `dev` | `answered` | 2 | 2 | rubric atomized |
| `g056` | `challenge` | `answered` | 1 | 1 | approved as drafted; roles/types normalized |
| `g057` | `dev` | `insufficient_evidence` | 1 | 1 | approved as drafted; roles/types normalized |
| `g058` | `dev` | `version_conflict` | 2 | 1 | approved as drafted; roles/types normalized |
| `g059` | `dev` | `answered` | 3 | 3 | selector refined; rubric atomized |
| `g060` | `dev` | `answered` | 3 | 3 | selector refined; rubric atomized |
| `g061` | `challenge` | `answered` | 2 | 3 | rubric atomized |
| `g062` | `challenge` | `answered` | 3 | 4 | selector refined; rubric atomized |
| `g063` | `dev` | `answered` | 4 | 4 | selector refined; rubric atomized |
| `g064` | `challenge` | `answered` | 2 | 4 | selector refined; rubric atomized |
| `g065` | `challenge` | `answered` | 3 | 3 | selector refined; rubric atomized |
| `g066` | `dev` | `answered` | 3 | 2 | rubric atomized |
| `g067` | `dev` | `answered` | 3 | 3 | rubric atomized |
| `g068` | `dev` | `answered` | 4 | 4 | rubric atomized |
| `g069` | `dev` | `answered` | 3 | 3 | rubric atomized |
| `g070` | `dev` | `answered` | 3 | 3 | selector refined; rubric atomized |
| `g071` | `challenge` | `answered` | 3 | 3 | selector refined; rubric atomized |
| `g072` | `dev` | `answered` | 4 | 4 | rubric atomized |
| `g073` | `dev` | `answered` | 4 | 3 | selector refined; rubric atomized |
| `g074` | `dev` | `answered` | 3 | 3 | rubric atomized |
| `g075` | `challenge` | `answered` | 4 | 4 | rubric atomized |
| `g076` | `dev` | `insufficient_evidence` | 2 | 1 | approved as drafted; roles/types normalized |
| `g077` | `dev` | `version_conflict` | 2 | 1 | selector refined |
| `g078` | `dev` | `answered` | 3 | 3 | selector refined; rubric atomized |
| `g079` | `dev` | `answered` | 6 | 5 | rubric atomized; typed evidence added |
| `g080` | `challenge` | `answered` | 6 | 5 | rubric atomized; typed evidence added |
| `g081` | `dev` | `answered` | 3 | 2 | selector refined; rubric atomized; typed evidence added |
| `g082` | `challenge` | `answered` | 4 | 3 | selector refined; rubric atomized; typed evidence added |
| `g083` | `challenge` | `answered` | 3 | 2 | rubric atomized; typed evidence added |
| `g084` | `challenge` | `answered` | 4 | 3 | rubric atomized; typed evidence added |
| `g085` | `dev` | `answered` | 4 | 3 | rubric atomized; typed evidence added |
| `g086` | `dev` | `answered` | 2 | 4 | rubric atomized |
| `g087` | `regression` | `answered` | 3 | 3 | selector refined; rubric atomized; typed evidence added |
| `g088` | `dev` | `answered` | 2 | 2 | selector refined; rubric atomized |
| `g089` | `dev` | `answered` | 4 | 3 | selector refined; rubric atomized; typed evidence added |
| `g090` | `regression` | `answered` | 4 | 3 | selector refined; rubric atomized; typed evidence added |
| `g091` | `challenge` | `answered` | 2 | 4 | selector refined; rubric atomized |
| `g092` | `regression` | `answered` | 8 | 7 | selector refined; rubric atomized; typed evidence added |
| `g093` | `regression` | `answered` | 3 | 4 | rubric atomized; typed evidence added |
| `g094` | `regression` | `answered` | 4 | 3 | selector refined; rubric atomized; typed evidence added |
| `g095` | `dev` | `insufficient_evidence` | 1 | 1 | selector refined |
| `g096` | `dev` | `version_conflict` | 2 | 1 | approved as drafted; roles/types normalized |
| `g097` | `regression` | `answered` | 4 | 4 | selector refined; rubric atomized |
| `g098` | `regression` | `answered` | 3 | 3 | selector refined |
| `g099` | `regression` | `answered` | 5 | 4 | selector refined; rubric atomized; typed evidence added |
| `g100` | `regression` | `answered` | 8 | 5 | selector refined; rubric atomized; typed evidence added |
| `g101` | `regression` | `answered` | 3 | 3 | selector refined; rubric atomized |
| `g102` | `dev` | `answered` | 2 | 3 | selector refined; rubric atomized |
| `g103` | `regression` | `answered` | 4 | 3 | rubric atomized; typed evidence added |
| `g104` | `regression` | `answered` | 4 | 3 | selector refined; rubric atomized; typed evidence added |
| `g105` | `dev` | `answered` | 3 | 3 | selector refined; rubric atomized |
| `g106` | `regression` | `answered` | 4 | 3 | selector refined; rubric atomized; typed evidence added |
| `g107` | `challenge` | `insufficient_evidence` | 1 | 1 | selector refined |
| `g108` | `dev` | `version_conflict` | 2 | 1 | selector refined |
| `g109` | `regression` | `answered` | 2 | 3 | selector refined; rubric atomized |
| `g110` | `dev` | `answered` | 2 | 3 | selector refined; rubric atomized |
| `g111` | `regression` | `answered` | 2 | 4 | selector refined; rubric atomized |
| `g112` | `dev` | `answered` | 2 | 4 | selector refined |
| `g113` | `dev` | `answered` | 2 | 3 | rubric atomized |
| `g114` | `dev` | `answered` | 2 | 3 | rubric atomized |
| `g115` | `dev` | `answered` | 2 | 3 | rubric atomized |
| `g116` | `regression` | `answered` | 2 | 3 | selector refined; rubric atomized |
| `g117` | `challenge` | `insufficient_evidence` | 1 | 1 | approved as drafted; roles/types normalized |
| `g118` | `challenge` | `insufficient_evidence` | 1 | 1 | approved as drafted; roles/types normalized |
| `g119` | `dev` | `insufficient_evidence` | 1 | 1 | selector refined |
| `g120` | `challenge` | `version_conflict` | 2 | 1 | selector refined |

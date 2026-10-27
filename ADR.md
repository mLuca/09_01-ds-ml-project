# Architecture Decision Records – Fraud Detection (STEG)

Decisions of the team (Karl, Mohamed, Hadi, Luca), taken from the team calls on **2026-10-21** (13:30–18:00) and **2026-10-22** (14:44–16:07).

**Status:** ✅ accepted · ⚠️ open / disputed · ↩️ replaced

| # | Decision | Status |
| --- | --- | --- |
| [ADR-001](#adr-001-evaluate-on-our-own-holdout-not-on-the-zindi-test-set) | Evaluate on our own holdout, Zindi test only for the submission | ✅ |
| [ADR-002](#adr-002-one-shared-split-stratified-by-client-no-time-split) | One shared split: 80/20, stratified, by client, no time split | ✅ |
| [ADR-003](#adr-003-one-row-per-client) | One row per client (bills are summarised into features) | ✅ |
| [ADR-004](#adr-004-same-metrics-for-every-model) | Same metrics for every model: ROC-AUC + Recall / F2 | ✅ |
| [ADR-005](#adr-005-notebook-workflow-personal-copies-one-merger) | Notebook workflow: personal copies local, one model notebook per person, Karl merges | ✅ (updated 10-22) |
| [ADR-006](#adr-006-one-baseline-logistic-regression-on-consumption) | One baseline: Logistic Regression on consumption | ✅ (updated 10-22) |
| [ADR-007](#adr-007-a-shared-base-feature-pool-with-room-to-experiment) | A shared base feature pool, with room to experiment | ✅ |
| [ADR-008](#adr-008-district-is-used-as-a-feature) | `disrict` is used as a feature | ✅ |
| [ADR-009](#adr-009-drop-reading_remarque) | Drop `reading_remarque` | ✅ |
| [ADR-010](#adr-010-months_number-no-derived-features) | `months_number`: no derived features | ✅ (`months_number_nunique` ⚠️) |
| [ADR-011](#adr-011-counter_statue) | `counter_statue` | ⚠️ |
| [ADR-012](#adr-012-no-linear-regression-as-a-model) | No linear regression as a model | ✅ |
| [ADR-013](#adr-013-stage-5-one-model-per-person-compared-on-the-same-features) | Stage 5: one model per person, compared on the same features | ✅ (updated 10-22) |
| [ADR-014](#adr-014-presentation-non-technical-split-between-the-team) | Presentation: non-technical, HTML + PDF, frauds found per 10,000 visits | ✅ (updated 10-22) |
| [ADR-015](#adr-015-drop-n_counters-leakage) | Drop `n_counters` (leakage) | ✅ |

---

## ADR-001: Evaluate on our own holdout, not on the Zindi test set

- **Status:** ✅ accepted (2026-10-21, 13:30 call)
- **Context:** `client_test` / `invoice_test` have no `target`, so we cannot check our model on them ourselves.
- **Decision:** We train and evaluate only on a split of `client_train`. The Zindi test set is used only for the submission; its leaderboard score is an extra outside comparison at the end (Stage 7).
- **Alternatives:** use the Zindi leaderboard as validation (Mohamed's idea) – rejected as the main check, because tuning on the leaderboard would make the score too optimistic.
- **Consequences:** a 20 % holdout must stay untouched until Stage 7.
- **Note (2026-10-22):** some first model results were already shown on the holdout. Treat them as preliminary; the final holdout number is reported **once**, for the one chosen model (Stage 7).
- **Amendment (2026-10-23, Karl – confirm in team):** each model **may report** its holdout AUC (column `holdout_auc` in `models/results.csv`), as information. Models are still **compared and chosen by CV only** – nobody changes features or settings because of a holdout score. First values: LightGBM (Mohamed) 0.8212 vs. CV 0.819 ✅ close; XGBoost (Luca) 0.838 vs. CV 0.773 ⚠ unusually high, still to explain.

## ADR-002: One shared split, stratified by client, no time split

- **Status:** ✅ accepted
- **Context:** the label belongs to the client, not to a bill; we don't know when a fraud started (Hadi). Splitting bills would put the same client into train and holdout (leakage).
- **Decision:** 80/20 split of the **clients** in `client_train`, `stratify=target` (5.6 % fraud in both parts), `random_state=42`. All bills follow their client. Everyone uses this split from the team notebook (Hadi, end of the second call).
- **Alternatives:** time-based split – not needed, the target has no date.
- **Consequences:** results of different team members are comparable.

## ADR-003: One row per client

- **Status:** ✅ accepted (Luca, Hadi)
- **Context:** if bills and clients are simply merged, every bill of a fraud client is labelled "fraud", although maybe only some of them show the fraud. The bills of a client are a kind of time series, not independent rows.
- **Decision:** condense the bills of each client into **one row of features** (e.g. mean consumption, variation, mismatch flag) – `build_features` in the notebook.
- **Consequences:** the model learns client behaviour, not single bills.

## ADR-004: Same metrics for every model

- **Status:** ✅ accepted
- **Context:** only 5.6 % fraud → accuracy is useless ("never fraud" is 94.4 % right). Comparing models only makes sense with the same metric (Hadi).
- **Decision:** **ROC-AUC** (Zindi metric, ranking quality) for model comparison; **Recall & F2** at a chosen threshold for the business view. 5-fold stratified CV on the train part.
- **Consequences:** every model is reported with CV AUC (mean ± spread).

## ADR-005: Notebook workflow – personal copies, one merger

- **Status:** ✅ accepted
- **Context:** merging several people's changes in one `.ipynb` causes conflicts; copy-pasting cells between notebooks does not work well (Luca).
- **Decision:**
  - Everyone experiments in a **personal copy** (`04_fraud_project_<initials>.ipynb`, ignored by git) – **not pushed** (Luca).
  - **Karl merges** agreed parts into the team notebook `04_fraud_project.ipynb` and opens a pull request; the others review and merge.
  - Do **not** overwrite the team notebook with "save as" – the history must stay traceable (Luca, Hadi).
  - Placeholders for all stages, so everybody sees which stage is filled by whom (Karl, Mohamed).
- **Proposed (Hadi):** keep the notebook short and readable; put functions close together instead of scattered over the notebook.
- **Update (2026-10-22, Luca, Mohamed, Hadi):** every model lives in its **own minimal model notebook** (load data → `build_features` → train / evaluate the model, "run all" works). Karl may now edit the team notebook directly; the model notebooks are merged into it afterwards.
- **Lesson for later projects (Karl):** split the work into several notebooks by purpose (problem framing, EDA, feature building, models).
- **Consequences:** one team notebook with everyone's work; Luca's EDA (PR #19) is kept as section 2.9.

## ADR-006: One baseline – Logistic Regression on consumption

- **Status:** ✅ accepted (2026-10-22: Karl, Luca, Mohamed) – replaces the earlier version with Dummy and Scorecard
- **Context:** Stage 4 first had three baselines (Dummy, a scorecard with hand-picked or calculated weights, Logistic Regression on 17 EDA-based features). The team found this too complex: a baseline should be the first naive guess **before** any EDA (Luca, Hadi).
- **Decision:** **only one baseline: Logistic Regression** on the consumption features – "fraud must somehow show in the consumption": `level_1_mean` … `level_4_mean`, `total_mean`, `total_std` (Luca: the four level means; total mean / std "can go in").
- **Removed:** Dummy reference and scorecard.
- **Values (5-fold CV AUC, train part):** 4 level means only 0.653 · **with `total_mean`, `total_std`: 0.663** · for comparison the full 15-feature set: 0.728.
- **Consequences:** every Stage 5 model is compared with this baseline; the gain from EDA features + model choice becomes visible ("baseline feature set" vs. "model feature set", Karl).

## ADR-007: A shared base feature pool, with room to experiment

- **Status:** ✅ accepted (compromise by Hadi)
- **Context:** Mohamed wanted free feature work per person; Luca wanted a fixed minimum pool because of the deadline.
- **Decision:** the agreed features (`build_features`) are the **base** everyone uses; each person may add or remove features for their model if it helps, and reports it.
- **Consequences:** Karl shares `build_features` in the team notebook. Hadi delivers a **seasonal / district anomaly** feature (consumption range per season compared with the district, as one column) that others can add.

## ADR-008: `disrict` is used as a feature

- **Status:** ✅ accepted (vote 3:1)
- **Context:** fraud rates differ by area (district 60: 3.6 % vs. 69: 7.1 %); regions lie inside districts. Luca raised the ethical question whether clients may be judged by where they live; Karl was against using it.
- **Decision:** use `disrict` (data-driven signal; Mohamed's idea: combine `disrict` + `region` into one "address" column).
- **Consequences:** Karl's simple baseline runs without `disrict` / `region`; they are added and compared in Stage 5. The ethics point should be mentioned in the presentation.

## ADR-009: Drop `reading_remarque`

- **Status:** ✅ accepted
- **Context:** codes 6, 8, 9 have almost the same fraud rate; code 7 has only ~500 bills; codes over 100 look like entry errors. Mean vs. mode per client was discussed (Luca, Hadi).
- **Decision:** not used.

## ADR-010: `months_number` – no derived features

- **Status:** ✅ accepted (Luca, Mohamed, Karl) – ⚠️ `months_number_nunique` still disputed
- **Context:** Luca tested what the column means: not the month of the bill (very low correlation), not the months since the last bill (only 40 %, or 65 % when gas and electricity are separated), not the months since client creation (1–1.5 %). Its meaning is unknown.
- **Decision (2026-10-22):** no feature that **assumes a meaning** of the column → `months_error` (flag > 240 months) and `total_per_month_mean` (consumption per month) are **removed** from `build_features`.
- **Open point:** Karl added `months_number_nunique` = number of **distinct** values per client ("the more different numbers, the stranger"); Luca had no better idea than to drop the column completely. Check in Stage 5 with vs. without.

## ADR-011: `counter_statue`

- **Status:** ⚠️ open
- **Context:** correlation with `target` ~0.004; more than 30 % of the clients have changing status values across their bills; meaning of the codes unknown. Hadi wanted to keep it (most common value); Luca proposed not to use it.
- **Current state:** Luca's cleaning (PR #19) deletes bills with invalid status values (41 bills, 5 clients, no fraud case). Karl's notebook uses `statue_1` / `statue_other` (most common value per client).
- **To decide:** keep the flags, or drop the column completely.

## ADR-012: No linear regression as a model

- **Status:** ✅ accepted (Luca, Mohamed; explanation Hadi)
- **Context:** the target is 0 / 1; a linear regression predicts a continuous number, not a probability.
- **Decision:** classification models only (Logistic Regression and later models).

## ADR-013: Stage 5 – one model per person, compared on the same features

- **Status:** ✅ accepted (updated 2026-10-22)
- **Decision:**
  - **Every person delivers one model** in its own model notebook; an ensemble can be built on top later (Mohamed, Luca).
  - **Luca:** XGBoost with `RandomizedSearchCV` tuned on **F2** and a tuned decision threshold (best ≈ 0.07); first result AUC ≈ 0.8, F2 ≈ 0.4. Used Karl's features without the `months_number` features and without `n_invoices`, kept `region`.
  - **Mohamed:** a tuned model (LightGBM / Random Forest), AUC ≈ 0.80 on the agreed features, ≈ 0.82 with `region` + `disrict` (train CV); compares the model without and with extra features.
  - **Hadi:** seasonal anomaly feature – benchmark per group (`client_catg` × electricity / gas = 6 groups): seasonal range = (max − min) / mean of the monthly consumption cycle; each client's own range is compared with the benchmark → **one column** ("suspicious range"). Code is shared in Discord so others can add it; then a model with and without it.
  - **Karl:** baseline, team notebook, merging, presentation.
- **Open:** `disrict` as category vs. number (trees don't care much, Luca).

## ADR-014: Presentation – non-technical, split between the team

- **Status:** ✅ accepted
- **Context:** 10 minutes **per group**, for a non-technical audience – slides, no code (Luca).
- **Decision:** Karl presents the start up to the baseline (features in two sentences, Logistic Regression as the value to beat); then the models of the others, compared with each other.
- **Update (2026-10-22, Karl):**
  - Format: **HTML** (interactive: confusion matrix with a slider for the number of visits) **and PDF** (the assignment requires a PDF on GitHub).
  - Key message for STEG: not "recall is better", but **how many more fraudsters are found with 10,000 inspections** than with the baseline.
  - Show all models, recommend the simpler one if the gap to the best model is small (business view: cost vs. gain).
  - Karl builds the template with placeholders today; it is filled when the model results arrive.

## ADR-015: Drop `n_counters` (leakage)

- **Status:** ✅ accepted (2026-10-22, Karl, Luca; Mohamed and Hadi informed)
- **Context:** `n_counters` (number of different meters per client) was the strongest feature. Suspicion: when STEG catches a fraudster, it replaces the manipulated meter – the new meter would then be a *result* of the detection, not a *sign* of fraud, and would not exist yet when STEG wants to predict (data leakage). Checks on the train part (Karl's notebook, Stage 6 marker):

  | Check | Honest clients | Fraud clients |
  | --- | --- | --- |
  | Meter change (same type) | 18.6 % | 59.8 % |
  | Newest meter starts (0 = start, 1 = last bill), median | 0.34 | 0.71 |
  | Change in the last 10 % of the history | 7.8 % | 23.6 % |

  | Logistic Regression (5-fold CV AUC, old 17 features) | AUC |
  | --- | --- |
  | with `n_counters` | 0.788 |
  | `n_counters` without the last 12 months | 0.761 |
  | without `n_counters` | 0.727 |

- **Options discussed:** A keep and name the risk · **B drop** · C count meters only without the last 12 months.
- **Decision:** **B – `n_counters` is removed** from `build_features`. "It looks good if we show that we recognised the issue and did not use it" (Luca).
- **Consequences:** all Stage 5 models use the feature set without `n_counters`; the turning point is part of the presentation (why the score dropped, and why that is the honest number).

## ADR-016: Keep `n_counter_codes` (known residual risk)

- **Status:** ✅ accepted (2026-10-26, team)
- **Context:** `n_counter_codes` (number of different counter codes per client) could be the same meter-change leak as `n_counters` (ADR-015) through the back door: a new meter after a detected fraud probably brings a new code. It is used by Mohamed (LightGBM, feature group `meter_codes`), Luca (XGBoost, since PR #25) and the shared `helper.build_features`; Hadi's ensemble does not use it.

  | LightGBM (Mohamed), 5-fold CV AUC on train | AUC |
  | --- | --- |
  | with `n_counter_codes` | 0.817 |
  | without `n_counter_codes` | 0.795 (−0.021) |

  For comparison: dropping the real leak `n_counters` cost about 0.05.
- **Options discussed:** A drop it · **B keep it and name the risk** · C keep it only if a test shows no leak.
- **Decision:** **B – `n_counter_codes` stays**, nothing else is changed. The gap is small for a potential target leak.
- **Consequences:** the model results (Stages 5–7, presentation) are reported **with** `n_counter_codes`; the residual risk is named in the limits / turning points (Stage 7.6). **Possible proof later:** count the codes without the last 12 and 24 months of each client, like the `n_counters` check (Stage 6 marker) – if the AUC stays close to 0.817, it is a real signal; if it drops towards 0.795, it is a leak and ADR-016 is revisited.

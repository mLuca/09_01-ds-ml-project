# Architecture Decision Records – Fraud Detection (STEG)

Decisions of the team (Karl, Mohamed, Hadi, Luca), taken from the team calls on **2026-10-21** (13:30 – – 18:00).

**Status:** ✅ accepted · ⚠️ open / disputed · ↩️ replaced

| # | Decision | Status |
| --- | --- | --- |
| [ADR-001](#adr-001-evaluate-on-our-own-holdout-not-on-the-zindi-test-set) | Evaluate on our own holdout, Zindi test only for the submission | ✅ |
| [ADR-002](#adr-002-one-shared-split-stratified-by-client-no-time-split) | One shared split: 80/20, stratified, by client, no time split | ✅ |
| [ADR-003](#adr-003-one-row-per-client) | One row per client (bills are summarised into features) | ✅ |
| [ADR-004](#adr-004-same-metrics-for-every-model) | Same metrics for every model: ROC-AUC + Recall / F2 | ✅ |
| [ADR-005](#adr-005-notebook-workflow-personal-copies-one-merger) | Notebook workflow: personal copies stay local, Karl merges via PR | ✅ |
| [ADR-006](#adr-006-logistic-regression-is-the-baseline-model) | Logistic Regression is the baseline model | ✅ (scope ⚠️) |
| [ADR-007](#adr-007-a-shared-base-feature-pool-with-room-to-experiment) | A shared base feature pool, with room to experiment | ✅ |
| [ADR-008](#adr-008-district-is-used-as-a-feature) | `disrict` is used as a feature | ✅ |
| [ADR-009](#adr-009-drop-reading_remarque) | Drop `reading_remarque` | ✅ |
| [ADR-010](#adr-010-drop-months_number) | Drop `months_number` | ✅ (`months_error` ⚠️) |
| [ADR-011](#adr-011-counter_statue) | `counter_statue` | ⚠️ |
| [ADR-012](#adr-012-no-linear-regression-as-a-model) | No linear regression as a model | ✅ |
| [ADR-013](#adr-013-stage-5-models-and-work-split) | Stage 5: models and work split | ✅ |
| [ADR-014](#adr-014-presentation-non-technical-split-between-the-team) | Presentation: non-technical, split between the team | ✅ |

---

## ADR-001: Evaluate on our own holdout, not on the Zindi test set

- **Status:** ✅ accepted (2026-10-21, 13:30 call)
- **Context:** `client_test` / `invoice_test` have no `target`, so we cannot check our model on them ourselves.
- **Decision:** We train and evaluate only on a split of `client_train`. The Zindi test set is used only for the submission; its leaderboard score is an extra outside comparison at the end (Stage 7).
- **Alternatives:** use the Zindi leaderboard as validation (Mohamed's idea) – rejected as the main check, because tuning on the leaderboard would make the score too optimistic.
- **Consequences:** a 20 % holdout must stay untouched until Stage 7.

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
- **Consequences:** one team notebook with everyone's work; Luca's EDA (PR #19) is kept as section 2.9.

## ADR-006: Logistic Regression is the baseline model

- **Status:** ✅ accepted (Mohamed) – ⚠️ scope of the baseline features disputed
- **Context:** the assignment needs a baseline to beat. Results: Dummy 0.500, scorecard ~0.67, Logistic Regression ~0.79 (CV AUC).
- **Decision:** Logistic Regression is the baseline model; boosting models belong to Stage 5 (Karl).
- **Open point:** Luca and Hadi see a baseline as a **very naive** first guess (e.g. only consumption and remarks in a Logistic Regression, or only `client_catg` 51). Karl's current baseline already uses many EDA insights ("pretty complex", Luca). The original starter notebook used only the mean of each consumption level.
- **Consequences:** Stage 5 models must beat the Logistic Regression clearly (more than the CV spread).

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

## ADR-010: Drop `months_number`

- **Status:** ✅ accepted (Luca, Mohamed) – ⚠️ the flag `months_error` is disputed
- **Context:** Luca tested what the column means: not the month of the bill (very low correlation), not the months since the last bill (only 40 %, or 65 % when gas and electricity are separated), not the months since client creation (1–1.5 %). Its meaning is unknown.
- **Decision:** `months_number` is not used.
- **Open point:** Karl's flag `months_error` (bills with > 240 months, 38 clients) is still in the notebook; Luca sees no meaning for it, because the 240-month limit assumes a meaning of the column. If it goes, the median imputation in the pipeline may become unnecessary.

## ADR-011: `counter_statue`

- **Status:** ⚠️ open
- **Context:** correlation with `target` ~0.004; more than 30 % of the clients have changing status values across their bills; meaning of the codes unknown. Hadi wanted to keep it (most common value); Luca proposed not to use it.
- **Current state:** Luca's cleaning (PR #19) deletes bills with invalid status values (41 bills, 5 clients, no fraud case). Karl's notebook uses `statue_1` / `statue_other` (most common value per client).
- **To decide:** keep the flags, or drop the column completely.

## ADR-012: No linear regression as a model

- **Status:** ✅ accepted (Luca, Mohamed; explanation Hadi)
- **Context:** the target is 0 / 1; a linear regression predicts a continuous number, not a probability.
- **Decision:** classification models only (Logistic Regression and later models).

## ADR-013: Stage 5 models and work split

- **Status:** ✅ accepted
- **Decision:**
  - **Luca:** XGBoost (gradient boosting, "industry standard").
  - **Hadi:** XGBoost / several methods (Logistic Regression, KNN, trees) combined as an **ensemble**; delivers the anomaly feature first.
  - **Mohamed:** a different model, announced in Discord so nobody works on the same one.
  - **Karl:** merges the notebook, makes it easy to understand, prepares the presentation; AdaBoost is an option.
  - Stick to the course material; neural networks only if there is time left at the end.
  - Afterwards: compare the models, pick the best or build an ensemble.
- **Next meeting:** 2026-10-22, 14:30.

## ADR-014: Presentation – non-technical, split between the team

- **Status:** ✅ accepted
- **Context:** 10 minutes **per group**, for a non-technical audience – slides, no code (Luca).
- **Decision:** Karl presents the start up to the baseline (features in two sentences, Logistic Regression as the value to beat); then the models of the others, compared with each other.

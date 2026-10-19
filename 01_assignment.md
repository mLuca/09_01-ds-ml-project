# Machine Learning Project: Assignment

This is your second project. As a team, you will take a real dataset from raw data to a working machine learning model and a stakeholder presentation. The aim is to practise the full data science lifecycle together: frame a problem, build a baseline, iterate with error analysis, and communicate your findings to a non-technical audience.

This template repository is your starting point. It ships a configured environment and an example notebook that trains a simple model with minimal cleaning and feature selection. Treat it as scaffolding for your own project.

Work through the sections below in order: first choose a project, then plan it on a board, build and iterate, and finally prepare your deliverables.

## Choose a Project

Pick one option as a team. Aim for a problem with a clear stakeholder and a clear business value.

### Option A: Zindi challenge (Easy to Advanced)

Choose one challenge on [Zindi](https://zindi.africa/competitions). Follow the requirements of the challenge, and also prepare a stakeholder presentation.

1. [Tanzania Tourism Prediction](https://zindi.africa/competitions/tanzania-tourism-prediction/data) (Easy, 2 people)
2. [Fraud Detection in Electricity and Gas Consumption](https://zindi.africa/competitions/fraud-detection-in-electricity-and-gas-consumption-challenge) (Medium, has a starter notebook, 2 to 3 people)
3. [Urban Air Pollution Challenge](https://zindi.africa/competitions/zindiweekendz-learning-urban-air-pollution-challenge) (Medium to Advanced, 3 people and some domain knowledge)
4. [Flight Delay Prediction](https://zindi.africa/competitions/flight-delay-prediction-challenge) (Medium, 3 people; airport data via [airportsdata](https://pypi.org/project/airportsdata/))
5. [Financial Inclusion in Africa](https://zindi.africa/competitions/financial-inclusion-in-africa) (Easy, 2 people)

### Option B: Kickstarter project success (Medium)

In recent years, the range of funding options for projects created by individuals and small companies has expanded considerably. Alongside savings, bank loans, and friends and family funding, crowdfunding has become a popular and readily available alternative.

Kickstarter, founded in 2009, is a well-known crowdfunding platform. It uses an all-or-nothing funding model: a project is only funded if it meets its goal amount, otherwise backers give no money to the project.

Many factors contribute to the success or failure of a project, in general and also on Kickstarter. Some of these can be quantified or categorised, which makes it possible to build a model that predicts whether a project will succeed. The aim of this project is to build such a model and to analyse Kickstarter project data more generally, so you can help potential creators assess whether Kickstarter is a good funding option for them and what their chances of success are.

Data: [Kickstarter Projects on Kaggle](https://www.kaggle.com/datasets/kemical/kickstarter-projects).

### Option C: Other tabular datasets (Kaggle)

Structured, tabular datasets from real companies with a clear business case. Choose a regression or a classification problem.

**Regression (continuous target):**

- [Zillow Prize: Home Value Prediction](https://www.kaggle.com/competitions/zillow-prize-1): predict the log error between Zillow's automated price estimate and the actual sale price. Target: `logerror`.
- [Mercedes-Benz Greener Manufacturing](https://www.kaggle.com/competitions/mercedes-benz-greener-manufacturing): predict the time a car takes on the test bench from its configuration. Target: testing time (`y`).
- [Santander Value Prediction Challenge](https://www.kaggle.com/competitions/santander-value-prediction-challenge): predict a continuous customer value score from anonymised data. Target: `target`.
- [Allstate Claims Severity](https://www.kaggle.com/competitions/allstate-claims-severity): predict the cost of insurance claims. Target: `loss`.
- [Expedia Hotel Recommendations](https://www.kaggle.com/competitions/expedia-hotel-recommendations) (regression variant): predict the likelihood of a user booking a hotel cluster.

**Classification (categorical target):**

- [Porto Seguro Safe Driver Prediction](https://www.kaggle.com/competitions/porto-seguro-safe-driver-prediction): predict whether a driver will file a claim next year. Target: binary.
- [Santander Customer Transaction Prediction](https://www.kaggle.com/competitions/santander-customer-transaction-prediction): predict which customers will make a specific transaction. Target: binary.
- [Expedia Hotel Recommendations](https://www.kaggle.com/competitions/expedia-hotel-recommendations): classify which hotel cluster a user is most likely to book. Target: multi-class (`hotel_cluster`).
- [Avito Demand Prediction](https://www.kaggle.com/competitions/avito-demand-prediction): predict whether an advert will be successful (demand). Target: classification.
- [Home Credit Default Risk](https://www.kaggle.com/competitions/home-credit-default-risk): predict whether a loan applicant will default. Target: binary (`TARGET`).

## Timeline and Milestones

The project runs over four days. Track your progress on a GitHub Kanban board. The board setup is described in [02_kanban_board.md](02_kanban_board.md).

| Milestone | What it is | Target |
| --- | --- | --- |
| Milestone 0 | Data Ingestion  | Day 1, 12:00 |
| Milestone 1 | EDA  | Day 2, 12:00 |
| Milestone 2 | First model, the baseline | Day 3, 12:00 |
| Milestone 3 | A model with error analysis | Day 4, 12:00 |
| Milestone 4 | Final deliverables and presentation | Day 5, 14:00 |

For each milestone, write two things in the GitHub issue:

1. What needs to be completed to be done with the milestone.
2. The definition of done: what your result looks like when the milestone is complete.

### Baseline model example (Milestone 1)

A baseline is the simplest thing that could work. It gives you a score to beat. For example, for a fraud detection project:

- **Value of the product:** find fraudulent transactions, save money, avoid reputation damage, and prevent money laundering.
- **Prediction:** whether a transaction is fraudulent.
- **Evaluation metric:** F1 score. We want to minimise losses through fraud and at the same time avoid falsely accusing customers (and perhaps losing them). Both false positives and false negatives have strong negative effects, so a balanced metric like the F1 score fits.
- **Baseline model:** assume transactions that happen at midnight are likely to be fraudulent.
- **Score:** F1 score = 0.1.

## Things to Think About

As you build and iterate on your models, keep these in mind:

- Check for data imbalance.
- What is the right performance metric for your problem: precision, recall, accuracy, F1 score, or something else? (Consider the true positive rate.)
- Try at least three different machine learning algorithms to see which performs best, including cross validation and hyperparameter tuning.

## Final Deliverables

1. A slide deck (PDF, pushed to GitHub) designed for non-technical stakeholders that outlines your findings, recommendations, and future work. This supports a 10 minute presentation.
2. A Jupyter notebook following PEP 8, designed for a data science and technical audience. The notebook should be well documented and reproducible, with a clear narrative and visualisations that support your findings. It should be pushed to GitHub.
3. One slide about a potential data product: how could the predictions be used?

## Resources

If your dataset is imbalanced, these are useful starting points:

- [8 Tactics to Combat Imbalanced Classes](https://machinelearningmastery.com/tactics-to-combat-imbalanced-classes-in-your-machine-learning-dataset/)
- [Random Oversampling and Undersampling for Imbalanced Classification](https://machinelearningmastery.com/random-oversampling-and-undersampling-for-imbalanced-classification/)

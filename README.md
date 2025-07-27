# 📊 Wallet Risk Scoring System – Zeru Finance Assignment

## 🔍 Objective

Build a wallet risk scoring model using on-chain activity data from Compound V3 transactions. The goal is to assign a **risk score between 0–1000** to each wallet address, identifying potentially risky behavior patterns based on transactional and behavioral attributes.

---

## 🧠 Approach

We adopted a hybrid **unsupervised → interpretable** pipeline to score DeFi wallets, combining **Isolation Forest** (to model anomalous activity) and **Linear Regression** (to derive a simple, explainable formula).

### Step 1: Data Parsing & Cleaning

- Data collection done by fetching queries from TheGraph's enpoint for compound V2
- Relied on Etherscan API key, (replace it in .env for reproducibility of results)
- Parsed nested JSON transaction data for 100 wallet addresses.
- Extracted raw event data such as function names, gas usage, status flags, block numbers, timestamps, etc.
- Merged data across wallets into a unified `DataFrame`.

### Step 2: Feature Engineering

Divided into multiple steps:

1. Transactional-features
  Selected based on correlation and domain knowledge

2. Aggregate Features
  Selected using Pearson matrix to find the correlation and dropping columns
  Dropped some columns based on analysis of values and real-world scope

3. Isolation forest to calculate pseudo-scores
  Used the scores to further tune columns down to final under 20 columns using xgbregressor for feature_importances_

4. Handpicked 5-6 features
  The features are shown in the table with description.
  These columns were used as the input for a linear regression model and the psuedo-risk scores as the label
  Linear regression coefficients help right the formula for the final risk scores.

Derived behavioral and statistical features for each wallet. Notable examples:

| Feature | Description |
|--------|-------------|
| `fn_entropy` | Entropy of function types (higher = more diverse activity) |
| `unique_to_ratio` | Ratio of unique recipients to total transactions |
| `fncount_approve_ratio` | Ratio of `approve()` function calls |
| `gas_std`, `gas_mean` | Variability and average of gas used |
| `tx_gap_std` | Standard deviation of time gaps between transactions |
| `value_sum` | Total transaction value across all events |
| `error_rate`, `fail_rate` | Fraction of failed/errored transactions |

In total, ~25 features were generated per wallet before xgb-pruning

### Step 3: Risk Score Modeling (Unsupervised)

Used an **Isolation Forest** model to generate a raw anomaly score for each wallet. The model identifies outliers based on multivariate feature distribution.

- Tuned for `contamination="auto"` and fitted on all engineered features.
- Raw scores were scaled to a **0–1000** range to produce a human-readable **`scaled_risk_score`**.

---

### Step 4: Interpretable Risk Formula (Linear Regression)

To explain the risk computation in a simple, business-friendly way:

- Trained a **Linear Regression** model using top features to predict the Isolation Forest scores.
- Selected 6 most intuitive and important features based on:
  - XGBoost feature importance
  - Feature correlation with raw scores
  - Domain reasoning

**Final selected features:**

- `gas_std`
- `unique_to_ratio`
- `fncount_approve_ratio`
- `fn_entropy`
- `gas_mean`
- `tx_gap_std`

**Final scoring formula:**

```python
final_risk_score = (
    + 4.56 * gas_std
    - 3 * unique_to_ratio
    - 1.9 * fncount_approve_ratio
    - 1.15 * fn_entropy
    + 1.2 * fncount_borrow_ratio
)
Post scoring, the values would have to be scaled in the range 0-1000, easily achievable by using minmaxscaler.

```

These coefficients were extracted directly from the trained linear model and rounded for simplicity.

### 📈 Results & Distribution

The final_risk_score was scaled to 0–1000 and shows a skewed distribution (most wallets are low-to-medium risk).

### ✅ Deliverables

final_df.csv: Risk scores + features per wallet.

workflow.ipynb: Jupyter notebook with all code and reasonings.

fetch.py: A seperate python script to handle data-fetching

README.md: This file.

### 💡 Possible Improvements (if more time allowed)

- Add more protocol-specific features (liquidations, borrow health).

- refine Isolation Forest parameters and scoring thresholds.

- fix skewed data thoroughly

### 👨‍💻 Author

Jaspreet Singh

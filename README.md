# EcoTrace – Food Waste Supply Chain & Relief Router

<p align="center">
  <strong>Reducing food waste through machine learning, donation prioritization, and location-aware relief routing.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Machine%20Learning-Random%20Forest-2E8B57" />
  <img src="https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Academic%20Project-blue" />
</p>

---

## Overview

**EcoTrace** is a machine learning-driven food waste management and relief routing project. It aims to identify perishable food inventory at elevated risk of spoilage, prioritize suitable surplus food for donation, and assign donation batches to nearby partner NGOs.

The project combines a supervised machine learning workflow with a geographical allocation process and an interactive Streamlit dashboard. It brings together food inventory data, spoilage-risk estimates, donation quantities, and NGO dispatch information in one workflow.

## Problem Statement

Food waste can occur when perishable products remain unsold as their expiration dates approach. At the same time, food-relief organizations need timely access to available food resources.

EcoTrace explores how data-driven prioritization and location-aware NGO allocation can help connect surplus food with potential relief partners before it goes to waste.

## Project Workflow

```text
Perishable Goods Dataset
          |
          v
Data Exploration & Preprocessing
          |
          v
Random Forest Spoilage Classifier
          |
          v
Spoilage Probability Estimation
          |
          v
Donation Prioritization
          |
          v
Available Donation Quantity Calculation
          |
          v
Nearest NGO Allocation
          |
          v
Dispatch Manifest & NGO Summary
          |
          v
Streamlit Dashboard
```

## Key Features

### 1. Food Spoilage Prediction
- Uses a supervised **Random Forest Classifier** to estimate the probability of food spoilage.
- Processes numerical and categorical inventory features.
- Handles missing numerical and categorical values using imputation.
- Applies one-hot encoding to categorical variables.
- Uses stratified train-test splitting and GridSearchCV for model selection.

### 2. Donation Prioritization
Food records are shortlisted using the following conditions in the notebook:
- The product is not in the Pharmaceuticals category.
- The product has between 0 and 3 days remaining until expiry.
- Predicted spoilage probability is at least 0.50.
- Available quantity is greater than zero.

Available donation units are calculated as:

```python
available_units = max(initial_quantity - units_sold, 0)
```

The selected records are exported to `food_selected_for_donation.csv`.

### 3. NGO Allocation & Relief Routing
- Maintains a predefined directory of partner NGOs across five geographic regions.
- Calculates geographical distance using the **Haversine formula**.
- Assigns each donation batch to the nearest eligible NGO in the same region, considering its remaining daily capacity.
- Estimates transit time using an assumed average speed of 50 km/h and a 0.5-hour loading buffer.
- Classifies dispatch urgency based on the number of days remaining until expiry.
- Exports a dispatch manifest and NGO-wise delivery summary to Excel.

> **Routing note:** The current implementation uses nearest-neighbour NGO allocation based on Haversine distance. It is not a road-network shortest-path algorithm; actual road routes and live traffic are not integrated.

### 4. Interactive Streamlit Dashboard
The dashboard provides an overview of donation and dispatch information, including:

- Total batches flagged.
- Potential units available for diversion.
- Average predicted spoilage-risk score.
- Number of partner NGOs.
- Regional donation volume.
- Spoilage probability distribution.
- Dispatch manifest.
- NGO allocation summary.
- Dispatch urgency overview.

Users can filter the displayed records by region, food category, expiry window, and risk threshold.

## Tech Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Data manipulation | Pandas, NumPy |
| Machine learning | Scikit-learn, Random Forest |
| Data visualization | Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Excel processing | OpenPyXL |
| Development | Jupyter Notebook, VS Code |

## Dataset & Project Files

The project uses a perishable-goods dataset containing **100,000 records and 42 columns**.

| File | Description |
|---|---|
| `perishable_goods_management.csv` | Main inventory dataset used for exploration and model training |
| `EcoTrace.ipynb` | Notebook containing preprocessing, model training, donation selection, and routing workflow |
| `food_selected_for_donation.csv` | Food records selected for potential donation |
| `EcoTrace_Relief_Router_Shortest_Path.xlsx` | Excel output containing dispatch details and NGO delivery summaries |
| `app.py` | Streamlit dashboard application |

### Generated Outputs

The routing workbook contains two sheets:

1. **Shortest Path Dispatch** – donation batch details, assigned NGO, geographical distance, estimated transit time, and dispatch urgency.
2. **NGO Deliveries Summary** – NGO-wise batch counts, total units received, and average allocation distance.

## Model Configuration & Results

The notebook uses a Random Forest classifier with GridSearchCV.

**Selected hyperparameters:**

| Parameter | Selected value |
|---|---:|
| `n_estimators` | 250 |
| `max_depth` | 14 |
| `min_samples_leaf` | 3 |
| Cross-validation folds | 3 |
| Scoring metric | ROC-AUC |

**Observed project outputs:**

| Metric | Result |
|---|---:|
| Source dataset records | 100,000 |
| Selected donation records | 7,145 |
| Potential units identified for donation | 575,524 |
| Best cross-validation ROC-AUC | 0.586 |

The reported ROC-AUC is the notebook's best cross-validation score, not a held-out test score. It indicates that the current model has limited predictive discrimination and should be improved and validated further before real-world use. The donation figures represent quantities identified by the project workflow, not verified food donations or confirmed waste reduction.

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/EcoTrace.git
cd EcoTrace
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install numpy pandas scikit-learn matplotlib seaborn streamlit openpyxl jupyter
```

### 4. Arrange the project files

Keep the following files in the same project directory:

```text
EcoTrace/
│
├── app.py
├── EcoTrace.ipynb
├── perishable_goods_management.csv
├── food_selected_for_donation.csv
├── EcoTrace_Relief_Router_Shortest_Path.xlsx
└── README.md
```

The filenames above are the names expected by the application. Rename the downloaded files accordingly if their local filenames contain suffixes such as `(2)` or `(3)`.

### 5. Run the Streamlit dashboard

```bash
streamlit run app.py
```

Streamlit will provide a local URL in the terminal. Open that URL in your browser to access the dashboard.

### 6. Run the notebook

Launch Jupyter:

```bash
jupyter notebook
```

Open `EcoTrace.ipynb` and update the dataset path in the data-loading cell to point to the location of `perishable_goods_management.csv` on your system. Run the notebook cells in sequence to execute the analysis and workflow.

## Current Limitations & Future Improvements

- Improve model performance through feature engineering, model comparison, class-imbalance analysis, and further hyperparameter tuning.
- Evaluate the final model on a held-out test set using appropriate classification metrics.
- Replace generated store coordinates with verified geographical coordinates.
- Integrate road-network routing and live traffic data for more realistic delivery estimates.
- Enforce NGO capacity constraints in every allocation scenario, including the fallback case.
- Add food-safety and donation eligibility checks before recommending any food for distribution.
- Deploy the dashboard so that authorized stakeholders can access it.

## Project Scope & Disclaimer

EcoTrace is an academic prototype built to demonstrate a potential application of machine learning and data analytics to food waste management and humanitarian logistics. Its dataset, generated coordinates, NGO directory, and estimated transit times should not be interpreted as a live operational system. Food safety, legal requirements, recipient needs, and real-world logistics must be independently verified before any actual donation or dispatch.

## Author

**Aditi Jha**

Computer Science & Engineering

- GitHub: [aditi-jha25](https://github.com/aditi-jha25)

---

<p align="center">
  <strong>EcoTrace — Turning surplus food data into informed relief decisions.</strong>
</p>

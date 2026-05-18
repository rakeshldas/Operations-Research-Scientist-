# Azure-Enabled Supply Chain Optimization Engine

## Project Purpose

This project is designed as an Operations Research Scientist interview showcase for ORMAE-style roles.

It demonstrates how an OR optimization model can be converted from a local Python notebook into a cloud-ready decision-support workflow using Microsoft Azure.

## Business Problem

A company has:
- 15 manufacturing plants
- 120 warehouse demand zones
- 1,800 transportation lanes
- capacity limits
- demand requirements
- route-wise cost, distance, lead time, emission, and risk data

The goal is to minimize total transportation cost while satisfying all warehouse demand and respecting plant and route constraints.

## Mathematical Model

Decision variable:

x[i,j] = quantity shipped from plant i to warehouse j

Objective:

Minimize total transportation cost.

Constraints:
- Plant capacity constraint
- Warehouse demand fulfillment constraint
- Route capacity constraint
- Non-negativity constraint

## Project Structure

```text
azure_supply_chain_or_full_project/
│
├── data/
│   ├── plants.csv
│   ├── warehouses.csv
│   └── transport_cost.csv
│
├── notebooks/
│   └── 01_supply_chain_optimization_walkthrough.ipynb
│
├── src/
│   ├── optimize_transportation.py
│   ├── azure_read_blob.py
│   └── azure_upload.py
│
├── outputs/
│
├── azure_deployment/
│   └── deployment_steps.md
│
├── requirements.txt
└── README.md
```

## How to Run Locally

```bash
pip install -r requirements.txt
python src/optimize_transportation.py
```

## Expected Outputs

- optimal_shipment_plan.csv
- capacity_utilization.csv
- demand_fulfillment.csv
- cost_summary.csv

## Azure Workflow

1. Upload input CSV files to Azure Blob Storage
2. Run optimization in Azure Machine Learning Compute Instance
3. Save result files
4. Upload output CSV files to Azure Blob Storage
5. Connect outputs to Power BI or use them for decision reporting

## Interview Positioning

This is not just a transportation problem. It is a cloud-ready decision optimization engine. It shows mathematical modeling, Python implementation, Azure deployment thinking, and business-facing decision support.

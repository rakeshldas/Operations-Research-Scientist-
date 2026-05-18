# Azure Deployment Steps for OR Scientist Project

## Objective

Deploy a supply chain transportation optimization model using Azure as a decision-science platform.

## Azure Services Used

1. Azure Resource Group
2. Azure Storage Account
3. Azure Blob Storage
4. Azure Machine Learning Workspace
5. Azure Compute Instance
6. Optional: Power BI / Azure ML Batch Endpoint

## Step 1: Create Resource Group

Azure Portal:
- Search: Resource Groups
- Create: `rg-or-supply-chain-demo`
- Region: Central India / West India / East US

## Step 2: Create Storage Account

- Name: `orsupplychainstorage<unique>`
- Performance: Standard
- Redundancy: LRS
- Create containers:
  - `or-input-data`
  - `or-output-results`

Upload these files to `or-input-data`:
- plants.csv
- warehouses.csv
- transport_cost.csv

## Step 3: Create Azure Machine Learning Workspace

- Name: `mlw-or-supply-chain`
- Connect it to the same Resource Group
- Create a Compute Instance
- Open JupyterLab / Notebooks

## Step 4: Upload Project Files

Upload:
- data folder
- src folder
- notebooks folder
- requirements.txt

Install requirements:

```bash
pip install -r requirements.txt
```

## Step 5: Run Local/Azure Notebook

Execute:
- load data
- validate feasibility
- solve optimization model
- generate outputs

## Step 6: Save Outputs

Output files:
- optimal_shipment_plan.csv
- capacity_utilization.csv
- demand_fulfillment.csv
- cost_summary.csv

Upload them to:
- `or-output-results`

## Step 7: Explain Interview Architecture

Business data is uploaded to Azure Blob Storage. Azure ML reads the data, executes an OR model, solves the optimization problem, stores the optimal decisions back into Blob Storage, and Power BI or business users consume the final result.

## Step 8: Possible Extensions

- MILP route activation
- Carbon-minimization objective
- Multi-objective optimization
- Scenario analysis
- Batch endpoint for scheduled runs
- Power BI dashboard

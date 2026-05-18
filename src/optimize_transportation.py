"""
Cloud-Based Supply Chain Network Optimization
Author: Dr. Rakesh L. Das - OR Scientist Showcase Project

This script solves a large transportation optimization problem:
- Multiple plants
- Multiple warehouse demand zones
- Route-wise transportation cost
- Plant capacity limits
- Warehouse demand satisfaction
- Route capacity limits

Solver: Google OR-Tools Linear Solver
"""

import pandas as pd
from pathlib import Path
from ortools.linear_solver import pywraplp


def load_data(data_dir: str = "data"):
    data_path = Path(data_dir)
    plants = pd.read_csv(data_path / "plants.csv")
    warehouses = pd.read_csv(data_path / "warehouses.csv")
    routes = pd.read_csv(data_path / "transport_cost.csv")
    return plants, warehouses, routes


def validate_data(plants, warehouses, routes):
    total_capacity = plants["capacity"].sum()
    total_demand = warehouses["demand"].sum()

    if total_capacity < total_demand:
        raise ValueError(
            f"Infeasible data: total capacity {total_capacity} is less than total demand {total_demand}"
        )

    required_routes = len(plants) * len(warehouses)
    if len(routes) < required_routes:
        print("Warning: Some plant-warehouse lanes may be missing.")

    return {
        "total_capacity": total_capacity,
        "total_demand": total_demand,
        "capacity_buffer_percent": round((total_capacity / total_demand - 1) * 100, 2),
        "num_plants": len(plants),
        "num_warehouses": len(warehouses),
        "num_routes": len(routes),
    }


def solve_transportation_model(plants, warehouses, routes, output_dir: str = "outputs"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert key columns to string to avoid ID mismatch
    plants["plant_id"] = plants["plant_id"].astype(str)
    warehouses["warehouse_id"] = warehouses["warehouse_id"].astype(str)
    routes["plant_id"] = routes["plant_id"].astype(str)
    routes["warehouse_id"] = routes["warehouse_id"].astype(str)

    plant_ids = plants["plant_id"].tolist()
    warehouse_ids = warehouses["warehouse_id"].tolist()

    capacity = dict(zip(plants["plant_id"], plants["capacity"]))
    demand = dict(zip(warehouses["warehouse_id"], warehouses["demand"]))

    cost = {
        (row.plant_id, row.warehouse_id): row.cost_per_unit
        for row in routes.itertuples(index=False)
    }

    route_capacity = {
        (row.plant_id, row.warehouse_id): row.route_capacity
        for row in routes.itertuples(index=False)
    }

    # Create solver
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if solver is None:
        raise RuntimeError("Could not create OR-Tools GLOP solver.")

    # Decision variables
    # x[i,j] = shipment quantity from plant i to warehouse j
    x = {}
    for i in plant_ids:
        for j in warehouse_ids:
            if (i, j) in cost:
                x[(i, j)] = solver.NumVar(0, route_capacity[(i, j)], f"x_{i}_{j}")

    # Plant capacity constraints
    for i in plant_ids:
        solver.Add(
            sum(x[(i, j)] for j in warehouse_ids if (i, j) in x) <= capacity[i],
            f"Capacity_{i}"
        )

    # Warehouse demand constraints
    for j in warehouse_ids:
        solver.Add(
            sum(x[(i, j)] for i in plant_ids if (i, j) in x) == demand[j],
            f"Demand_{j}"
        )

    # Objective function: minimize total transportation cost
    objective = solver.Objective()
    for (i, j), var in x.items():
        objective.SetCoefficient(var, cost[(i, j)])
    objective.SetMinimization()

    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL:
        raise RuntimeError("No optimal solution found. Check capacity, demand, and route capacity.")

    # Prepare result tables
    route_lookup = routes.set_index(["plant_id", "warehouse_id"]).to_dict("index")
    plant_lookup = plants.set_index("plant_id").to_dict("index")
    warehouse_lookup = warehouses.set_index("warehouse_id").to_dict("index")

    shipments = []
    for (i, j), var in x.items():
        qty = var.solution_value()
        if qty > 1e-6:
            r = route_lookup[(i, j)]
            p = plant_lookup[i]
            w = warehouse_lookup[j]
            shipments.append({
                "plant_id": i,
                "plant": p["plant"],
                "plant_region": p["region"],
                "warehouse_id": j,
                "warehouse": w["warehouse"],
                "warehouse_region": w["region"],
                "quantity_shipped": round(qty, 2),
                "cost_per_unit": r["cost_per_unit"],
                "total_route_cost": round(qty * r["cost_per_unit"], 2),
                "distance_km": r["distance_km"],
                "lead_time_days": r["lead_time_days"],
                "emission_kg_per_unit": r["emission_kg_per_unit"],
                "total_emission_kg": round(qty * r["emission_kg_per_unit"], 2),
                "route_risk_score": r["route_risk_score"]
            })

    shipments_df = pd.DataFrame(shipments)

    plant_usage = (
        shipments_df.groupby(["plant_id", "plant", "plant_region"], as_index=False)
        .agg(total_shipped=("quantity_shipped", "sum"),
             total_cost=("total_route_cost", "sum"),
             total_emission_kg=("total_emission_kg", "sum"))
    )
    plant_usage = plant_usage.merge(
        plants[["plant_id", "capacity"]],
        on="plant_id",
        how="left"
    )
    plant_usage["utilization_percent"] = round(
        plant_usage["total_shipped"] / plant_usage["capacity"] * 100, 2
    )
    plant_usage["unused_capacity"] = round(plant_usage["capacity"] - plant_usage["total_shipped"], 2)

    demand_fulfillment = (
        shipments_df.groupby(["warehouse_id", "warehouse", "warehouse_region"], as_index=False)
        .agg(total_received=("quantity_shipped", "sum"),
             total_inbound_cost=("total_route_cost", "sum"),
             avg_lead_time_days=("lead_time_days", "mean"))
    )
    demand_fulfillment = demand_fulfillment.merge(
        warehouses[["warehouse_id", "demand", "priority", "service_level_target"]],
        on="warehouse_id",
        how="left"
    )
    demand_fulfillment["fulfillment_gap"] = round(
        demand_fulfillment["demand"] - demand_fulfillment["total_received"], 2
    )
    demand_fulfillment["fulfillment_percent"] = round(
        demand_fulfillment["total_received"] / demand_fulfillment["demand"] * 100, 2
    )

    summary = pd.DataFrame([{
        "minimum_total_transportation_cost": round(objective.Value(), 2),
        "total_quantity_shipped": round(shipments_df["quantity_shipped"].sum(), 2),
        "total_demand_fulfilled": round(demand_fulfillment["total_received"].sum(), 2),
        "total_emission_kg": round(shipments_df["total_emission_kg"].sum(), 2),
        "active_routes_used": len(shipments_df),
        "plants_used": shipments_df["plant_id"].nunique(),
        "warehouses_served": shipments_df["warehouse_id"].nunique(),
        "average_cost_per_unit": round(objective.Value() / shipments_df["quantity_shipped"].sum(), 4)
    }])

    shipments_df.to_csv(output_path / "optimal_shipment_plan.csv", index=False)
    plant_usage.to_csv(output_path / "capacity_utilization.csv", index=False)
    demand_fulfillment.to_csv(output_path / "demand_fulfillment.csv", index=False)
    summary.to_csv(output_path / "cost_summary.csv", index=False)

    return shipments_df, plant_usage, demand_fulfillment, summary


if __name__ == "__main__":
    plants, warehouses, routes = load_data("data")
    print("Data validation summary:")
    print(validate_data(plants, warehouses, routes))
    shipments, plant_usage, demand_fulfillment, summary = solve_transportation_model(
        plants, warehouses, routes, "outputs"
    )
    print("\nOptimization Summary:")
    print(summary.to_string(index=False))
    print("\nOutput files created in /outputs folder.")

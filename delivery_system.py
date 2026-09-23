
import argparse
import json
import math
from typing import Any


def load_data(file_path: str) -> dict[str, Any]:
    
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_locations(locations: Any, item_name: str) -> dict[str, list[float]]:
    
    if isinstance(locations, dict):
        return locations

    if isinstance(locations, list):
        normalized = {}
        for item in locations:
            if not isinstance(item, dict) or "id" not in item:
                raise ValueError(f"Invalid {item_name} entry: {item}")

            location = item.get("location")
            if not isinstance(location, list) or len(location) != 2:
                raise ValueError(
                    f"Invalid location for {item_name} {item['id']}: {location}"
                )
            normalized[item["id"]] = location
        return normalized

    raise ValueError(f"'{item_name}' must be an object or list.")


def normalize_packages(packages: Any) -> list[dict[str, Any]]:
    
    if not isinstance(packages, list):
        raise ValueError("'packages' must be a list.")

    normalized = []
    for package in packages:
        if not isinstance(package, dict):
            raise ValueError(f"Invalid package: {package}")

        package_copy = dict(package)

        if "warehouse" not in package_copy and "warehouse_id" in package_copy:
            package_copy["warehouse"] = package_copy["warehouse_id"]

        for key in ("id", "warehouse", "destination"):
            if key not in package_copy:
                raise ValueError(f"Package is missing '{key}': {package_copy}")

        normalized.append(package_copy)

    return normalized


def normalize_data(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Input JSON must contain an object at the root.")

    for key in ("warehouses", "agents", "packages"):
        if key not in data:
            raise ValueError(f"Missing required field: '{key}'")

    return {
        "warehouses": normalize_locations(data["warehouses"], "warehouse"),
        "agents": normalize_locations(data["agents"], "agent"),
        "packages": normalize_packages(data["packages"]),
    }


def validate_data(data: dict[str, Any]) -> None:
    if not data["agents"]:
        raise ValueError("At least one delivery agent is required.")

    for agent_id, location in data["agents"].items():
        if not isinstance(location, list) or len(location) != 2:
            raise ValueError(f"Invalid location for agent {agent_id}: {location}")

    for warehouse_id, location in data["warehouses"].items():
        if not isinstance(location, list) or len(location) != 2:
            raise ValueError(
                f"Invalid location for warehouse {warehouse_id}: {location}"
            )

    for package in data["packages"]:
        if package["warehouse"] not in data["warehouses"]:
            raise ValueError(
                f"Package {package['id']} references unknown warehouse "
                f"'{package['warehouse']}'."
            )

        if (
            not isinstance(package["destination"], list)
            or len(package["destination"]) != 2
        ):
            raise ValueError(
                f"Invalid destination for package {package['id']}: "
                f"{package['destination']}"
            )


def euclidean_distance(point_a: list[float], point_b: list[float]) -> float:
    return math.sqrt(
        (point_a[0] - point_b[0]) ** 2
        + (point_a[1] - point_b[1]) ** 2
    )


def assign_packages(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    
    assignments = {agent_id: [] for agent_id in data["agents"]}

    for package in data["packages"]:
        warehouse_location = data["warehouses"][package["warehouse"]]

        nearest_agent = min(
            data["agents"],
            key=lambda agent_id: (
                euclidean_distance(
                    data["agents"][agent_id], warehouse_location
                ),
                agent_id,
            ),
        )
        assignments[nearest_agent].append(package)

    return assignments


def simulate_delivery(
    data: dict[str, Any],
    assignments: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    
    package_to_agent = {}
    for agent_id, packages in assignments.items():
        for package in packages:
            package_to_agent[package["id"]] = agent_id

    ordered_assignments = {agent_id: [] for agent_id in data["agents"]}
    for package in data["packages"]:
        ordered_assignments[package_to_agent[package["id"]]].append(package)

    results = {}

    for agent_id, packages in ordered_assignments.items():
        current_location = list(data["agents"][agent_id])
        total_distance = 0.0

        for package in packages:
            warehouse_location = data["warehouses"][package["warehouse"]]
            destination = package["destination"]

            total_distance += euclidean_distance(
                current_location, warehouse_location
            )
            total_distance += euclidean_distance(
                warehouse_location, destination
            )

            current_location = list(destination)

        count = len(packages)
        efficiency = total_distance / count if count else 0.0

        results[agent_id] = {
            "packages_delivered": count,
            "total_distance": round(total_distance, 2),
            "efficiency": round(efficiency, 2),
        }

    active_agents = [
        agent_id
        for agent_id, result in results.items()
        if result["packages_delivered"] > 0
    ]

    best_agent = (
        min(
            active_agents,
            key=lambda agent_id: (
                results[agent_id]["efficiency"],
                agent_id,
            ),
        )
        if active_agents
        else None
    )

    results["best_agent"] = best_agent
    return results


def run(input_file: str, output_file: str) -> dict[str, Any]:
    """Run the complete simulation and save report.json."""
    raw_data = load_data(input_file)
    data = normalize_data(raw_data)
    validate_data(data)

    assignments = assign_packages(data)
    report = simulate_delivery(data, assignments)

    total_delivered = sum(
        result["packages_delivered"]
        for agent_id, result in report.items()
        if agent_id != "best_agent"
    )

    if total_delivered != len(data["packages"]):
        raise RuntimeError(
            "Validation failed: delivered package count does not match "
            "the number of input packages."
        )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FastBox Mystery Delivery System"
    )
    parser.add_argument(
        "-i", "--input", default="data.json",
        help="Input JSON file (default: data.json)"
    )
    parser.add_argument(
        "-o", "--output", default="report.json",
        help="Output JSON file (default: report.json)"
    )
    args = parser.parse_args()

    report = run(args.input, args.output)
    print(f"Report generated: {args.output}")
    print(f"Best agent: {report['best_agent']}")


if __name__ == "__main__":
    main()

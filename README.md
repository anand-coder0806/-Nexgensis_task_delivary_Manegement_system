# Mystery Delivery System

Python Developer assignment submission for the FastBox logistics simulation.

## Project Structure

```text
mystery-delivery-system/

├── data.json
├── delivery_system.py
├── report.json
├── README.md
├── requirements.txt
├── .gitignore
├── test_cases/
│   ├── test_case_1.json
│   ├── test_case_2.json
│   ├── test_case_3.json
│   ├── test_case_4.json
│   ├── test_case_5.json
│   ├── test_case_6.json
│   ├── test_case_7.json
│   ├── test_case_8.json
│   ├── test_case_9.json
│   └── test_case_10.json
└── reports/
    ├── report_test_1.json
    ├── report_test_2.json
    ├── report_test_3.json
    ├── report_test_4.json
    ├── report_test_5.json
    ├── report_test_6.json
    ├── report_test_7.json
    ├── report_test_8.json
    ├── report_test_9.json
    └── report_test_10.json

## Requirements

- Python 3.9+
- No third-party dependencies

## Run

Base case:

```bash
python delivery_system.py
```

Specific test case:

```bash
python delivery_system.py --input test_cases/test_case_1.json --output report_test_1.json
```

You can replace `test_case_1.json` with any of the 10 supplied test cases.

## How It Works

### 1. JSON parsing

The program reads the input JSON using Python's standard `json` module.

It supports both the dictionary-style format in the test cases and the list-of-objects format used by the supplied base case.

### 2. Nearest-agent assignment

For every package, the program compares the agent's starting position with the package's warehouse using Euclidean distance:

```text
sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

The closest agent receives the package.

If there is an exact distance tie, the lexicographically smaller agent ID is selected to keep the result deterministic.

### 3. Delivery simulation

Packages are processed in their original input order.

For every assigned package:

```text
Agent current position
        ↓
Warehouse
        ↓
Destination
```

Both travel distances are added to the agent's total.

After delivery, the agent's current position becomes that package's destination.

### 4. Efficiency

```text
efficiency = total_distance / packages_delivered
```

The agent with the lowest average distance per package is selected as `best_agent`.

### 5. Validation

Before writing the report, the program checks that:

```text
total delivered packages == total input packages
```

This prevents packages from silently disappearing from the simulation.

## Assumptions

The assignment asks candidates to make reasonable assumptions for undefined scenarios and document them.

This implementation assumes:

1. Packages are processed in input order.
2. Assignment is based on the agent's original starting location and warehouse location, as stated in the assignment.
3. Once an agent completes a delivery, its current location becomes the package destination.
4. The agent travels to the warehouse before every assigned package.
5. The agent does not return to its starting location after delivery.
6. Equal nearest-agent distances are resolved using the smaller agent ID.
7. Efficiency means average distance travelled per delivered package.
8. Lower efficiency value means less distance per package.
9. All valid packages must be delivered.
10. No external libraries are necessary.

## Output Format

The generated `report.json` follows the requested structure:

```json
{
    "A1": {
        "packages_delivered": 2,
        "total_distance": 85.32,
        "efficiency": 42.66
    },
    "A2": {
        "packages_delivered": 2,
        "total_distance": 120.12,
        "efficiency": 60.06
    },
    "A3": {
        "packages_delivered": 1,
        "total_distance": 50.0,
        "efficiency": 50.0
    },
    "best_agent": "A1"
}
```

Those values are the assignment document's example output. The program calculates actual values from the input and does not hardcode the example.

## Testing

The repository contains all 10 supplied test cases.

Suggested commands:

```bash
python delivery_system.py -i test_cases/test_case_1.json -o report_test_1.json
python delivery_system.py -i test_cases/test_case_2.json -o report_test_2.json
python delivery_system.py -i test_cases/test_case_3.json -o report_test_3.json
```

Repeat through `test_case_10.json`.

Controll flow:
              data.json
                  │
                  ▼
           Read / Parse JSON
                  │
                  ▼
        Normalize input format
                  │
                  ▼
       Validate input data
                  │
                  ▼
       Assign every package
       to nearest agent
                  │
                  ▼
        Simulate deliveries
                  │
                  ▼
       Calculate distance
       for every delivery
                  │
                  ▼
       Generate agent report
                  │
                  ▼
        Find best_agent
                  │
                  ▼
             report.json
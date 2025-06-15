
# BSPSSEPy Bus Functions Manual

This manual provides a comprehensive guide to the bus-related functions available in the `BSPSSEPyBusFunctions` module. These functions allow for dynamic retrieval, control, and status updates of buses in the BSPSSEPy simulation framework, utilizing both PSSE and custom `BSPSSEPyBus` data.

---

## Overview of Functions

The module includes the following key functions:

1. **GetBusInfo**: Retrieve bus data dynamically from PSSE and the `BSPSSEPyBus` DataFrame.
2. **GetBusInfoPSSE**: Directly fetch bus data from PSSE.
3. **BusTrip**: Trip a bus and update its status in the `BSPSSEPyBus` DataFrame.
4. **BusClose**: Close a bus and update its status in the `BSPSSEPyBus` DataFrame.

---

## **1. GetBusInfo**

**Description:**
Fetches information about buses based on specified keys. This function supports querying by bus name, number, or custom keys and integrates data from both PSSE and the custom `BSPSSEPyBus` DataFrame.

### **Features**

- Handles multiple cases:
  - **Case 1:** Single key for a specific bus -> Returns a single value.
  - **Case 2:** Multiple keys for a specific bus -> Returns a list of values.
  - **Case 3:** Single key for all buses -> Returns a list of values for all buses.
  - **Case 4:** Multiple keys for all buses -> Returns a dictionary with keys and corresponding lists for all buses.

### **Arguments**

- `BusKeys` (*str* or *list of str*): The key(s) for the required information. Valid keys include:
  - **PSSE keys:** Defined in `BusInfoDic`.
  - **BSPSSEPyBus keys:** Columns in the `BSPSSEPyBus` DataFrame.
- `BusName` (*str, optional*): The name of the bus.
- `BusNumber` (*int, optional*): The number of the bus.
- `BSPSSEPyBus` (*pd.DataFrame, optional*): The DataFrame containing custom bus data.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- **Case 1:** Single value (e.g., *str*, *int*, *float*).
- **Case 2:** List of values.
- **Case 3:** List of values.
- **Case 4:** Dictionary of lists.

### **Example Usage**

```python
result = GetBusInfo(
    BusKeys=["TYPE", "NAME"],
    BusNumber=101,
    BSPSSEPyBus=Sim.BSPSSEPyBuses,
    DebugPrint=True
)
```

---

## **2. GetBusInfoPSSE**

**Description:**
Fetches specific information about buses directly from the PSSE library.

### **Features**

- Flexible querying options for attributes like bus type, name, and number.

### **Arguments**

- `abusString` (*str*): Requested information string (e.g., "NUMBER", "TYPE").
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- List of requested information for the bus(es).

### **Example Usage**

```python
bus_types = GetBusInfoPSSE("TYPE", DebugPrint=True)
```

---

## **3. BusTrip**

**Description:**
Trips a bus (sets its status to "Tripped") and updates the `BSPSSEPyBus` DataFrame.

### **Features**

- Updates simulation-specific metadata, such as action time and status.
- Supports querying by bus name or number.

### **Arguments**

- `t` (*float*): Current simulation time.
- `BSPSSEPyBus` (*pd.DataFrame*): The DataFrame containing custom bus data.
- `BusNumber` (*int, optional*): The number of the bus.
- `BusName` (*str, optional*): The name of the bus.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- `int`: Status of the operation (`0` for success).

### **Example Usage**

```python
status = BusTrip(
    t=10.0,
    BSPSSEPyBus=Sim.BSPSSEPyBuses,
    BusNumber=101,
    DebugPrint=True
)
```

---

## **4. BusClose**

**Description:**
Closes a bus (sets its status to "Closed") and updates the `BSPSSEPyBus` DataFrame.

### **Features**

- Ensures proper synchronization with the simulation state.
- Supports querying by bus name or number.

### **Arguments**

- `t` (*float*): Current simulation time.
- `BSPSSEPyBus` (*pd.DataFrame*): The DataFrame containing custom bus data.
- `BusNumber` (*int, optional*): The number of the bus.
- `BusName` (*str, optional*): The name of the bus.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- `int`: Status of the operation (`0` for success).

### **Example Usage**

```python
status = BusClose(
    t=15.0,
    BSPSSEPyBus=Sim.BSPSSEPyBuses,
    BusName="Main Bus",
    DebugPrint=True
)
```

---

## **DataFrame Structure:** `BSPSSEPyBus`

The `BSPSSEPyBus` DataFrame stores simulation-specific bus data. The following columns are maintained:

| Column Name               | Description                                         |
| ------------------------- | --------------------------------------------------- |
| `NAME`                    | Name of the bus.                                    |
| `NUMBER`                  | Bus number.                                         |
| `BSPSSEPyType`            | Bus type (e.g., 1, 2, 3, 4).                        |
| `BSPSSEPyStatus`          | Current status of the bus (`Closed`/`Tripped`).     |
| `BSPSSEPyLastAction`      | Last action performed (`Close`/`Trip`).             |
| `BSPSSEPyLastActionTime`  | Timestamp of the last action.                       |
| `BSPSSEPySimulationNotes` | Notes about the bus state or actions.               |

---

## **Best Practices and Recommendations**

- Use `GetBusInfo` for most queries to dynamically retrieve bus information.
- Update the `BSPSSEPyBus` DataFrame with every action (`BusTrip`, `BusClose`) to maintain consistency (*Done Automatically*).
- Validate keys using `BusInfoDic` for accurate data retrieval from PSSE.

For additional details or to report issues, contact the developer at `ilyas.farhat@outlook.com`.

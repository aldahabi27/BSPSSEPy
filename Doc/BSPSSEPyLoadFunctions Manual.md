
# BSPSSEPy Load Functions Manual

This manual provides a comprehensive guide to the load-related functions available in the `BSPSSEPyLoadFunctions` module. These functions allow for dynamic retrieval, control, and management of loads in the BSPSSEPy simulation framework, utilizing both PSSE and the `BSPSSEPyLoads` DataFrame.

---

## Overview of Functions

The module includes the following key functions:

1. **GetLoadInfo**: Retrieve load data dynamically from PSSE and the `BSPSSEPyLoads` DataFrame.
2. **GetLoadInfoPSSE**: Directly fetch load data from PSSE.
3. **LoadDisable**: Disable a load and update its status in the `BSPSSEPyLoads` DataFrame.
4. **LoadEnable**: Enable a load and update its status in the `BSPSSEPyLoads` DataFrame.
5. **NewLoad**: Add a new load to the PSSE system and update the `BSPSSEPyLoads` DataFrame.

---

## **1. GetLoadInfo**

**Description:**
Fetches information about loads based on specified keys. This function supports querying by load name, ID, or custom keys and integrates data from both PSSE and the custom `BSPSSEPyLoads` DataFrame.

### **Features**

- Handles multiple cases:
  - **Case 1:** Single key for a specific load -> Returns a single value.
  - **Case 2:** Multiple keys for a specific load -> Returns a list of values.
  - **Case 3:** Single key for all loads -> Returns a list of values for all loads.
  - **Case 4:** Multiple keys for all loads -> Returns a dictionary with keys and corresponding lists for all loads.

### **Arguments**

- `LoadKeys` (*str* or *list of str*): The key(s) for the required information. Valid keys include:
  - **PSSE keys:** Defined in `LoadInfoDic`.
  - **BSPSSEPyLoads keys:** Columns in the `BSPSSEPyLoads` DataFrame.
- `LoadName` (*str, optional*): The name of the load.
- `LoadID` (*str, optional*): The ID of the load.
- `BSPSSEPyLoads` (*pd.DataFrame, optional*): The DataFrame containing custom load data.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- **Case 1:** Single value (e.g., *str*, *int*, *float*).
- **Case 2:** List of values.
- **Case 3:** List of values.
- **Case 4:** Dictionary of lists.

### **Example Usage**

```python
result = GetLoadInfo(
    LoadKeys=["ID", "LOADNAME", "NAME", "NUMBER"],
    LoadID="L1",
    LoadName="Load1",
    BSPSSEPyLoads=Sim.BSPSSEPyLoads,
    DebugPrint=True
)
```

---

## **2. GetLoadInfoPSSE**

**Description:**
Fetches specific information about loads directly from the PSSE library.

### **Features**

- Flexible querying options for attributes like load name, ID, and type.

### **Arguments**

- `aloadString` (*str*): Requested information string (e.g., "ID", "NAME").
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- List of requested information for the load(s).

### **Example Usage**

```python
load_ids = GetLoadInfoPSSE("ID", DebugPrint=True)
```

---

## **3. LoadDisable**

**Description:**
Disables a load (sets its status to 0) and updates the `BSPSSEPyLoads` DataFrame.

### **Features**

- Updates simulation-specific metadata, such as action time and status.
- Supports querying by load name or ID.

### **Arguments**

- `t` (*float*): Current simulation time.
- `BSPSSEPyLoads` (*pd.DataFrame*): The DataFrame containing custom load data.
- `LoadName` (*str, optional*): The name of the load.
- `LoadID` (*str, optional*): The ID of the load.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- `int`: Status of the operation (`0` for success).

### **Example Usage**

```python
status = LoadDisable(
    t=5.0,
    BSPSSEPyLoads=Sim.BSPSSEPyLoads,
    LoadName="Load1",
    DebugPrint=True
)
```

---

## **4. LoadEnable**

**Description:**
Enables a load (sets its status to 1) and updates the `BSPSSEPyLoads` DataFrame.

### **Features**

- Ensures proper synchronization with the simulation state.
- Supports querying by load name or ID.

### **Arguments**

- `t` (*float*): Current simulation time.
- `BSPSSEPyLoads` (*pd.DataFrame*): The DataFrame containing custom load data.
- `LoadName` (*str, optional*): The name of the load.
- `LoadID` (*str, optional*): The ID of the load.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- `int`: Status of the operation (`0` for success).

### **Example Usage**

```python
status = LoadEnable(
    t=10.0,
    BSPSSEPyLoads=Sim.BSPSSEPyLoads,
    LoadID="L1",
    DebugPrint=True
)
```

---

## **5. NewLoad**

**Description:**
Adds a new load entry to the PSSE system and updates the `BSPSSEPyLoads` DataFrame.

### **Features**

- Automatically determines the bus location based on the specified element or bus.
- Configurable power parameters using the `PowerArray`.

### **Arguments**

- `LoadID` (*str, optional*): Unique identifier for the load (default: "ZZ").
- `LoadName` (*str, optional*): Name of the load (default: None).
- `BSPSSEPyLoads` (*pd.DataFrame*): The DataFrame to store the load data.
- `BusName` (*str, optional*): Name of the bus where the load will be created.
- `BusNumber` (*int, optional*): Number of the bus where the load will be created.
- `ElementName` (*str, optional*): Name of the element (e.g., generator) to locate the bus.
- `ElementType` (*str, optional*): Type of the element (e.g., "Gen", "TWTF", "Load").
- `PowerArray` (*list, optional*): A list containing power-related parameters:
  - [PL, QL, IP, IQ, YP, YQ, Power Factor (optional)].
- `UseFromBus` (*bool, optional*): If True, use the "from bus" for branches/transformers; otherwise, use "to bus". Default is True.
- `DebugPrint` (*bool, optional*): Enables detailed debug output (default: False).

### **Returns**

- `int`: PSSE error code (`0` for success).

### **Example Usage**

```python
status = NewLoad(
    LoadID="NL",
    LoadName="CustomLoad1",
    BSPSSEPyLoads=Sim.BSPSSEPyLoads,
    BusNumber=101,
    PowerArray=[10.0, 5.0],
    DebugPrint=True
)
```

---

## **DataFrame Structure:** `BSPSSEPyLoads`

The `BSPSSEPyLoads` DataFrame stores simulation-specific load data. The following columns are maintained:

| Column Name               | Description                                      |
| ------------------------- | ------------------------------------------------ |
| `ID`                      | Unique identifier for the load (2 chars).        |
| `LOADNAME`                | Name of the load.                                |
| `NAME`                    | Bus name where the load is located.              |
| `NUMBER`                  | Bus number where the load is located.            |
| `BSPSSEPyStatus`          | Current status of the load (`Closed`/`Tripped`). |
| `BSPSSEPyLastAction`      | Last action performed (`Close`/`Trip`).          |
| `BSPSSEPyLastActionTime`  | Timestamp of the last action.                    |
| `BSPSSEPySimulationNotes` | Notes about the load state or actions.           |
| `TiedDeviceName`          | Name of the associated element, if any.          |
| `TiedDeviceType`          | Type of the associated element, if any.          |

---

## **Best Practices and Recommendations**

- Use `GetLoadInfo` for most queries to dynamically retrieve load information.
- Update the `BSPSSEPyLoads` DataFrame with every action (`LoadDisable`, `LoadEnable`) to maintain consistency (*Done Automatically*).
- Validate keys using `LoadInfoDic` for accurate data retrieval from PSSE.

For additional details or to report issues, contact the developer at `ilyas.farhat@outlook.com`.


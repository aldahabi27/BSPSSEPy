# BSPSSEPy Transformer Functions Manual

This manual provides a comprehensive guide to the transformer-related functions available in the `BSPSSEPyTrnFunctions` module. These functions facilitate the retrieval, control, and status management of two-winding transformers in the BSPSSEPy simulation framework, leveraging both PSSE and custom `BSPSSEPyTrn` data.

---

## Overview of Functions

The module includes the following key functions:

1. **GetTrnInfo**: Retrieve transformer data dynamically from PSSE and the `BSPSSEPyTrn` DataFrame.
2. **GetTrnInfoPSSE**: Directly fetch transformer data from PSSE.
3. **TrnTrip**: Trip a transformer and update its status in the `BSPSSEPyTrn` DataFrame.
4. **TrnClose**: Close a transformer and update its status in the `BSPSSEPyTrn` DataFrame.

---

## **1. GetTrnInfo**

**Description:**
Fetches information about two-winding transformers based on specified keys. This function supports querying by transformer name, ID, or bus connections, and integrates data from both PSSE and the custom `BSPSSEPyTrn` DataFrame.

### **Features**

- Handles multiple cases:
  - **Case 1:** Single key for a specific transformer -> Returns a single value.
  - **Case 2:** Multiple keys for a specific transformer -> Returns a list of values.
  - **Case 3:** Single key for all transformers -> Returns a list of values for all transformers.
  - **Case 4:** Multiple keys for all transformers -> Returns a dictionary with keys and corresponding lists for all transformers.

### **Arguments**

- `TrnKeys` (*str* or *list of str*): The key(s) for the required information. Valid keys include:
  - **PSSE keys:** Defined in `TrnInfoDic`.
  - **BSPSSEPyTrn keys:** Columns in the `BSPSSEPyTrn` DataFrame.
- `TrnName` (*str, optional*): The name of the transformer.
- `FromBus` (*int or str, optional*): The "from" bus number or name.
- `ToBus` (*int or str, optional*): The "to" bus number or name.
- `BSPSSEPyTrn` (*pd.DataFrame, optional*): The DataFrame containing custom transformer data.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- **Case 1:** Single value (e.g., *str*, *int*, *float*).
- **Case 2:** List of values.
- **Case 3:** List of values.
- **Case 4:** Dictionary of lists.

### **Example Usage**

```python
result = GetTrnInfo(
    TrnKeys=["STATUS", "RXACT"],
    TrnName="Transformer1",
    BSPSSEPyTrn=Sim.BSPSSEPyTrn,
    DebugPrint=True
)
```

---

## **2. GetTrnInfoPSSE**

**Description:**
Fetches specific information about transformers directly from the PSSE library.

### **Features**

- Flexible querying options:
  - Single entry per transformer.
  - Bi-directional entries for each transformer.

### **Arguments**

- `atrnString` (*str*): Requested information string (e.g., "RXACT", "STATUS").
- `TrnEntry` (*int*): Specifies data retrieval direction:
  - `1`: Single entry per transformer.
  - `2`: Bi-directional entries for each transformer.
- `TrnName` (*str, optional*): The name of the transformer.
- `FromBus` (*int or str, optional*): The "from" bus number or name.
- `ToBus` (*int or str, optional*): The "to" bus number or name.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- List of requested information for the transformer(s).

### **Example Usage**

```python
rx_data = GetTrnInfoPSSE("RXACT", TrnName="Transformer1", DebugPrint=True)
```

---

## **3. TrnTrip**

**Description:**
Trips a transformer (sets its status to "Tripped") and updates the `BSPSSEPyTrn` DataFrame.

### **Features**

- Updates simulation-specific metadata, such as action time and status.
- Supports querying by transformer name, ID, or bus connections.

### **Arguments**

- `t` (*float*): Current simulation time.
- `BSPSSEPyTrn` (*pd.DataFrame*): The DataFrame containing custom transformer data.
- `TrnID` (*str or int, optional*): The unique ID of the transformer.
- `TrnName` (*str, optional*): The name of the transformer.
- `TrnFromBus` (*int or str, optional*): The "from" bus number or name.
- `TrnToBus` (*int or str, optional*): The "to" bus number or name.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- `int`: Status of the operation (`0` for success).

### **Example Usage**

```python
status = TrnTrip(
    t=10.0,
    BSPSSEPyTrn=Sim.BSPSSEPyTrn,
    TrnName="Transformer1",
    DebugPrint=True
)
```

---

## **4. TrnClose**

**Description:**
Closes a transformer (sets its status to "Closed") and updates the `BSPSSEPyTrn` DataFrame.

### **Features**

- Ensures proper synchronization with the simulation state.
- Supports querying by transformer name, ID, or bus connections.

### **Arguments**

- `t` (*float*): Current simulation time.
- `BSPSSEPyTrn` (*pd.DataFrame*): The DataFrame containing custom transformer data.
- `TrnID` (*str or int, optional*): The unique ID of the transformer.
- `TrnName` (*str, optional*): The name of the transformer.
- `TrnFromBus` (*int or str, optional*): The "from" bus number or name.
- `TrnToBus` (*int or str, optional*): The "to" bus number or name.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- `int`: Status of the operation (`0` for success).

### **Example Usage**

```python
status = TrnClose(
    t=15.0,
    BSPSSEPyTrn=Sim.BSPSSEPyTrn,
    TrnFromBus=101,
    TrnToBus=102,
    DebugPrint=True
)
```

---

## **DataFrame Structure: **`BSPSSEPyTrn`**

The `BSPSSEPyTrn` DataFrame stores simulation-specific transformer data. The following columns are maintained:

| Column Name               | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| `ID`                      | Transformer ID.                                      |
| `XFRNAME`                 | Name of the transformer.                            |
| `FROMNUMBER`              | "From" bus number.                                  |
| `FROMNAME`                | "From" bus name.                                    |
| `TONUMBER`                | "To" bus number.                                    |
| `TONAME`                  | "To" bus name.                                      |
| `BSPSSEPyStatus`          | Current status of the transformer (`Closed`/`Tripped`). |
| `BSPSSEPyStatus_0`        | Initial status at simulation start (`Closed`/`Tripped`). |
| `BSPSSEPyLastAction`      | Last action performed (`Close`/`Trip`).             |
| `BSPSSEPyLastActionTime`  | Timestamp of the last action.                       |
| `BSPSSEPySimulationNotes` | Notes about the transformer state or actions.       |

---

## **Best Practices and Recommendations**

- Use `GetTrnInfo` for most queries to dynamically retrieve transformer information.
- Update the `BSPSSEPyTrn` DataFrame with every action (`TrnTrip`, `TrnClose`) to maintain consistency (*Done Automatically*).
- Validate keys using `TrnInfoDic` for accurate data retrieval from PSSE.

For additional details or to report issues, contact the developer at `ilyas.farhat@outlook.com`.

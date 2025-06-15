# BSPSSEPy Branch Functions Manual

This manual provides a comprehensive guide to the branch-related functions available in the `BSPSSEPyBrnFunctions` module. These functions allow for dynamic retrieval, control, and status updates of branches in the BSPSSEPy simulation framework, utilizing both PSSE and custom `BSPSSEPyBranch` data.

---

## Overview of Functions

The module includes the following key functions:

1. **GetBrnInfo**: Retrieve branch data dynamically from PSSE and the `BSPSSEPyBranch` DataFrame.
2. **GetBrnInfoPSSE**: Directly fetch branch data from PSSE.
3. **BrnTrip**: Trip a branch and update its status in the `BSPSSEPyBranch` DataFrame.
4. **BrnClose**: Close a branch and update its status in the `BSPSSEPyBranch` DataFrame.

---

## **1. GetBrnInfo**

**Description:**
Fetches information about branches based on specified keys. This function supports querying by branch name, ID, or bus connections, and integrates data from both PSSE and the custom `BSPSSEPyBranch` DataFrame.

### **Features**

- Handles multiple cases:
  - **Case 1:** Single key for a specific branch -> Returns a single value.
  - **Case 2:** Multiple keys for a specific branch -> Returns a dataframe with columns corresponding to keys with one row data corresponding to the branch.
  - **Case 3:** Single key for all branches -> Returns a dataframe with 1 column corresponding  or 3 columns: 
  - **Case 4:** Multiple keys for all branches -> Returns a dictionary with keys and corresponding lists for all branches.

### **Arguments**

- `BranchKeys` (*str* or *list of str*): The key(s) for the required information. Valid keys include:
  - **PSSE keys:** Defined in `BranchInfoDic`.
  - **BSPSSEPyBranch keys:** Columns in the `BSPSSEPyBranch` DataFrame.
- `BranchName` (*str, optional*): The name of the branch.
- `FromBus` (*int or str, optional*): The "from" bus number or name.
- `ToBus` (*int or str, optional*): The "to" bus number or name.
- `BSPSSEPyBranch` (*pd.DataFrame, optional*): The DataFrame containing custom branch data.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- **Case 1:** Single value (e.g., *str*, *int*, *float*).
- **Case 2:** List of values.
- **Case 3:** List of values.
- **Case 4:** Dictionary of lists.

### **Example Usage**

```python
result = GetBranchInfo(
    BranchKeys=["STATUS", "AMPS"],
    BranchName="Branch1",
    BSPSSEPyBranch=Sim.BSPSSEPyBranch,
    DebugPrint=True
)
```

---

## **2. GetBranchInfoPSSE**

**Description:**
Fetches specific information about branches directly from the PSSE library.

### **Features**

- Flexible querying options:
  - Single entry per branch.
  - Bi-directional entries for each branch.

### **Arguments**

- `abrnString` (*str*): Requested information string (e.g., "AMPS", "STATUS").
- `BranchEntry` (*int*): Specifies data retrieval direction:
  - `1`: Single entry per branch.
  - `2`: Bi-directional entries for each branch.
- `BranchName` (*str, optional*): The name of the branch.
- `FromBus` (*int or str, optional*): The "from" bus number or name.
- `ToBus` (*int or str, optional*): The "to" bus number or name.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- List of requested information for the branch(es).

### **Example Usage**

```python
amps_data = GetBranchInfoPSSE("AMPS", BranchName="Branch1", DebugPrint=True)
```

---

## **3. BranchTrip**

**Description:**
Trips a branch (sets its status to "Tripped") and updates the `BSPSSEPyBranch` DataFrame.

### **Features**

- Updates simulation-specific metadata, such as action time and status.
- Supports querying by branch name, ID, or bus connections.

### **Arguments**

- `t` (*float*): Current simulation time.
- `BSPSSEPyBranch` (*pd.DataFrame*): The DataFrame containing custom branch data.
- `BranchID` (*str or int, optional*): The unique ID of the branch.
- `BranchName` (*str, optional*): The name of the branch.
- `BranchFromBus` (*int or str, optional*): The "from" bus number or name.
- `BranchToBus` (*int or str, optional*): The "to" bus number or name.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- `int`: Status of the operation (`0` for success).

### **Example Usage**

```python
status = BranchTrip(
    t=10.0,
    BSPSSEPyBranch=Sim.BSPSSEPyBranch,
    BranchName="Branch1",
    DebugPrint=True
)
```

---

## **4. BranchClose**

**Description:**
Closes a branch (sets its status to "Closed") and updates the `BSPSSEPyBranch` DataFrame.

### **Features**

- Ensures proper synchronization with the simulation state.
- Supports querying by branch name, ID, or bus connections.

### **Arguments**

- `t` (*float*): Current simulation time.
- `BSPSSEPyBranch` (*pd.DataFrame*): The DataFrame containing custom branch data.
- `BranchID` (*str or int, optional*): The unique ID of the branch.
- `BranchName` (*str, optional*): The name of the branch.
- `BranchFromBus` (*int or str, optional*): The "from" bus number or name.
- `BranchToBus` (*int or str, optional*): The "to" bus number or name.
- `DebugPrint` (*bool, optional*): Enables detailed debug output.

### **Returns**

- `int`: Status of the operation (`0` for success).

### **Example Usage**

```python
status = BranchClose(
    t=15.0,
    BSPSSEPyBranch=Sim.BSPSSEPyBranch,
    BranchFromBus=101,
    BranchToBus=102,
    DebugPrint=True
)
```

---

## \*\*DataFrame Structure: \*\***`BSPSSEPyBranch`**

The `BSPSSEPyBranch` DataFrame stores simulation-specific branch data. The following columns are maintained:

| Column Name               | Description                                        |
| ------------------------- | -------------------------------------------------- |
| `ID`                      | Branch ID.                                         |
| `BRANCHNAME`              | Name of the branch.                                |
| `FROMNUMBER`              | "From" bus number.                                 |
| `FROMNAME`                | "From" bus name.                                   |
| `TONUMBER`                | "To" bus number.                                   |
| `TONAME`                  | "To" bus name.                                     |
| `BSPSSEPyStatus`          | Current status of the branch (`Closed`/`Tripped`). |
| `BSPSSEPyLastAction`      | Last action performed (`Close`/`Trip`).            |
| `BSPSSEPyLastActionTime`  | Timestamp of the last action.                      |
| `BSPSSEPySimulationNotes` | Notes about the branch state or actions.           |

---

## **Best Practices and Recommendations**

- Use `GetBranchInfo` for most queries to dynamically retrieve branch information.
- Update the `BSPSSEPyBranch` DataFrame with every action (`BranchTrip`, `BranchClose`) to maintain consistency (*Done Automatically*).
- Validate keys using `BranchInfoDic` for accurate data retrieval from PSSE.

For additional details or to report issues, contact the developer at `ilyas.farhat@outlook.com`.


import pandas as pd
from Functions.BSPSSEPy.BSPSSEPyDictionary import *


# Function to map the row entries to the correct canonical forms (case insensitive)
def BSPSSEPyControlSequenceTable(CSVFile):
    """
    This function will read the Control Plan CSV file, convert it to the right format for the code to operate,
    and return it as a fixed DataFrame.
    """
    # Read the CSV file into a DataFrame
    BSPSSEPySequence = pd.read_csv(CSVFile, dtype=str)
    
    # Iterate through each row and map the entries using the predefined mappings
    for index, row in BSPSSEPySequence.iterrows():
        # Device Type (map to standard name, case insensitive)
        deviceType = str(row["Device Type"]).strip().lower()  # Convert to lowercase
        row["Device Type"] = DeviceTypeMapping.get(deviceType, row["Device Type"])  # Default to original if not found

        # Identification Type (map to standard name, case insensitive)
        identificationType = str(row["Identification Type"]).strip().lower()
        row["Identification Type"] = IdentificationTypeMapping.get(identificationType, row["Identification Type"])

        # Action Type (map to standard action, case insensitive)
        actionType = str(row["Action Type"]).strip().lower()
        row["Action Type"] = ActionTypeMapping.get(actionType, row["Action Type"])

        # Update the row in the DataFrame
        BSPSSEPySequence.loc[index] = row
    
    # Enforce data types for each column
    BSPSSEPySequence = BSPSSEPySequence.astype({
        "Device Type": "string",
        "Identification Type": "string",
        "Identification Value": "string",
        "Action Type": "string",
        "Action Time": "float"  # Use "int" if the values are always integers
    })
    # Return the fixed DataFrame
    return BSPSSEPySequence

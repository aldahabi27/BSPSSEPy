import pandas as pd
from fun.bspssepy.bspssepy_dict import *


# Function to map the row entries to the correct canonical forms (case insensitive)
def BSPSSEPyControlSequenceTable(CSVFile):
    """
    This function will read the Control Plan CSV file, convert it to the right format for the code to operate,
    and return it as a fixed DataFrame.
    """
    # Read the CSV file into a DataFrame
    bspssepy_sequence = pd.read_csv(CSVFile, dtype=str)
    
    # Iterate through each row and map the entries using the predefined mappings
    for index, row in bspssepy_sequence.iterrows():
        # Device Type (map to standard name, case insensitive)
        deviceType = str(row["Device Type"]).strip().lower()  # Convert to lowercase
        row["Device Type"] = device_type_mapping.get(deviceType, row["Device Type"])  # Default to original if not found

        # Identification Type (map to standard name, case insensitive)
        identificationType = str(row["Identification Type"]).strip().lower()
        row["Identification Type"] = identification_type_mapping.get(identificationType, row["Identification Type"])

        # Action Type (map to standard action, case insensitive)
        actionType = str(row["Action Type"]).strip().lower()
        row["Action Type"] = action_type_mapping.get(actionType, row["Action Type"])

        # Update the row in the DataFrame
        bspssepy_sequence.loc[index] = row
    
    # Enforce data types for each column
    bspssepy_sequence = bspssepy_sequence.astype({
        "Device Type": "string",
        "Identification Type": "string",
        "Identification Value": "string",
        "Action Type": "string",
        "Action Time": "float"  # Use "int" if the values are always integers
    })
    # Return the fixed DataFrame
    return bspssepy_sequence

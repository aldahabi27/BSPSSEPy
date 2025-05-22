# ===========================================================
#   BSPSSEPy Application - CSV Control Plan Configuration
# ===========================================================
#   This module loads and processes the Control Plan CSV file
#   to define the sequence of power system operations.
#
#   Last Updated: BSPSSEPy Ver 0.3 (4 Feb 2025)
#   Copyright (c) 2024-2025, Ilyas Farhat
#   Contact: ilyas.farhat@outlook.com
# ===========================================================

import pandas as pd
from Functions.BSPSSEPy.BSPSSEPyDictionary import *
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import bsprint
import asyncio
import ast  # Used to safely parse dictionary strings

async def BSPSSEPyControlSequenceTable(CSVFile, DebugPrint=False, app=None):
    """
    Load and process the BSPSSEPy Control Plan CSV file, enforcing `Values` as a dictionary.

    Parameters:
        CSVFile (Path): The path to the Control Plan CSV file.
        DebugPrint (bool): Enables debug messages.
    
    Returns:
        pd.DataFrame: A structured DataFrame containing the processed control plan.
    """

    # Check if CSV file exists
    if not CSVFile.exists():
        bsprint("[ERROR] Control Plan CSV file missing. Generating a template file.", app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

        # Define the required columns
        columns = [
            "UID",                      # Unique ID for the action - best thing to set this as row index
            "Device Type",              
            "Identification Type",
            "Identification Value",
            "Action Type",
            "Action Time",
            "Action Status",
            "Values"
        ]

        # Create an empty DataFrame and save as CSV template
        pd.DataFrame(columns=columns).to_csv(CSVFile, index=False)
        
        if DebugPrint:
            bsprint(f"[DEBUG] No control plan found. A template file has been generated at '{CSVFile}'.", app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)
        raise SystemExit(f"CSV file created: {CSVFile.name}. Please configure the control plan and restart.")

    # Load CSV
    if DebugPrint:
        bsprint(f"[DEBUG] Loading Control Plan CSV file: {CSVFile}", app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Read CSV with dtype as string (for consistency)
    # BSPSSEPySequence = pd.read_csv(CSVFile, dtype=str)
    BSPSSEPySequence = pd.read_csv(
        CSVFile, 
        dtype=str, 
        keep_default_na=False,  # Prevent automatic NaN conversion
        na_values=[""]          # Ensure empty cells are treated as empty strings
    )
    
    # Ensure all required columns exist
    required_columns = {"Device Type", "Identification Type", "Identification Value",
                        "Action Type", "Action Time", "Action Status", "Values"}

    missing_columns = required_columns - set(BSPSSEPySequence.columns)
    
    # if missing_columns:
    #     raise ValueError(f"[ERROR] Missing columns in CSV: {missing_columns}")

    if DebugPrint:
        bsprint(f"[DEBUG] CSV file '{CSVFile.name}' loaded successfully. Processing entries...", app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Check if the Values column exists before processing
    if "Values" not in BSPSSEPySequence.columns:
        bsprint("[INFO] No 'Values' column found in Control Plan CSV file.", app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)
    else:
        # Check if any UPDATE action is missing Values
        for index, row in BSPSSEPySequence.iterrows():
            if row["Action Type"].strip().lower() in [key for key,value in ActionTypeMapping.items() if value == "UPDATE"] and (pd.isna(row["Values"]) or str(row["Values"]).strip() == ""):
                bsprint(f"[WARNING] Action at row {index} is 'UPDATE' but has no 'Values' specified in Control Plan CSV file.", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
    
    if "Tied Action" not in set(BSPSSEPySequence.columns):
        BSPSSEPySequence["Tied Action"] = [-1]*len(BSPSSEPySequence)
        
    if "UID" not in set(BSPSSEPySequence.columns):
        BSPSSEPySequence["UID"] = range(1, len(BSPSSEPySequence) + 1)
    
    # Process each row to standardize mappings and force `Values` to be a dictionary
    for index, row in BSPSSEPySequence.iterrows():
        # Standardize column values (case insensitive mapping)
        row["Device Type"] = DeviceTypeMapping.get(row["Device Type"].strip().lower(), row["Device Type"])
        
        row["Identification Type"] = IdentificationTypeMapping.get(row["Identification Type"].strip().lower(), row["Identification Type"])
        
        row["Action Type"] = ActionTypeMapping.get(row["Action Type"].strip().lower(), row["Action Type"])

        # Standardize 'Device Type'
        deviceType = str(row["Device Type"]).strip().lower()  # Convert to lowercase
        row["Device Type"] = DeviceTypeMapping.get(deviceType, row["Device Type"])  # Default to original if not found

        # Identification Type (map to standard name, case insensitive)
        identificationType = str(row["Identification Type"]).strip().lower()
        row["Identification Type"] = IdentificationTypeMapping.get(identificationType, row["Identification Type"])

        # Action Type (map to standard action, case insensitive)
        actionType = str(row["Action Type"]).strip().lower()
        row["Action Type"] = ActionTypeMapping.get(actionType, row["Action Type"])

        # Update the DataFrame row
        BSPSSEPySequence.loc[index] = row


        # Ensure `Values` column is always a dictionary
        if "Values" in BSPSSEPySequence.columns:
            ValuesData = str(row["Values"]).strip()
            if ValuesData:
                try:
                    row["Values"] = ast.literal_eval(ValuesData)  # Convert to dictionary
                    if not isinstance(row["Values"], dict):
                        raise ValueError(f"Invalid format: Values must be a dictionary. Found: {type(row['Values'])}")
                    
                    ValuesDic: dict = row["Values"]
                    if "Tied Action" in ValuesDic.keys():
                        TiedActionUID = ValuesDic["Tied Action"]
                        row["Tied Action"] = int(TiedActionUID)
                        row["Action Time"] = BSPSSEPySequence.loc[BSPSSEPySequence['UID'].astype(int) == TiedActionUID, 'Action Time'].values[0]
                        
                        
                    
                except Exception as e:
                    bsprint(f"[ERROR] Failed to parse 'Values' column at row {index}: {ValuesData} - {e}", app=app)
                    await asyncio.sleep(app.bsprintasynciotime if app else 0)
                    row["Values"] = {}  # Default to an empty dictionary if parsing fails

        # Update the DataFrame row
        BSPSSEPySequence.loc[index] = row

    
    # Enforce correct data types
    BSPSSEPySequence = BSPSSEPySequence.astype({
        "UID": "int",
        "Tied Action": "int",
        "Device Type": "string",
        "Identification Type": "string",
        "Identification Value": "string",
        "Action Type": "string",
        "Action Time": "float",
        "Action Status": "int"
    })
    
 
    if DebugPrint:
        bsprint(f"[DEBUG] Processed BSPSSEPySequence:\n{BSPSSEPySequence}", app=app)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Return the processed DataFrame
    return BSPSSEPySequence

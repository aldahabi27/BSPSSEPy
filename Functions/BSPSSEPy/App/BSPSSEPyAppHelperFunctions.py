import os
from pathlib import Path
from rich.text import Text
from textual.app import App
from textual import events
from textual.widgets import Tree, DataTable
import pandas as pd
import asyncio  # Used for async operations
import time
import psse3601
import psspy
# from textual.widgets

async def GetBSPSSEPyAppDFs(
        app: App,   # the app handle
        Initialize: bool | None = False,  # If Initialize is true, this will return the DFs as if the simulation is just starting (not sure if needed, but will see)
):
    """
    This function will return all dataframes needed for the GUI Tables. Then, the returned DFs can be compared with the "displayed" tables and update the changes only to have faster GUI updates.

    Parameters:
        app (App): The app handle to BSPSSEPyApp
        Initialize (bool, default = False): To indicate if the generated DFs are at the beginning of the simulation (reset all stuff to zero/default values - i.e. Actions status --> did not start yet)
    """

    if app is None:
        return
    
    RoundDigit = 3
    

    DebugPrint = app.DebugCheckBox.value

    # Debugging information
    if DebugPrint:
        bsprint(f"[DEBUG] Running GetBSPSSEPyAppDFs with Initialize = {Initialize}", app=app)



    
    if DebugPrint:
        bsprint("Generating shortcuts to simulation dataframes", app=app)

    # Check if the simulation has started (i.e., if `app.myBSPSSEPy` exists)
    SameSAVFile = False
    if hasattr(app, "myBSPSSEPy") and app.myBSPSSEPy is not None:
        if str(app.myBSPSSEPy.Config.SAVFile).lower().strip() == app.SAVFilePath.lower().strip():
            SameSAVFile = True




    # If the simulation has not started, use empty DataFrames
    if not SameSAVFile:
        bsprint("[INFO] New SAV File selected. Attempting to run a quick analysis to update the Tables - please wait..", app=app)
        
        from Functions.BSPSSEPy.App.BSPSSEPyAppRun import RunSimulation
        await RunSimulation(app=app, DummyRun = True)
        await asyncio.sleep(app.bsprintasynciotime if app else 0)

        
        # await asyncio.sleep(0)

        




    # Create a shortcut reference
    BSPSSEPySequence = app.myBSPSSEPy.Sim.Config.BSPSSEPySequence
    BSPSSEPyBrn = app.myBSPSSEPy.Sim.BSPSSEPyBrn
    BSPSSEPyBus = app.myBSPSSEPy.Sim.BSPSSEPyBus
    BSPSSEPyLoad = app.myBSPSSEPy.Sim.BSPSSEPyLoad
    BSPSSEPyTrn = app.myBSPSSEPy.Sim.BSPSSEPyTrn
    BSPSSEPyGen = app.myBSPSSEPy.Sim.BSPSSEPyGen
    BSPSSEPyAGC = app.myBSPSSEPy.Sim.BSPSSEPyAGCDF

    if DebugPrint:
        bsprint("Shortcut to simulation dataframes acquired", app=app)

    # Define a function to map Action Status to emojis
    def MapStatusToEmoji(status):
        if status == 0:
            return " 🔴 "  # Not started
        elif status == 1:
            return " ⏳ "  # Running/Loading (sand watch)
        elif status == 2:
            return " ✅ "  # Completed (green check)
        elif status == -999:
            return "⚠︎ "  # Skipped
        else:
            return " ☠️ "  # Unexpected status (error)
        
    def ActionTimeMinSec(ActionTime, InSeconds = False):
        """
        Converts an action time in minutes to a formatted string with both minutes and seconds.
        
        If the seconds value is a whole number, it is displayed as an integer without decimals.
        
        Parameters:
            ActionTime (float | int): The action time in minutes.

        Returns:
            str: Formatted string in the format "X min (Ys)".
        """
        if InSeconds:
            ActionTime = ActionTime / 60 # Convert to Minuts first
        
        TotalSeconds = ActionTime * 60  # Convert to seconds

        # ✅ If seconds are whole (integer), display as int
        SecondsFormatted = int(TotalSeconds) if TotalSeconds.is_integer() else round(TotalSeconds, 1)

        return f"{round(ActionTime, RoundDigit)} min ({SecondsFormatted}s)"


    

    # Define the ProgressDF DataFrame with mapped columns
    ProgressDF = pd.DataFrame({
        "Progress": BSPSSEPySequence["Action Status"].apply(MapStatusToEmoji),  # Initially all actions are not started
        "Control Sequence": BSPSSEPySequence["Control Sequence"],  # All set to zero for now
        "Device Type": BSPSSEPySequence["Device Type"],  # Mapped from BSPSSEPySequence
        "ID Type": BSPSSEPySequence["Identification Type"],  # Mapped from BSPSSEPySequence
        "ID Value": BSPSSEPySequence["Identification Value"],  # Mapped from BSPSSEPySequence
        "Action Type": BSPSSEPySequence["Action Type"],  # Mapped from BSPSSEPySequence
        "Action Time": BSPSSEPySequence["Action Time"].apply(ActionTimeMinSec),  # Mapped from BSPSSEPySequence
        "Start Time": BSPSSEPySequence["Start Time"].apply(lambda x: ActionTimeMinSec(x, InSeconds=True)),
        "End Time": BSPSSEPySequence["End Time"].apply(lambda x: ActionTimeMinSec(x, InSeconds=True)),
        "Action Status": BSPSSEPySequence["Action Status"],  # Mapped from BSPSSEPySequence
    })



    AGCDF = BSPSSEPyAGC
    AGCDF["ΔPᴳ"] = AGCDF["ΔPᴳ"].apply(lambda x: round(x, RoundDigit))
    AGCDF["Δf (Hz)"] = AGCDF["Δf (Hz)"].apply(lambda x: round(x, RoundDigit))
    AGCDF["Δf' (Hz/s)"] = AGCDF["Δf' (Hz/s)"].apply(lambda x: round(x, RoundDigit))


    # Fetch all required channel values asynchronously
    PELECValues, PMECHValues, QELECValues, GREFValues, VREFValues = await FetchGeneratorChannelValues(BSPSSEPyGen, DebugPrint, app)

    # Fetch the MVA base for each generator
    MVA_Base_List = []
    for idx, GeneratorRow in BSPSSEPyGen.iterrows():
        GeneratorID = GeneratorRow["ID"]
        BusNumber = GeneratorRow["NUMBER"]

        # Get the base MVA value
        ierr, GeneratorMVA_Base = psspy.macdat(BusNumber, GeneratorID, 'MBASE')

        if ierr == 0:
            if DebugPrint:
                bsprint(f"[DEBUG] Retrieved MVA Base for Generator at Bus {BusNumber}, ID {GeneratorID}: {GeneratorMVA_Base} MVA", app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
        else:
            bsprint(f"[ERROR] Could not retrieve MVA Base for Generator at Bus {BusNumber}, ID {GeneratorID}. Error code: {ierr}", app=app)
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

        MVA_Base_List.append(GeneratorMVA_Base)

    # System_MVA_BASE = psspy.get_sbase()
    # Convert PU to MW/MVar for each generator
    PELEC_MW = [round(pe * mb, RoundDigit) for pe, mb in zip(PELECValues, [100]*len(PELECValues))]
    PELEC_PU = [round(pe, RoundDigit) for pe in PELECValues]

    PMECH_MW = [round(pm * mb, RoundDigit) for pm, mb in zip(PMECHValues, MVA_Base_List)]
    PMECH_PU = [round(pm, RoundDigit) for pm in PMECHValues]

    QELEC_MVar = [round(qe * mb, RoundDigit) for qe, mb in zip(QELECValues, [100]*len(PELECValues))]
    QELEC_PU = [round(qe, RoundDigit) for qe in QELECValues]

    # Handle GREF scaling (assuming it follows the same rule as power)
    GREF_MW = [round(gr * mb, RoundDigit) for gr, mb in zip(GREFValues, MVA_Base_List)]
    GREF_PU = [round(gr, RoundDigit) for gr in GREFValues]

    # Voltage remains in PU
    VREF_PU = [round(vr, RoundDigit) for vr in VREFValues]

    # Create the DataFrame with formatted values
    GenDF = pd.DataFrame({
        "Gen Name": BSPSSEPyGen["MCNAME"],
        "Bus #" : BSPSSEPyGen["NUMBER"],
        "Bus Name": BSPSSEPyGen["NAME"],
        "Δf": BSPSSEPyAGC["Δf (Hz)"],  # Assuming already in correct format
        "Pᴱ MW (p.u.)": [f"{mw} MW ({pu} p.u.)" for mw, pu in zip(PELEC_MW, PELEC_PU)],
        "Pᴹ MW (p.u.)": [f"{mw} MW ({pu} p.u.)" for mw, pu in zip(PMECH_MW, PMECH_PU)],
        "Qᴱ MVar (p.u.)": [f"{mvar} MVar ({pu} p.u.)" for mvar, pu in zip(QELEC_MVar, QELEC_PU)],
        "Gᴿᴱꟳ MW (p.u.)": [f"{mw} MW ({pu} p.u.)" for mw, pu in zip(GREF_MW, GREF_PU)],
        "Vᴿᴱꟳ (p.u.)": VREF_PU,  # Voltage remains in PU
    })



    
    from Functions.BSPSSEPy.Sim.BSPSSEPyLoadFunctions import GetLoadInfo
    LoadDFtemp = await GetLoadInfo(["LOADNAME", "NUMBER", "NAME", "MVAACT", "ILACT", "YLACT", "LDGNACT", "STATUS"], DebugPrint=DebugPrint, app=app)
    # bsprint(LoadDFtemp, app=app)
    # Create the DataFrame
    RoundDigit = 3
    LoadDF = pd.DataFrame({
        "Load Name": LoadDFtemp["LOADNAME"],
        "Bus #": LoadDFtemp["NUMBER"],
        "Bus Name": LoadDFtemp["NAME"],
        "Power Array [PL, QL, IP, IQ, YP, YQ, PG, QG]": LoadDFtemp.apply(lambda row: [
            round(row["MVAACT"].real, RoundDigit), round(row["MVAACT"].imag, RoundDigit),
            round(row["ILACT"].real, RoundDigit), round(row["ILACT"].imag, RoundDigit),
            round(row["YLACT"].real, RoundDigit), round(row["YLACT"].imag, RoundDigit),
            round(row["LDGNACT"].real, RoundDigit), round(row["LDGNACT"].imag, RoundDigit)
        ], axis=1),
        "Status": LoadDFtemp["STATUS"]
    })



    
    from Functions.BSPSSEPy.Sim.BSPSSEPyBusFunctions import GetBusInfo
    BusDFtemp = await GetBusInfo(["NUMBER", "NAME", "TYPE"], DebugPrint=DebugPrint, app=app)
    BusStatus = await GetBusInfo(["BSPSSEPyStatus"], BSPSSEPyBus=BSPSSEPyBus, DebugPrint=DebugPrint, app=app)

    BusDF = pd.DataFrame({
        "Bus #": BusDFtemp["NUMBER"],
        "Bus Name": BusDFtemp["NAME"],
        "Type": BusDFtemp["TYPE"],
        "Status": BusStatus,
    })
    
    BrnDF = pd.DataFrame({
        "Branch Name": BSPSSEPyBrn["BRANCHNAME"],
        "From Bus #": BSPSSEPyBrn["FROMNUMBER"],
        "To Bus #": BSPSSEPyBrn["TONUMBER"],
        "From Bus Name": BSPSSEPyBrn["FROMNAME"],
        "To Bus Name": BSPSSEPyBrn["TONAME"],
        "Status": BSPSSEPyBrn["STATUS"],  
    })


    TrnDF = pd.DataFrame({
        "Trans. Name": BSPSSEPyTrn["XFRNAME"],
        "From Bus #": BSPSSEPyTrn["FROMNUMBER"],
        "To Bus #": BSPSSEPyTrn["TONUMBER"],
        "From Bus Name": BSPSSEPyTrn["FROMNAME"],
        "To Bus Name": BSPSSEPyTrn["TONAME"],
        "Status": BSPSSEPyTrn["STATUS"],
    })

    
    DataFrames = {
        "Progress": ProgressDF,
        "AGC": AGCDF,
        "Generator": GenDF,
        "Load": LoadDF,
        "Bus": BusDF,
        "Branch": BrnDF,
        "Transformer": TrnDF,
    }

    return DataFrames
    

async def UpdateBSPSSEPyAppGUI(app: App, ResetTables: bool | None = False):
    
    if ResetTables:
        app.ProgressTable.clear(columns=True)
        app.AGCTable.clear(columns=True)
        app.GeneratorTable.clear(columns=True)
        app.LoadTable.clear(columns=True)
        app.BusTable.clear(columns=True)
        app.BranchTable.clear(columns=True)
        app.TransformerTable.clear(columns=True)

        app.ProgressTable.loading = True
        app.AGCTable.loading = True
        app.GeneratorTable.loading = True
        app.LoadTable.loading = True
        app.BusTable.loading = True
        app.BranchTable.loading = True
        app.TransformerTable.loading = True
        await asyncio.sleep(0)


    

    DataFrames = await GetBSPSSEPyAppDFs(app=app)

    # Apply only the changed values instead of resetting everything
    UpdateGUITables(app, DataFrames)
    # app.refresh()
    # await asyncio.sleep(0)

    # bsprint("[INFO] GUI Tables updated with new simulation data.", app=app)


    # # Loop through all tables and reset them dynamically
    # for TableName, TableInfo in Tables.items():
    #     bsprint(f"[INFO] Resetting {TableName} table...", app=app)

    #     BSPSSEPyAppResetTable(
    #         BSPSSEPyDataFrame=DataFrames[TableName],
    #         TableCol=TableInfo["columns"],
    #         app=app,
    #         appTable=TableInfo["AppTable"],
    #         UseConfigOnly=False
    #     )
        # await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Final Debugging Information
    # bsprint("[INFO] All tables have been reset successfully.", app=app)
    # await asyncio.sleep(app.bsprintasynciotime if app else 0)


    if app.DebugCheckBox.value:
        bsprint("[DEBUG] BSPSSEPyApp tables initialized.", app=app)
        # await asyncio.sleep(app.bsprintasynciotime if app else 0)    
    app.ProgressTable.loading = False
    app.AGCTable.loading = False
    app.GeneratorTable.loading = False
    app.LoadTable.loading = False
    app.BusTable.loading = False
    app.BranchTable.loading = False
    app.TransformerTable.loading = False
    await asyncio.sleep(0)


    app.RunButton.disabled = False






# def bsprint(Message, app=None, type = None):
#     """
#     Prints messages to the DetailsTextArea in the app if available.
#     Falls back to printing in the terminal if no app is provided.

#     This function automatically handles async execution using `call_later`
#     when inside the GUI, so you don't have to use `await` explicitly.

#     Parameters:
#         Message (str): The message to print.
#         app (BSPSSEPyApp, optional): The Textual app instance (default is None).
#         # type (optional): ["d","debug"] --> will check if app.DebugCheckBox.value is true, then will be displayed, otherwise skip
#     """
#     if app:
#         # DebugPrint = app.DebugCheckBox.value
        
#         # if check if Message is a string
#         app.call_later(AppendToDetailsTextArea, app.DetailsTextArea, Message)
#     else:
#         print(Message)  # ✅ Fallback to terminal output when no GUI is available

# def BSPSSEPyAppResetTables(
#         # TableName: str | None = None,
#         app: App | None = None,
#         UseConfigOnly: bool | None = False,
# ) -> None:
#     """ This function will initialize BSPSSEPyApp Tables. This function is called when all info needed is "collected"/"built" (after SimInit is run).
    
#     Future plan: 
#         Add a functionality to update the tables (or some of them) when SAV file is selected before the Run starts.
#     """

#     app.ProgressTableCol = ["Progrss", "Control Sequence", "Device Type", "ID Type", "ID Value", "Action Type", "Action Time", "Action Status"]
#     app.AGCTableCol = ["Gen Name", "Alpha", "ΔPᴳ"]
#     app.GeneratorTableCol = ["Gen Name", "Bus #", "Bus Name", "Δf", "Pᴱ", "Pᴹ", "Qᴱ", "Gᴿᴱꟳ", "Vᴿᴱꟳ"]
#     app.LoadTableCol = ["Load Name", "Bus #", "Bus Name", "Power Array", "Status"]
#     app.BusTableCol = ["Bus #", "Bus Name", "Status"]
#     app.BranchTableCol = ["Branch Name", "Bus #", "Bus Name", "Status"]
#     app.TransformerTableCol = ["Trans. Name", "Bus #", "Bus Name", "Status"]


def GetDataFramesFromGUITables(app: App) -> dict:
    """
    Extracts current data from the GUI tables and returns them as pandas DataFrames.

    Parameters:
        app (App): The Textual app instance.

    Returns:
        dict: A dictionary where keys are table names and values are pandas DataFrames.
    """
    DebugPrint = app.DebugCheckBox.value

    Tables = {
        "Progress": app.ProgressTable,
        "AGC": app.AGCTable,
        "Generator": app.GeneratorTable,
        "Load": app.LoadTable,
        "Bus": app.BusTable,
        "Branch": app.BranchTable,
        "Transformer": app.TransformerTable,
    }

    GUIDataFrames = {}

    for TableName, Table in Tables.items():
        if Table:
            ColumnNames = [col.label.plain for col in Table.columns.values()]

            # ✅ Extract row data using `get_row(row_key)`
            RowData = []
            for row_key in Table.rows.keys():  # Iterate over row keys
                row_cells = Table.get_row(row_key)  # Fetch the row's cell data
                RowData.append([cell for cell in row_cells])  # Extract text
            
            # ✅ Handle case where table is empty
            if (not ColumnNames or not RowData) and DebugPrint:
                bsprint(f"[DEBUG] Table '{TableName}' is empty.", app=app)
            
            GUIDataFrames[TableName] = pd.DataFrame(RowData, columns=ColumnNames) 
    return GUIDataFrames


def CompareDataFrames(df1: pd.DataFrame, df2: pd.DataFrame) -> dict:
    """
    Compares two DataFrames and returns a dictionary of changes.

    Parameters:
        df1 (pd.DataFrame): The first DataFrame (old/current GUI data).
        df2 (pd.DataFrame): The second DataFrame (new data from simulation).

    Returns:
        dict: 
            - "changes": List of tuples (row_index, column_name, old_value, new_value) for modified cells.
            - "reset_required": Boolean indicating if table dimensions or column names don't match.
    """
    changes = []

    # ✅ Check if dimensions OR column names are different
    reset_required = (df1.shape != df2.shape) or (list(df1.columns) != list(df2.columns))

    if reset_required:
        return {"changes": [], "reset_required": True}

    # ✅ Compare only if column names and shape match
    for row in range(len(df1)):
        for col in df1.columns:
            if str(df1.at[row, col]) != str(df2.at[row, col]):  # Convert to string for comparison
                changes.append((row, col, df1.at[row, col], df2.at[row, col]))

    return {"changes": changes, "reset_required": False}




def UpdateGUITables(app: App, DataFrames: dict):
    """
    Updates GUI tables by comparing current GUI data with new DataFrames and applying only changes.
    If a table is initially empty, has different dimensions, or different columns, it gets fully reset.

    Parameters:
        app (App): The Textual app instance.
        DataFrames (dict): The new DataFrames from GetBSPSSEPyAppDFs.
    """
    
    DebugPrint = app.DebugCheckBox.value

    CurrentGUIData = GetDataFramesFromGUITables(app)

    Tables = {
        "Progress": app.ProgressTable,
        "AGC": app.AGCTable,
        "Generator": app.GeneratorTable,
        "Load": app.LoadTable,
        "Bus": app.BusTable,
        "Branch": app.BranchTable,
        "Transformer": app.TransformerTable,
    }

    for TableName, NewDF in DataFrames.items():
        if TableName in CurrentGUIData:
                
            CurrentDF = CurrentGUIData[TableName]
            ComparisonResult = CompareDataFrames(CurrentDF, NewDF)

            Table: DataTable = Tables[TableName]
            
            # Get row and column mappings from keys
            RowKeys = list(Table.rows.keys())  # Extract row keys
            ColKeys = {col.label.plain: col.key for col in Table.columns.values()}  # Map column names to keys

            
            # if TableName == "Transformer":
            #     bsprint("Transformer Table Update Details:\n"
            #             f"CurrentDF: {CurrentDF}\n"
            #             f"NewDF: {NewDF}\n"
            #             f"ComparisonResult: {ComparisonResult}\n"
            #             f"RowKeys: {RowKeys}\n"
            #             f"ColKeys: {ColKeys}\n"
            #             )
            
            
            
            
            if ComparisonResult["reset_required"]:
                # Reset table if needed
                if DebugPrint:
                    bsprint(f"[INFO] Resetting table {TableName} due to column or shape mismatch.", app=app)
                Table.clear(columns=True)

                # Add new columns
                for col in NewDF.columns:
                    Table.add_column(col, width=None)
                # Add new rows
                for _, row in NewDF.iterrows():
                    Table.add_row(*[Text(str(cell), justify="center") for cell in row])

            else:
                
                
                # Apply only changed values with correct row and column keys
                for row_idx, col_name, old_value, new_value in ComparisonResult["changes"]:
                    if row_idx < len(RowKeys) and col_name in ColKeys:
                        row_key = RowKeys[row_idx]  # Get actual RowKey
                        col_key = ColKeys[col_name]  # Get actual ColumnKey

                        # Measure the new content width
                        NewText = Text(str(new_value), justify="center")
                        NewContentWidth = len(str(new_value))  # Estimate content width
                        CurrentColumn = Table.columns[col_key]

                        # Check if new content exceeds column width
                        if NewContentWidth > CurrentColumn.width:
                            # Rebuild the entire table with adjusted column widths
                            if DebugPrint:
                                bsprint(f"[INFO] Column '{col_name}' is too small. Resizing...", app=app)

                            # Clear & re-add table with resized columns
                            Columns = list(NewDF.columns)
                            Table.clear(columns=True)

                            # Rebuild columns with increased width
                            for col in Columns:
                                # Find max width between content and column name
                                MaxContentWidth = max(len(str(val)) for val in NewDF[col])  # Find max content width
                                ColumnNameWidth = len(str(col))  # Get column name width
                                FinalWidth = max(MaxContentWidth, ColumnNameWidth) + 0  # Ensure padding

                                Table.add_column(col, width=FinalWidth)  # Add column with adjusted width


                            # Re-add rows with updated content
                            for _, row in NewDF.iterrows():
                                Table.add_row(*[Text(str(cell), justify="center") for cell in row])


                            # app.call_later(lambda: Table.refresh())
                            # app.call_later(lambda: Table.post_message(events.Idle()))  # Force recalculation

                            return  # Exit loop early since table was rebuilt

                        # If content fits, just update normally
                        if DebugPrint:
                            bsprint(f"Updating: row_key={row_key}, col_key={col_key}, old={old_value}, new={new_value}", app=app)

                        # CurrentScrollX = Table.scroll_x
                        # CurrentScrollY = Table.scroll_y
                        # # Table.move_cursor(row=row_idx)
                        # Table.update_cell(row_key, col_key, NewText)
                        # app.call_later(lambda: Table.move_cursor(row=row_idx))
                        # put in call later
                        # Table.scroll_x = CurrentScrollX
                        # Table.scroll_y = CurrentScrollY
                        
                        CurrentScrollX = Table.scroll_x
                        CurrentScrollY = Table.scroll_y

                        # Update the cell
                        Table.update_cell(row_key, col_key, NewText)

                        # bsprint(f"moving cursor to row: {row_idx} on Table: {TableName}")
                        
                        # Use call_later to move the cursor after the update
                        app.call_later(lambda: Table.move_cursor(row=row_idx))

                        # Restore scroll position after the cursor move
                        app.call_later(lambda: setattr(Table, 'scroll_x', CurrentScrollX))
                        app.call_later(lambda: setattr(Table, 'scroll_y', CurrentScrollY))
                        
                        

            # Force table refresh
            # app.call_later(lambda: Table.refresh())

                

    # Refresh UI
    # asyncio.sleep(0)
    # app.refresh()
    



async def BSPSSEPyAppResetTables(
        app: App,  # The Textual app instance needed for UI updates
        UseConfigOnly: bool = False  # Flag to determine if only configuration-based columns should be used
) -> None:
    """
    Initializes and resets all BSPSSEPyApp tables.

    This function is called when all required simulation data is collected (e.g., after `SimInit` is run).
    If the simulation has not started yet (`app.myBSPSSEPy` is not generated), it initializes the tables 
    with empty DataFrames.

    Future plan:
        - Add functionality to update tables (or some of them) when a SAV file is selected before the Run starts.

    Parameters:
        app (textual.app.App): The Textual app instance required for UI updates.
        UseConfigOnly (bool, optional): If True, only predefined columns will be used without computing additional data.

    Returns:
        None

    Notes:
        - Uses a dictionary for cleaner, scalable table reset handling.
        - Calls `BSPSSEPyAppResetTable` for each table dynamically.
        - If `app.myBSPSSEPy` is not initialized, resets tables with empty data.
        - Debug information is logged via `bsprint` when `app.DebugCheckBox.value` is `True`.
    """

    from Functions.BSPSSEPy.Sim.BSPSSEPyChannels import FetchChannelValue


    if app is None:
        # bsprint("[ERROR] App instance is missing.", app=app)
        return
    

    RoundDigit = 3

    DebugPrint = app.DebugCheckBox.value
    # Create a shortcut reference
    BSPSSEPySequence = app.myBSPSSEPy.Sim.Config.BSPSSEPySequence
    BSPSSEPyBrn = app.myBSPSSEPy.Sim.BSPSSEPyBrn
    BSPSSEPyBus = app.myBSPSSEPy.Sim.BSPSSEPyBus
    BSPSSEPyLoad = app.myBSPSSEPy.Sim.BSPSSEPyLoad
    BSPSSEPyTrn = app.myBSPSSEPy.Sim.BSPSSEPyTrn
    BSPSSEPyGen = app.myBSPSSEPy.Sim.BSPSSEPyGen
    BSPSSEPyAGCDF = app.myBSPSSEPy.Sim.BSPSSEPyAGCDF


    # Debugging information
    if app.DebugCheckBox.value:
        bsprint("[DEBUG] Resetting all BSPSSEPyApp tables...", app=app)

    # Check if the simulation has started (i.e., if `app.myBSPSSEPy` exists)
    SimulationStarted = hasattr(app, "myBSPSSEPy") and app.myBSPSSEPy is not None

    # If the simulation has not started, use empty DataFrames
    if not SimulationStarted:
        bsprint("[INFO] No active simulation detected. Initializing tables with empty DataFrames.", app=app)

    # Retrieve or initialize DataFrames
    if SimulationStarted:
        
        # Define the ProgressDF DataFrame with mapped columns
        ProgressDF = pd.DataFrame({
            "Progress": [" 🔴"] * len(BSPSSEPySequence),  # Initially all actions are not started
            "Control Sequence": [0] * len(BSPSSEPySequence),  # All set to zero for now
            "Device Type": BSPSSEPySequence["Device Type"],  # Mapped from BSPSSEPySequence
            "ID Type": BSPSSEPySequence["Identification Type"],  # Mapped from BSPSSEPySequence
            "ID Value": BSPSSEPySequence["Identification Value"],  # Mapped from BSPSSEPySequence
            "Action Type": BSPSSEPySequence["Action Type"],  # Mapped from BSPSSEPySequence
            "Action Time": BSPSSEPySequence["Action Time"],  # Mapped from BSPSSEPySequence
            "Action Status": BSPSSEPySequence["Action Status"],  # Mapped from BSPSSEPySequence
        })

        AGCDF = BSPSSEPyAGCDF

        # # Fetch all required channel values asynchronously
        PELECValues, PMECHValues, QELECValues, GREFValues, VREFValues = await FetchGeneratorChannelValues(BSPSSEPyGen, DebugPrint, app)


        # ✅ Apply rounding to all numeric lists
        PELECValues = [round(val, RoundDigit) for val in PELECValues]
        PMECHValues = [round(val, RoundDigit) for val in PMECHValues]
        QELECValues = [round(val, RoundDigit) for val in QELECValues]
        GREFValues = [round(val, RoundDigit) for val in GREFValues]
        VREFValues = [round(val, RoundDigit) for val in VREFValues]

        GenDF = pd.DataFrame({
            "Gen Name": BSPSSEPyGen["MCNAME"],
            "Bus #" : BSPSSEPyGen["NUMBER"],
            "Bus Name": BSPSSEPyGen["NAME"],
            "Δf": BSPSSEPyAGCDF["Δf (Hz)"],
            "Pᴱ": PELECValues,
            "Pᴹ": PMECHValues,
            "Qᴱ": QELECValues,
            "Gᴿᴱꟳ": GREFValues,
            "Vᴿᴱꟳ": VREFValues,
        })
        
        from Functions.BSPSSEPy.Sim.BSPSSEPyLoadFunctions import GetLoadInfo
        LoadDFtemp = await GetLoadInfo(["LOADNAME", "NUMBER", "NAME", "MVAACT", "ILACT", "YLACT", "LDGNACT", "STATUS"], DebugPrint=DebugPrint, app=app)
        # bsprint(LoadDFtemp, app=app)
        # Create the DataFrame
        LoadDF = pd.DataFrame({
            "Load Name": LoadDFtemp["LOADNAME"],
            "Bus #": LoadDFtemp["NUMBER"],
            "Bus Name": LoadDFtemp["NAME"],
            "Power Array [PL, QL, IP, IQ, YP, YQ, PG, QG]": LoadDFtemp.apply(lambda row: [
                round(row["MVAACT"].real, RoundDigit), round(row["MVAACT"].imag, RoundDigit),
                round(row["ILACT"].real, RoundDigit), round(row["ILACT"].imag, RoundDigit),
                round(row["YLACT"].real, RoundDigit), round(row["YLACT"].imag, RoundDigit),
                round(row["LDGNACT"].real, RoundDigit), round(row["LDGNACT"].imag, RoundDigit)
            ], axis=1),
            "Status": LoadDFtemp["STATUS"]
        })



        
        from Functions.BSPSSEPy.Sim.BSPSSEPyBusFunctions import GetBusInfo
        BusDFtemp = await GetBusInfo(["NUMBER", "NAME", "TYPE"], DebugPrint=DebugPrint, app=app)
        BusStatus = await GetBusInfo(["BSPSSEPyStatus"], BSPSSEPyBus=BSPSSEPyBus, DebugPrint=DebugPrint, app=app)

        BusDF = pd.DataFrame({
            "Bus #": BusDFtemp["NUMBER"],
            "Bus Name": BusDFtemp["NAME"],
            "Type": BusDFtemp["TYPE"],
            "Status": BusStatus,
        })
        
        BrnDF = pd.DataFrame({
            "Branch Name": BSPSSEPyBrn["BRANCHNAME"],
            "From Bus #": BSPSSEPyBrn["FROMNUMBER"],
            "To Bus #": BSPSSEPyBrn["TONUMBER"],
            "From Bus Name": BSPSSEPyBrn["FROMNAME"],
            "To Bus Name": BSPSSEPyBrn["TONAME"],
            "Status": BSPSSEPyBrn["STATUS"],  
        })


        TrnDF = pd.DataFrame({
            "Trans. Name": BSPSSEPyTrn["XFRNAME"],
            "From Bus #": BSPSSEPyTrn["FROMNUMBER"],
            "To Bus #": BSPSSEPyTrn["TONUMBER"],
            "From Bus Name": BSPSSEPyTrn["FROMNAME"],
            "To Bus Name": BSPSSEPyTrn["TONAME"],
            "Status": BSPSSEPyTrn["STATUS"],  
        })



        # TrnDF = pd.DataFrame()
    else:
        ProgressDF = pd.DataFrame()
        AGCDF = pd.DataFrame()
        GenDF = pd.DataFrame()
        LoadDF = pd.DataFrame()
        BusDF = pd.DataFrame()
        BrnDF = pd.DataFrame()
        TrnDF = pd.DataFrame()


    
    DataFrames = {
        "Progress": ProgressDF,
        "AGC": AGCDF,
        "Generator": GenDF,
        "Load": LoadDF,
        "Bus": BusDF,
        "Branch": BrnDF,
        "Transformer": TrnDF,
    }

    # Dictionary to map table names, column structures, and app table objects
    Tables = {
        "Progress": {
            "columns": ["Progress", "Control Sequence", "Device Type", "ID Type", "ID Value", "Action Type", "Action Time", "Action Status"],
            "AppTable": app.ProgressTable,
        },
        "AGC": {
            "columns": ["Gen Name", "Alpha", "ΔPᴳ", "Δf"],
            "AppTable": app.AGCTable,
        },
        "Generator": {
            "columns": ["Gen Name", "Bus #", "Bus Name", "Δf", "Pᴱ", "Pᴹ", "Qᴱ", "Gᴿᴱꟳ", "Vᴿᴱꟳ"],
            "AppTable": app.GeneratorTable,
        },
        "Load": {
            "columns": ["Load Name", "Bus #", "Bus Name", "Power Array [PL, QL, IP, IQ, YP, YQ, PG, QG]", "Status"],
            "AppTable": app.LoadTable,
        },
        "Bus": {
            "columns": ["Bus #", "Bus Name", "Type", "Status"],
            "AppTable": app.BusTable,
        },
        "Branch": {
            "columns": ["Branch Name", "From Bus #", "To Bus #", "From Bus Name", "To Bus Name", "Status"],
            "AppTable": app.BranchTable,
        },
        "Transformer": {
            "columns": ["Trans. Name", "From Bus #", "To Bus #", "From Bus Name", "To Bus Name", "Status"],
            "AppTable": app.TransformerTable,
        }
    }

    # Loop through all tables and reset them dynamically
    for TableName, TableInfo in Tables.items():
        bsprint(f"[INFO] Resetting {TableName} table...", app=app)

        BSPSSEPyAppResetTable(
            BSPSSEPyDataFrame=DataFrames[TableName],
            TableCol=TableInfo["columns"],
            app=app,
            appTable=TableInfo["AppTable"],
            UseConfigOnly=UseConfigOnly
        )
        # await asyncio.sleep(app.bsprintasynciotime if app else 0)

    # Final Debugging Information
    bsprint("[INFO] All tables have been reset successfully.", app=app)
    # await asyncio.sleep(app.bsprintasynciotime if app else 0)


    if app.DebugCheckBox.value:
        bsprint("[DEBUG] BSPSSEPyApp tables initialized.", app=app)
        # await asyncio.sleep(app.bsprintasynciotime if app else 0)




def BSPSSEPyAppResetTable(
        BSPSSEPyDataFrame: pd.DataFrame,  # DataFrame containing the source data for the table
        TableCol: list[str],           # List of column names to be displayed in the table (can include computed columns)
        app: App,                # The Textual app instance (needed for UI updates)
        appTable: DataTable,           # The specific table widget in the GUI to be updated (e.g., app.MyTable)
        UseConfigOnly: bool | None = False, # Flag to determine if only configuration-based columns should be used
) -> None:
    """
    Resets and updates a Textual DataTable using the provided DataFrame.

    Parameters:
        BSPSSEPyDataFrame (pd.DataFrame): The DataFrame containing the source data.
        TableCol (list of str): List of column names to include in the table.
            - This list may contain columns that are not in BSPSSEPyDataFrame but will be computed dynamically.
        app (textual.app.App): The Textual app instance required for UI updates.
        appTable (textual.widgets.DataTable): The specific table widget to be updated.
        UseConfigOnly (bool, optional): If True, only predefined columns will be used without computing additional data.

    Returns:
        None

    Notes:
        - The function clears the table, reinitializes columns, and inserts updated rows.
        - If a requested column is not in the DataFrame, it is handled dynamically (e.g., status icons).
        - This function should be called in an async context or a worker to avoid blocking the UI.
    """

    # Ensure required parameters are provided
    if app is None or appTable is None:
        bsprint("[ERROR] App instance or table reference is missing.", app=app)
        return

    if BSPSSEPyDataFrame is None or TableCol is None:
        bsprint("[ERROR] DataFrame or TableCol list is missing.", app=app)
        return

    # Clear existing table data before updating
    appTable.clear(columns=True)

    # Debugging information
    if app.DebugCheckBox.value:
        bsprint(f"[DEBUG] Resetting table {appTable.id} with columns: {TableCol}", app=app)

    # Add columns to the table
    for Column in TableCol:
        appTable.add_column(Column)  # No need to set justify here, we do it per cell
    # Debugging information
    if app.DebugCheckBox.value:
        bsprint(f"[DEBUG] Added columns: {TableCol} (content will be centered)", app=app)

    # Populate the table with rows from the DataFrame
    for _, Row in BSPSSEPyDataFrame.iterrows():
        RowData = []

        for Column in TableCol:
            if Column in BSPSSEPyDataFrame.columns:
                cell_value = Row[Column]  # Get the original value
            else:
                cell_value = ""  # Default empty value for unknown computed columns

            # Convert value to `Text` object with center alignment
            RowData.append(Text(str(cell_value), justify="center"))

        # Add the row to the table
        appTable.add_row(*RowData)
    # Force a UI refresh to reflect changes
    app.call_later(appTable.refresh)
    # app.refresh()

    bsprint("[INFO] Table successfully reset and updated.", app=app)

    # Debugging information
    if app.DebugCheckBox.value:
        bsprint("[DEBUG] Table update completed.", app=app)

    


def BSPSSEPyAppUpdateTables(
        *args,
        app = None
        ) -> None:
    """ This function will update the BSPSSEPyApp Tables using the available data-frames and by calling PSSE functions to collect new measurements (mainly from channels)"""



# async def GetLoadInfoPSSE(LoadNames: list(str), DebugPrint, app):
# "Write a function that calls BSPSSEPyLoad"



async def FetchGeneratorChannelValues(BSPSSEPyGen, DebugPrint, app):
    """
    Asynchronously fetches channel values for all generators in BSPSSEPyGen.

    Parameters:
        BSPSSEPyGen (pd.DataFrame): Generator DataFrame.
        DebugPrint (bool): Enables debugging messages if True.
        app (textual.app.App): The Textual app instance.

    Returns:
        Tuple of lists: (PELECValues, PMECHValues, QELECValues, GREFValues, VREFValues)
    """

    async def fetch_row_channels(row):
        from Functions.BSPSSEPy.Sim.BSPSSEPyChannels import FetchChannelValue
        """
        Fetches channel values for a single generator row asynchronously.
        """
        return (
            await FetchChannelValue(int(row["PELECChannel"]), DebugPrint=DebugPrint, app=app),
            await FetchChannelValue(int(row["PMECHChannel"]), DebugPrint=DebugPrint, app=app),
            await FetchChannelValue(int(row["QELECChannel"]), DebugPrint=DebugPrint, app=app),
            await FetchChannelValue(int(row["GREFChannel"]), DebugPrint=DebugPrint, app=app),
            await FetchChannelValue(int(row["VREFChannel"]), DebugPrint=DebugPrint, app=app)
        )

    # Use `asyncio.gather()` to fetch all generator data in parallel
    results = await asyncio.gather(*(fetch_row_channels(row) for _, row in BSPSSEPyGen.iterrows()))

    # Unpack results into separate lists
    PELECValues, PMECHValues, QELECValues, GREFValues, VREFValues = zip(*results)

    return list(PELECValues), list(PMECHValues), list(QELECValues), list(GREFValues), list(VREFValues)



    

def bsprint(*args, app=None, type: str | None = None, sep="\n", end=""):
    """
    Prints messages to the DetailsTextArea in the app if available.
    Falls back to printing in the terminal if no app is provided.

    This function automatically handles async execution using `call_later`
    when inside the GUI, so you don't have to use `await` explicitly.

    Parameters:
        *args: Variable number of arguments to print, similar to `print()`.
        app (BSPSSEPyApp, optional): The Textual app instance (default is None).
        type (optional): If type is ["d", "debug"], the message will only be displayed if `app.DebugCheckBox.value` is True.
        sep (str, optional): Separator used between arguments (default: space).
        end (str, optional): String appended at the end (default: newline).
    """
    # If no explicit app is provided but the last arg seems to be an app instance,     
    # remove it from args and assign it to the app parameter.  

    
    if not app and args and hasattr(args[-1], "BSPSSEPyApplication"):
        app = args[-1]
        args = args[:-1]

    Message = sep.join(map(str, args)) + end  # Join all arguments into a single string

    if app:
        
        if app.DummyRun:
            return
        if type:
            # If DebugCheckBox is checked, allow debug messages
            if type.lower() in ["d", "debug"] and not app.DebugCheckBox.value:
                return  # ✅ Skip debug messages if debugging is disabled
            
        AppendToDetailsTextArea(app.DetailsTextArea, Message,app=app)

        
    else:
        print(Message)  # ✅ Fallback to terminal output when no GUI is available



def AppendToDetailsTextArea(DetailsTextArea, Message,app=None):
    """
    Appends a new message to the DetailsTextArea without erasing previous content.

    Parameters:
        DetailsTextArea (TextArea): The TextArea widget where the message should be added.
        Message (str): The message to append.
    """
    if DetailsTextArea:
        if DetailsTextArea.document.line_count > 5000:  # ✅ Prevents UI lag by clearing old messages
            DetailsTextArea.clear()
            DetailsTextArea.insert(text="[LOG CLEARED - TOO LONG]\n")


        # Append new text at the last line
        DetailsTextArea.insert(
            text=f"{Message}",
            location=(DetailsTextArea.document.line_count, 0),  # Move to last line
            maintain_selection_offset=True
        )

        if app:
            
            # def DetailsTextAreaSmartScroll (app: App, DetailsTextArea):
            #     # Step 1: Move the cursor to the end of the DetailsTextArea
            #     while not DetailsTextArea.cursor_at_last_line:
            #         for i in range(5):
            #             app.call_later(DetailsTextArea.action_cursor_page_down)
            #             app.call_later(DetailsTextArea.action_cursor_line_end)
            #             print(f"CurrentCursorLoc={DetailsTextArea.cursor_location}")
            #             print(f"contentheight = {DetailsTextArea.content_size.height}")
            #         print(f"End? = {DetailsTextArea.cursor_at_last_line}")
            #         break
            # DetailsTextAreaSmartScroll(app=app, DetailsTextArea=DetailsTextArea)
            app.call_later(DetailsTextArea.scroll_end, animate=False, immediate=True)#, animate, False)  # Ensure latest message is visible
            # print(f"DetailsTextArea.cursor_at_end_of_text = {DetailsTextArea.cursor_at_end_of_text}")

            # print(f"")

def ProgressBarUpdate(ProgressBar, CurrentTime, TotalTime, App=None, label=None):
    """
    Updates the progress bar based on the current simulation time.

    Parameters:
        ProgressBar (ProgressBar): The ProgressBar widget to update.
        CurrentTime (int | float): The current simulation time in seconds.
        TotalTime (int | float): The total simulation time in seconds (set only once).
        App (BSPSSEPyApp, optional): The main Textual app instance for UI updates.
        label (Label, optional): The label to display the current simulation time.
    """
    
    # Ensure TotalTime is greater than 0 to avoid division errors
    if TotalTime <= 0:
        return

    # Calculate progress percentage
    ProgressPercentage = min((CurrentTime / TotalTime) * 100, 100)  # Cap at 100%
    
    ProgressBar.update(total=100, progress=ProgressPercentage)  # Update the progress bar
    
    # Format the time display with hours, minutes, and seconds
    hours = CurrentTime // 3600
    minutes = (CurrentTime % 3600) // 60
    seconds = CurrentTime % 60

    if hours > 0:
        TimeDisplay = f"t = {int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        TimeDisplay = f"t = {int(minutes)}m {int(seconds)}s"
    else:
        TimeDisplay = f"t = {int(seconds)}s"

    # Format the time display
    # TimeDisplay = f"t = {int(CurrentTime)}s" if CurrentTime < 60 else f"t = {int(CurrentTime//60)}m {int(CurrentTime%60)}s"

    # # ✅ Schedule UI updates to prevent lagging
    # if App:
    #     App.call_later(AppendToDetailsTextArea, App.DetailsTextArea, f"Progress: {ProgressPercentage}%")
    
    if label:
        App.call_later(label.update, TimeDisplay)  # ✅ Properly schedules label update


def AddSavFilesToTree(ParentNode, FolderPath):
    """
    Recursively scans the given folder and adds .sav files as leaves 
    and subfolders as expandable nodes in the tree.

    Parameters:
        ParentNode (Tree.Node): The parent node where items will be added.
        FolderPath (str): The path of the folder to scan.
    """
    try:
        # Get a sorted list of all items (files & directories) in the folder
        for Entry in sorted(os.scandir(FolderPath), key=lambda E: E.name.lower()):
            if Entry.is_dir():
                # If it's a folder, add it as a node and recurse into it
                FolderNode = ParentNode.add(Entry.name, expand=False)
                AddSavFilesToTree(FolderNode, Entry.path)
            elif Entry.is_file() and Entry.name.endswith(".sav"):
                # If it's a .sav file, add it as a leaf
                ParentNode.add_leaf(Entry.name)
    except PermissionError:
        pass  # If permission is denied, just skip that folder
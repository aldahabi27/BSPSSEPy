from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import *
import asyncio
import random  # ✅ Used to generate random values for table updates

import psspy

async def RunSimulation(app, DummyRun: bool | None = False):
    """
    Runs the simulation while dynamically updating tables and progress bar.

    Args:
        app: The BSPSSEPyApp instance, used to access UI elements.

    Simulation Workflow:
    - Initializes tables with dummy data.
    - Updates table values dynamically at each time step.
    - Shows the progress of the simulation.
    """
    DebugPrint = app.DebugCheckBox.value


    if DummyRun:
        # Ensure no previous PSSE Setup is in memory - critical to empty channels and any other selected case-specific info not to be carried over unintentionally!
        psspy.pssehalt_2()

        app.DummyRun = True
        app.CaseTree.disabled = True
        app.StopButton.disabled = False

        # Importing main Class BSPSSEPy
        from Functions.BSPSSEPy.BSPSSEPy import BSPSSEPy
        
        # Call the main constructor and load the configurations for PSSE Simulation
        app.myBSPSSEPy = BSPSSEPy()
            
        await app.myBSPSSEPy.BSPSSEPyInit(ConfigPath=app.ConfigPath, app=app)

        app.DummyRun = False
        app.CaseTree.disabled = False
        app.StopButton.disabled = True


    else:

        try:
            # Ensure no previous PSSE Setup is in memory - critical to empty channels and any other selected case-specific info not to be carried over unintentionally!
            psspy.pssehalt_2()

            del app.myBSPSSEPy
            app.StopButton.disabled = False
            app.RunButton.disabled = True

            AppendToDetailsTextArea(app.DetailsTextArea, f"Run Started")
            AppendToDetailsTextArea(app.DetailsTextArea, f"Config: {app.ConfigPath}")

            # Importing main Class BSPSSEPy
            from Functions.BSPSSEPy.BSPSSEPy import BSPSSEPy
            
            # Call the main constructor and load the configurations for PSSE Simulation
            app.myBSPSSEPy = BSPSSEPy()
            
            await app.myBSPSSEPy.BSPSSEPyInit(ConfigPath=app.ConfigPath, app=app)
            await BSPSSEPyAppResetTables(app)
            
            if app.DebugCheckBox.value:
                bsprint("[DEBUG] BSPSSEPy initialized successfully.",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            await app.myBSPSSEPy.Sim.SetBlackStart(app=app)
            await app.myBSPSSEPy.Sim.Run(app=app)

            

            
            app.myBSPSSEPy.Plot(DebugPrint=app.DebugCheckBox.value,app=app)


            if app.DebugCheckBox.value:
                bsprint("Debug Information:",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  Case Name: {app.myBSPSSEPy.Config.CaseName}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  Version: {app.myBSPSSEPy.Config.Ver}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  Number of Buses: {app.myBSPSSEPy.Config.NumberOfBuses}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  Buses to Monitor (Frequency): {app.myBSPSSEPy.Config.BusesToMonitor_Frequency}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  Buses to Monitor (Voltage): {app.myBSPSSEPy.Config.BusesToMonitor_Voltage}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  Frequency Flag: {app.myBSPSSEPy.Config.FrequencyFlag}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  PSSE Max Iteration (Newton-Raphson): {app.myBSPSSEPy.Config.PSSEMaxIterationNewtonRaphson}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  Control Sequence: {app.myBSPSSEPy.Config.BSPSSEPySequence}",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)
                bsprint(f"  Case Initialization Flag: {app.myBSPSSEPy.PSSE.CaseInitializationFlag} (0 indicates no errors)",app=app)
                await asyncio.sleep(app.bsprintasynciotime if app else 0)

            
            
            # TotalSimulationTime = 1  # Example total simulation time (120 seconds)
            
            # AppendToDetailsTextArea(app.DetailsTextArea, "Run Button Pressed")

            # # Disable tree and reset progress bar
            # app.CaseTree.disabled = True
            # app.TopBarProgressBar.value = 0

            # # ==========================
            # # Initialize Tables with Dummy Data
            # # ==========================

            # # ✅ Progress Table: 25 columns, 5 rows
            # app.ProgressTable.clear(columns = True)
            # ColumnNames = [f"Col {i}" for i in range(1, 26)]
            # app.ProgressTable.add_columns(*ColumnNames)
            # for _ in range(5):
            #     app.ProgressTable.add_row(*[str(random.randint(0, 100)) for _ in range(25)])
            
            # ProgressTableRowDic = app.ProgressTable.rows
            # ProgressTableColumnDic = app.ProgressTable.columns
            # # AppendToDetailsTextArea(app.DetailsTextArea, ProgressTableRowDic)
            # # AppendToDetailsTextArea(app.DetailsTextArea, ProgressTableColumnDic)

            # # ✅ AGC Table: 3 columns, 8 rows
            # app.AGCTable.clear(columns = True)
            # app.AGCTable.add_columns("AGC Name", "Setpoint", "Output")
            # for i in range(8):
            #     app.AGCTable.add_row(f"AGC {i+1}", str(random.randint(50, 150)), str(random.randint(20, 120)))

            # AGCTableRowDic = app.AGCTable.rows
            # AGCTableColumnDic = app.AGCTable.columns
            # # AppendToDetailsTextArea(app.DetailsTextArea, AGCTableRowDic)
            # # AppendToDetailsTextArea(app.DetailsTextArea, AGCTableColumnDic)


            # # ✅ Generator Table: 4 columns, 6 rows
            # app.GeneratorTable.clear(columns = True)
            # app.GeneratorTable.add_columns("Gen ID", "Power (MW)", "Voltage (V)", "Status")
            # for i in range(6):
            #     app.GeneratorTable.add_row(f"Gen {i+1}", str(random.randint(100, 300)), str(random.uniform(0.9, 1.1)), random.choice(["ON", "OFF"]))
            # GeneratorTableRowDic = app.GeneratorTable.rows
            # GeneratorTableColumnDic = app.GeneratorTable.columns


            # # ✅ Load Table: 3 columns, 10 rows
            # app.LoadTable.clear(columns = True)
            # app.LoadTable.add_columns("Load ID", "P (MW)", "Q (MVar)")
            # for i in range(10):
            #     app.LoadTable.add_row(f"Load {i+1}", str(random.randint(50, 200)), str(random.randint(10, 100)))
            # LoadTableRowDic = app.LoadTable.rows
            # LoadTableColumnDic = app.LoadTable.columns


            # # ✅ Bus Table: 5 columns, 15 rows
            # app.BusTable.clear(columns = True)
            # app.BusTable.add_columns("Bus ID", "Voltage (kV)", "Angle (deg)", "Load (MW)", "Status")
            # for i in range(15):
            #     app.BusTable.add_row(f"Bus {i+1}", str(random.uniform(10, 50)), str(random.uniform(-30, 30)), str(random.randint(100, 400)), random.choice(["Active", "Inactive"]))
            # BusTableRowDic = app.BusTable.rows
            # BusTableColumnDic = app.BusTable.columns

            # # ✅ Branch Table: 4 columns, 7 rows
            # app.BranchTable.clear(columns = True)
            # app.BranchTable.add_columns("Branch ID", "From Bus", "To Bus", "Status")
            # for i in range(7):
            #     app.BranchTable.add_row(f"Br {i+1}", f"Bus {random.randint(1, 15)}", f"Bus {random.randint(1, 15)}", random.choice(["Closed", "Open"]))
            # BranchTableRowDic = app.BranchTable.rows
            # BranchTableColumnDic = app.BranchTable.columns

            # # ✅ Transformer Table: 3 columns, 4 rows
            # app.TransformerTable.clear(columns = True)
            # app.TransformerTable.add_columns("Transformer ID", "Primary Bus", "Secondary Bus", "Status")
            # for i in range(4):
            #     app.TransformerTable.add_row(f"TX {i+1}", f"Bus {random.randint(1, 15)}", f"Bus {random.randint(1, 15)}", random.choice(["Closed", "Open"]))
            # TransformerTableRowDic = app.TransformerTable.rows
            # TransformerTableColumnDic = app.TransformerTable.columns

            # # Small delay to simulate real-time updates
            # await asyncio.sleep(0.1)

            # # ==========================
            # # Run Simulation (Update Tables Dynamically)
            # # ==========================
            # for CurrentTime in range(0, TotalSimulationTime + 1, 1):  # Simulating time steps
            #     ProgressBarUpdate(app.TopBarProgressBar, CurrentTime, TotalSimulationTime, App=app, label=app.TopBarProgressBarLabel)
            #     # await asyncio.sleep(0.1)
            #     # app.ProgressTable.update_cell_at((2, 2), str(random.randint(0, 100)))


            #     # ✅ Dynamically update random table values at each time step

            #     # import random

            #     # Update Progress Table (Row 0 gets updated with random values)
            #     for column_key in ProgressTableColumnDic.keys():
            #         for row_key in ProgressTableRowDic.keys():
            #     #     column_key = ProgressTableColumnKeys(col)  # Column keys are "Col 1", "Col 2", ..., "Col 25"
            #             app.ProgressTable.update_cell(row_key=row_key, column_key=column_key, value=str(random.randint(0, 100)))

            #     # ✅ Update AGC Table (Setpoints change)
            #     for row_key in AGCTableRowDic.keys():
            #         app.AGCTable.update_cell(row_key=row_key, column_key=list(AGCTableColumnDic.keys())[1], value=str(random.randint(50, 150)))  # Setpoint
            #         app.AGCTable.update_cell(row_key=row_key, column_key=list(AGCTableColumnDic.keys())[2], value=str(random.randint(20, 120)))  # Output

            #     # ✅ Update Generator Table (Power changes)
            #     for row_key in GeneratorTableRowDic.keys():
            #         app.GeneratorTable.update_cell(row_key=row_key, column_key=list(GeneratorTableColumnDic.keys())[1], value=str(random.randint(100, 300)))  # Power
            #         app.GeneratorTable.update_cell(row_key=row_key, column_key=list(GeneratorTableColumnDic.keys())[2], value=str(round(random.uniform(0.9, 1.1), 2)))  # Voltage

            #     # ✅ Update Load Table (Power varies)
            #     for row_key in LoadTableRowDic.keys():
            #         app.LoadTable.update_cell(row_key=row_key, column_key=list(LoadTableColumnDic.keys())[1], value=str(random.randint(50, 200)))  # P
            #         app.LoadTable.update_cell(row_key=row_key, column_key=list(LoadTableColumnDic.keys())[2], value=str(random.randint(10, 100)))  # Q

            #     # ✅ Update Bus Table (Voltage fluctuates)
            #     for row_key in BusTableRowDic.keys():
            #         app.BusTable.update_cell(row_key=row_key, column_key=list(BusTableColumnDic.keys())[1], value=str(round(random.uniform(10, 50), 2)))  # Voltage
            #         app.BusTable.update_cell(row_key=row_key, column_key=list(BusTableColumnDic.keys())[2], value=str(round(random.uniform(-30, 30), 2)))  # Angle
            #         app.BusTable.update_cell(row_key=row_key, column_key=list(BusTableColumnDic.keys())[3], value=str(random.randint(100, 400)))  # Load


            #     # ✅ Update Branch Table (Status change)
            #     for row_key in BranchTableRowDic.keys():
            #         app.BranchTable.update_cell(row_key=row_key, column_key=list(BranchTableColumnDic.keys())[3], value=random.choice(["Closed", "Open"]))  # Status
                    

            #     # ✅ Update Transformer Table (Status change)
            #     for row_key in TransformerTableRowDic.keys():
            #         app.TransformerTable.update_cell(row_key=row_key, column_key=list(TransformerTableColumnDic.keys())[3], value=str(random.choice(["Closed", "Open"])))  # Voltage
                    

                # Small delay to simulate real-time updates
                # await asyncio.sleep(0.0001)

                # AppendToDetailsTextArea(app.DetailsTextArea, app.ProgressTable._label_row_key)
                # AppendToDetailsTextArea(app.DetailsTextArea, app.ProgressTable._label_column_key.__str__)

            # ==========================
            # Simulation Completed
            # ==========================
            app.CaseTree.disabled = False
            AppendToDetailsTextArea(app.DetailsTextArea, "Run Completed")
            app.StopButton.disabled = True
            app.RunButton.disabled = False
                    

        except Exception as error:

            import traceback
            import asyncio

        
            app.CaseTree.disabled = False
            app.StopButton.disabled = True

            # Capture the full exception traceback
            full_traceback = traceback.format_exc()

            # Print to console for debugging (optional)
            print(full_traceback)

            # Send the full error log to the GUI DetailsTextArea
            bsprint(f"❌ Fatal Error Occurred:\n{full_traceback}", app=app)

            # Ensure UI has time to update
            await asyncio.sleep(app.bsprintasynciotime if app else 0)

            # app.CaseTree.disabled = False
            # app.StopButton.disabled = True
            # import io
            # from contextlib import redirect_stdout

            #  # Create a StringIO object to capture the output
            # output_capture = io.StringIO()

            # # Use the context manager to capture the stdout
            # with redirect_stdout(output_capture):
            #     print("Fatel Error Occured:")
            #     print(error)
            # # Get the captured output
            # captured_output = output_capture.getvalue()
            
            # bsprint(captured_output, app=app)
            # print(app)
            # print('here')
            # bsprint("HELLO")
            # await asyncio.sleep(app.bsprintasynciotime if app else 0)
            
        
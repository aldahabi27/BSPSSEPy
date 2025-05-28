"""Run button execution sequence for BSPSSEPyApp."""
from __future__ import annotations
# import asyncio
# pyright: reportMissingImports=false
import psspy  # noqa: F401 pylint: disable=import-error 
from textual.app import App
from fun.bspssepy.app.app_helper_funs import (
    ProgressBarUpdate,
    BSPSSEPyAppResetTables,
)
from fun.bspssepy.app.bspssepy_print import (
    append_to_details_text_area,
    bspssepy_print as bp
)

async def run_simulation(app: App, dummy_run: bool | None = False):
    """
    Runs the simulation while dynamically updating tables and progress bar.

    Args:
        app: The BSPSSEPyApp instance, used to access UI elements.

    Simulation Workflow:
    - Initializes tables with dummy data.
    - Updates table values dynamically at each time step.
    - Shows the progress of the simulation.
    """
    debug_print = app.debug_checkbox.value

    if dummy_run:
        # Ensure no previous PSSE Setup is in memory - critical to empty
        # channels and any other selected case-specific info not to be
        # carried over unintentionally!
        psspy.pssehalt_2()

        app.dummy_run = True
        app.case_tree.disabled = True
        app.stop_button.disabled = False

        # Importing main Class BSPSSEPy
        from fun.bspssepy.bspssepy_core import BSPSSEPy
        
        # Call the main constructor and load the configurations for PSSE Simulation
        app.bspssepy = BSPSSEPy()
            
        await app.bspssepy.BSPSSEPyInit(ConfigPath=app.config_path, app=app)

        app.dummy_run = False
        app.case_tree.disabled = False
        app.stop_button.disabled = True


    else:

        try:
            # Ensure no previous PSSE Setup is in memory - critical to empty channels and any other selected case-specific info not to be carried over unintentionally!
            psspy.pssehalt_2()

            del app.bspssepy
            app.stop_button.disabled = False
            app.run_button.disabled = True

            append_to_details_text_area(app.details_text_area, f"Run Started")
            append_to_details_text_area(app.details_text_area, f"config: {app.config_path}")

            # Importing main Class BSPSSEPy
            from fun.bspssepy.bspssepy_core import BSPSSEPy
            
            # Call the main constructor and load the configurations for PSSE Simulation
            app.bspssepy = BSPSSEPy()
            
            await app.bspssepy.BSPSSEPyInit(ConfigPath=app.config_path, app=app)
            await BSPSSEPyAppResetTables(app)
            
            if app.debug_checkbox.value:
                bp("[DEBUG] BSPSSEPy initialized successfully.",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            await app.bspssepy.sim.SetBlackStart(app=app)
            await app.bspssepy.sim.Run(app=app)

            

            
            app.bspssepy.Plot(debug_print=app.debug_checkbox.value,app=app)


            if app.debug_checkbox.value:
                bp("Debug Information:",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  Case Name: {app.bspssepy.config.CaseName}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  Version: {app.bspssepy.config.Ver}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  Number of Buses: {app.bspssepy.config.NumberOfBuses}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  Buses to Monitor (Frequency): {app.bspssepy.config.BusesToMonitor_Frequency}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  Buses to Monitor (Voltage): {app.bspssepy.config.BusesToMonitor_Voltage}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  Frequency Flag: {app.bspssepy.config.FrequencyFlag}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  PSSE Max Iteration (Newton-Raphson): {app.bspssepy.config.PSSEMaxIterationNewtonRaphson}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  Control Sequence: {app.bspssepy.config.bspssepy_sequence}",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)
                bp(f"  Case Initialization Flag: {app.bspssepy.PSSE.CaseInitializationFlag} (0 indicates no errors)",app=app)
                await asyncio.sleep(app.async_print_delay if app else 0)

            
            
            # TotalSimulationTime = 1  # Example total simulation time (120 seconds)
            
            # append_to_details_text_area(app.details_text_area, "Run Button Pressed")

            # # Disable tree and reset progress bar
            # app.case_tree.disabled = True
            # app.top_bar_progress_bar.value = 0

            # # ==========================
            # # Initialize Tables with Dummy Data
            # # ==========================

            # # ✅ Progress Table: 25 columns, 5 rows
            # app.progress_table.clear(columns = True)
            # ColumnNames = [f"Col {i}" for i in range(1, 26)]
            # app.progress_table.add_columns(*ColumnNames)
            # for _ in range(5):
            #     app.progress_table.add_row(*[str(random.randint(0, 100)) for _ in range(25)])
            
            # ProgressTableRowDic = app.progress_table.rows
            # ProgressTableColumnDic = app.progress_table.columns
            # # append_to_details_text_area(app.details_text_area, ProgressTableRowDic)
            # # append_to_details_text_area(app.details_text_area, ProgressTableColumnDic)

            # # ✅ AGC Table: 3 columns, 8 rows
            # app.agc_table.clear(columns = True)
            # app.agc_table.add_columns("AGC Name", "Setpoint", "Output")
            # for i in range(8):
            #     app.agc_table.add_row(f"AGC {i+1}", str(random.randint(50, 150)), str(random.randint(20, 120)))

            # AGCTableRowDic = app.agc_table.rows
            # AGCTableColumnDic = app.agc_table.columns
            # # append_to_details_text_area(app.details_text_area, AGCTableRowDic)
            # # append_to_details_text_area(app.details_text_area, AGCTableColumnDic)


            # # ✅ Generator Table: 4 columns, 6 rows
            # app.gen_table.clear(columns = True)
            # app.gen_table.add_columns("Gen ID", "Power (MW)", "Voltage (V)", "Status")
            # for i in range(6):
            #     app.gen_table.add_row(f"Gen {i+1}", str(random.randint(100, 300)), str(random.uniform(0.9, 1.1)), random.choice(["ON", "OFF"]))
            # GeneratorTableRowDic = app.gen_table.rows
            # GeneratorTableColumnDic = app.gen_table.columns


            # # ✅ load Table: 3 columns, 10 rows
            # app.load_table.clear(columns = True)
            # app.load_table.add_columns("load ID", "P (MW)", "Q (MVar)")
            # for i in range(10):
            #     app.load_table.add_row(f"load {i+1}", str(random.randint(50, 200)), str(random.randint(10, 100)))
            # LoadTableRowDic = app.load_table.rows
            # LoadTableColumnDic = app.load_table.columns


            # # ✅ Bus Table: 5 columns, 15 rows
            # app.bus_table.clear(columns = True)
            # app.bus_table.add_columns("Bus ID", "Voltage (kV)", "Angle (deg)", "load (MW)", "Status")
            # for i in range(15):
            #     app.bus_table.add_row(f"Bus {i+1}", str(random.uniform(10, 50)), str(random.uniform(-30, 30)), str(random.randint(100, 400)), random.choice(["Active", "Inactive"]))
            # BusTableRowDic = app.bus_table.rows
            # BusTableColumnDic = app.bus_table.columns

            # # ✅ Branch Table: 4 columns, 7 rows
            # app.brn_table.clear(columns = True)
            # app.brn_table.add_columns("Branch ID", "From Bus", "To Bus", "Status")
            # for i in range(7):
            #     app.brn_table.add_row(f"Br {i+1}", f"Bus {random.randint(1, 15)}", f"Bus {random.randint(1, 15)}", random.choice(["Closed", "Open"]))
            # BranchTableRowDic = app.brn_table.rows
            # BranchTableColumnDic = app.brn_table.columns

            # # ✅ Transformer Table: 3 columns, 4 rows
            # app.trn_table.clear(columns = True)
            # app.trn_table.add_columns("Transformer ID", "Primary Bus", "Secondary Bus", "Status")
            # for i in range(4):
            #     app.trn_table.add_row(f"TX {i+1}", f"Bus {random.randint(1, 15)}", f"Bus {random.randint(1, 15)}", random.choice(["Closed", "Open"]))
            # TransformerTableRowDic = app.trn_table.rows
            # TransformerTableColumnDic = app.trn_table.columns

            # # Small delay to simulate real-time updates
            # await asyncio.sleep(0.1)

            # # ==========================
            # # Run Simulation (Update Tables Dynamically)
            # # ==========================
            # for CurrentTime in range(0, TotalSimulationTime + 1, 1):  # Simulating time steps
            #     ProgressBarUpdate(app.top_bar_progress_bar, CurrentTime, TotalSimulationTime, App=app, label=app.top_bar_progress_bar_label)
            #     # await asyncio.sleep(0.1)
            #     # app.progress_table.update_cell_at((2, 2), str(random.randint(0, 100)))


            #     # ✅ Dynamically update random table values at each time step

            #     # import random

            #     # Update Progress Table (Row 0 gets updated with random values)
            #     for column_key in ProgressTableColumnDic.keys():
            #         for row_key in ProgressTableRowDic.keys():
            #     #     column_key = ProgressTableColumnKeys(col)  # Column keys are "Col 1", "Col 2", ..., "Col 25"
            #             app.progress_table.update_cell(row_key=row_key, column_key=column_key, value=str(random.randint(0, 100)))

            #     # ✅ Update AGC Table (Setpoints change)
            #     for row_key in AGCTableRowDic.keys():
            #         app.agc_table.update_cell(row_key=row_key, column_key=list(AGCTableColumnDic.keys())[1], value=str(random.randint(50, 150)))  # Setpoint
            #         app.agc_table.update_cell(row_key=row_key, column_key=list(AGCTableColumnDic.keys())[2], value=str(random.randint(20, 120)))  # Output

            #     # ✅ Update Generator Table (Power changes)
            #     for row_key in GeneratorTableRowDic.keys():
            #         app.gen_table.update_cell(row_key=row_key, column_key=list(GeneratorTableColumnDic.keys())[1], value=str(random.randint(100, 300)))  # Power
            #         app.gen_table.update_cell(row_key=row_key, column_key=list(GeneratorTableColumnDic.keys())[2], value=str(round(random.uniform(0.9, 1.1), 2)))  # Voltage

            #     # ✅ Update load Table (Power varies)
            #     for row_key in LoadTableRowDic.keys():
            #         app.load_table.update_cell(row_key=row_key, column_key=list(LoadTableColumnDic.keys())[1], value=str(random.randint(50, 200)))  # P
            #         app.load_table.update_cell(row_key=row_key, column_key=list(LoadTableColumnDic.keys())[2], value=str(random.randint(10, 100)))  # Q

            #     # ✅ Update Bus Table (Voltage fluctuates)
            #     for row_key in BusTableRowDic.keys():
            #         app.bus_table.update_cell(row_key=row_key, column_key=list(BusTableColumnDic.keys())[1], value=str(round(random.uniform(10, 50), 2)))  # Voltage
            #         app.bus_table.update_cell(row_key=row_key, column_key=list(BusTableColumnDic.keys())[2], value=str(round(random.uniform(-30, 30), 2)))  # Angle
            #         app.bus_table.update_cell(row_key=row_key, column_key=list(BusTableColumnDic.keys())[3], value=str(random.randint(100, 400)))  # load


            #     # ✅ Update Branch Table (Status change)
            #     for row_key in BranchTableRowDic.keys():
            #         app.brn_table.update_cell(row_key=row_key, column_key=list(BranchTableColumnDic.keys())[3], value=random.choice(["Closed", "Open"]))  # Status
                    

            #     # ✅ Update Transformer Table (Status change)
            #     for row_key in TransformerTableRowDic.keys():
            #         app.trn_table.update_cell(row_key=row_key, column_key=list(TransformerTableColumnDic.keys())[3], value=str(random.choice(["Closed", "Open"])))  # Voltage
                    

                # Small delay to simulate real-time updates
                # await asyncio.sleep(0.0001)

                # append_to_details_text_area(app.details_text_area, app.progress_table._label_row_key)
                # append_to_details_text_area(app.details_text_area, app.progress_table._label_column_key.__str__)

            # ==========================
            # Simulation Completed
            # ==========================
            app.case_tree.disabled = False
            append_to_details_text_area(app.details_text_area, "Run Completed")
            app.stop_button.disabled = True
            app.run_button.disabled = False
                    

        except Exception as error:

            import traceback
            import asyncio

        
            app.case_tree.disabled = False
            app.stop_button.disabled = True

            # Capture the full exception traceback
            full_traceback = traceback.format_exc()

            # Print to console for debugging (optional)
            print(full_traceback)

            # Send the full error log to the GUI details_text_area
            bp(f"❌ Fatal Error Occurred:\n{full_traceback}", app=app)

            # Ensure UI has time to update
            await asyncio.sleep(app.async_print_delay if app else 0)

            # app.case_tree.disabled = False
            # app.stop_button.disabled = True
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
            
            # bp(captured_output, app=app)
            # print(app)
            # print('here')
            # bp("HELLO")
            # await asyncio.sleep(app.async_print_delay if app else 0)
            
        
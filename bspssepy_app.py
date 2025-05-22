"""Main executable of BSPSSEPy Application"""

# Enables future Python features (not strictly needed here but good practice)
from __future__ import annotations

# Essential Imports to install missing libraries
import subprocess
import sys
import pkg_resources
from fun.bspssepy.meta import VER_NUM, BUILD_NUM, current_timestamp
# ==========================
#  BSPSSEPy Program Code
# ==========================
current_date = current_timestamp()

print("===========================================================")
print("             Welcome to the BSPSSEPy Program!             ")
print("===========================================================")
print(f"Version: {VER_NUM}")
print("Last Updated: 20 May 2025")
print(f"Current Date and Time: {current_date}")
print("-----------------------------------------------------------")
print("Developed by: Ilyas Farhat")
print("Contact: ilyas.farhat@outlook.com")
print("Copyright (c) 2024-2025, Ilyas Farhat")
print("All rights reserved.")
print("-----------------------------------------------------------")

# ==========================
#  Library Verification
# ==========================
# List of required libraries - to install any missing libraries for all 
# methods and all sub-methods
RequiredLibraries = [
    "psse3601",
    "psspy",
    "dyntools",
    "os",
    "sys",
    "pathlib",
    "datetime",
    "csv",
    "matplotlib",
    "pandas",
    "plotext",
    "importlib",
    "json",
    "numbers",
    "numpy",
    # "textual==2.1.1",
    "textual",
    # "textual-dev",
    "asyncio",
    "time",
    "functools",
    "random",
    "io",
    "contextlib",
    # "BSPSSEPyApp",
]

print("Verifying that needed libraries are installed.")

# Attempt to import each library and install if missing
for lib in RequiredLibraries:
    lib_name, _, lib_version = lib.partition("==")
    try:
        # Try to import the library
        globals()[lib_name] = __import__(lib_name)
        if lib_version:
            installed_version = (
                pkg_resources.get_distribution(lib_name).version
            )
            if installed_version != lib_version:
                raise ImportError(
                    f"{lib_name} version {lib_version} is required, "
                    f"but version {installed_version} is installed."
                ) from None  # or from e if catching an error

        print(f"{lib_name}{f' {installed_version}' if lib_version else ''} ✔")

    except ImportError as ie:
        print(f"{lib} is missing or has the wrong version. Installing it...")
        try:
            # Install the missing or correct version of the library
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", lib]
                )
            # Try importing again after installation
            globals()[lib_name] = __import__(lib_name)
            installed_version = (
                pkg_resources.get_distribution(lib_name).version
            )
            if lib_version and installed_version != lib_version:
                raise ImportError(
                    f"{lib_name} version {lib_version} is required, "
                    f"but version {installed_version} is installed."
                ) from ie
            print(f"{lib} installed successfully ✔")
        except Exception as e:
            print(f"Failed to install {lib}. Error: {e}")
            print("Don't run Cell 1. Missing library cannot be installed.")
            # Stop execution
            raise SystemExit(
                f"Aborting execution due to missing library: {lib}"
            ) from e

print("Loading BSPSSEPyApp GUI. Please Wait...")

# Importing standard Python modules
from functools import partial  # Allows partial function application (not used yet)
from typing import Any  # Used for type hints
from datetime import datetime  # Used to format the date/time manually
import time  # Used for time-related operations
import asyncio  # Used for async operations

import os  # Used for file system operations
from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import AddSavFilesToTree # Importing custom helper functions
# Importing core Textual modules
from textual._on import on  # Used for event handling
from textual.app import App, ComposeResult  # Base classes for a Textual app
from textual.binding import Binding  # Used for keyboard bindings (not yet used)
from textual.containers import Container, Grid, Horizontal, VerticalScroll, HorizontalScroll  # Layout containers
from textual.widgets import (  # Importing various UI widgets
    Button,
    Collapsible,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    MarkdownViewer,
    OptionList,
    ProgressBar,
    RadioSet,
    RichLog,
    Select,
    SelectionList,
    Switch,
    TabbedContent,
    TextArea,
    Tree,
    Static,
    Checkbox,
    Link,
)
from textual.widgets._masked_input import MaskedInput  # Specialized input field
from textual.widgets._toggle_button import ToggleButton  # Toggle button widget
from textual.widgets.option_list import Option  # Dropdown options
from textual.widgets.text_area import Selection  # Text selection handling

class BSPSSEPyApp(App[None]):  # Inheriting from the Textual App class
    """
    This class defines the main Textual application. 
    It sets up the layout, UI components, and event handling.
    """

    # Defining CSS styling for the application
    CSS_PATH = "./Functions/BSPSSEPy/App/BSPSSEPyAppCSS.tcss"


    def compose(self) -> ComposeResult:
        """
        This method defines the UI components and how they are structured.
        """
        self.BSPSSEPyApplication = "Main"
        self.bsprintasynciotime = 0.02
        self.DummyRun = False

        # Setting the title and subtitle of the application
        self.title = "BSPSSEPy Application"
        self.sub_title = f"Version {VER_NUM} - Build {BUILD_NUM}"

        # Creating a header with the current time format
        yield Header(show_clock=True, icon="⚡️📊", time_format=datetime.now().strftime("%I:%M %p %b %d, %Y"))

        # ==========================
        # Defining Application widgets
        # ==========================

        # ==========================
        # Top Bar Section
        # ==========================
        
        # Buttons
        self.ExitButton = Button ("❌", variant="default", id="ExitButton", tooltip ="Exit Application")
        self.RunButton = Button ("✅", variant="default", id="RunButton", disabled=True, tooltip= "Run")
        self.PauseButton = Button ("🫸", variant="default", id="PauseButton", disabled=True, tooltip="Pause (coming soon)")
        self.StopButton = Button ("⏹", variant="default", id="StopButton", disabled=True, tooltip="Stop")
        self.DebugCheckBox = Checkbox ("Debug", id="DebugCheckBox", tooltip="Display debug print messages during the simulation")


        self.TopBarLabel = Label(
            "[b]© 2025 BSPSSEPy | Developed By Ilyas Farhat[/b]\n"
            "📧 [blue][link='mailto:ilyas.farhat@outlook.com']ilyas.farhat@outlook.com[/][/blue]\n"
            "🌍 [green][link='https://github.com/aldahabi27']GitHub: aldahabi27[/][/green]",
            variant="primary",
            id="TopBarLabel"
        )


        # Progress Bar
        self.TopBarProgressBar = ProgressBar(total=100, id="TopBarProgressBar")
        self.TopBarProgressBarLabel = Label("t = 0s", id="TopBarProgressBarLabel")


        # ==========================
        # Main Grid Section
        # ==========================

        # Case Tree
        # Create the main tree with root "Case"
        self.CaseTree = Tree("Case", id="CaseTree")
        self.CaseTree.root.expand()

        # Get the current script's directory and append "Case"
        self.CaseFolderPath = os.path.join(os.getcwd(), "Case")

        # Add the .sav files & subfolders recursively
        if os.path.exists(self.CaseFolderPath):
            AddSavFilesToTree(self.CaseTree.root, self.CaseFolderPath)

        
        # All Tables --> DataTables
        self.ProgressTable = DataTable(id="ProgressTable", zebra_stripes=True, cursor_type="row")
        self.ProgressTableCol = []
        self.AGCTable = DataTable(id="AGCTable", zebra_stripes=True, cursor_type="row")
        self.AGCTableCol = []
        self.GeneratorTable = DataTable(id="GeneratorTable", zebra_stripes=True, cursor_type="row")
        self.GeneratorTableCol = []
        self.LoadTable = DataTable(id="LoadTable", zebra_stripes=True, cursor_type="row")
        self.LoadTableCol = []
        self.BusTable = DataTable(id="BusTable", zebra_stripes=True, cursor_type="row")
        self.BusTableCol = []
        self.BranchTable = DataTable(id="BranchTable", zebra_stripes=True, cursor_type="row")
        self.BranchTableCol = []
        self.TransformerTable = DataTable(id="TransformerTable", zebra_stripes=True, cursor_type="row")
        self.TransformerTableCol = []

        app.ProgressTable.loading = True

        # ==========================
        # Details Text Area
        # ==========================

        # Create a text area for displaying details
        self.DetailsTextArea = TextArea(id="DetailsTextArea",
                                      soft_wrap=True,
                                      read_only=True,
                                      text="BSPSSEPy Application Messages",
                                      show_line_numbers= True,
                                      max_checkpoints=0
                                      )
        self.DetailsTextArea.border_title = "Details"



        # ==========================
        # BSPSSEPy Application Layout
        # ==========================

        # Creating a grid layout for the application
        with Grid(id="AppGrid") as self.AppGrid:

            # Creating a top bar with three sections
            with Horizontal(id="TopBar"):
                with Horizontal(id="TopBarButtonHorizontal"):
                    yield self.ExitButton
                    yield self.RunButton
                    yield self.PauseButton
                    yield self.StopButton
                    yield self.DebugCheckBox

                with Horizontal(id="TopBarLabelHorizontal"):
                    yield self.TopBarLabel
                    
                with Horizontal(id="TopBarProgressBarHorizontal"):
                    yield self.TopBarProgressBarLabel
                    yield self.TopBarProgressBar

            # Main Grid (Scrollable)
            with VerticalScroll(id="MainGrid") as self.MainGrid:  # ✅ MainGrid takes all 5 columns
                with Horizontal(id="CaseTreeProgressTableRow"):
                    # Case Tree Container
                    with Grid(id="CaseTreeContainer") as self.CaseTreeContainerGrid:  # ✅ CaseTree takes 2 columns
                        self.CaseTreeContainerGrid.border_title = "BSPSSEPy Case Explorer"
                        yield self.CaseTree 

                    with Grid(id="ProgressTableContainer") as self.ProgressTableContainerGrid:
                        self.ProgressTableContainerGrid.border_title = "Progress Table"
                        with VerticalScroll():
                            yield self.ProgressTable  # ✅ Empty table added


                with Horizontal(id="AGCGeneratorTablesRow"):
                    # AGC Table Container
                    with Grid(id="AGCTableContainer") as self.AGCTableContainerGrid:
                        self.AGCTableContainerGrid.border_title = "AGC Table"
                        with VerticalScroll():
                            yield self.AGCTable  # ✅ Empty table added


                    # Generator Table Container
                    with Grid(id="GeneratorTableContainer") as self.GeneratorTableContainerGrid:
                        self.GeneratorTableContainerGrid.border_title = "Generator Table"
                        with VerticalScroll():
                            yield self.GeneratorTable  # ✅ Empty table added


                with Horizontal(id="LoadBusTablesRow"):
                    # Load Table Container
                    with Grid(id="LoadTableContainer") as self.LoadTableContainerGrid:
                        self.LoadTableContainerGrid.border_title = "Load Table"
                        with VerticalScroll():
                            yield self.LoadTable  # ✅ Empty table added

                    # Bus Table Container
                    with Grid(id="BusTableContainer") as self.BusTableContainerGrid:
                        self.BusTableContainerGrid.border_title = "Bus Table"
                        with VerticalScroll():
                            yield self.BusTable  # ✅ Empty table added

                with Horizontal(id="BranchTransformerTablesRow"):
                    # Branch Table Container
                    with Grid(id="BranchTableContainer") as self.BranchTableContainerGrid:
                        self.BranchTableContainerGrid.border_title = "Branch Table"
                        with VerticalScroll():
                            yield self.BranchTable  # ✅ Empty table added

                    # Transformer Table Container
                    with Grid(id="TransformerTableContainer") as self.TransformerTableContainerGrid:
                        self.TransformerTableContainerGrid.border_title = "Transformer Table"
                        with VerticalScroll():
                            yield self.TransformerTable  # ✅ Empty table added

            # Details Text Area
            yield self.DetailsTextArea

            
            
            

        

        yield Footer()

        

    def on_mount(self) -> None:
        """Runs when the app starts."""
        self.theme = "textual-light"
        # self.theme = "dracula"

    def on_button_pressed(self, event: Button) -> None:
        """Handles button clicks."""
        if event.button.id == "ExitButton":
            self.exit()

        elif event.button.id == "StopButton":
            self.RunWorker.cancel()
            self.StopButton.disabled = True
            self.CaseTree.disabled = False
            app.DummyRun = False

            # fix the line below for me plz
            if self.CaseTree.cursor_node and str(self.CaseTree.cursor_node.label).lower().endswith(".sav"):
                self.RunButton.disabled = False

            # if str(self.CaseTree.selectednode.label).lower().endswith(".sav"):
            #     self.RunButton.disabled = False
            
            
        elif event.button.id == "RunButton":
            
            
            
            from Functions.BSPSSEPy.App.BSPSSEPyAppRun import RunSimulation
            # Schedule the async function properly
            self.RunWorker = self.run_worker(RunSimulation(self))

            



            

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """
        Handles the event when a tree node (file or folder) is selected.
        Logs the selected item in the DetailsTextArea.
        """
        if event.node.tree.id == "CaseTree":  
            SelectedItem = event.node.label  # Get the selected file/folder name
            
            NewText = f"Selected: {SelectedItem}"


            # Only log the path if the selected item is a .sav file
            if str(SelectedItem).lower().endswith(".sav"):
                # Traverse up the tree to construct the full file path
                FullPathParts = []
                CurrentNode = event.node

                while (CurrentNode is not None) and (str(CurrentNode.label).lower() != "case"):
                    FullPathParts.insert(0, str(CurrentNode.label))  # Insert at the beginning
                    CurrentNode = CurrentNode.parent  # Move up to parent node

                # Construct the correct full file path
                app.SAVFilePath = os.path.join(self.CaseFolderPath, *FullPathParts)
                app.ConfigPath = f"{app.SAVFilePath[:-4]}_Config.py"

                # Update GUI Tables
                from Functions.BSPSSEPy.App.BSPSSEPyAppHelperFunctions import UpdateBSPSSEPyAppGUI
                self.RunWorker = self.run_worker(UpdateBSPSSEPyAppGUI(app=self, ResetTables=True))

                

            else:
                self.RunButton.disabled = True



# Running the application
app = BSPSSEPyApp()

if __name__ == "__main__":
    import sys
    # app.run(log="textual.log", web=True if "--web" in sys.argv else False)
    app.run()

"""Main GUI Application for BSPSSEPy"""

from __future__ import annotations

# Importing standard Python modules
# from functools import partial  # Allows partial function application
# (not used yet)
# from typing import Any  # Used for type hints
from datetime import datetime  # Used to format the date/time manually
# import time  # Used for time-related operations
# import asyncio  # Used for async operations

import os  # Used for file system operations

# Importing core Textual modules
# from textual._on import on  # Used for event handling
# from textual.binding import Binding  # Used for keyboard bindings
# (not yet used)
# from textual.containers import Container, HorizontalScroll
from textual.app import App, ComposeResult  # Base classes for a Textual app
# Layout containers
from textual.containers import Grid, Horizontal, VerticalScroll
from textual.widgets import (  # Importing various UI widgets
    Button,
    # Collapsible,
    DataTable,
    Footer,
    Header,
    # Input,
    Label,
    # ListItem,
    # ListView,
    # MarkdownViewer,
    # OptionList,
    ProgressBar,
    # RadioSet,
    # RichLog,
    # Select,
    # SelectionList,
    # Switch,
    # TabbedContent,
    TextArea,
    Tree,
    # Static,
    Checkbox,
    # Link,
)
# Specialized input field
# from textual.widgets._masked_input import MaskedInput

# Toggle button widget
# from textual.widgets._toggle_button import ToggleButton

# Dropdown options
# from textual.widgets.option_list import Option

# Text selection handling
# from textual.widgets.text_area import Selection

# Importing custom helper functions
from fun.bspssepy.app.app_helper_funs import add_sav_files_to_tree


class BSPSSEPyApp(App[None]):  # Inheriting from the Textual App class
    """
    This class defines the main Textual application.
    It sets up the layout, UI components, and event handling.
    """

    # Defining CSS styling for the application
    CSS_PATH = "./bspssepy_app_css.tcss"

    def __init__(self) -> None:
        """ Initialize the application. """
        super().__init__()
        self.app_name = "BSPSSEPy"
        # self.bspssepy_application = "Main"
        self.bspssepy_application = "Main"
        self.async_print_delay = 0.02
        self.dummy_run = False
        # pylint: disable=import-outside-toplevel
        from fun.bspssepy.meta import VER_NUM, BUILD_NUM

        # Setting the title and subtitle of the application
        self.title = "BSPSSEPy Application"
        self.sub_title = f"Version {VER_NUM} - Build {BUILD_NUM}"

        # top bar elements

        # Buttons
        self.exit_button = None
        self.run_button = None
        self.pause_button = None
        self.stop_button = None
        self.debug_checkbox = None
        self.top_bar_label = None
        self.top_bar_progress_bar = None
        self.top_bar_progress_bar_label = None

        # main grid elements
        self.case_tree = None
        self.case_folder_path = None
        self.progress_table = None
        self.progress_table_col = None
        self.agc_table = None
        self.agc_table_col = None
        self.gen_table = None
        self.gen_table_col = None
        self.load_table = None
        self.load_table_col = None
        self.bus_table = None
        self.bus_table_col = None
        self.brn_table = None
        self.brn_table_col = None
        self.trn_table = None
        self.trn_table_col = None
        self.case_tree_progress_table_row = None
        self.case_tree_container_grid = None
        self.progress_table_container_grid = None
        self.gen_tables_row = None
        self.agc_table_container_grid = None
        self.gen_table_container_grid = None
        self.load_bus_tables_row = None
        self.load_table_container_grid = None
        self.bus_table_container_grid = None
        self.brn_trn_tables_row = None
        self.brn_table_container_grid = None
        self.trn_table_container_grid = None
        self.main_grid = None
        self.details_text_area = None
        self.app_grid = None
        self.bspssepy_worker = None
        self.sav_file_path = None
        self.config_path = None

    def _build_header(self) -> Header:
        """Build the header for the application."""
        return Header(
            show_clock=True,
            icon="⚡️📊",
            time_format=datetime.now().strftime("%I:%M %p %b %d, %Y")
        )

    def _build_top_bar(self) -> Horizontal:
        """Build the top bar for the application."""

        # Buttons
        self.exit_button = Button(
            "❌",
            variant="default",
            id="exit_button",
            tooltip="Exit Application"
        )

        self.run_button = Button(
            "✅",
            variant="default",
            id="run_button",
            disabled=True,
            tooltip="Run"
        )

        self.pause_button = Button(
            "🫸",
            variant="default",
            id="pause_button",
            disabled=True,
            tooltip="Pause (coming soon)"
        )

        self.stop_button = Button(
            "⏹",
            variant="default",
            id="stop_button",
            disabled=True,
            tooltip="Stop"
        )

        self.debug_checkbox = Checkbox(
            "Debug",
            id="debug_checkbox",
            tooltip="Display debug print messages during the simulation"
        )

        self.top_bar_label = Label(
            "[b]© 2025 BSPSSEPy | Developed By Ilyas Farhat[/b]\n"
            "📧 [blue][link='mailto:ilyas.farhat@outlook.com']"
            "ilyas.farhat@outlook.com[/][/blue]\n"
            "🌍 [green][link='https://github.com/aldahabi27']"
            "GitHub: aldahabi27[/][/green]",
            variant="primary",
            id="top_bar_label"
        )

        # Progress Bar
        self.top_bar_progress_bar = ProgressBar(
            total=100,
            id="top_bar_progress_bar"
        )

        self.top_bar_progress_bar_label = Label(
            "t = 0s",
            id="top_bar_progress_bar_label"
        )

        return Horizontal(
            Horizontal(
                self.exit_button,
                self.run_button,
                self.pause_button,
                self.stop_button,
                self.debug_checkbox,
                id="top_bar_button_horizontal"
            ),
            Horizontal(
                self.top_bar_label,
                id="top_bar_label_horizontal"
            ),
            Horizontal(
                self.top_bar_progress_bar_label,
                self.top_bar_progress_bar,
                id="top_bar_progress_bar_horizontal"
            ),
            id="top_bar"
        )

    def _build_main_grid(self) -> VerticalScroll:
        """Build the main grid for the application."""

        # Case Tree
        # Create the main tree with root "Case"
        self.case_tree = Tree("Case", id="case_tree")
        self.case_tree.root.expand()

        # Get the current script's directory and append "Case"
        self.case_folder_path = os.path.join(os.getcwd(), "Case")

        # Add the .sav files & subfolders recursively
        if os.path.exists(self.case_folder_path):
            add_sav_files_to_tree(self.case_tree.root, self.case_folder_path)

        # All Tables --> DataTables
        def create_table(id_str: str) -> DataTable:
            """Create a DataTable with the given ID."""
            return DataTable(
                id=id_str,
                zebra_stripes=True,
                cursor_type="row"
            )

        self.progress_table = create_table("progress_table")
        self.progress_table.loading = True
        self.progress_table_col = []

        self.agc_table = create_table("agc_table")
        self.agc_table_col = []

        self.gen_table = create_table("gen_table")
        self.gen_table_col = []

        self.load_table = create_table("load_table")
        self.load_table_col = []

        self.bus_table = create_table("bus_table")
        self.bus_table_col = []

        self.brn_table = create_table("brn_table")
        self.brn_table_col = []

        self.trn_table = create_table("trn_table")
        self.trn_table_col = []

        # === Container Grids ===
        self.case_tree_container_grid = Grid(
            self.case_tree,
            id="case_tree_container"
        )
        self.case_tree_container_grid.border_title = "BSPSSEPy Case Explorer"

        self.progress_table_container_grid = Grid(
            VerticalScroll(self.progress_table),
            id="progress_table_container"
        )
        self.progress_table_container_grid.border_title = "Progress Table"

        self.agc_table_container_grid = Grid(
            VerticalScroll(self.agc_table),
            id="agc_table_container"
        )
        self.agc_table_container_grid.border_title = "AGC Table"

        self.gen_table_container_grid = Grid(
            VerticalScroll(self.gen_table),
            id="gen_table_container"
        )
        self.gen_table_container_grid.border_title = "Generator Table"

        self.load_table_container_grid = Grid(
            VerticalScroll(self.load_table),
            id="load_table_container"
        )
        self.load_table_container_grid.border_title = "load Table"

        self.bus_table_container_grid = Grid(
            VerticalScroll(self.bus_table),
            id="bus_table_container"
        )
        self.bus_table_container_grid.border_title = "Bus Table"

        self.brn_table_container_grid = Grid(
            VerticalScroll(self.brn_table),
            id="brn_table_container"
        )
        self.brn_table_container_grid.border_title = "Branch Table"

        self.trn_table_container_grid = Grid(
            VerticalScroll(self.trn_table),
            id="trn_table_container"
        )
        self.trn_table_container_grid.border_title = "Transformer Table"

        # === Horizontal Rows ===
        self.case_tree_progress_table_row = Horizontal(
            self.case_tree_container_grid,
            self.progress_table_container_grid,
            id="case_tree_progress_table_row"
        )

        self.gen_tables_row = Horizontal(
            self.agc_table_container_grid,
            self.gen_table_container_grid,
            id="gen_tables_row"
        )

        self.load_bus_tables_row = Horizontal(
            self.load_table_container_grid,
            self.bus_table_container_grid,
            id="load_bus_tables_row"
        )

        self.brn_trn_tables_row = Horizontal(
            self.brn_table_container_grid,
            self.trn_table_container_grid,
            id="brn_trn_tables_row"
        )

        # === Main Grid (VerticalScroll) ===
        self.main_grid = VerticalScroll(
            self.case_tree_progress_table_row,
            self.gen_tables_row,
            self.load_bus_tables_row,
            self.brn_trn_tables_row,
            id="main_grid",
        )
        
        return self.main_grid

    def _build_details_text_area(self) -> TextArea:
        """Build the details text area for the application."""
        # Create a text area for displaying details
        self.details_text_area = TextArea(
            id="details_text_area",
            soft_wrap=True,
            read_only=True,
            text="BSPSSEPy Application Messages",
            show_line_numbers=True,
            max_checkpoints=0
        )
        self.details_text_area.border_title = "Details"

        return self.details_text_area

    def compose(self) -> ComposeResult:
        """
        This method defines the UI components and how they are structured.
        """
        # Header
        yield self._build_header()

        # Main Application Layout
        with Grid(id="app_grid") as self.app_grid:
            yield self._build_top_bar()
            yield self._build_main_grid()
            yield self._build_details_text_area()

        # Footer
        yield Footer()

    def on_mount(self) -> None:
        """Runs when the app starts."""
        self.theme = "textual-light"
        # self.theme = "dracula"

    def on_button_pressed(self, event: Button) -> None:
        """Handles button clicks."""
        if event.button.id == "exit_button":
            self.exit()

        elif event.button.id == "stop_button":
            self.bspssepy_worker.cancel()
            self.stop_button.disabled = True
            self.case_tree.disabled = False
            self.dummy_run = False

            # fix the line below for me plz
            if (
                self.case_tree.cursor_node
                and str(self.case_tree.cursor_node.label)
                    .lower().endswith(".sav")
            ):
                self.run_button.disabled = False

        elif event.button.id == "run_button":
            # pylint: disable=import-outside-toplevel
            from fun.bspssepy.app.bspssepy_app_run import run_simulation
            # Schedule the async function properly
            self.bspssepy_worker = self.run_worker(run_simulation(self))

    def on_tree_node_selected(
        self: BSPSSEPyApp,
        event: Tree.NodeSelected
    ) -> None:
        """
        Handles the event when a tree node (file or folder) is selected.
        Logs the selected item in the details_text_area.
        """
        if event.node.tree.id == "case_tree":
            # Get the selected file/folder name
            selected_item = event.node.label

            # Only log the path if the selected item is a .sav file
            if str(selected_item).lower().endswith(".sav"):
                # Traverse up the tree to construct the full file path
                full_path_parts = []
                current_node = event.node

                while (
                    (current_node is not None)
                    and (str(current_node.label).lower() != "case")
                ):
                    # Insert at the beginning
                    full_path_parts.insert(0, str(current_node.label))
                    # Move up to parent node
                    current_node = current_node.parent

                # Construct the correct full file path
                self.sav_file_path = os.path.join(
                    self.case_folder_path, *full_path_parts)
                self.config_path = f"{self.sav_file_path[:-4]}_Config.py"

                # Update GUI Tables
                # pylint: disable=import-outside-toplevel
                from fun.bspssepy.app.app_helper_funs import (
                    update_bspssepy_app_gui
                )
                self.bspssepy_worker = self.run_worker(
                    update_bspssepy_app_gui(app=self, ResetTables=True)
                )

            else:
                self.run_button.disabled = True


def launch_app():
    """Public method to launch the app (used in __main__.py)."""
    app = BSPSSEPyApp()
    app.run()
# # Running the application
# app = BSPSSEPyApp()

# if __name__ == "__main__":
#     import sys
#     # app.run(log="textual.log", web=True if "--web" in sys.argv else False)
#     app.run()

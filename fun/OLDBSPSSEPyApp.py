import random
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Static, Header, Footer
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual import on
from textual.timer import Timer

class BSPSSEPyApp(App):
    CSS_PATH = "BSPSSEPyApp.tcss"
    BINDINGS = [("q", "quit", "Quit")]

    current_time = reactive(0)
    progress_percentage = reactive(0)
    control_sequence_index = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Static("Case Name: Simulation Case", id="case-name"),
            Static("Case Version: 0.4", id="case-version"),
            Static(id="progress-bar"),
            DataTable(id="control-sequence-table"),
            DataTable(id="acc-table"),
            DataTable(id="generators-live-measurements"),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "BSPSSEPvV0.4 Dashboard"
        self.sub_title = "Dynamic Simulation Dashboard"

        control_table = self.query_one("#control-sequence-table", DataTable)
        acc_table = self.query_one("#acc-table", DataTable)
        gen_table = self.query_one("#generators-live-measurements", DataTable)

        control_table.add_columns("Progress", "Control Sequence", "Device Type", "Identification Type", "Identification Value", "Action Type", "Action Time", "Action Status")
        acc_table.add_columns("Alpha", "Delta P_G")
        gen_table.add_columns("Delta f", "Pe", "Pm", "Qe", "Gref")

        self.populate_tables()
        self.update_timer = self.set_interval(2, self.update_data)

    def populate_tables(self):
        control_table = self.query_one("#control-sequence-table", DataTable)
        acc_table = self.query_one("#acc-table", DataTable)
        gen_table = self.query_one("#generators-live-measurements", DataTable)

        for i in range(1, 20):
            control_table.add_row("✓" if i < 5 else "", str(i), "TRN" if i % 2 == 0 else "BRN", "Name", f"TWTF{i}" if i % 2 == 0 else f"BRN{i}", "ON", f"{i}.0", "2" if i < 5 else "1")

        for i in range(1, 4):
            acc_table.add_row(f"GEN{i}", f"{random.uniform(0.5, 1.5):.2f}")

        for i in range(1, 4):
            gen_table.add_row(f"GEN{i}", f"{random.uniform(0.5, 1.5):.2f}", f"{random.uniform(0.5, 1.5):.2f}", f"{random.uniform(0.5, 1.5):.2f}", f"{random.uniform(0.5, 1.5):.2f}")

    def update_data(self):
        self.current_time += 1
        self.progress_percentage = (self.current_time / 60) * 100

        if self.current_time % 10 == 0:
            self.control_sequence_index += 1

        progress_bar = self.query_one("#progress-bar", Static)
        progress_bar.update(f"Progress: {self.progress_percentage:.2f}% | Time: {self.current_time}s")

        gen_table = self.query_one("#generators-live-measurements", DataTable)
        if gen_table.row_count > 0:
            for row in range(gen_table.row_count):
                gen_table.update_cell(row, 0, f"{random.uniform(0.5, 1.5):.2f}")
                gen_table.update_cell(row, 1, f"{random.uniform(0.5, 1.5):.2f}")
                gen_table.update_cell(row, 2, f"{random.uniform(0.5, 1.5):.2f}")
                gen_table.update_cell(row, 3, f"{random.uniform(0.5, 1.5):.2f}")

        if self.current_time >= 60:
            self.update_timer.pause()

# if __name__ == "__main__":
#     app = Dashboard()
#     app.run()
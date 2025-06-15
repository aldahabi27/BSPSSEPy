from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.columns import Columns
import time
import random



def generate_generators_data():
    """Simulates generator updates."""
    return [
        ["Gen A", f"{random.uniform(49.8, 50.2):.2f} Hz", f"{random.randint(0, 1)}"],
        ["Gen B", f"{random.uniform(49.8, 50.2):.2f} Hz", f"{random.randint(0, 1)}"],
        ["Gen C", f"{random.uniform(49.8, 50.2):.2f} Hz", f"{random.randint(0, 1)}"]
    ]

def generate_buses_data():
    """Simulates bus frequency updates."""
    return [
        ["Bus 1", f"{random.uniform(49.8, 50.2):.2f} Hz"],
        ["Bus 2", f"{random.uniform(49.8, 50.2):.2f} Hz"],
        ["Bus 3", f"{random.uniform(49.8, 50.2):.2f} Hz"]
    ]

def generate_loads_data():
    """Simulates load updates."""
    return [
        ["load 1", f"{random.randint(10, 100)} MW"],
        ["load 2", f"{random.randint(10, 100)} MW"],
        ["load 3", f"{random.randint(10, 100)} MW"]
    ]

def make_table(title, headers, data):
    """Creates a table with a title."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    for header in headers:
        table.add_column(header, style="cyan", justify="left")
    
    for row in data:
        table.add_row(*row)
    
    return table

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.layout import Layout
from rich.align import Align
import time

def CreateHeaderSection(SimTime, ProgressValue):
    """
    Creates the top section of the dashboard, including:
    - Left (2/3 width): Program info (Name, Case Name, Version, Date/Time)
    - Right (1/3 width): Progress Bar, current simulation time, and % progress.
    """
    # Left Side: Program Details (Fixed formatting issues)
    ProgramInfo = (
        "[bold cyan]BSPSSEPy v0.3[/bold cyan]\n"
        "[bold]Case Name: [/bold]ExampleCase\n"
        "[bold]Version: [/bold]1.0\n"
        f"[bold]DateTime: [/bold]{time.strftime('%Y-%m-%d %H:%M:%S')}"  # ✅ Fixed
    )

    # Right Side: Progress Bar + Simulation Time
    RightSection = f"[bold]t = {SimTime}s[/bold]".ljust(20) + f"[bold magenta]{ProgressValue:.1f}%[/bold magenta]".rjust(10)

    # Layouts for alignment
    LeftPanel = Panel(ProgramInfo, title="[bold blue]Simulation Info[/bold blue]", border_style="blue", expand=True)
    RightPanel = Panel(Align.right(RightSection), title="[bold green]Progress[/bold green]", border_style="green", expand=True)

    return LeftPanel, RightPanel


def CreateMainDashboard(SimTime, ProgressValue):
    """
    Assembles the entire dashboard layout inside a bordered box.
    - Uses `rich.layout.Layout` for precise control.
    - Contains a header and three tables.
    """
    LayoutMain = Layout()
    
    # Top Section: Header with 2/3 and 1/3 Split
    LeftHeader, RightHeader = CreateHeaderSection(SimTime, ProgressValue)
    HeaderLayout = Layout(name="Header", size=5)
    HeaderLayout.split_row(
        Layout(LeftHeader, ratio=2),  # 2/3 width
        Layout(RightHeader, ratio=1)  # 1/3 width
    )

    # Placeholder for Tables (will replace later)
    TablesLayout = Layout(name="Tables")
    TablesLayout.split_row(
        Layout(Panel("Control Sequence Table", title="[bold red]Control Sequences[/bold red]", border_style="red"), ratio=1),
        Layout(Panel("AGC Table", title="[bold yellow]AGC[/bold yellow]", border_style="yellow"), ratio=1),
        Layout(Panel("Generator Measurements", title="[bold cyan]Generator Data[/bold cyan]", border_style="cyan"), ratio=1),
    )

    # Combine Everything into a Bordered Box
    LayoutMain.split_column(
        HeaderLayout,
        TablesLayout
    )

    return Panel(LayoutMain, title="[bold magenta]BSPSSEPy Live Dashboard[/bold magenta]", border_style="bold magenta")


# Initialize Console
ConsoleMain = Console()

try:
    for i in range(10):
        time.sleep(1)
        SimTime = i * 5  
        ProgressPercent = (i / 10) * 100

        ConsoleMain.clear()

        # Debug Step: Capture the output
        DashboardPanel = CreateMainDashboard(SimTime, ProgressPercent)

        # print("=== DEBUG: Dashboard Output ===")
        # print(DashboardPanel)  # Shows raw panel object (before rendering)
        # print("==============================")

        # Now try printing the panel (where the error happens)
        ConsoleMain.print(DashboardPanel)

except Exception as e:
    print("\n[ERROR] Issue in Rich Markup Formatting!")
    print(f"Exception Type: {type(e).__name__}")
    print(f"Error Message: {e}")


def BSPSSEPyLiveMonitor(iterations=None):
    """ 
    Live Monitoring Console for BSPSSEPy: Displays real-time Generator, Bus, and load status in a table format.
    
    This function continuously updates and displays:
    - Generator Frequencies & Status
    - Bus Frequencies
    - load Power Consumption
    
    Uses `rich` library to present tables **side by side** with live updates.
    
    Parameters:
        iterations (int, optional): Number of updates before stopping. If `None`, runs indefinitely.

    Refresh Rate: 2 updates per second.
    """
    console = Console()
    iterations = 5
    with Live(refresh_per_second=2) as live:
        count = 0
        while iterations is None or count < iterations:
            time.sleep(1)
            
            # Create three tables
            gen_table = make_table("Generators", ["Generator", "Frequency", "Status"], generate_generators_data())
            bus_table = make_table("Buses", ["Bus", "Frequency"], generate_buses_data())
            load_table = make_table("Loads", ["load", "Power"], generate_loads_data())

            # Combine tables side by side
            live.update(Columns([gen_table, bus_table, load_table]))

            count += 1
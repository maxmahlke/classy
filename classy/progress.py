"""Implement classy progress bars."""
from rich import progress

# Progress bar for MofN task counting
mofn = progress.Progress(
    progress.TextColumn("{task.description}", justify="right"),
    progress.BarColumn(bar_width=None),
    progress.MofNCompleteColumn(),
    disable=False,
)

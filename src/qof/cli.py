# Libraries
import typer
from rich.console import Console
from rich.panel import Panel

import os
import shutil
import pathlib
from typing import List

# App
app = typer.Typer()
console = Console()

# Functions
def error_msg(msg: str):
    console.print(
        Panel.fit(
            msg,
            title="Error",
            title_align="left",
            border_style="red"
        )
    )
    raise typer.Exit()

def success_msg(msg: str):
    console.print(
        Panel.fit(
            msg,
            title="Success",
            title_align="left",
            border_style="green"
        )
    )

# Commands
@app.command()
def organize(
    folders: List[str] = typer.Option(..., "--folder", help="List of folder names"),
    exts: List[str] = typer.Option(..., "--ext", help="List of exts to organize")
):
    if len(folders) == len(exts):
        for index, folder in enumerate(folders):
            cwd = pathlib.Path.cwd()

            # Create folder
            try:
                folder_path = cwd / folder
                os.makedirs(folder_path, exist_ok=True)
            except Exception as error:
                error_msg(error)

            # Move Files
            try:
                for filename in os.listdir(cwd):
                    file_path = os.path.join(cwd, filename)

                    if os.path.isfile(file_path) and filename.endswith(f".{exts[index]}"):
                        shutil.move(file_path, folder_path)
            except Exception as error:
                error_msg(error)

        success_msg("Successfully organized your files!")        
    else:
        error_msg("Both arguments must be lists of the same length.")

if __name__ == "__main__":
    app()
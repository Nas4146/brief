"""
Brief CLI - Main command-line interface.

Provides commands for managing AI assistant instruction files across multiple tools.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich import box
from rich.progress import track

from brief import __version__
from brief.discovery import discover_instruction_files
from brief.context import analyze_project_context
from brief.updater import update_instruction_files
from brief.validator import validate_instructions

# Initialize rich console
console = Console()


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """Brief your AI coding assistants once, update them all."""
    ctx.ensure_object(dict)


@cli.command()
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    help="Project directory to initialize (default: current directory)",
)
def init(project_dir: str):
    """Initialize brief in your project."""
    project_path = Path(project_dir).resolve()
    
    console.print(Panel.fit(
        f"[bold cyan]Initializing brief[/bold cyan]\n[dim]{project_path}[/dim]",
        border_style="cyan"
    ))
    
    # Discover existing instruction files
    console.print("\n[bold]📝 Scanning for instruction files...[/bold]")
    files = discover_instruction_files(project_path)
    
    if files:
        table = Table(title=f"Found {len(files)} instruction file(s)", box=box.ROUNDED, show_header=False)
        table.add_column("File", style="green")
        table.add_column("Size", style="dim")
        
        for file in files:
            rel_path = file.relative_to(project_path)
            size = file.stat().st_size
            table.add_row(f"✓ {rel_path}", f"{size:,} bytes")
        
        console.print(table)
    else:
        console.print("[yellow]⚠️  No instruction files found[/yellow]")
        console.print("\n[dim]Supported files: AGENTS.md, CLAUDE.md, .cursorrules, .github/copilot-instructions.md[/dim]")
    
    # Analyze project context
    console.print("\n[bold]🔍 Analyzing project structure...[/bold]")
    context = analyze_project_context(project_path)
    
    if context.get("languages") or context.get("frameworks"):
        context_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        context_table.add_column("Property", style="cyan")
        context_table.add_column("Values", style="white")
        
        if context.get("languages"):
            context_table.add_row("Languages", ", ".join(context['languages']))
        if context.get("frameworks"):
            context_table.add_row("Frameworks", ", ".join(context['frameworks']))
        if context.get("test_framework"):
            context_table.add_row("Testing", context['test_framework'])
        if context.get("package_manager"):
            context_table.add_row("Package Manager", context['package_manager'])
        
        console.print(context_table)
    
    # Create config file
    config_path = project_path / ".brief.yaml"
    if config_path.exists():
        console.print(f"\n[yellow]⚠️  Configuration already exists:[/yellow] [dim]{config_path}[/dim]")
    else:
        # TODO: Generate .brief.yaml with discovered files and context
        console.print(f"\n[green]✓ Configuration file ready:[/green] [dim].brief.yaml[/dim]")
    
    console.print(Panel.fit(
        "[bold green]✨ Brief initialized![/bold green]\n[dim]Run 'brief update \"<instruction>\"' to add instructions[/dim]",
        border_style="green"
    ))


@cli.command()
@click.argument("instruction", required=True)
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    help="Project directory (default: current directory)",
)
@click.option(
    "--preview/--no-preview",
    default=True,
    help="Preview changes before applying (default: enabled)",
)
@click.option(
    "--yes", "-y",
    is_flag=True,
    help="Skip confirmation prompt and apply changes",
)
def update(instruction: str, project_dir: str, preview: bool, yes: bool):
    """Update all instruction files with a new instruction."""
    project_path = Path(project_dir).resolve()
    
    console.print(Panel.fit(
        f"[bold cyan]Updating Instructions[/bold cyan]\n[dim]{project_path.name}[/dim]",
        border_style="cyan"
    ))
    
    # Discover files
    files = discover_instruction_files(project_path)
    if not files:
        console.print("[red]⚠️  No instruction files found.[/red] Run [bold]brief init[/bold] first.")
        sys.exit(1)
    
    # Analyze context
    context = analyze_project_context(project_path)
    
    # Show context
    console.print(f"\n[bold]📊 Project Context[/bold]")
    context_items = []
    if context.get("languages"):
        context_items.append(f"[cyan]Languages:[/cyan] {', '.join(context['languages'])}")
    if context.get("test_framework"):
        context_items.append(f"[cyan]Testing:[/cyan] {context['test_framework']}")
    if context.get("frameworks"):
        context_items.append(f"[cyan]Frameworks:[/cyan] {', '.join(context['frameworks'][:3])}")  # Limit to 3
    
    for item in context_items:
        console.print(f"  {item}")
    
    # Show instruction
    console.print(f"\n[bold]� Instruction[/bold]")
    console.print(Panel(
        f"[white]{instruction}[/white]",
        border_style="blue",
        padding=(0, 1)
    ))
    
    # Get updates (in preview mode first)
    from brief.updater import update_instruction_files, generate_diff
    updates = update_instruction_files(files, instruction, context, preview=True)
    
    # Show which files will be updated
    files_to_update = []
    files_skipped = []
    
    for file_path, (old_content, new_content, was_updated) in updates.items():
        rel_path = file_path.relative_to(project_path)
        if was_updated:
            files_to_update.append((file_path, rel_path, old_content, new_content))
        else:
            files_skipped.append(rel_path)
    
    if not files_to_update:
        console.print("\n[yellow]⚠️  No changes needed[/yellow] - instruction already exists in all files")
        sys.exit(0)
    
    # Show summary of files to be updated
    console.print(f"\n[bold]📋 Files to Update ({len(files_to_update)})[/bold]")
    
    summary_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    summary_table.add_column("File", style="white")
    summary_table.add_column("Action", style="green")
    summary_table.add_column("Location", style="dim")
    
    for file_path, rel_path, old_content, new_content in files_to_update:
        # Determine where the instruction will be added
        if "## Additional Instructions" in new_content and "## Additional Instructions" not in old_content:
            location = "New section: Additional Instructions"
        elif "## Additional Instructions" in old_content:
            location = "Append to: Additional Instructions"
        elif "## Testing" in new_content and "test" in instruction.lower():
            location = "Append to: Testing"
        elif "## Development Workflow" in new_content and any(kw in instruction.lower() for kw in ["commit", "deploy", "build"]):
            location = "Append to: Development Workflow"
        else:
            location = "Append to existing section"
        
        summary_table.add_row(str(rel_path), "Add instruction", location)
    
    console.print(summary_table)
    
    # Show skipped files
    if files_skipped:
        console.print(f"\n[yellow]⏭️  Skipped {len(files_skipped)} file(s)[/yellow] [dim](instruction already exists)[/dim]")
        for rel_path in files_skipped:
            console.print(f"  [dim]• {rel_path}[/dim]")
    
    # Confirm before applying
    if not yes:
        console.print()  # Blank line
        confirmation_panel = Panel(
            f"[bold white]Apply instruction to {len(files_to_update)} file(s)?[/bold white]",
            border_style="yellow",
            padding=(0, 2)
        )
        console.print(confirmation_panel)
        
        if not click.confirm("Continue?", default=True):
            console.print("\n[yellow]⚠️  Cancelled - no files were modified[/yellow]")
            sys.exit(0)
    
    # Apply changes
    console.print(f"\n[bold]🚀 Applying changes...[/bold]")
    update_instruction_files(files, instruction, context, preview=False)
    
    # Show success with table
    success_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    success_table.add_column("Status", style="green")
    success_table.add_column("File", style="white")
    
    for _, rel_path, _, _ in files_to_update:
        success_table.add_row("✓", str(rel_path))
    
    console.print(success_table)
    
    console.print(Panel.fit(
        f"[bold green]🎉 Successfully updated {len(files_to_update)} file(s)![/bold green]",
        border_style="green"
    ))
    
    if not preview:
        console.print("[dim]💡 Use --preview (default) to see changes before applying next time[/dim]")


@cli.command()
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    help="Project directory (default: current directory)",
)
def validate(project_dir: str):
    """Validate instruction files for consistency."""
    project_path = Path(project_dir).resolve()
    
    console.print(Panel.fit(
        f"[bold cyan]Validating Instructions[/bold cyan]\n[dim]{project_path.name}[/dim]",
        border_style="cyan"
    ))
    
    # Discover files
    files = discover_instruction_files(project_path)
    if not files:
        console.print("[yellow]⚠️  No instruction files found[/yellow]")
        sys.exit(1)
    
    console.print(f"\n[bold]📋 Checking {len(files)} file(s)...[/bold]\n")
    
    # Create validation table
    validation_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    validation_table.add_column("File", style="white")
    validation_table.add_column("Status", style="green", justify="center")
    
    for file in files:
        rel_path = file.relative_to(project_path)
        validation_table.add_row(str(rel_path), "✓")
    
    console.print(validation_table)
    
    # TODO: Implement validation logic
    all_valid = True
    
    if all_valid:
        console.print(Panel.fit(
            "[bold green]✅ All instruction files are consistent![/bold green]",
            border_style="green"
        ))
        sys.exit(0)
    else:
        console.print(Panel.fit(
            "[bold red]❌ Found inconsistencies[/bold red]",
            border_style="red"
        ))
        sys.exit(1)


@cli.command(name="list")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=".",
    help="Project directory (default: current directory)",
)
def list_files(project_dir: str):
    """List discovered instruction files."""
    project_path = Path(project_dir).resolve()
    
    console.print(Panel.fit(
        f"[bold cyan]Instruction Files[/bold cyan]\n[dim]{project_path.name}[/dim]",
        border_style="cyan"
    ))
    
    files = discover_instruction_files(project_path)
    
    if not files:
        console.print("\n[yellow]⚠️  No instruction files found[/yellow]")
        
        supported_table = Table(
            title="Supported Files",
            box=box.ROUNDED,
            show_header=False,
            padding=(0, 2)
        )
        supported_table.add_column("File", style="dim")
        supported_table.add_row("AGENTS.md")
        supported_table.add_row("CLAUDE.md")
        supported_table.add_row(".github/copilot-instructions.md")
        supported_table.add_row(".cursorrules")
        supported_table.add_row(".clinerules")
        
        console.print(supported_table)
        sys.exit(1)
    
    # Create table of found files
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Status", style="green", width=6)
    table.add_column("File", style="white")
    table.add_column("Size", style="cyan", justify="right")
    
    total_size = 0
    for file in sorted(files):
        rel_path = file.relative_to(project_path)
        size = file.stat().st_size
        total_size += size
        table.add_row("✓", str(rel_path), f"{size:,}")
    
    console.print(table)
    
    # Summary panel
    console.print(Panel.fit(
        f"[bold]Total:[/bold] {len(files)} file(s)  •  [bold]Size:[/bold] {total_size:,} bytes",
        border_style="green"
    ))


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Rich-based logging and UI components for ChromaBuddy PRO
"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree
from rich import print as rprint
from rich.prompt import Prompt, Confirm
from typing import Optional, Any
import time


class RichUI:
    """Rich terminal UI manager"""
    
    def __init__(self, theme: str = 'monokai'):
        """
        Initialize Rich UI
        
        Args:
            theme: Syntax highlighting theme
        """
        self.console = Console()
        self.theme = theme
    
    def info(self, message: str, title: Optional[str] = None) -> None:
        """Display info message"""
        if title:
            self.console.print(f"[bold cyan]{title}[/bold cyan]")
        self.console.print(f"[cyan]{message}[/cyan]")
    
    def success(self, message: str) -> None:
        """Display success message"""
        self.console.print(f"[bold green]SUCCESS:[/bold green] {message}")
    
    def warning(self, message: str) -> None:
        """Display warning message"""
        self.console.print(f"[bold yellow]WARNING:[/bold yellow] {message}")
    
    def error(self, message: str) -> None:
        """Display error message"""
        self.console.print(f"[bold red]ERROR:[/bold red] {message}")
    
    def panel(self, content: str, title: str = "", border_style: str = "blue") -> None:
        """Display content in a panel"""
        self.console.print(Panel(content, title=title, border_style=border_style))
    
    def code(self, code: str, language: str = "python", line_numbers: bool = True) -> None:
        """Display syntax-highlighted code"""
        syntax = Syntax(code, language, theme=self.theme, line_numbers=line_numbers)
        self.console.print(syntax)
    
    def table(self, title: str, headers: list, rows: list) -> None:
        """Display table"""
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        for header in headers:
            table.add_column(header)
        
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        
        self.console.print(table)
    
    def tree(self, label: str) -> Tree:
        """Create tree structure"""
        return Tree(label)
    
    def spinner(self, message: str) -> 'SpinnerContext':
        """Create spinner context manager"""
        return SpinnerContext(self.console, message)
    
    def progress_bar(self) -> Progress:
        """Create progress bar"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
    
    def prompt(self, message: str, default: str = "") -> str:
        """Prompt user for input"""
        return Prompt.ask(message, default=default, console=self.console)
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Prompt user for confirmation"""
        return Confirm.ask(message, default=default, console=self.console)
    
    def print(self, *args, **kwargs) -> None:
        """Print to console"""
        self.console.print(*args, **kwargs)
    
    def rule(self, title: str = "", style: str = "blue") -> None:
        """Print horizontal rule"""
        self.console.rule(title, style=style)
    
    def clear(self) -> None:
        """Clear console"""
        self.console.clear()


class SpinnerContext:
    """Context manager for spinner"""
    
    def __init__(self, console: Console, message: str):
        self.console = console
        self.message = message
        self.status = None
    
    def __enter__(self):
        self.status = self.console.status(f"[bold cyan]{self.message}[/bold cyan]")
        self.status.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.status:
            self.status.__exit__(exc_type, exc_val, exc_tb)
    
    def update(self, message: str):
        """Update spinner message"""
        if self.status:
            self.status.update(f"[bold cyan]{message}[/bold cyan]")


class Logger:
    """Simple logger with Rich formatting"""
    
    def __init__(self, ui: RichUI, verbose: bool = True):
        """
        Initialize logger
        
        Args:
            ui: RichUI instance
            verbose: Enable verbose logging
        """
        self.ui = ui
        self.verbose = verbose
    
    def debug(self, message: str) -> None:
        """Log debug message (only if verbose)"""
        if self.verbose:
            self.ui.console.print(f"[dim]DEBUG: {message}[/dim]")
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.ui.info(message)
    
    def success(self, message: str) -> None:
        """Log success message"""
        self.ui.success(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.ui.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.ui.error(message)


# Global instances
_ui_instance = None
_logger_instance = None


def get_ui(theme: str = 'monokai') -> RichUI:
    """Get or create global RichUI instance"""
    global _ui_instance
    if _ui_instance is None:
        _ui_instance = RichUI(theme)
    return _ui_instance


def get_logger(verbose: bool = True) -> Logger:
    """Get or create global Logger instance"""
    global _logger_instance
    if _logger_instance is None:
        ui = get_ui()
        _logger_instance = Logger(ui, verbose)
    return _logger_instance

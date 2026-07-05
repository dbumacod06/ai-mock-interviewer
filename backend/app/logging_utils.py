import logging
import sys
from datetime import datetime
from typing import Any

# ANSI color codes
COLORS = {
    "DEBUG": "\033[36m",      # Cyan
    "INFO": "\033[32m",       # Green
    "WARNING": "\033[33m",    # Yellow
    "ERROR": "\033[31m",     # Red
    "CRITICAL": "\033[35m",   # Magenta
    "RESET": "\033[0m",      # Reset
    "BOLD": "\033[1m",       # Bold
    "DIM": "\033[2m",        # Dim
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console."""

    def format(self, record: logging.LogRecord) -> str:
        # Get color for level
        level_color = COLORS.get(record.levelname, COLORS["RESET"])
        reset = COLORS["RESET"]
        bold = COLORS["BOLD"]
        dim = COLORS["DIM"]

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Format the log message
        log_message = f"{dim}{timestamp}{reset} | {level_color}{bold}{record.levelname:8}{reset} | {bold}{record.name:30}{reset} | {record.getMessage()}"

        return log_message


class MethodLogger:
    """Utility for logging method entry and exit."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def enter(self, method_name: str, **kwargs: Any) -> None:
        """Log method entry with formatted dynamic string."""
        if kwargs:
            params = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            self.logger.info(f"→ ENTER {method_name} | {params}")
        else:
            self.logger.info(f"→ ENTER {method_name}")

    def exit(self, method_name: str, result: Any = None) -> None:
        """Log method exit with optional result."""
        if result is not None:
            self.logger.info(f"← EXIT  {method_name} | result={result!r}")
        else:
            self.logger.info(f"← EXIT  {method_name}")

    def agent_invoked(self, agent_name: str, prompt: str) -> None:
        """Log when an agent is invoked."""
        self.logger.info(f"🤖 AGENT INVOKED: {agent_name} | prompt={prompt!r}")

    def agent_used(self, agent_name: str, response: str) -> None:
        """Log when an agent is used/completed."""
        self.logger.info(f"✅ AGENT USED: {agent_name} | response={response!r}")

    def tool_used(self, tool_name: str, **kwargs: Any) -> None:
        """Log when a tool is used."""
        if kwargs:
            params = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            self.logger.info(f"🔧 TOOL USED: {tool_name} | {params}")
        else:
            self.logger.info(f"🔧 TOOL USED: {tool_name}")

    def dynamic_string(self, message: str, **kwargs: Any) -> None:
        """Log a formatted dynamic string."""
        formatted = message.format(**kwargs)
        self.logger.info(f"📝 {formatted}")


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the colored formatter."""
    logger = logging.getLogger(name)
    
    # Only add handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def get_method_logger(name: str) -> MethodLogger:
    """Get a MethodLogger instance for the given module name."""
    logger = get_logger(name)
    return MethodLogger(logger)

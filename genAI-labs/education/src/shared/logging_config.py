"""
Logging configuration for the AWS GenAI Learning Platform.
"""

import logging
import sys
from typing import Optional
import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None
) -> None:
    """
    Setup logging configuration for the learning platform.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Log format type (json, text)
        log_file: Optional log file path
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if format_type == "json" else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if format_type == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_agent_loggers()
    
    logging.info(f"Logging configured with level: {level}, format: {format_type}")


def configure_agent_loggers():
    """Configure loggers for specific agent components."""
    
    # Agent loggers
    agent_logger = logging.getLogger("agent")
    agent_logger.setLevel(logging.INFO)
    
    # Module loggers
    module_logger = logging.getLogger("module")
    module_logger.setLevel(logging.INFO)
    
    # API loggers
    api_logger = logging.getLogger("api")
    api_logger.setLevel(logging.INFO)
    
    # AWS client loggers
    aws_logger = logging.getLogger("boto3")
    aws_logger.setLevel(logging.WARNING)
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class LearningPlatformLogger:
    """Custom logger for the learning platform."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def log_exercise_execution(self, module_name: str, exercise_id: str, user_id: str, success: bool):
        """Log exercise execution."""
        self.logger.info(
            "Exercise executed",
            module_name=module_name,
            exercise_id=exercise_id,
            user_id=user_id,
            success=success
        )
    
    def log_agent_interaction(self, agent_name: str, user_id: str, message_type: str, success: bool):
        """Log agent interaction."""
        self.logger.info(
            "Agent interaction",
            agent_name=agent_name,
            user_id=user_id,
            message_type=message_type,
            success=success
        )
    
    def log_workflow_execution(self, workflow_id: str, status: str, duration: float):
        """Log workflow execution."""
        self.logger.info(
            "Workflow executed",
            workflow_id=workflow_id,
            status=status,
            duration=duration
        )

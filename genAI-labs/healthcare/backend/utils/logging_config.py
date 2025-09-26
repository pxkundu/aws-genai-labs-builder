"""
Healthcare ChatGPT Clone - Logging Configuration
This module sets up structured logging for the healthcare application.
"""

import logging
import logging.config
import sys
from pathlib import Path
import structlog
from datetime import datetime

from config.settings import get_settings

settings = get_settings()


def setup_logging():
    """Set up structured logging for the application."""
    
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
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": structlog.dev.ConsoleRenderer(colors=False),
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "standard",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/healthcare-chatgpt.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/healthcare-chatgpt-errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "audit_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/healthcare-chatgpt-audit.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "healthcare": {  # Application logger
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "audit": {  # Audit logger
                "handlers": ["audit_file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn": {  # Uvicorn logger
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {  # Uvicorn access logger
                "handlers": ["file"],
                "level": "INFO",
                "propagate": False
            },
            "sqlalchemy": {  # SQLAlchemy logger
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            },
            "boto3": {  # Boto3 logger
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            },
            "botocore": {  # Botocore logger
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            }
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Set up audit logger
    audit_logger = structlog.get_logger("audit")
    
    # Log application startup
    logger = logging.getLogger(__name__)
    logger.info(f"Healthcare ChatGPT Clone starting up in {settings.ENVIRONMENT} mode")
    logger.info(f"Log level set to {settings.LOG_LEVEL}")
    
    return audit_logger


def get_audit_logger():
    """Get the audit logger for security and compliance logging."""
    return structlog.get_logger("audit")


def log_user_action(user_id: str, action: str, resource: str, details: dict = None):
    """Log user actions for audit purposes."""
    audit_logger = get_audit_logger()
    audit_logger.info(
        "user_action",
        user_id=user_id,
        action=action,
        resource=resource,
        details=details or {},
        timestamp=datetime.utcnow().isoformat()
    )


def log_system_event(event_type: str, message: str, details: dict = None):
    """Log system events for monitoring."""
    audit_logger = get_audit_logger()
    audit_logger.info(
        "system_event",
        event_type=event_type,
        message=message,
        details=details or {},
        timestamp=datetime.utcnow().isoformat()
    )


def log_security_event(event_type: str, message: str, severity: str = "medium", details: dict = None):
    """Log security events for monitoring and compliance."""
    audit_logger = get_audit_logger()
    audit_logger.warning(
        "security_event",
        event_type=event_type,
        message=message,
        severity=severity,
        details=details or {},
        timestamp=datetime.utcnow().isoformat()
    )


def log_performance_metric(metric_name: str, value: float, unit: str = None, details: dict = None):
    """Log performance metrics for monitoring."""
    audit_logger = get_audit_logger()
    audit_logger.info(
        "performance_metric",
        metric_name=metric_name,
        value=value,
        unit=unit,
        details=details or {},
        timestamp=datetime.utcnow().isoformat()
    )


def log_healthcare_interaction(
    user_id: str,
    interaction_type: str,
    patient_info: dict = None,
    medical_content: str = None,
    details: dict = None
):
    """Log healthcare-specific interactions for compliance."""
    audit_logger = get_audit_logger()
    
    # Ensure patient info is properly handled for HIPAA compliance
    safe_patient_info = {}
    if patient_info:
        # Only log non-PHI information
        safe_patient_info = {
            "age_group": patient_info.get("age_group"),
            "department": patient_info.get("department"),
            "interaction_type": interaction_type
        }
    
    audit_logger.info(
        "healthcare_interaction",
        user_id=user_id,
        interaction_type=interaction_type,
        patient_info=safe_patient_info,
        has_medical_content=bool(medical_content),
        details=details or {},
        timestamp=datetime.utcnow().isoformat()
    )

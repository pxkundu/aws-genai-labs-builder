"""
Healthcare ChatGPT Clone - Input Validators
This module provides input validation functions for healthcare data.
"""

import re
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import phonenumbers
from email_validator import validate_email, EmailNotValidError

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_chat_input(message: str) -> bool:
    """
    Validate chat message input.
    
    Args:
        message: The chat message to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    if not message or not isinstance(message, str):
        raise ValidationError("Message cannot be empty")
    
    if len(message.strip()) == 0:
        raise ValidationError("Message cannot be empty")
    
    if len(message) > 4000:
        raise ValidationError("Message is too long (maximum 4000 characters)")
    
    # Check for potentially harmful content
    if _contains_malicious_content(message):
        raise ValidationError("Message contains potentially harmful content")
    
    return True


def validate_email_address(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    if not email or not isinstance(email, str):
        raise ValidationError("Email address is required")
    
    try:
        validate_email(email)
        return True
    except EmailNotValidError as e:
        raise ValidationError(f"Invalid email address: {str(e)}")


def validate_phone_number(phone: str, country_code: str = "US") -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        country_code: Country code for validation
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    if not phone or not isinstance(phone, str):
        raise ValidationError("Phone number is required")
    
    try:
        parsed_number = phonenumbers.parse(phone, country_code)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError("Invalid phone number")
        return True
    except phonenumbers.NumberParseException as e:
        raise ValidationError(f"Invalid phone number format: {str(e)}")


def validate_user_id(user_id: str) -> bool:
    """
    Validate user ID format.
    
    Args:
        user_id: User ID to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID is required")
    
    if len(user_id) < 3 or len(user_id) > 50:
        raise ValidationError("User ID must be between 3 and 50 characters")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise ValidationError("User ID can only contain letters, numbers, underscores, and hyphens")
    
    return True


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format (UUID).
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    if not session_id or not isinstance(session_id, str):
        raise ValidationError("Session ID is required")
    
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, session_id, re.IGNORECASE):
        raise ValidationError("Invalid session ID format")
    
    return True


def validate_healthcare_data(data: Dict[str, Any]) -> bool:
    """
    Validate healthcare-specific data.
    
    Args:
        data: Healthcare data to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValidationError("Healthcare data must be a dictionary")
    
    # Validate age if present
    if "age" in data:
        age = data["age"]
        if not isinstance(age, int) or age < 0 or age > 150:
            raise ValidationError("Age must be a valid integer between 0 and 150")
    
    # Validate medical record number if present
    if "medical_record_number" in data:
        mrn = data["medical_record_number"]
        if not isinstance(mrn, str) or len(mrn) < 1 or len(mrn) > 20:
            raise ValidationError("Medical record number must be between 1 and 20 characters")
    
    # Validate department if present
    if "department" in data:
        department = data["department"]
        valid_departments = [
            "emergency", "cardiology", "neurology", "oncology", "pediatrics",
            "surgery", "internal_medicine", "radiology", "pathology", "pharmacy"
        ]
        if department not in valid_departments:
            raise ValidationError(f"Invalid department. Must be one of: {', '.join(valid_departments)}")
    
    return True


def validate_knowledge_base_item(data: Dict[str, Any]) -> bool:
    """
    Validate knowledge base item data.
    
    Args:
        data: Knowledge base item data to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    required_fields = ["title", "content", "category", "source"]
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Required field '{field}' is missing")
        
        if not isinstance(data[field], str) or len(data[field].strip()) == 0:
            raise ValidationError(f"Field '{field}' cannot be empty")
    
    # Validate title length
    if len(data["title"]) > 500:
        raise ValidationError("Title is too long (maximum 500 characters)")
    
    # Validate content length
    if len(data["content"]) > 100000:
        raise ValidationError("Content is too long (maximum 100,000 characters)")
    
    # Validate category
    valid_categories = [
        "medical_guidelines", "faq", "policies", "procedures", "departments",
        "medications", "symptoms", "treatments", "emergency", "general"
    ]
    if data["category"] not in valid_categories:
        raise ValidationError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    # Validate source
    if len(data["source"]) > 255:
        raise ValidationError("Source is too long (maximum 255 characters)")
    
    # Validate tags if present
    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, list):
            raise ValidationError("Tags must be a list")
        
        for tag in tags:
            if not isinstance(tag, str) or len(tag.strip()) == 0:
                raise ValidationError("All tags must be non-empty strings")
            
            if len(tag) > 50:
                raise ValidationError("Tag is too long (maximum 50 characters)")
    
    return True


def validate_analytics_query(data: Dict[str, Any]) -> bool:
    """
    Validate analytics query parameters.
    
    Args:
        data: Analytics query data to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate date range
    if "start_date" in data:
        try:
            if isinstance(data["start_date"], str):
                datetime.fromisoformat(data["start_date"].replace('Z', '+00:00'))
            elif isinstance(data["start_date"], datetime):
                pass  # Already a datetime object
            else:
                raise ValidationError("Invalid start_date format")
        except (ValueError, TypeError):
            raise ValidationError("Invalid start_date format")
    
    if "end_date" in data:
        try:
            if isinstance(data["end_date"], str):
                datetime.fromisoformat(data["end_date"].replace('Z', '+00:00'))
            elif isinstance(data["end_date"], datetime):
                pass  # Already a datetime object
            else:
                raise ValidationError("Invalid end_date format")
        except (ValueError, TypeError):
            raise ValidationError("Invalid end_date format")
    
    # Validate limit
    if "limit" in data:
        limit = data["limit"]
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise ValidationError("Limit must be an integer between 1 and 1000")
    
    # Validate offset
    if "offset" in data:
        offset = data["offset"]
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer")
    
    return True


def _contains_malicious_content(message: str) -> bool:
    """
    Check if message contains potentially malicious content.
    
    Args:
        message: Message to check
        
    Returns:
        True if malicious content is detected
    """
    # List of potentially harmful patterns
    malicious_patterns = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'data:text/html',  # Data URLs
        r'vbscript:',  # VBScript protocol
        r'onload\s*=',  # Event handlers
        r'onerror\s*=',
        r'onclick\s*=',
        r'<iframe[^>]*>',  # Iframe tags
        r'<object[^>]*>',  # Object tags
        r'<embed[^>]*>',  # Embed tags
    ]
    
    message_lower = message.lower()
    
    for pattern in malicious_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE | re.DOTALL):
            logger.warning(f"Potentially malicious content detected: {pattern}")
            return True
    
    return False


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and other attacks.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        True if password meets strength requirements
        
    Raises:
        ValidationError: If validation fails
    """
    if not password or not isinstance(password, str):
        raise ValidationError("Password is required")
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if len(password) > 128:
        raise ValidationError("Password is too long (maximum 128 characters)")
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character")
    
    return True


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API key is required")
    
    if len(api_key) < 20:
        raise ValidationError("API key is too short")
    
    if len(api_key) > 200:
        raise ValidationError("API key is too long")
    
    # Check for valid characters (alphanumeric and some special chars)
    if not re.match(r'^[a-zA-Z0-9\-_\.]+$', api_key):
        raise ValidationError("API key contains invalid characters")
    
    return True

"""
Customer Service Agent System Module

This module demonstrates a multi-agent customer service system with specialized agents
for different types of customer inquiries. It showcases agent delegation, knowledge base
integration, and conversation management patterns.
"""

from .supervisor_agent import SupervisorAgent
from .product_specialist_agent import ProductSpecialistAgent
from .technical_support_agent import TechnicalSupportAgent
from .billing_agent import BillingAgent
from .knowledge_base_agent import KnowledgeBaseAgent
from .customer_service_module import CustomerServiceModule

__all__ = [
    "SupervisorAgent",
    "ProductSpecialistAgent",
    "TechnicalSupportAgent", 
    "BillingAgent",
    "KnowledgeBaseAgent",
    "CustomerServiceModule"
]

"""
Data Ingestion Agent for Data Analysis System

This agent specializes in collecting and validating data from multiple sources,
including databases, APIs, files, and streaming data. It demonstrates data
validation, schema detection, and initial data quality assessment.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import pandas as pd

from langchain.tools import BaseTool
from langchain.agents import Tool

from ...core.agent_base import BaseAgent, AgentConfig, AgentResponse


class DataSourceConnectorTool(BaseTool):
    """Tool for connecting to various data sources."""
    
    name = "data_source_connector"
    description = "Connect to and retrieve data from various sources (databases, APIs, files)"
    
    def _run(self, source_config: str) -> str:
        """Connect to data source and retrieve data."""
        try:
            config = json.loads(source_config)
            source_type = config.get("type", "csv")
            source_path = config.get("path", "")
            
            # Simulated data source connections
            if source_type == "csv":
                # Simulate CSV data
                sample_data = {
                    "columns": ["id", "name", "email", "age", "department", "salary"],
                    "sample_rows": [
                        [1, "John Doe", "john@example.com", 30, "Engineering", 75000],
                        [2, "Jane Smith", "jane@example.com", 28, "Marketing", 65000],
                        [3, "Bob Johnson", "bob@example.com", 35, "Sales", 70000]
                    ],
                    "total_rows": 1000,
                    "file_size": "2.5 MB"
                }
            elif source_type == "database":
                # Simulate database connection
                sample_data = {
                    "connection": "successful",
                    "database": config.get("database", "analytics_db"),
                    "tables": ["users", "orders", "products", "transactions"],
                    "sample_table": {
                        "name": "users",
                        "columns": ["user_id", "username", "created_at", "last_login"],
                        "row_count": 50000
                    }
                }
            elif source_type == "api":
                # Simulate API connection
                sample_data = {
                    "endpoint": config.get("url", "https://api.example.com/data"),
                    "status": "connected",
                    "response_format": "JSON",
                    "rate_limit": "1000 requests/hour",
                    "sample_response": {
                        "data": [
                            {"id": 1, "value": 100, "timestamp": "2024-01-01T00:00:00Z"},
                            {"id": 2, "value": 150, "timestamp": "2024-01-01T01:00:00Z"}
                        ],
                        "total_records": 8760
                    }
                }
            else:
                sample_data = {"error": f"Unsupported source type: {source_type}"}
            
            return json.dumps({
                "source_type": source_type,
                "source_path": source_path,
                "connection_status": "successful",
                "data_info": sample_data,
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"Failed to connect to data source: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
    
    async def _arun(self, source_config: str) -> str:
        """Async version of data source connection."""
        return self._run(source_config)


class DataValidationTool(BaseTool):
    """Tool for validating data quality and schema."""
    
    name = "data_validation"
    description = "Validate data quality, schema, and detect anomalies"
    
    def _run(self, data_info: str) -> str:
        """Validate data quality and schema."""
        try:
            data = json.loads(data_info)
            
            # Simulated data validation
            validation_result = {
                "validation_timestamp": datetime.utcnow().isoformat(),
                "schema_validation": {
                    "status": "passed",
                    "columns_detected": data.get("columns", []),
                    "data_types": {
                        "id": "integer",
                        "name": "string",
                        "email": "string",
                        "age": "integer",
                        "department": "string",
                        "salary": "integer"
                    },
                    "schema_issues": []
                },
                "quality_metrics": {
                    "total_records": data.get("total_rows", 0),
                    "completeness": 0.95,  # 95% of records have all fields
                    "accuracy": 0.98,      # 98% of records are accurate
                    "consistency": 0.92,   # 92% of records are consistent
                    "validity": 0.96       # 96% of records are valid
                },
                "data_issues": {
                    "missing_values": {
                        "email": 25,       # 25 missing email values
                        "age": 10,         # 10 missing age values
                        "department": 5    # 5 missing department values
                    },
                    "duplicate_records": 12,
                    "outliers": {
                        "salary": 3,       # 3 salary outliers
                        "age": 1           # 1 age outlier
                    },
                    "format_issues": {
                        "email_format": 8,  # 8 invalid email formats
                        "date_format": 2    # 2 invalid date formats
                    }
                },
                "recommendations": [
                    "Handle missing email values before analysis",
                    "Review salary outliers for data entry errors",
                    "Standardize date formats across all records",
                    "Remove or merge duplicate records"
                ]
            }
            
            return json.dumps(validation_result, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"Data validation failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
    
    async def _arun(self, data_info: str) -> str:
        """Async version of data validation."""
        return self._run(data_info)


class SchemaDetectionTool(BaseTool):
    """Tool for detecting and inferring data schema."""
    
    name = "schema_detection"
    description = "Detect and infer data schema, data types, and relationships"
    
    def _run(self, sample_data: str) -> str:
        """Detect schema from sample data."""
        try:
            data = json.loads(sample_data)
            
            # Simulated schema detection
            schema_result = {
                "detection_timestamp": datetime.utcnow().isoformat(),
                "inferred_schema": {
                    "columns": [
                        {
                            "name": "id",
                            "type": "integer",
                            "nullable": False,
                            "unique": True,
                            "description": "Primary key identifier"
                        },
                        {
                            "name": "name",
                            "type": "string",
                            "nullable": False,
                            "unique": False,
                            "description": "Full name of the person"
                        },
                        {
                            "name": "email",
                            "type": "string",
                            "nullable": True,
                            "unique": True,
                            "description": "Email address"
                        },
                        {
                            "name": "age",
                            "type": "integer",
                            "nullable": True,
                            "unique": False,
                            "description": "Age in years"
                        },
                        {
                            "name": "department",
                            "type": "string",
                            "nullable": True,
                            "unique": False,
                            "description": "Department or division"
                        },
                        {
                            "name": "salary",
                            "type": "integer",
                            "nullable": True,
                            "unique": False,
                            "description": "Annual salary in USD"
                        }
                    ],
                    "primary_key": ["id"],
                    "foreign_keys": [],
                    "indexes": ["email", "department"],
                    "constraints": [
                        "age >= 18 AND age <= 100",
                        "salary >= 0",
                        "email LIKE '%@%.%'"
                    ]
                },
                "data_relationships": {
                    "department_salary": {
                        "type": "one_to_many",
                        "description": "Each department can have multiple employees with different salaries"
                    },
                    "age_salary": {
                        "type": "correlation",
                        "strength": 0.65,
                        "description": "Moderate positive correlation between age and salary"
                    }
                },
                "data_patterns": {
                    "categorical_columns": ["department"],
                    "numerical_columns": ["id", "age", "salary"],
                    "text_columns": ["name", "email"],
                    "date_columns": [],
                    "boolean_columns": []
                },
                "statistical_summary": {
                    "age": {
                        "mean": 32.5,
                        "median": 31.0,
                        "std": 8.2,
                        "min": 22,
                        "max": 65
                    },
                    "salary": {
                        "mean": 72000,
                        "median": 70000,
                        "std": 15000,
                        "min": 45000,
                        "max": 120000
                    }
                }
            }
            
            return json.dumps(schema_result, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"Schema detection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }, indent=2)
    
    async def _arun(self, sample_data: str) -> str:
        """Async version of schema detection."""
        return self._run(sample_data)


class DataIngestionAgent(BaseAgent):
    """
    Data ingestion agent for collecting and validating data from multiple sources.
    
    This agent specializes in connecting to various data sources, validating data
    quality, detecting schemas, and preparing data for analysis.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the data ingestion agent."""
        super().__init__(config)
        
        # Initialize ingestion-specific tools
        self.data_source_connector_tool = DataSourceConnectorTool()
        self.data_validation_tool = DataValidationTool()
        self.schema_detection_tool = SchemaDetectionTool()
        
        # Add tools to the agent
        self.tools["data_source_connector"] = self.data_source_connector_tool
        self.tools["data_validation"] = self.data_validation_tool
        self.tools["schema_detection"] = self.schema_detection_tool
        
        self.logger.info("Data ingestion agent initialized with ingestion tools")
    
    def _create_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Create ingestion-specific tools."""
        if tool_name == "data_source_connector":
            return DataSourceConnectorTool()
        elif tool_name == "data_validation":
            return DataValidationTool()
        elif tool_name == "schema_detection":
            return SchemaDetectionTool()
        return None
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process data ingestion requests.
        
        Args:
            message: Data ingestion request or data source information
            context: Optional context information
            
        Returns:
            AgentResponse: Comprehensive data ingestion analysis and recommendations
        """
        try:
            # Analyze the ingestion request
            analysis = await self._analyze_ingestion_request(message)
            
            # Gather ingestion data
            ingestion_data = await self._gather_ingestion_data(analysis, message, context)
            
            # Generate comprehensive ingestion response
            ingestion_response = await self._generate_ingestion_response(message, analysis, ingestion_data)
            
            return AgentResponse(
                content=ingestion_response,
                confidence=0.9,
                reasoning=f"Processed data ingestion request based on: {analysis.get('ingestion_type', 'general')}",
                tools_used=analysis.get("tools_used", []),
                metadata={
                    "ingestion_analysis": analysis,
                    "ingestion_data": ingestion_data,
                    "context": context
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error processing ingestion request: {str(e)}")
            return AgentResponse(
                content="I apologize, but I'm having trouble processing your data ingestion request right now. Please try again or provide more specific details about your data sources.",
                confidence=0.0,
                reasoning="Error occurred during ingestion processing",
                metadata={"error": str(e)}
            )
    
    async def _analyze_ingestion_request(self, message: str) -> Dict[str, Any]:
        """Analyze the data ingestion request."""
        
        analysis_prompt = f"""
        Analyze this data ingestion request:
        
        Request: {message}
        
        Determine:
        1. What type of data ingestion is needed
        2. What data sources are involved
        3. Which tools should be used
        4. The complexity and scope of the ingestion
        
        Provide analysis in JSON format:
        {{
            "ingestion_type": "single_source|multi_source|streaming|batch|real_time",
            "data_sources": ["csv", "database", "api", "file"],
            "data_format": "structured|semi_structured|unstructured",
            "data_volume": "small|medium|large",
            "tools_needed": ["data_source_connector", "data_validation", "schema_detection"],
            "complexity": "simple|moderate|complex",
            "validation_required": true|false,
            "schema_detection_needed": true|false,
            "estimated_processing_time": "minutes|hours|days"
        }}
        """
        
        try:
            response = await self._invoke_model(analysis_prompt)
            analysis = json.loads(response)
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing ingestion request: {str(e)}")
            return {
                "ingestion_type": "single_source",
                "data_sources": ["csv"],
                "data_format": "structured",
                "data_volume": "medium",
                "tools_needed": ["data_source_connector", "data_validation"],
                "complexity": "moderate",
                "validation_required": True,
                "schema_detection_needed": True,
                "estimated_processing_time": "minutes"
            }
    
    async def _gather_ingestion_data(self, analysis: Dict[str, Any], message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Gather ingestion data based on the analysis."""
        ingestion_data = {}
        tools_used = []
        
        try:
            # Connect to data sources if needed
            if "data_source_connector" in analysis.get("tools_needed", []):
                # Extract source configuration from message or context
                source_config = self._extract_source_config(message, context)
                connection_result = await self.data_source_connector_tool._arun(source_config)
                ingestion_data["source_connection"] = connection_result
                tools_used.append("data_source_connector")
            
            # Validate data if needed
            if "data_validation" in analysis.get("tools_needed", []):
                # Use sample data for validation
                sample_data = self._extract_sample_data(message, context)
                validation_result = await self.data_validation_tool._arun(sample_data)
                ingestion_data["data_validation"] = validation_result
                tools_used.append("data_validation")
            
            # Detect schema if needed
            if "schema_detection" in analysis.get("tools_needed", []):
                sample_data = self._extract_sample_data(message, context)
                schema_result = await self.schema_detection_tool._arun(sample_data)
                ingestion_data["schema_detection"] = schema_result
                tools_used.append("schema_detection")
            
            ingestion_data["tools_used"] = tools_used
            
        except Exception as e:
            self.logger.error(f"Error gathering ingestion data: {str(e)}")
            ingestion_data["error"] = str(e)
        
        return ingestion_data
    
    def _extract_source_config(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Extract data source configuration from message or context."""
        # Default configuration
        default_config = {
            "type": "csv",
            "path": "data/sample.csv"
        }
        
        # Try to extract from context
        if context and "source_config" in context:
            return json.dumps(context["source_config"])
        
        # Try to extract from message (simplified)
        if "database" in message.lower():
            return json.dumps({
                "type": "database",
                "host": "localhost",
                "database": "analytics_db",
                "table": "users"
            })
        elif "api" in message.lower():
            return json.dumps({
                "type": "api",
                "url": "https://api.example.com/data",
                "method": "GET"
            })
        else:
            return json.dumps(default_config)
    
    def _extract_sample_data(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Extract sample data for validation and schema detection."""
        # Default sample data
        default_sample = {
            "columns": ["id", "name", "email", "age", "department", "salary"],
            "sample_rows": [
                [1, "John Doe", "john@example.com", 30, "Engineering", 75000],
                [2, "Jane Smith", "jane@example.com", 28, "Marketing", 65000]
            ],
            "total_rows": 1000
        }
        
        # Try to extract from context
        if context and "sample_data" in context:
            return json.dumps(context["sample_data"])
        
        return json.dumps(default_sample)
    
    async def _generate_ingestion_response(self, message: str, analysis: Dict[str, Any], ingestion_data: Dict[str, Any]) -> str:
        """Generate a comprehensive data ingestion response."""
        
        response_prompt = f"""
        You are a data ingestion expert. Generate a comprehensive data ingestion analysis based on this request:
        
        Original Request: {message}
        Analysis: {json.dumps(analysis, indent=2)}
        Ingestion Data: {json.dumps(ingestion_data, indent=2)}
        
        Create a detailed data ingestion report that includes:
        1. Executive summary of the data ingestion process
        2. Data source connection status and details
        3. Data quality assessment and validation results
        4. Schema detection and data structure analysis
        5. Data quality issues and recommendations
        6. Next steps for data cleaning and preparation
        7. Recommendations for data storage and processing
        8. Performance considerations and optimization tips
        
        Be thorough, actionable, and provide specific guidance for data preparation
        and quality improvement.
        """
        
        try:
            response = await self._invoke_model(response_prompt)
            return response
        except Exception as e:
            self.logger.error(f"Error generating ingestion response: {str(e)}")
            return "I apologize, but I'm having trouble generating your data ingestion analysis right now. Please try again with more specific data source information."
    
    async def execute_task(self, task: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute data ingestion-specific tasks."""
        if task == "connect_to_source":
            source_config = parameters.get("source_config", "{}") if parameters else "{}"
            result = await self.data_source_connector_tool._arun(source_config)
            return {"connection_result": result}
        
        elif task == "validate_data":
            data_info = parameters.get("data_info", "{}") if parameters else "{}"
            result = await self.data_validation_tool._arun(data_info)
            return {"validation_result": result}
        
        elif task == "detect_schema":
            sample_data = parameters.get("sample_data", "{}") if parameters else "{}"
            result = await self.schema_detection_tool._arun(sample_data)
            return {"schema_result": result}
        
        elif task == "comprehensive_ingestion":
            message = parameters.get("message", "") if parameters else ""
            context = parameters.get("context") if parameters else None
            analysis = await self._analyze_ingestion_request(message)
            ingestion_data = await self._gather_ingestion_data(analysis, message, context)
            response = await self._generate_ingestion_response(message, analysis, ingestion_data)
            return {
                "ingestion_analysis": response,
                "analysis": analysis,
                "data": ingestion_data
            }
        
        else:
            return {"error": f"Unknown task: {task}"}

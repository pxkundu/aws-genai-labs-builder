"""
Product Specialist Agent for Customer Service System

This agent specializes in handling product-related inquiries, including
product information, features, specifications, comparisons, and recommendations.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.tools import BaseTool
from langchain.agents import Tool

from ...core.agent_base import BaseAgent, AgentConfig, AgentResponse


class ProductSearchTool(BaseTool):
    """Tool for searching product information."""
    
    name = "product_search"
    description = "Search for product information by name, category, or features"
    
    def _run(self, query: str) -> str:
        """Search for products."""
        # Simulated product database
        products = {
            "laptop": {
                "name": "ProBook X1",
                "category": "Laptops",
                "price": "$1299",
                "features": ["Intel i7", "16GB RAM", "512GB SSD", "15.6\" Display"],
                "availability": "In Stock"
            },
            "smartphone": {
                "name": "SmartPhone Pro",
                "category": "Mobile",
                "price": "$899",
                "features": ["5G", "128GB Storage", "Triple Camera", "All-day Battery"],
                "availability": "In Stock"
            },
            "tablet": {
                "name": "Tablet Air",
                "category": "Tablets",
                "price": "$599",
                "features": ["10.9\" Display", "64GB Storage", "WiFi + Cellular", "Stylus Support"],
                "availability": "Limited Stock"
            }
        }
        
        # Simple search logic
        query_lower = query.lower()
        for product_key, product_info in products.items():
            if (product_key in query_lower or 
                any(feature.lower() in query_lower for feature in product_info["features"]) or
                product_info["category"].lower() in query_lower):
                return json.dumps(product_info, indent=2)
        
        return "No products found matching your search criteria."
    
    async def _arun(self, query: str) -> str:
        """Async version of product search."""
        return self._run(query)


class ProductComparisonTool(BaseTool):
    """Tool for comparing products."""
    
    name = "product_comparison"
    description = "Compare multiple products side by side"
    
    def _run(self, product_names: str) -> str:
        """Compare products."""
        # Parse product names
        products = [name.strip() for name in product_names.split(",")]
        
        # Simulated comparison data
        comparison_data = {
            "ProBook X1": {
                "price": "$1299",
                "performance": "High",
                "battery_life": "8 hours",
                "weight": "3.2 lbs",
                "display": "15.6\" FHD"
            },
            "SmartPhone Pro": {
                "price": "$899",
                "performance": "High",
                "battery_life": "12 hours",
                "weight": "0.4 lbs",
                "display": "6.1\" OLED"
            },
            "Tablet Air": {
                "price": "$599",
                "performance": "Medium",
                "battery_life": "10 hours",
                "weight": "1.0 lbs",
                "display": "10.9\" Retina"
            }
        }
        
        # Build comparison table
        comparison_result = "Product Comparison:\n\n"
        comparison_result += f"{'Feature':<15} {'ProBook X1':<15} {'SmartPhone Pro':<15} {'Tablet Air':<15}\n"
        comparison_result += "-" * 60 + "\n"
        
        features = ["price", "performance", "battery_life", "weight", "display"]
        for feature in features:
            row = f"{feature.replace('_', ' ').title():<15}"
            for product in products:
                if product in comparison_data:
                    row += f"{comparison_data[product].get(feature, 'N/A'):<15}"
                else:
                    row += f"{'N/A':<15}"
            comparison_result += row + "\n"
        
        return comparison_result
    
    async def _arun(self, product_names: str) -> str:
        """Async version of product comparison."""
        return self._run(product_names)


class InventoryCheckTool(BaseTool):
    """Tool for checking product inventory."""
    
    name = "inventory_check"
    description = "Check product availability and inventory levels"
    
    def _run(self, product_name: str) -> str:
        """Check inventory for a product."""
        # Simulated inventory data
        inventory = {
            "probook x1": {"available": True, "quantity": 15, "location": "Warehouse A"},
            "smartphone pro": {"available": True, "quantity": 8, "location": "Warehouse B"},
            "tablet air": {"available": True, "quantity": 3, "location": "Warehouse A"},
            "default": {"available": False, "quantity": 0, "location": "N/A"}
        }
        
        product_key = product_name.lower()
        for key, data in inventory.items():
            if key in product_key or product_key in key:
                return json.dumps(data, indent=2)
        
        return json.dumps(inventory["default"], indent=2)
    
    async def _arun(self, product_name: str) -> str:
        """Async version of inventory check."""
        return self._run(product_name)


class ProductSpecialistAgent(BaseAgent):
    """
    Product specialist agent for handling product-related customer inquiries.
    
    This agent specializes in providing detailed product information, comparisons,
    recommendations, and inventory status to customers.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the product specialist agent."""
        super().__init__(config)
        
        # Initialize product-specific tools
        self.product_search_tool = ProductSearchTool()
        self.product_comparison_tool = ProductComparisonTool()
        self.inventory_check_tool = InventoryCheckTool()
        
        # Add tools to the agent
        self.tools["product_search"] = self.product_search_tool
        self.tools["product_comparison"] = self.product_comparison_tool
        self.tools["inventory_check"] = self.inventory_check_tool
        
        self.logger.info("Product specialist agent initialized with product tools")
    
    def _create_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Create product-specific tools."""
        if tool_name == "product_search":
            return ProductSearchTool()
        elif tool_name == "product_comparison":
            return ProductComparisonTool()
        elif tool_name == "inventory_check":
            return InventoryCheckTool()
        return None
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process product-related customer inquiries.
        
        Args:
            message: Customer inquiry about products
            context: Optional context information
            
        Returns:
            AgentResponse: Detailed product information and recommendations
        """
        try:
            # Analyze the inquiry to determine what product information is needed
            analysis = await self._analyze_product_inquiry(message)
            
            # Gather relevant product information
            product_info = await self._gather_product_information(analysis, message)
            
            # Generate comprehensive response
            response_content = await self._generate_product_response(message, analysis, product_info)
            
            return AgentResponse(
                content=response_content,
                confidence=0.9,
                reasoning=f"Provided product information based on inquiry analysis: {analysis.get('inquiry_type', 'general')}",
                tools_used=analysis.get("tools_used", []),
                metadata={
                    "inquiry_analysis": analysis,
                    "product_info": product_info,
                    "customer_context": context
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error processing product inquiry: {str(e)}")
            return AgentResponse(
                content="I apologize, but I'm having trouble accessing our product information right now. Please try again or contact our sales team directly.",
                confidence=0.0,
                reasoning="Error occurred during product inquiry processing",
                metadata={"error": str(e)}
            )
    
    async def _analyze_product_inquiry(self, message: str) -> Dict[str, Any]:
        """Analyze the product inquiry to understand what information is needed."""
        
        analysis_prompt = f"""
        Analyze this product-related customer inquiry:
        
        Inquiry: {message}
        
        Determine:
        1. What type of product information is being requested
        2. Which products are mentioned or implied
        3. What tools should be used to gather information
        4. The complexity and urgency of the request
        
        Provide analysis in JSON format:
        {{
            "inquiry_type": "search|comparison|specifications|recommendation|availability",
            "products_mentioned": ["product1", "product2"],
            "tools_needed": ["product_search", "product_comparison", "inventory_check"],
            "complexity": "simple|moderate|complex",
            "urgency": "low|medium|high",
            "customer_intent": "browsing|purchasing|researching|troubleshooting"
        }}
        """
        
        try:
            response = await self._invoke_model(analysis_prompt)
            analysis = json.loads(response)
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing product inquiry: {str(e)}")
            return {
                "inquiry_type": "search",
                "products_mentioned": [],
                "tools_needed": ["product_search"],
                "complexity": "moderate",
                "urgency": "medium",
                "customer_intent": "researching"
            }
    
    async def _gather_product_information(self, analysis: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Gather relevant product information based on the analysis."""
        product_info = {}
        tools_used = []
        
        try:
            # Use product search tool if needed
            if "product_search" in analysis.get("tools_needed", []):
                search_query = message
                if analysis.get("products_mentioned"):
                    search_query = " ".join(analysis["products_mentioned"])
                
                search_result = await self.product_search_tool._arun(search_query)
                product_info["search_results"] = search_result
                tools_used.append("product_search")
            
            # Use product comparison tool if needed
            if "product_comparison" in analysis.get("tools_needed", []):
                products = analysis.get("products_mentioned", [])
                if len(products) >= 2:
                    comparison_result = await self.product_comparison_tool._arun(",".join(products))
                    product_info["comparison_results"] = comparison_result
                    tools_used.append("product_comparison")
            
            # Use inventory check tool if needed
            if "inventory_check" in analysis.get("tools_needed", []):
                products = analysis.get("products_mentioned", [])
                for product in products:
                    inventory_result = await self.inventory_check_tool._arun(product)
                    product_info[f"inventory_{product}"] = inventory_result
                tools_used.append("inventory_check")
            
            product_info["tools_used"] = tools_used
            
        except Exception as e:
            self.logger.error(f"Error gathering product information: {str(e)}")
            product_info["error"] = str(e)
        
        return product_info
    
    async def _generate_product_response(self, message: str, analysis: Dict[str, Any], product_info: Dict[str, Any]) -> str:
        """Generate a comprehensive product response."""
        
        response_prompt = f"""
        You are a knowledgeable product specialist. Generate a helpful response to this customer inquiry:
        
        Customer Inquiry: {message}
        Inquiry Analysis: {json.dumps(analysis, indent=2)}
        Product Information: {json.dumps(product_info, indent=2)}
        
        Provide a comprehensive response that:
        1. Directly addresses the customer's question
        2. Includes relevant product details and specifications
        3. Offers helpful recommendations if appropriate
        4. Mentions availability and pricing information
        5. Suggests next steps or additional information
        
        Be friendly, professional, and informative. If you don't have specific information,
        acknowledge it and offer to help in other ways.
        """
        
        try:
            response = await self._invoke_model(response_prompt)
            return response
        except Exception as e:
            self.logger.error(f"Error generating product response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again or contact our sales team for assistance."
    
    async def execute_task(self, task: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute product specialist-specific tasks."""
        if task == "search_products":
            query = parameters.get("query", "") if parameters else ""
            result = await self.product_search_tool._arun(query)
            return {"search_results": result}
        
        elif task == "compare_products":
            products = parameters.get("products", []) if parameters else []
            if len(products) >= 2:
                result = await self.product_comparison_tool._arun(",".join(products))
                return {"comparison_results": result}
            else:
                return {"error": "At least 2 products required for comparison"}
        
        elif task == "check_inventory":
            product_name = parameters.get("product_name", "") if parameters else ""
            result = await self.inventory_check_tool._arun(product_name)
            return {"inventory_result": result}
        
        elif task == "get_product_recommendations":
            criteria = parameters.get("criteria", {}) if parameters else {}
            # Generate recommendations based on criteria
            recommendations = await self._generate_recommendations(criteria)
            return {"recommendations": recommendations}
        
        else:
            return {"error": f"Unknown task: {task}"}
    
    async def _generate_recommendations(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate product recommendations based on criteria."""
        # Simulated recommendation logic
        recommendations = [
            {
                "product": "ProBook X1",
                "match_score": 0.9,
                "reason": "High performance laptop with excellent specifications",
                "price": "$1299"
            },
            {
                "product": "SmartPhone Pro",
                "match_score": 0.8,
                "reason": "Feature-rich smartphone with great value",
                "price": "$899"
            }
        ]
        
        return recommendations

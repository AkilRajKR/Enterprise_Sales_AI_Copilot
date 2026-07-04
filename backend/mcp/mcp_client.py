import os
import requests
import logging
from typing import Any, List, Dict

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for MCP SQLite server"""
    
    def __init__(self, mcp_url: str = "http://localhost:8001"):
        self.mcp_url = mcp_url
    
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query via MCP server"""
        try:
            response = requests.post(
                f"{self.mcp_url}/execute",
                json={"query": sql_query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    logger.info(f"MCP query executed successfully")
                    return result["data"]
                else:
                    logger.error(f"MCP error: {result['error']}")
                    return []
            else:
                logger.error(f"MCP server error: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error executing MCP query: {e}")
            return []
    
    def get_schema(self) -> List[str]:
        """Get database schema from MCP server"""
        try:
            response = requests.get(f"{self.mcp_url}/schema", timeout=10)
            if response.status_code == 200:
                return response.json().get("tables", [])
            return []
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return []
    
    def health_check(self) -> bool:
        """Check if MCP server is healthy"""
        try:
            response = requests.get(f"{self.mcp_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

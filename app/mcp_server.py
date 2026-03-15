from fastapi_mcp import FastApiMCP
from .tools.financial_analyzer import analyze_financial_pdf

def register_tools(mcp):

    @mcp.tool()
    def analyze_pdf(query: str, file_name: str):

        file_path = f"uploads/{file_name}"

        return analyze_financial_pdf(query, file_path)
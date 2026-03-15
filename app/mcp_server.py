from fastapi_mcp import FastApiMCP
from .tools.financial_analyzer import analyze_financial_pdf
from pathlib import Path

def register_tools(mcp):
    """Register MCP tools with proper path handling"""

    @mcp.tool()
    def analyze_financial_pdf_mcp(query: str, file: str):
        """Analyze financial PDF and return charts/metrics
        
        Args:
            query: Analysis query (e.g., 'revenue growth', 'profit comparison')
            file: Path to PDF file (relative or absolute)
        """
        # Resolve file path
        file_path = Path(file)
        
        # If relative path, try uploads directory
        if not file_path.is_absolute():
            uploads_path = Path(__file__).parent.parent / "uploads" / file
            if uploads_path.exists():
                file_path = uploads_path
        
        # Ensure file exists
        if not file_path.exists():
            return {"error": f"File not found: {file}"}
        
        # Read PDF bytes and analyze
        pdf_bytes = file_path.read_bytes()
        return analyze_financial_pdf(query, pdf_bytes)
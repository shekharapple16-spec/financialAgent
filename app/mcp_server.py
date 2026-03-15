from .tools.financial_analyzer import analyze_financial_pdf
from pathlib import Path

def register_tools(mcp):
    """Register MCP tools with proper path handling"""
    
    def _resolve_pdf_path(file: str) -> Path:
        """Helper to resolve PDF file path from multiple locations"""
        file_path = Path(file)
        
        # If absolute path, use as-is
        if file_path.is_absolute():
            if file_path.exists() and file_path.suffix.lower() == '.pdf':
                return file_path
            return None
        
        # Try uploads directory first (primary location)
        uploads_path = Path(__file__).parent.parent / "uploads" / file
        if uploads_path.exists() and uploads_path.suffix.lower() == '.pdf':
            return uploads_path
        
        # Try current working directory
        cwd_path = Path.cwd() / file
        if cwd_path.exists() and cwd_path.suffix.lower() == '.pdf':
            return cwd_path
        
        # Try uploads directory with .pdf extension if not provided
        if not file.lower().endswith('.pdf'):
            pdf_with_ext = uploads_path.parent / f"{file}.pdf"
            if pdf_with_ext.exists():
                return pdf_with_ext
        
        return None

    # Tools are registered via the mcp.tools dict
    # These will be automatically exposed via the MCP protocol
    
    def list_available_pdfs() -> dict:
        """List all available PDF files in the uploads directory
        
        Returns:
            Dictionary with list of available PDF filenames
        """
        uploads_dir = Path(__file__).parent.parent / "uploads"
        
        if not uploads_dir.exists():
            return {"error": "Uploads directory not found"}
        
        pdf_files = sorted([f.name for f in uploads_dir.glob("*.pdf")])
        
        return {
            "available_pdfs": pdf_files,
            "count": len(pdf_files),
            "upload_directory": str(uploads_dir)
        }

    def analyze_financial_pdf_mcp(query: str, file: str):
        """Analyze ANY financial PDF and return charts/metrics
        
        Args:
            query: Analysis query (e.g., 'revenue growth', 'profit comparison', 'summary')
            file: PDF filename (e.g., 'report.pdf', 'financial_statement.pdf')
                  Can be just filename or relative path
        
        Returns:
            Dictionary with analysis results including chart image and metrics
        """
        # Resolve file path
        file_path = _resolve_pdf_path(file)
        
        if not file_path:
            # Return helpful error with available files
            uploads_dir = Path(__file__).parent.parent / "uploads"
            available = []
            if uploads_dir.exists():
                available = [f.name for f in uploads_dir.glob("*.pdf")]
            
            return {
                "error": f"PDF file not found: {file}",
                "available_files": available,
                "tip": "Use list_available_pdfs() to see available files or upload to /uploads directory"
            }
        
        # Read PDF bytes and analyze
        try:
            pdf_bytes = file_path.read_bytes()
            result = analyze_financial_pdf(query, pdf_bytes)
            result["file_analyzed"] = file_path.name
            return result
        except Exception as e:
            return {
                "error": f"Failed to process PDF: {str(e)}",
                "file": file_path.name
            }
    
    # Store tools in the MCP instance
    if hasattr(mcp, 'tools'):
        mcp.tools['list_available_pdfs'] = list_available_pdfs
        mcp.tools['analyze_financial_pdf'] = analyze_financial_pdf_mcp
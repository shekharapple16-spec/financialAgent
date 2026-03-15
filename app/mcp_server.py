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

    def upload_pdf_to_uploads(file_path: str):
        """Upload a PDF file to the uploads directory by copying from a given path
        
        Args:
            file_path: Path to the PDF file to upload (absolute or relative)
        
        Returns:
            Confirmation message with filename
        """
        source_path = Path(file_path)
        
        if not source_path.exists():
            return {"error": f"Source file not found: {file_path}"}
        
        if not source_path.suffix.lower() == '.pdf':
            return {"error": "Only PDF files are allowed"}
        
        uploads_dir = Path(__file__).parent.parent / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        dest_path = uploads_dir / source_path.name
        
        try:
            import shutil
            shutil.copy2(source_path, dest_path)
            return {
                "message": f"File uploaded successfully",
                "filename": source_path.name,
                "location": str(dest_path),
                "size_bytes": dest_path.stat().st_size
            }
        except Exception as e:
            return {"error": f"Failed to upload file: {str(e)}"}

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
    # Be defensive about how to register - different FastApiMCP versions may vary
    tools_registered = False
    
    if hasattr(mcp, 'tools'):
        tools_attr = getattr(mcp, 'tools', None)
        # Check if it's a dict before trying to assign
        if isinstance(tools_attr, dict):
            tools_attr['list_available_pdfs'] = list_available_pdfs
            tools_attr['upload_pdf_to_uploads'] = upload_pdf_to_uploads
            tools_attr['analyze_financial_pdf'] = analyze_financial_pdf_mcp
            tools_registered = True
    
    # Alternative registration methods
    if not tools_registered:
        if hasattr(mcp, 'tool'):
            # Try using decorator/registration method if available
            try:
                mcp.tool()(list_available_pdfs)
                mcp.tool()(upload_pdf_to_uploads)
                mcp.tool()(analyze_financial_pdf_mcp)
                tools_registered = True
            except:
                pass
        
        # As a fallback, try setting as attributes
        if not tools_registered:
            try:
                setattr(mcp, '_list_available_pdfs', list_available_pdfs)
                setattr(mcp, '_upload_pdf_to_uploads', upload_pdf_to_uploads)
                setattr(mcp, '_analyze_financial_pdf', analyze_financial_pdf_mcp)
            except:
                pass
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from .tools.financial_analyzer import analyze_financial_pdf
from .mcp_server import register_tools

app = FastAPI(title="Financial Chart Agent")

# Enable CORS for better compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
uploads_dir = Path(__file__).parent.parent / "uploads"
uploads_dir.mkdir(exist_ok=True)


class AnalyzeRequest(BaseModel):
    query: str
    file: str   # PDF filename


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file to the uploads directory
    
    Args:
        file: PDF file to upload
    
    Returns:
        Confirmation with filename
    """
    if not file.filename.lower().endswith('.pdf'):
        return {"error": "Only PDF files are allowed"}
    
    file_path = uploads_dir / file.filename
    
    try:
        contents = await file.read()
        file_path.write_bytes(contents)
        return {
            "message": f"File uploaded successfully",
            "filename": file.filename,
            "location": str(file_path),
            "size_bytes": len(contents)
        }
    except Exception as e:
        return {"error": f"Failed to upload file: {str(e)}"}


@app.post("/analyze", operation_id="analyze_financial_pdf")
async def analyze(req: AnalyzeRequest):
    """REST API endpoint for financial PDF analysis
    
    Args:
        query: Analysis query (e.g., 'revenue growth')
        file: PDF filename in uploads directory
    """
    # Resolve file path from uploads directory
    pdf_path = uploads_dir / req.file
    
    # Also try without extension if provided
    if not pdf_path.exists() and not req.file.endswith('.pdf'):
        pdf_path = uploads_dir / f"{req.file}.pdf"
    
    if not pdf_path.exists():
        return {
            "error": f"File not found: {req.file}",
            "upload_directory": str(uploads_dir)
        }

    try:
        contents = pdf_path.read_bytes()
        result = analyze_financial_pdf(req.query, contents)
        result["file_analyzed"] = pdf_path.name
        return result
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


@app.get("/pdfs")
async def list_pdfs():
    """List all available PDF files"""
    if not uploads_dir.exists():
        return {"pdfs": [], "count": 0}
    
    pdfs = [f.name for f in uploads_dir.glob("*.pdf")]
    return {
        "pdfs": sorted(pdfs),
        "count": len(pdfs),
        "directory": str(uploads_dir)
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Financial Chart Agent",
        "uploads_directory": str(uploads_dir),
        "mcp_endpoint": "/mcp"
    }


# Initialize MCP server - wrapped in try-except for compatibility
try:
    from fastapi_mcp import FastApiMCP
    mcp = FastApiMCP(app, exclude_operations=["upload_pdf"])
    
    # Register MCP tools
    try:
        register_tools(mcp)
        if hasattr(mcp, 'mount'):
            mcp.mount()
    except (TypeError, AttributeError, KeyError) as e:
        # Known issue: mcp.tools might be a list or have incompatible type
        print(f"Warning: Could not mount MCP tools: {type(e).__name__}: {e}")
        print("REST API endpoints will continue to work normally")
    except Exception as e:
        print(f"Warning: Could not mount MCP tools: {e}")
        print("REST API endpoints will continue to work normally")
except Exception as e:
    print(f"Warning: FastApiMCP initialization failed: {e}")
    print("REST API endpoints will continue to work normally")
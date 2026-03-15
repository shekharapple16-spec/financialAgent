from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
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


class AnalyzeRequest(BaseModel):
    query: str
    file: str   # path to pdf


@app.post("/analyze", operation_id="analyze_financial_pdf")
async def analyze(req: AnalyzeRequest):
    """REST API endpoint for financial PDF analysis"""
    # Resolve file path
    pdf_path = Path(req.file)
    
    # If relative path, try uploads directory
    if not pdf_path.is_absolute():
        uploads_path = Path(__file__).parent.parent / "uploads" / req.file
        if uploads_path.exists():
            pdf_path = uploads_path
    
    if not pdf_path.exists():
        return {"error": f"File not found: {req.file}"}

    contents = pdf_path.read_bytes()
    result = analyze_financial_pdf(req.query, contents)

    return result


# Initialize MCP server
mcp = FastApiMCP(app)

# Register MCP tools
register_tools(mcp)

# Mount MCP
mcp.mount()
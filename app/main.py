from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from pathlib import Path

from .tools.financial_analyzer import analyze_financial_pdf

app = FastAPI(title="Financial Chart Agent")


class AnalyzeRequest(BaseModel):
    query: str
    file: str   # path to pdf


@app.post("/analyze", operation_id="analyze_financial_pdf")
async def analyze(req: AnalyzeRequest):

    pdf_path = Path(req.file)

    if not pdf_path.exists():
        return {"error": f"File not found: {req.file}"}

    contents = pdf_path.read_bytes()

    result = analyze_financial_pdf(req.query, contents)

    return result


mcp = FastApiMCP(app)
mcp.mount()
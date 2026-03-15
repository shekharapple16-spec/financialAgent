from fastapi import FastAPI, UploadFile, File
from fastapi_mcp import FastApiMCP

from .tools.financial_analyzer import analyze_financial_pdf

app = FastAPI(title="Financial Chart Agent")


@app.get("/")
def health():
    return {"status": "Financial Chart Agent running"}


@app.post("/analyze")
async def analyze(query: str, file: UploadFile = File(...)):
    contents = await file.read()
    result = analyze_financial_pdf(query, contents)
    return result


# MCP wrapper
mcp = FastApiMCP(app)
mcp.mount()
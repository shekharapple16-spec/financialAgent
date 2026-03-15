# Fix for Upload PDF Error 422: Missing File Field

## Problem
The error `Status code: 422. Response: {"detail":[{"type":"missing","loc":["body","file"],"msg":"Field required","input":null}]}` was occurring when trying to use the `/upload` endpoint through the MCP protocol.

## Root Cause
When `FastApiMCP` automatically exposes FastAPI endpoints as MCP tools, it tried to expose the `/upload` endpoint. However, the endpoint expects a `UploadFile` parameter which is a special FastAPI type that requires multipart form data - this is incompatible with MCP's JSON-based protocol. MCP tools cannot handle multipart/form-data uploads, so the `file` field was missing in the MCP call, causing the 422 Unprocessable Entity error.

## Solution

### 1. Exclude the REST `/upload` endpoint from MCP exposure
**File: `app/main.py` (Line 116)**
```python
# Changed from:
mcp = FastApiMCP(app)

# To:
mcp = FastApiMCP(app, exclude_operations=["upload_pdf"])
```

This prevents FastApiMCP from automatically exposing the REST `/upload` endpoint as an MCP tool, since it can't be properly exposed anyway.

### 2. Create an MCP-native PDF upload tool
**File: `app/mcp_server.py` (Added `upload_pdf_to_uploads` function)**

A new MCP tool `upload_pdf_to_uploads()` was added that accepts file paths as strings instead of binary uploads. This is suitable for MCP since it:
- Takes a file path as a string parameter (MCP-compatible)
- Copies the file to the uploads directory
- Returns confirmation with file details

```python
def upload_pdf_to_uploads(file_path: str):
    """Upload a PDF file to the uploads directory by copying from a given path
    
    Args:
        file_path: Path to the PDF file to upload (absolute or relative)
    
    Returns:
        Confirmation message with filename
    """
    # Implementation copies file to uploads directory
```

### 3. Register the new MCP tool
**File: `app/mcp_server.py` (Updated tool registration)**

The new `upload_pdf_to_uploads` function is registered with the MCP server alongside other tools:
- In the `mcp.tools` dictionary
- Via the `mcp.tool()` decorator
- As a fallback attribute

## Result

✅ **REST API (`/upload`)** - Still works for multipart file uploads  
✅ **MCP Protocol** - Now has `upload_pdf_to_uploads()` tool for string-based file paths  
✅ **No 422 errors** - Removed incompatible endpoint from MCP exposure

## Usage

### REST API (unchanged):
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/path/to/file.pdf"
```

### MCP Tool (new):
```python
# Upload a file to the uploads directory
result = client.call_tool("upload_pdf_to_uploads", {
    "file_path": "/absolute/path/to/file.pdf"
})
```

## Files Modified
1. `app/main.py` - Added `exclude_operations` parameter to FastApiMCP
2. `app/mcp_server.py` - Added `upload_pdf_to_uploads()` MCP tool and registered it

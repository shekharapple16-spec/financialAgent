# How to Use - ANY PDF Files

## 🎯 On Render - Flexible PDF Handling

Your system now handles **ANY PDF file** in these ways:

### Method 1: Upload via REST API (Easiest on Render)

```bash
# Upload any PDF file
curl -X POST https://financialagent-g2qu.onrender.com/upload \
  -F "file=@/path/to/your/financial_report.pdf"

# Response:
# {
#   "message": "File uploaded successfully",
#   "filename": "financial_report.pdf",
#   "size_bytes": 245632
# }
```

### Method 2: Upload to `/uploads` Directory

1. In your Render service, upload PDF to `/uploads` folder
2. System will automatically find and process it

### Method 3: Use Python Script to Upload

```python
import requests

# Upload file
with open('myreport.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'https://financialagent-g2qu.onrender.com/upload',
        files=files
    )
    print(response.json())
```

---

## 📝 How to Prompt Claude for Results

### After uploading "myreport.pdf":

**Prompt 1 - Revenue Analysis (Any PDF):**
```
Analyze the revenue growth in myreport.pdf
```

**Prompt 2 - Profit Analysis (Any PDF):**
```
Show profit trends in myreport.pdf
```

**Prompt 3 - Comparison (Any PDF):**
```
Compare revenue vs profit in myreport.pdf
```

**Prompt 4 - Quick View (Any PDF):**
```
Summarize financial data from myreport.pdf
```

---

## 🔍 Available Tools (MCP)

### 1. **analyze_financial_pdf_mcp**
- Works with ANY PDF filename
- Queries: "revenue growth", "profit", "comparison", "summary"
- Returns: Chart image + data

### 2. **list_available_pdfs**
- Shows all uploaded PDFs
- Helps you remember filenames
- Use when uncertain about filename

---

## 📋 Complete Workflow on Render

```
1. Upload PDF via /upload endpoint
   ↓
2. Check available files with /pdfs endpoint
   ↓
3. Prompt Claude: "Analyze [filename.pdf]"
   ↓
4. Claude calls MCP tool with your PDF
   ↓
5. Get chart + analysis results
```

---

## 🛠️ Helpful Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload` | POST | Upload any PDF file |
| `/analyze` | POST | Analyze via REST |
| `/pdfs` | GET | List available PDFs |
| `/health` | GET | Check service status |
| `/mcp` | WebSocket | MCP protocol endpoint |

---

## 💡 Examples

### Upload Sales Report
```bash
curl -X POST https://financialagent-g2qu.onrender.com/upload \
  -F "file=@sales_2024.pdf"
```

### Check What's Available
```bash
curl https://financialagent-g2qu.onrender.com/pdfs
```

### Prompt Claude
```
"Show revenue growth in sales_2024.pdf"
```

---

## ✅ Features

✅ Accept ANY PDF filename  
✅ Auto-resolve from uploads folder  
✅ File upload endpoint  
✅ List available files  
✅ Helpful error messages  
✅ Works with generic prompts  
✅ No file extension restrictions  

---

## 🚀 Next Steps

1. **Push code to GitHub** (already done via git push)
2. **Redeploy on Render** (auto-redeploy from GitHub)
3. **Upload your PDF** via `/upload` endpoint
4. **Prompt Claude** with filename
5. **Get results** with chart + analysis

No more hardcoded filenames! 🎉

# Invoice IDP - Intelligent Document Processing

Extract structured data from PDF invoices using AI + LangGraph pipeline.

---

## 🏗️ Architecture

```
PDF Upload
    ↓
Docling Parser ──┐
                 ├─→ Merge Text
LlamaParse   ────┘
    ↓
Classify (Invoice?)
    ↓
Rule Extract (Regex patterns)
    ↓
Confidence < 1?
    ├─ YES → LLM Extract
    └─ NO  → Validate
    ↓
Pydantic Validation
    ↓
JSON Response
```

**Explanation**: The system receives a PDF, parses it using two methods simultaneously (Docling + LlamaParse), merges the extracted text, tries rule-based extraction first using regex patterns, and if confidence is low, calls an LLM to extract better. Finally, Pydantic validates all fields and returns a clean JSON response.

---

## 🔄 LangGraph Workflow

The pipeline has **7 nodes** and **conditional routing**:

### Nodes:

1. **Docling Node**
   - Extracts text/markdown from PDF using Docling
   - Runs in parallel with LlamaParse

2. **LlamaParse Node**
   - Extracts text/markdown from PDF using LlamaParse
   - Runs in parallel with Docling

3. **Merge Node**
   - Combines text from both parsers
   - Ensures maximum coverage of extracted content

4. **Classify Node**
   - Detects document type
   - Currently returns: `"invoice"`

5. **Rule Extract Node**
   - Regex-based extraction of:
     - Invoice numbers
     - Dates
     - Amounts/Totals
     - Issuer/Vendor name
   - Calculates confidence (0.25 per field found)

6. **Decision Node (Conditional)**
   - **If confidence < 0.5** → Route to LLM Node
   - **If confidence ≥ 0.5** → Route to Validate Node

7. **LLM Node**
   - Calls Google Gemini 2.5-Flash
   - Sends merged text + structured prompt
   - Extracts JSON data
   - Sets confidence to 0.9

8. **Validate Node**
   - Pydantic validation
   - Adds missing field errors
   - Returns final JSON response

### Data Flow:
```
START
  ├→ Docling ──┐
  │            ├→ Merge → Classify → Rule ─┐
  └→ LlamaParse┘                            │
                                     Decision
                                     /        \
                              (< 1)    (= 1)
                               /            \
                            LLM          Validate → END
                             \            /
                              \          /
                               Validate → END
```

---

## 🚀 Run Locally

### 1. Install Packages

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Set API Keys

Create `.env` file:
```bash
GOOGLE_API_KEY=your_gemini_key_here
LLAMA_CLOUD_API_KEY=your_llama_parse_key_here
```

Get keys from:
- Google: https://makersuite.google.com/app/apikey
- LlamaParse: https://www.llamaindex.ai/

### 3. Run Server

```bash
uvicorn main:api --reload
```

Server: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### 1. Health Check
```
GET /health
```
Verify if API is running.

**Postman**:
- Method: `GET`
- URL: `http://localhost:8000/health`
- Click Send

### 2. Extract Single PDF
```
POST /extract
```
Upload one invoice PDF and get extracted data.

**Postman**:
- Method: `POST`
- URL: `http://localhost:8000/extract`
- Body → form-data
- Add key: `file` (type: File)
- Select your PDF file
- Click Send

### 3. Batch Process
```
POST /batch
```
Upload multiple invoice PDFs and get list of results.

**Postman**:
- Method: `POST`
- URL: `http://localhost:8000/batch`
- Body → form-data
- Add key: `files` (type: File) - multiple times for each PDF
- Select your PDF files
- Click Send

---

## 📊 Example Response

**Postman Setup**:
1. Create new request
2. Method: `POST`
3. URL: `http://localhost:8000/extract`
4. Body → form-data → Add `file` (type: File) → Select invoice.pdf
5. Click Send

**Response**:
```json
{
  "document_type": "invoice",
  "issuer": "SuperStore",
  "date": "2012-02-19",
  "totals": {
    "total": 22.17
  },
  "reference_ids": ["39519", "CA-2012-AB10015140-40958"],
  "confidence": 0.75,
  "extraction_method": "rule/llm",
  "errors": []
}
```

---

## 📁 Project Files

- `main.py` - FastAPI app with endpoints
- `graph.py` - LangGraph pipeline
- `parser.py` - PDF parsing (Docling + LlamaParse)
- `extractor.py` - Rule-based + LLM extraction
- `validator.py` - Pydantic validation
- `models.py` - Response schema

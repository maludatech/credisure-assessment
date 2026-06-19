# Part 5: AI Engineering: CrediSure Parse AI

## Scenario

CrediSure Parse AI receives a bank statement PDF and must extract transactions, categorize spending and generate a risk summary for credit assessment.

---

## 1. How would you extract text from PDFs?

Use **pdfplumber** as the primary extraction library, it handles both text-based and scanned PDFs reliably.

```python
import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text
```

For scanned PDFs (images), fall back to **Tesseract OCR** via `pytesseract`:

```python
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_scanned_pdf(file_path: str) -> str:
    images = convert_from_path(file_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text
```

**Decision logic:**

- Try pdfplumber first
- If extracted text is empty or too short, fall back to OCR
- Log extraction method used for debugging

---

## 2. How would you structure extracted data?

After extraction, parse raw text into structured JSON:

```json
{
  "account_holder": "Victor Ugochukwu",
  "account_number": "****1234",
  "statement_period": {
    "from": "2026-01-01",
    "to": "2026-01-31"
  },
  "opening_balance": 150000.0,
  "closing_balance": 373000.0,
  "transactions": [
    {
      "date": "2026-01-03",
      "description": "SALARY PAYMENT - EMPLOYER",
      "amount": 500000.0,
      "type": "credit",
      "category": "income"
    },
    {
      "date": "2026-01-05",
      "description": "JUMIA ONLINE SHOPPING",
      "amount": 15000.0,
      "type": "debit",
      "category": "shopping"
    },
    {
      "date": "2026-01-10",
      "description": "RENT PAYMENT - LANDLORD",
      "amount": 80000.0,
      "type": "debit",
      "category": "rent"
    }
  ],
  "summary": {
    "total_credits": 500000.0,
    "total_debits": 277000.0,
    "net_flow": 223000.0,
    "transaction_count": 15
  }
}
```

This structured format feeds directly into the credit scoring engine.

---

## 3. How would you categorize transactions?

Use a **two-layer approach**:

**Layer 1: Keyword matching (fast, free):**

```python
CATEGORIES = {
    "income": ["salary", "transfer from", "payment received", "credit alert"],
    "food": ["restaurant", "food", "chicken republic", "dominos", "eating"],
    "transport": ["uber", "bolt", "fuel", "petrol", "bus"],
    "shopping": ["jumia", "konga", "amazon", "mall", "store"],
    "utilities": ["dstv", "electricity", "water", "internet", "airtime"],
    "loans": ["loan repayment", "emi", "credit payment"],
    "rent": ["rent", "landlord", "property"],
}

def categorize_by_keyword(description: str) -> str:
    description_lower = description.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in description_lower for keyword in keywords):
            return category
    return "other"
```

**Layer 2: AI fallback for uncategorized transactions:**
Send only uncategorized transactions to GPT-4o-mini for classification. This keeps AI costs low while handling edge cases keyword matching can't cover.

---

## 4. Prompt Engineering vs Fine-Tuning vs RAG

**Choice: Prompt Engineering**

**Why not Fine-Tuning:**

- Requires a large labeled dataset of Nigerian bank transactions
- Expensive to train and maintain
- Overkill for transaction categorization where patterns are consistent

**Why not RAG:**

- RAG is best for knowledge retrieval from a document corpus
- Transaction categorization is a classification task, not a retrieval task
- Adds unnecessary complexity and latency for no benefit here

**Why Prompt Engineering:**

- Works immediately with zero training data
- Easy to update categories by changing the prompt
- GPT-4o-mini is accurate enough for this use case
- Cost-effective when combined with keyword pre-filtering

**Example prompt:**

```
You are a financial transaction categorizer for Nigerian bank statements.

Categorize this transaction into one of these categories:
income, food, transport, shopping, utilities, loans, rent, entertainment, healthcare, other

Transaction: {description} | Amount: {amount} | Type: {type}

Respond with only the category name, nothing else.
```

---

## 5. How would you reduce AI costs?

**Strategy 1: Keyword pre-filtering (most impactful)**
Run keyword matching first. Only send unmatched transactions to the AI. In practice 60-70% of Nigerian bank transactions match known keywords, reducing AI calls by the same amount.

**Strategy 2: Batch processing**
Instead of one API call per transaction, batch 20 transactions per prompt:

```
Categorize these 20 transactions and return a JSON array of categories in the same order...
```

**Strategy 3: Use GPT-4o-mini instead of GPT-4**
GPT-4o-mini costs 95% less than GPT-4 and is accurate enough for transaction categorization which is a simple classification task.

**Strategy 4: Cache common descriptions**
Store categorization results in Redis. If the same merchant description appears again (e.g. "JUMIA ONLINE SHOPPING"), return the cached result without an API call.

**Strategy 5: Process asynchronously**
Run AI categorization as a background job after upload. The user gets an immediate upload confirmation while AI processes in the background. No latency cost is paid at upload time.

**Estimated cost reduction: 85-90% vs naive one-call-per-transaction approach.**

---

## AI Workflow Diagram

```
PDF Upload
    ↓
Text Extraction (pdfplumber / Tesseract OCR fallback)
    ↓
Transaction Parsing (regex + structured JSON)
    ↓
Keyword Categorization (free, instant — covers ~65% of transactions)
    ↓
Uncategorized transactions → GPT-4o-mini (batched, ~35% of transactions)
    ↓
Merged categorized transaction list
    ↓
Spending summary generation
    ↓
Risk summary → Credit Assessment Engine → Credit Score
```

---

## Integration with Upload Endpoint

In production, the `/upload-statement` endpoint would trigger this workflow asynchronously after storing the file in S3:

```python
@app.post("/upload-statement")
async def upload_statement(file: UploadFile, background_tasks: BackgroundTasks, ...):
    # 1. Store file in S3
    s3_url = await upload_to_s3(file)

    # 2. Save metadata to database
    document = UploadedDocument(user_id=user.id, file_name=file.filename, ...)
    db.add(document)
    db.commit()

    # 3. Trigger AI parsing in background
    background_tasks.add_task(parse_bank_statement, document.id, s3_url)

    return {"message": "Upload successful", "status": "processing"}
```

The background task runs the full Parse AI pipeline and updates the credit assessment once complete.

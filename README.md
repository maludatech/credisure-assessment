# CrediSure Full Stack Assessment

A full-stack credit intelligence platform built as part of the CrediSure Financial Technologies engineering assessment.

## Live Demo

- **Frontend:** https://credisure-assessment.vercel.app
- **Backend API:** https://credisure-assessment.onrender.com
- **API Docs:** https://credisure-assessment.onrender.com/docs

## Project Structure

```
credisure-assessment/
├── frontend/                    # Next.js 16, TypeScript, TailwindCSS
│   ├── app/
│   │   ├── page.tsx             # Login page
│   │   ├── register/page.tsx    # Register page
│   │   ├── dashboard/page.tsx   # Dashboard with credit score
│   │   └── upload/page.tsx      # Bank statement upload
│   └── components/ui/           # ShadCN UI components
├── backend/                     # Python FastAPI
│   ├── main.py                  # All API routes and database models
│   ├── requirements.txt         # Python dependencies
│   └── runtime.txt              # Python version for Render
├── README.md
├── ARCHITECTURE.md              # System design and cloud architecture
├── AI_ENGINEERING.md            # AI workflow documentation
└── DATABASE.md                  # Database schema and ER diagram
```

## Tech Stack

| Layer    | Technology                                        |
| -------- | ------------------------------------------------- |
| Frontend | Next.js 16, TypeScript, TailwindCSS v4, ShadCN UI |
| Backend  | Python 3.11, FastAPI, Pydantic, SQLAlchemy        |
| Database | Neon PostgreSQL (persistent, serverless)          |
| Auth     | JWT via python-jose, bcrypt password hashing      |
| Hosting  | Vercel (frontend) + Render (backend)              |

## Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.11+

### Frontend

```bash
cd frontend
npm install
```

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=https://credisure-assessment.onrender.com
```

```bash
npm run dev
```

Open http://localhost:3000

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

```bash
python -m uvicorn main:app --reload
```

API runs at http://localhost:8000
API docs at http://localhost:8000/docs

## API Endpoints

| Method | Endpoint          | Description                 | Auth |
| ------ | ----------------- | --------------------------- | ---- |
| POST   | /register         | Create account, returns JWT | No   |
| POST   | /login            | Login, returns JWT          | No   |
| POST   | /assessment       | Calculate credit score      | Yes  |
| POST   | /upload-statement | Upload PDF bank statement   | Yes  |
| GET    | /me               | Get current user profile    | Yes  |
| GET    | /health           | Health check                | No   |

### Register

```bash
curl -X POST https://credisure-assessment.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Victor Ugochukwu", "email": "victor@example.com", "password": "password123"}'
```

### Credit Assessment

```bash
curl -X POST https://credisure-assessment.onrender.com/assessment \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"monthly_income": 500000, "monthly_expense": 250000, "existing_loans": 50000}'
```

Response:

```json
{
  "credit_score": 780,
  "rating": "Very Good",
  "risk_level": "Low Risk",
  "funding_readiness": "Ready"
}
```

## Database Schema

Six tables with full relationships:

- **users**: account credentials and profile
- **kyc_records**: KYC verification status (BVN, NIN)
- **credit_assessments**: credit score history per user
- **uploaded_documents**: bank statement metadata
- **loan_applications**: funding applications linked to assessments
- **businesses**: business profile for SME users

See `DATABASE.md` for full ER diagram and table structures.

## Credit Score Algorithm

Score calculated based on three financial ratios:

| Factor                        | Impact      |
| ----------------------------- | ----------- |
| Expense ratio > 80% of income | -200 points |
| Expense ratio 60-80%          | -120 points |
| Expense ratio 40-60%          | -60 points  |
| Loan ratio > 40% of income    | -150 points |
| Loan ratio 20-40%             | -80 points  |
| Savings rate > 30%            | +50 points  |
| Negative savings rate         | -100 points |

Score range: 300-850

| Score   | Rating    | Risk Level     |
| ------- | --------- | -------------- |
| 800-850 | Excellent | Very Low Risk  |
| 740-799 | Very Good | Low Risk       |
| 670-739 | Good      | Moderate Risk  |
| 580-669 | Fair      | High Risk      |
| 300-579 | Poor      | Very High Risk |

## Known Limitations

File uploads store metadata only in the demo. Production would use AWS S3 for actual PDF storage with pre-signed URLs for secure access. The AI parsing pipeline (PDF extraction, transaction categorization, risk summary generation) is documented in AI_ENGINEERING.md as a design specification, the full implementation would connect the upload endpoint to the Parse AI workflow described there.

## Architecture

See `ARCHITECTURE.md` for full system design including AWS cloud deployment diagram, security model, scalability approach and cost estimates.

## AI Engineering

See `AI_ENGINEERING.md` for the complete AI workflow for bank statement parsing including PDF extraction, transaction categorization, prompt engineering approach, and cost reduction strategies.

# CrediSure Full Stack Assessment

A full-stack credit intelligence platform built as part of
the CrediSure Financial Technologies engineering assessment.

## Project Structure

credisure-assessment/
├── frontend/ # Next.js 15, TypeScript, TailwindCSS
└── backend/ # Python FastAPI, SQLAlchemy, MySQL

## Live Demo

- Frontend: [coming soon]
- Backend API: [coming soon]

## Tech Stack

| Layer        | Technology                          |
| ------------ | ----------------------------------- |
| Frontend     | Next.js 15, TypeScript, TailwindCSS |
| Backend      | Python, FastAPI, SQLAlchemy         |
| Database     | MySQL                               |
| Auth         | JWT                                 |
| File Storage | AWS S3                              |
| Hosting      | Vercel + Render                     |

## Setup Instructions

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Architecture

See ARCHITECTURE.md for full system design documentation.

## API Documentation

See backend/README.md for API endpoint documentation.

## Database Schema

See DATABASE.md for ER diagram and table structures.

## System Architecture

### Overview

CrediSure is a credit intelligence platform that enables
users to register, complete KYC, upload bank statements,
receive credit assessments, and apply for funding.

### Frontend — Next.js on Vercel

- Next.js 15 App Router with TypeScript and TailwindCSS
- JWT stored in httpOnly cookies for security
- Three core pages: Login, Dashboard, Upload
- Responsive across mobile and desktop

### Backend — FastAPI on Render

- Python FastAPI with Pydantic for request validation
- SQLAlchemy ORM for MySQL database interaction
- JWT authentication with access tokens
- RESTful API design with proper error handling

### Database — MySQL

- Six relational tables: Users, KYC Records,
  Credit Assessments, Uploaded Documents,
  Loan Applications, Businesses
- Foreign key relationships maintaining data integrity
- Indexed on user_id for query performance

### File Storage — AWS S3

- Bank statement PDFs uploaded to S3
- Pre-signed URLs for secure file access
- File metadata stored in MySQL

### Authentication Flow

1. User registers → password hashed with bcrypt
2. User logs in → JWT access token returned
3. Token sent in Authorization header on protected routes
4. Token verified on every protected endpoint

### Credit Score Algorithm

Score calculated based on:

- Debt-to-income ratio
- Expense-to-income ratio
- Existing loan burden
  Score range: 300-850
  Ratings: Poor / Fair / Good / Very Good / Excellent

### Cloud Deployment — AWS

- Frontend: Vercel (automatic CI/CD from GitHub)
- Backend: Render or AWS ECS
- Database: AWS RDS MySQL
- Storage: AWS S3
- CDN: AWS CloudFront
- Monitoring: AWS CloudWatch
- Backups: Automated RDS snapshots daily

### AI Engineering — Parse AI Workflow

1. PDF received → text extracted using PyMuPDF/pdfplumber
2. Transactions parsed and structured into JSON
3. Spending categorized using prompt engineering with GPT-4
4. Risk summary generated based on spending patterns
5. Results fed into credit assessment engine

## Known Limitations

The demo uses SQLite for simplicity. In production this would
be replaced with AWS RDS MySQL for persistent, scalable storage.
Render's free tier has an ephemeral filesystem so registered
users may be lost on server restart — this is expected behavior
for the demo environment.

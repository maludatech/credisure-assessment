# Part 1 & Part 6: System Design & Cloud Architecture

## System Overview

CrediSure is a credit intelligence platform enabling users to register, complete KYC, upload bank statements, receive credit assessment scores and apply for funding.

---

## Part 1: System Architecture

### Frontend Architecture

- **Framework:** Next.js 16 with App Router and TypeScript
- **Styling:** Tailwind CSS v4 with ShadCN UI components
- **Auth:** JWT tokens stored in localStorage, validated on every protected route
- **Pages:** Login, Register, Dashboard, Upload
- **Dark Mode:** Forced globally via `dark` class on html element
- **Form Validation:** Email regex, required field checks, password minimum length
- **Hosting:** Vercel with automatic CI/CD from GitHub

### Backend Architecture

- **Framework:** Python FastAPI
- **Validation:** Pydantic v2 for request/response schema validation
- **ORM:** SQLAlchemy with Neon PostgreSQL
- **Auth:** JWT tokens via python-jose, bcrypt for password hashing
- **Hosting:** Render (demo) / AWS ECS Fargate (production)

### Database Design

- **Demo + Production:** Neon PostgreSQL (persistent, serverless, free tier)
- **ORM:** SQLAlchemy with psycopg2-binary driver
- **Tables:** users, kyc_records, credit_assessments, uploaded_documents, loan_applications, businesses
- **Persistence:** Data survives server restarts, no ephemeral storage concerns

### File Storage

- **Demo:** File metadata stored in PostgreSQL only
- **Production:** AWS S3 for PDF bank statements with pre-signed URLs for secure access

### Authentication Flow

1. User registers → password hashed with bcrypt
2. User logs in → JWT access token returned (24hr expiry)
3. Token sent in Authorization header on all protected routes
4. Backend validates token and extracts user email on every request

### Credit Score Algorithm

Factors considered:

- Expense-to-income ratio (deducted if high)
- Loan-to-income ratio (deducted if high)
- Savings rate (rewarded if positive)

Score range: 300-850
Ratings: Poor / Fair / Good / Very Good / Excellent

---

## Part 6: AWS Cloud Architecture

### Services Used

| Component     | AWS Service               | Purpose                           |
| ------------- | ------------------------- | --------------------------------- |
| Frontend      | Vercel / S3 + CloudFront  | Next.js hosting and CDN           |
| Backend       | ECS Fargate               | Containerized FastAPI             |
| Database      | RDS PostgreSQL (Multi-AZ) | Persistent relational storage     |
| File Storage  | S3                        | Bank statement PDF storage        |
| Load Balancer | ALB                       | Traffic distribution              |
| DNS           | Route 53                  | Domain management                 |
| Secrets       | Secrets Manager           | API keys and DB credentials       |
| Monitoring    | CloudWatch                | Logs, metrics, alarms             |
| Cache         | ElastiCache Redis         | Session cache and AI result cache |

### Architecture Diagram (Text)

```
                    Internet
                       │
                  Route 53 (DNS)
                       │
              CloudFront (CDN)
                       │
            ┌──────────┴──────────┐
            │                     │
      Next.js (Vercel)     Application Load Balancer
                                  │
                         ┌────────┴────────┐
                         │                 │
                    ECS Fargate       ECS Fargate
                   (FastAPI #1)      (FastAPI #2)
                         │                 │
                    ┌────┴─────────────────┘
                    │
          ┌─────────┴──────────┐
          │                    │
    RDS PostgreSQL         S3 Bucket
    (Multi-AZ)          (Bank Statements)
          │
    ElastiCache
      (Redis)
```

### Security

**Network:**

- VPC with public and private subnets
- ECS tasks in private subnets (no direct internet access)
- ALB in public subnet
- RDS in private subnet (only accessible from ECS)
- Security groups restricting traffic between components

**Application:**

- All API keys stored in AWS Secrets Manager
- S3 bucket private: access via pre-signed URLs only (15-minute expiry)
- JWT tokens with 24-hour expiry
- HTTPS enforced everywhere via SSL/TLS certificates (ACM)
- bcrypt password hashing

**Data:**

- RDS encryption at rest enabled
- S3 server-side encryption (AES-256)
- CloudTrail for audit logging
- SSL required on all database connections (`sslmode=require`)

### Scalability

**Horizontal scaling:**

- ECS Fargate auto-scales based on CPU/memory metrics
- Target tracking policy: scale out at 70% CPU
- Minimum 2 tasks, maximum 10 tasks

**Database:**

- RDS Multi-AZ for high availability and automatic failover
- Read replicas for reporting queries
- ElastiCache Redis for frequently accessed data (credit scores, user sessions)

**CDN:**

- CloudFront caches static assets globally
- Reduces latency for international users

### Monitoring

**CloudWatch:**

- API response time alarms (alert if p99 > 2 seconds)
- Error rate alarms (alert if 5xx > 1%)
- RDS CPU and connection count monitoring
- Custom metrics for credit assessment volume

**Logging:**

- Structured JSON logs from FastAPI to CloudWatch Logs
- Log retention: 30 days
- Log Insights for querying production issues

### Backups

**RDS:**

- Automated daily snapshots retained for 7 days
- Point-in-time recovery enabled
- Cross-region backup copy to a secondary region

**S3:**

- Versioning enabled on bank statement bucket
- Cross-region replication for disaster recovery
- Lifecycle policy: move to S3 Glacier after 90 days

### Estimated Monthly Cost (Production)

| Service                                | Estimated Cost  |
| -------------------------------------- | --------------- |
| ECS Fargate (2 tasks)                  | ~$30            |
| RDS PostgreSQL (db.t3.medium Multi-AZ) | ~$80            |
| S3 (100GB storage)                     | ~$3             |
| ALB                                    | ~$20            |
| ElastiCache (cache.t3.micro)           | ~$15            |
| CloudFront                             | ~$5             |
| **Total**                              | **~$153/month** |

---

## Technology Choices — Justification

### Why Next.js?

- Hybrid rendering (SSR + CSR) for optimal performance
- Built-in API routes reduce infrastructure complexity
- Strong TypeScript support
- Vercel deployment is seamless and free for demo

### Why FastAPI?

- Python-native: aligns with AI/ML ecosystem
- Automatic OpenAPI documentation at /docs
- Pydantic integration for type-safe request validation
- Async support for high-concurrency scenarios

### Why SQLAlchemy?

- Database-agnostic ORM: switch between databases with one config change
- Relationship mapping reduces boilerplate
- Migration support via Alembic for production schema changes

### Why Neon PostgreSQL?

- Serverless PostgreSQL with persistent storage
- Free tier sufficient for demo and early production
- SSL enforced by default
- No ephemeral storage issues unlike SQLite on Render
- Scales to production with connection pooling via PgBouncer

### Why JWT?

- Stateless: no server-side session storage required
- Scales horizontally without session synchronization
- Industry standard for API authentication

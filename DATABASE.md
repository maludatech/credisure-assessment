# Part 4: Database Design

## ER Diagram (Text)

```
users
  │
  ├──< kyc_records (one-to-one)
  │
  ├──< credit_assessments (one-to-many)
  │         │
  │         └──< loan_applications (one-to-many)
  │
  ├──< uploaded_documents (one-to-many)
  │
  └──< businesses (one-to-many)
```

---

## Table Structures

### users

| Column        | Type         | Constraints                 |
| ------------- | ------------ | --------------------------- |
| id            | INT          | PRIMARY KEY, AUTO_INCREMENT |
| full_name     | VARCHAR(255) | NOT NULL                    |
| email         | VARCHAR(255) | UNIQUE, NOT NULL, INDEX     |
| password_hash | VARCHAR(255) | NOT NULL                    |
| created_at    | DATETIME     | DEFAULT CURRENT_TIMESTAMP   |

### kyc_records

| Column      | Type        | Constraints                      |
| ----------- | ----------- | -------------------------------- |
| id          | INT         | PRIMARY KEY, AUTO_INCREMENT      |
| user_id     | INT         | FOREIGN KEY → users.id, NOT NULL |
| bvn         | VARCHAR(11) | NULLABLE                         |
| nin         | VARCHAR(11) | NULLABLE                         |
| kyc_status  | VARCHAR(20) | DEFAULT 'pending'                |
| verified_at | DATETIME    | NULLABLE                         |

### credit_assessments

| Column            | Type          | Constraints                      |
| ----------------- | ------------- | -------------------------------- |
| id                | INT           | PRIMARY KEY, AUTO_INCREMENT      |
| user_id           | INT           | FOREIGN KEY → users.id, NOT NULL |
| monthly_income    | DECIMAL(15,2) | NOT NULL                         |
| monthly_expense   | DECIMAL(15,2) | NOT NULL                         |
| existing_loans    | DECIMAL(15,2) | DEFAULT 0                        |
| credit_score      | INT           | NOT NULL                         |
| rating            | VARCHAR(50)   | NOT NULL                         |
| risk_level        | VARCHAR(50)   | NOT NULL                         |
| funding_readiness | VARCHAR(20)   | NOT NULL                         |
| assessed_at       | DATETIME      | DEFAULT CURRENT_TIMESTAMP        |

### uploaded_documents

| Column        | Type         | Constraints                      |
| ------------- | ------------ | -------------------------------- |
| id            | INT          | PRIMARY KEY, AUTO_INCREMENT      |
| user_id       | INT          | FOREIGN KEY → users.id, NOT NULL |
| file_name     | VARCHAR(255) | NOT NULL                         |
| file_size     | INT          | NULLABLE                         |
| document_type | VARCHAR(50)  | DEFAULT 'bank_statement'         |
| uploaded_at   | DATETIME     | DEFAULT CURRENT_TIMESTAMP        |
| status        | VARCHAR(20)  | DEFAULT 'processing'             |

### loan_applications

| Column           | Type          | Constraints                                   |
| ---------------- | ------------- | --------------------------------------------- |
| id               | INT           | PRIMARY KEY, AUTO_INCREMENT                   |
| user_id          | INT           | FOREIGN KEY → users.id, NOT NULL              |
| assessment_id    | INT           | FOREIGN KEY → credit_assessments.id, NOT NULL |
| amount_requested | DECIMAL(15,2) | NOT NULL                                      |
| purpose          | VARCHAR(500)  | NULLABLE                                      |
| status           | VARCHAR(20)   | DEFAULT 'pending'                             |
| applied_at       | DATETIME      | DEFAULT CURRENT_TIMESTAMP                     |

### businesses

| Column              | Type          | Constraints                      |
| ------------------- | ------------- | -------------------------------- |
| id                  | INT           | PRIMARY KEY, AUTO_INCREMENT      |
| user_id             | INT           | FOREIGN KEY → users.id, NOT NULL |
| business_name       | VARCHAR(255)  | NOT NULL                         |
| registration_number | VARCHAR(100)  | NULLABLE                         |
| industry            | VARCHAR(100)  | NULLABLE                         |
| annual_revenue      | DECIMAL(15,2) | NULLABLE                         |
| created_at          | DATETIME      | DEFAULT CURRENT_TIMESTAMP        |

---

## Relationships

- **users → kyc_records:** One-to-one. Each user has one KYC record.
- **users → credit_assessments:** One-to-many. Each user can have multiple assessments over time.
- **users → uploaded_documents:** One-to-many. Each user can upload multiple bank statements.
- **users → loan_applications:** One-to-many. Each user can apply for multiple loans.
- **users → businesses:** One-to-many. A user can register multiple businesses.
- **credit_assessments → loan_applications:** One-to-many. Each loan application references the assessment it was based on.

---

## MySQL DDL

```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  full_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_email (email)
);

CREATE TABLE kyc_records (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  bvn VARCHAR(11),
  nin VARCHAR(11),
  kyc_status VARCHAR(20) DEFAULT 'pending',
  verified_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE credit_assessments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  monthly_income DECIMAL(15,2) NOT NULL,
  monthly_expense DECIMAL(15,2) NOT NULL,
  existing_loans DECIMAL(15,2) DEFAULT 0,
  credit_score INT NOT NULL,
  rating VARCHAR(50) NOT NULL,
  risk_level VARCHAR(50) NOT NULL,
  funding_readiness VARCHAR(20) NOT NULL,
  assessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE uploaded_documents (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_size INT,
  document_type VARCHAR(50) DEFAULT 'bank_statement',
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(20) DEFAULT 'processing',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE loan_applications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  assessment_id INT NOT NULL,
  amount_requested DECIMAL(15,2) NOT NULL,
  purpose VARCHAR(500),
  status VARCHAR(20) DEFAULT 'pending',
  applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (assessment_id) REFERENCES credit_assessments(id)
);

CREATE TABLE businesses (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  business_name VARCHAR(255) NOT NULL,
  registration_number VARCHAR(100),
  industry VARCHAR(100),
  annual_revenue DECIMAL(15,2),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

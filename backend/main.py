from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CrediSure API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://credisure-assessment.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "credisure-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In-memory store for demo
users_db = {}
assessments_db = {}
documents_db = {}


# ── Models
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AssessmentRequest(BaseModel):
    monthly_income: float
    monthly_expense: float
    existing_loans: float = 0

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


# ── Helpers
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return users_db[email]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def calculate_credit_score(
    monthly_income: float,
    monthly_expense: float,
    existing_loans: float
) -> dict:
    if monthly_income <= 0:
        raise HTTPException(status_code=400, detail="Monthly income must be greater than 0")

    expense_ratio = monthly_expense / monthly_income
    loan_ratio = existing_loans / monthly_income
    savings_rate = (monthly_income - monthly_expense - existing_loans) / monthly_income

    # Base score
    score = 850

    # Deduct for high expense ratio
    if expense_ratio > 0.8:
        score -= 200
    elif expense_ratio > 0.6:
        score -= 120
    elif expense_ratio > 0.4:
        score -= 60
    else:
        score -= 20

    # Deduct for loan burden
    if loan_ratio > 0.4:
        score -= 150
    elif loan_ratio > 0.2:
        score -= 80
    elif loan_ratio > 0.1:
        score -= 30

    # Reward for savings
    if savings_rate > 0.3:
        score += 50
    elif savings_rate > 0.2:
        score += 30
    elif savings_rate < 0:
        score -= 100

    score = max(300, min(850, score))

    if score >= 800:
        rating = "Excellent"
        risk_level = "Very Low Risk"
    elif score >= 740:
        rating = "Very Good"
        risk_level = "Low Risk"
    elif score >= 670:
        rating = "Good"
        risk_level = "Moderate Risk"
    elif score >= 580:
        rating = "Fair"
        risk_level = "High Risk"
    else:
        rating = "Poor"
        risk_level = "Very High Risk"

    return {
        "credit_score": score,
        "rating": rating,
        "risk_level": risk_level,
        "funding_readiness": "Ready" if score >= 670 else "Not Ready"
    }


# ── Routes

@app.get("/")
def root():
    return {"message": "CrediSure API", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest):
    if body.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(body.password)
    user = {
        "full_name": body.full_name,
        "email": body.email,
        "password_hash": hashed,
        "created_at": datetime.utcnow().isoformat()
    }
    users_db[body.email] = user

    token = create_token({"sub": body.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"full_name": body.full_name, "email": body.email}
    }


@app.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = users_db.get(body.email)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"sub": body.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"full_name": user["full_name"], "email": user["email"]}
    }


@app.post("/assessment")
def assess_credit(
    body: AssessmentRequest,
    current_user: dict = Depends(get_current_user)
):
    result = calculate_credit_score(
        body.monthly_income,
        body.monthly_expense,
        body.existing_loans
    )
    assessments_db[current_user["email"]] = result
    return result


@app.post("/upload-statement")
def upload_statement(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    document = {
        "file_name": file.filename,
        "file_size": file.size,
        "document_type": "bank_statement",
        "uploaded_by": current_user["email"],
        "uploaded_at": datetime.utcnow().isoformat(),
        "status": "processing"
    }
    documents_db[current_user["email"]] = document

    return {
        "message": "Bank statement uploaded successfully",
        "file_name": file.filename,
        "status": "processing",
        "uploaded_at": document["uploaded_at"]
    }


@app.get("/me")
def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "full_name": current_user["full_name"],
        "email": current_user["email"],
        "created_at": current_user["created_at"]
    }
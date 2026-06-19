from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# ── Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./credisure.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    assessments = relationship("CreditAssessment", back_populates="user")
    documents = relationship("UploadedDocument", back_populates="user")
    kyc = relationship("KYCRecord", back_populates="user", uselist=False)
    businesses = relationship("Business", back_populates="user")
    loan_applications = relationship("LoanApplication", back_populates="user")


class KYCRecord(Base):
    __tablename__ = "kyc_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bvn = Column(String(11))
    nin = Column(String(11))
    kyc_status = Column(String(20), default="pending")
    verified_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="kyc")


class CreditAssessment(Base):
    __tablename__ = "credit_assessments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    monthly_income = Column(Float, nullable=False)
    monthly_expense = Column(Float, nullable=False)
    existing_loans = Column(Float, default=0)
    credit_score = Column(Integer, nullable=False)
    rating = Column(String(50), nullable=False)
    risk_level = Column(String(50), nullable=False)
    funding_readiness = Column(String(20), default="Not Ready")
    assessed_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="assessments")
    loan_applications = relationship("LoanApplication", back_populates="assessment")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    document_type = Column(String(50), default="bank_statement")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="processing")
    user = relationship("User", back_populates="documents")


class LoanApplication(Base):
    __tablename__ = "loan_applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("credit_assessments.id"), nullable=False)
    amount_requested = Column(Float, nullable=False)
    purpose = Column(String(500))
    status = Column(String(20), default="pending")
    applied_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="loan_applications")
    assessment = relationship("CreditAssessment", back_populates="loan_applications")


class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String(255), nullable=False)
    registration_number = Column(String(100))
    industry = Column(String(100))
    annual_revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="businesses")


# Create all tables
Base.metadata.create_all(bind=engine)

# ── App
app = FastAPI(title="CrediSure API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Security
SECRET_KEY = os.getenv("SECRET_KEY", "credisure-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
security = HTTPBearer()


# ── DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Pydantic Schemas
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


# ── Helpers
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
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

    score = 850

    if expense_ratio > 0.8:
        score -= 200
    elif expense_ratio > 0.6:
        score -= 120
    elif expense_ratio > 0.4:
        score -= 60
    else:
        score -= 20

    if loan_ratio > 0.4:
        score -= 150
    elif loan_ratio > 0.2:
        score -= 80
    elif loan_ratio > 0.1:
        score -= 30

    if savings_rate > 0.3:
        score += 50
    elif savings_rate > 0.2:
        score += 30
    elif savings_rate < 0:
        score -= 100

    score = max(300, min(850, score))

    if score >= 800:
        rating, risk_level = "Excellent", "Very Low Risk"
    elif score >= 740:
        rating, risk_level = "Very Good", "Low Risk"
    elif score >= 670:
        rating, risk_level = "Good", "Moderate Risk"
    elif score >= 580:
        rating, risk_level = "Fair", "High Risk"
    else:
        rating, risk_level = "Poor", "Very High Risk"

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


@app.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=body.full_name,
        email=body.email,
        password_hash=hash_password(body.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"full_name": user.full_name, "email": user.email}
    }


@app.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"full_name": user.full_name, "email": user.email}
    }


@app.post("/assessment")
def assess_credit(
    body: AssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = calculate_credit_score(
        body.monthly_income,
        body.monthly_expense,
        body.existing_loans
    )

    assessment = CreditAssessment(
        user_id=current_user.id,
        monthly_income=body.monthly_income,
        monthly_expense=body.monthly_expense,
        existing_loans=body.existing_loans,
        credit_score=result["credit_score"],
        rating=result["rating"],
        risk_level=result["risk_level"],
        funding_readiness=result["funding_readiness"]
    )
    db.add(assessment)
    db.commit()

    return result


@app.post("/upload-statement")
def upload_statement(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    document = UploadedDocument(
        user_id=current_user.id,
        file_name=file.filename,
        file_size=file.size,
        document_type="bank_statement",
        status="processing"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "Bank statement uploaded successfully",
        "file_name": file.filename,
        "status": "processing",
        "uploaded_at": document.uploaded_at.isoformat()
    }


@app.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }
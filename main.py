from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext

from app_logic import SessionLocal, User, Document, rag_engine

app = FastAPI(title="Financial Document API")

# Security Config
SECRET_KEY = "your-hand-written-secret"
# Switching to pbkdf2 to avoid bcrypt version conflicts on Windows
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Helper: Database session
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# Helper: Get current user and check RBAC
def get_user_with_role(required_roles: list):
    def user_checker(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        if not user or user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Access Denied")
        return user
    return user_checker

# --- ENDPOINTS ---

@app.post("/auth/register")
def register(username: str, password: str, role: str, db: Session = Depends(get_db)):
    hashed = pwd_context.hash(password)
    new_user = User(username=username, hashed_password=hashed, role=role)
    db.add(new_user)
    db.commit()
    return {"status": "User registered"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong credentials")
    
    token = jwt.encode({"sub": user.username}, SECRET_KEY)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/documents/upload")
async def upload_document(
    title: str = Form(...),
    company: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_user_with_role(["Admin", "Financial Analyst"])),
    db: Session = Depends(get_db)
):
    # In a real scenario, use a PDF library. Here we read text for simplicity.
    content = (await file.read()).decode("utf-8", errors="ignore")
    
    # Save Metadata to SQL
    new_doc = Document(
        title=title, company_name=company, 
        doc_type=doc_type, uploaded_by=user.username
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # Index in RAG
    rag_engine.process_document(content, new_doc.id, title)
    
    return {"message": "Document processed semantically", "doc_id": new_doc.id}

@app.get("/documents")
def list_docs(db: Session = Depends(get_db), user: User = Depends(get_user_with_role(["Admin", "Auditor", "Financial Analyst", "Client"]))):
    return db.query(Document).all()

@app.post("/rag/search")
def search(query: str, user: User = Depends(get_user_with_role(["Admin", "Financial Analyst", "Auditor", "Client"]))):
    results = rag_engine.search_with_reranking(query)
    return {"query": query, "top_5_results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
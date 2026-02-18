from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from jose import JWTError, jwt
import bcrypt
import uuid
import os

# App initialization
app = FastAPI(title="Todo API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# In-memory storage (replace with database in production)
users_db = {}
tasks_db = {}

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    createdAt: str
    updatedAt: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: str
    userId: str
    title: str
    description: Optional[str]
    completed: bool
    createdAt: str
    updatedAt: str
    completedAt: Optional[str]

class TokenResponse(BaseModel):
    user: UserResponse
    token: str

# Helper functions
def generate_timestamp() -> str:
    return datetime.utcnow().isoformat()

def hash_password(password: str) -> str:
    # Hash password with bcrypt
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Helper to extract token from Authorization header
def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.split(" ")[1]

# Authentication dependency
def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    token = get_token_from_header(authorization)
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id or user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return users_db[user_id]

# Routes
@app.get("/")
def root():
    return {"message": "Todo API is running", "version": "1.0.0"}

@app.get("/api/health")
def health_check():
    return {"status": "OK", "timestamp": generate_timestamp()}

@app.post("/api/auth/signup", response_model=TokenResponse)
def signup(user_data: UserCreate):
    # Check if user exists
    for user in users_db.values():
        if user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
    
    # Create user
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password": hash_password(user_data.password),
        "createdAt": generate_timestamp(),
        "updatedAt": generate_timestamp()
    }
    
    users_db[user_id] = user
    
    # Create token
    token = create_access_token({"sub": user_id})
    
    # Return user without password
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        createdAt=user["createdAt"],
        updatedAt=user["updatedAt"]
    )
    
    return {"user": user_response, "token": token}

@app.post("/api/auth/signin", response_model=TokenResponse)
def signin(login_data: UserLogin):
    # Find user
    user = None
    for u in users_db.values():
        if u["email"] == login_data.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create token
    token = create_access_token({"sub": user["id"]})
    
    # Return user without password
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        createdAt=user["createdAt"],
        updatedAt=user["updatedAt"]
    )
    
    return {"user": user_response, "token": token}

@app.post("/api/auth/signout")
def signout():
    return {"message": "Signed out successfully"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        createdAt=current_user["createdAt"],
        updatedAt=current_user["updatedAt"]
    )

@app.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks(current_user: dict = Depends(get_current_user)):
    user_tasks = [
        task for task in tasks_db.values() 
        if task["userId"] == current_user["id"]
    ]
    
    # Sort by completion and date
    user_tasks.sort(key=lambda x: (x["completed"], x["createdAt"]), reverse=True)
    
    return [
        TaskResponse(
            id=task["id"],
            userId=task["userId"],
            title=task["title"],
            description=task.get("description"),
            completed=task["completed"],
            createdAt=task["createdAt"],
            updatedAt=task["updatedAt"],
            completedAt=task.get("completedAt")
        )
        for task in user_tasks
    ]

@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, current_user: dict = Depends(get_current_user)):
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "userId": current_user["id"],
        "title": task_data.title.strip(),
        "description": task_data.description.strip() if task_data.description else None,
        "completed": False,
        "createdAt": generate_timestamp(),
        "updatedAt": generate_timestamp(),
        "completedAt": None
    }
    
    tasks_db[task_id] = task
    
    return TaskResponse(
        id=task["id"],
        userId=task["userId"],
        title=task["title"],
        description=task.get("description"),
        completed=task["completed"],
        createdAt=task["createdAt"],
        updatedAt=task["updatedAt"],
        completedAt=task.get("completedAt")
    )

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task_data: TaskUpdate, current_user: dict = Depends(get_current_user)):
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task = tasks_db[task_id]
    
    if task["userId"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    # Update fields
    if task_data.title is not None:
        task["title"] = task_data.title.strip()
    if task_data.description is not None:
        task["description"] = task_data.description.strip()
    if task_data.completed is not None:
        task["completed"] = task_data.completed
        task["completedAt"] = generate_timestamp() if task_data.completed else None
    task["updatedAt"] = generate_timestamp()
    
    tasks_db[task_id] = task
    
    return TaskResponse(
        id=task["id"],
        userId=task["userId"],
        title=task["title"],
        description=task.get("description"),
        completed=task["completed"],
        createdAt=task["createdAt"],
        updatedAt=task["updatedAt"],
        completedAt=task.get("completedAt")
    )

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task = tasks_db[task_id]
    
    if task["userId"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    del tasks_db[task_id]
    
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# /app/gateway.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

# Import your modules
from .auth import AuthHandler
from .rate_limit import rate_limit
# Import the Router from main.py
from .main import router as product_router 

app = FastAPI(title="Production Gateway")

# 1. Global Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Login Route (Public)
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.password != "secret":
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token = AuthHandler.create_access_token(
        data={"sub": form_data.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
def health():
    return {"status": "Gateway is running"}

app.include_router(
    product_router,
    prefix="/product",
    tags=["Products"],
    dependencies=[Depends(rate_limit), Depends(AuthHandler.get_current_user)]
)
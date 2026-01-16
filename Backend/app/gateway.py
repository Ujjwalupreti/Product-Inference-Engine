from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from .auth import AuthHandler
from .rate_limit import rate_limit
from .main import router as product_router 
from .db import mongo, User, Signup, Token

app = FastAPI(title="Production Gateway")

@app.on_event("startup")
async def startup_db():
    mongo.connect()
    
@app.on_event("shutdown")
async def shutdown_db():
    mongo.close()    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/signup")
async def signup(user:Signup):
    existing_user = await mongo.db["users"].find_one({"username":user.username})
    if existing_user:
        raise HTTPException(status_code=400,detail = "Username already Taken")
    
    hashed_pwd = AuthHandler.get_password_hash(user.password)
    
    user_doc = User(
        username=user.username,
        email = user.email,
        hashed_password=hashed_pwd
    )
    
    await mongo.db["users"].insert_one(
        user_doc.model_dump(by_alias=True, exclude = ["id"])
    )
    
    return {"message":"User created successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await mongo.db["users"].find_one({"username": form_data.username})
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not AuthHandler.verify_method(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = AuthHandler.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
def health():
    return {"status": "Gateway is running"}

app.include_router(
    product_router,
    prefix="/product",
    tags=["Products"],
    dependencies=[Depends(rate_limit)]
)
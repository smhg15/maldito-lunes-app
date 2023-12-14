from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from db.models.user import Auth, User
from db.schemas.user import user_schema, auth_schema
from db.client import db_client
from bson import ObjectId
from dotenv import load_dotenv
import os

#env
load_dotenv()
ALGORITHM= os.getenv("ALGORITHM")
ACCESS_TOKEN_DURATION=int(os.getenv("ACCESS_TOKEN_DURATION"))
SECRET= os.getenv("SECRET")
#entorno FastAPI
router = APIRouter(responses={status.HTTP_404_NOT_FOUND:{"message":"Ups!... something is wrong"}},
                   tags=["authjwt"])

oauth2 = OAuth2PasswordBearer(tokenUrl="loginjwt")

crypt= CryptContext(schemes=["bcrypt"])

#functions
def search_user(key: str, value):
    #manejo de errores
    try:
        return User(**user_schema(db_client.users.find_one({key:value})))
    except:
        return({"error": f"{key} not found"})

def search_auth(key: str):
    #manejo de errores
    try:
        return Auth(**auth_schema(db_client.auths.find_one({"key":key})))
    except:
        return({"error": f"{key} not found"})

async def current_user(token: str = Depends(oauth2)):
    exception= HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="invalid authentication credentials", 
                    headers= {"WWW-Authenticate" : "Bearer"}) 
    
    
    try:
        username= jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception
        return User(**user_schema(db_client.users.find_one({"username":username})))
    except JWTError:
        raise exception
    
        
#routers
@router.post("/loginjwt", status_code=status.HTTP_200_OK)
async def auth(form: OAuth2PasswordRequestForm = Depends()):
#search user on databases
    userdb= search_user("username", form.username)
    if not type(userdb) == User:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
#search and validate permissions
    authdb=search_auth(userdb.key)
    if not crypt.verify(form.password, authdb.password):
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong password")
#token
    token={"sub":userdb.username,"exp":datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
    return {"access token": jwt.encode(token, SECRET, algorithm=ALGORITHM), "token type": "bearer"}
@router.get("/userjwt")
async def user(user: User = Depends(current_user)):
    return user


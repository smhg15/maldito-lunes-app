from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from db.models.user import Auth, User
from db.schemas.user import user_schema, auth_schema
from db.client import db_client
from bson import ObjectId
from typing import Annotated


#security vars
ALGORITHM= "HS256"
ACCESS_TOKEN_DURATION=5
SECRET= "$€ÇR€7"
#entorno FastAPI
router = APIRouter(prefix="/test", 
                   responses={status.HTTP_404_NOT_FOUND:{"message":"Ups!... something is wrong"}},
                   tags=["test"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login") # user + pass-> ... <- token. tokenUrl: url que usará el frontend para enviar datos del formulario (ej:user, password, id...). Si se valida correctamnente obtendrá un token

crypt= CryptContext(schemes=["bcrypt"])

#ENCODE/HASH
password= "id1"
hashed_password= crypt.hash(password)

#VERIFICACIÓN
verify=crypt.verify(password, hashed_password)

#databases
usersdatabases = [User(id="id1",key= "key1", username= 'user1', email= 'user1@user.com', public= True, player_id= 'idp1', team_id= ['idt1']),
                  User(id="id2",key= 'key2', username= 'user2', email= 'user2@user.com', public= True, player_id= 'idp2', team_id= ['idt2']),
                  User(id="id3",key= 'key3', username= 'user3', email= 'user3@user.com', public= True, player_id= 'idp3', team_id= ['idt3'])]

authdatabases = [Auth(key="key1", password="$2b$12$baSYFDMXcSjB99N5SzOLie/lL2RZcBvErs8s6fqM353TuQ4Ay7YaC")]

#INSERT EN AUTHDATABASES

@router.post("/login", status_code=status.HTTP_200_OK)
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

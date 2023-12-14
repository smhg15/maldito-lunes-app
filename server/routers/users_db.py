from fastapi import APIRouter, HTTPException, status
from db.models.user import User, Data
from db.schemas.user import user_schema, users_schema, auth_schema, data_schema
from db.client import db_client
from passlib.context import CryptContext
from bson import ObjectId


#entorno FastAPI
router = APIRouter(prefix="/usersdb", 
                   responses={status.HTTP_404_NOT_FOUND:{"message":"Ups!... something is wrong"}},
                   tags=["usersdb"])

#TRABAJO PENDIENTE:
#
# validar token para acceder a la información

crypt= CryptContext(schemes=["bcrypt"])

#functions
def search_user(key: str, value):
    #manejo de errores
    try:
        return User(**user_schema(db_client.users.find_one({key:value})))
    except:
        return({"error": f"{key} not found"})

#routers
@router.get("/", response_model= list[User], status_code=status.HTTP_200_OK)
async def users():
    if db_client.users.count_documents({}) > 0:
        return users_schema(db_client.users.find({}))
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No content")

#por PATH when you are searching an specific object
@router.get("/{id}", response_model= User, status_code=status.HTTP_200_OK) # @algo - a esto (@) se le llama decorador
async def user(id: str):
    if type(search_user("_id", ObjectId(id))) == User:
        return search_user("_id", ObjectId(id))
    else: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")


@router.post("/register", response_model= User, status_code=status.HTTP_201_CREATED)
async def user(data: Data):
    if type(search_user("email", data.email)) == User:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The user already exist")
    elif type(search_user("username", data.username)) == User:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The username is already in use, please choose another")
    else:
        data_dict= dict(data)
        hashed_password= crypt.hash(data_dict["password"]) 
        auth_JSON= {"key":data_dict["key"], "password": hashed_password}
        [data_dict.pop(key, None) for key in ["id", "password"]]

        id= db_client.users.insert_one(data_dict).inserted_id #insterta el nuevo usuario en base de datos y guarda el id en una variable
        db_client.auths.insert_one(auth_JSON)
        new_user=user_schema(db_client.users.find_one({"_id":id}))
        return User(**new_user) # crea un usuario de tipo User() con los datos de databases

@router.put("/", response_model= User, status_code=status.HTTP_200_OK)
async def user(user: User):

    user_dict= dict(user)
    del user_dict["id"]
    
    try:
        db_client.users.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict)

    except:
        return {"error": "the user was not updated successfully"}
    return search_user("_id", ObjectId(user.id))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def user(id: str):

    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

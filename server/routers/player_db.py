from fastapi import APIRouter, HTTPException, status
from db.models.player import Player, Statictics
from db.schemas.player import player_schema, players_schema
from db.client import db_client
from bson import ObjectId


#entorno FastAPI
router = APIRouter(prefix="/playersdb", 
                   responses={status.HTTP_404_NOT_FOUND:{"message":"Ups!... something is wrong"}},
                   tags=["playersdb"])

#routers
@router.get("/", response_model= list[Player], status_code=status.HTTP_200_OK)
async def players():
    if db_client.players.count_documents({}) > 0:
        return players_schema(db_client.players.find({}))
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No content")

#por PATH when you are searching an specific object
@router.get("/{id}", response_model= Player, status_code=status.HTTP_200_OK)
async def player(id: str):
    if type(search_player("_id", ObjectId(id))) == Player:
        return search_player("_id", ObjectId(id))
    else: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="player not found")
#por QUERY (http://127.0.0.1:8000/playerquery/?id=1) when you are filter for properties
#@router.get("/playerquery/")
#async def playerquery(id: int):
#    return search_player(id)

@router.post("/", response_model= Player, status_code=status.HTTP_201_CREATED)
async def player(player: Player):
    if type(search_player("_id", player.id)) == Player:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The user already exist")
    else:
        player_dict= dict(player)
        del player_dict["id"]

        id= db_client.players.insert_one(player_dict).inserted_id
        new_player=player_schema(db_client.players.find_one({"_id":id}))
        return Player(**new_player) # crea un jugador de tipo Player() con los datos de databases


@router.put("/", response_model= Player, status_code=status.HTTP_200_OK)
async def player(player: Player):
        
    player_dict= dict(player)
    del player_dict["id"]

    try:
        db_client.players.find_one_and_replace({"_id": ObjectId(player.id)}, player_dict)

    except:
        return {"error": "the player was not updated successfully"}
    return search_player("_id", ObjectId(player.id))

@router.delete("/{id}", response_model= list[Player], status_code=status.HTTP_200_OK)
async def player(id: str):

    found = db_client.players.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="player not found")


#functions

def search_player(key: str, value):
    #manejo de errores
    try:
        return Player(**player_schema(db_client.players.find_one({key:value})))
    except:
        return({"error": f"{key} not found"})

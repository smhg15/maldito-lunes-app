from fastapi import APIRouter, HTTPException, status
from db.models.team import Team
from db.schemas.team import team_schema, teams_schema
from db.client import db_client
from bson import ObjectId


#entorno FastAPI
router = APIRouter(prefix="/teamsdb", 
                   responses={status.HTTP_404_NOT_FOUND:{"message":"Ups!... something is wrong"}},
                   tags=["teamsdb"])

#routers
@router.get("/", response_model= list[Team], status_code=status.HTTP_200_OK)
async def teams():
    if db_client.teams.count_documents({}) > 0:
        return teams_schema(db_client.teams.find({}))
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No content")

#por PATH when you are searching an specific object
@router.get("/{id}", response_model= Team, status_code=status.HTTP_200_OK) # @algo - a esto (@) se le llama decorador
async def team(id: str):
    if type(search_team("_id", ObjectId(id))) == Team:
        return search_team("_id", ObjectId(id))
    else: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
#por QUERY (http://127.0.0.1:8000/teamquery/?id=1) when you are filter for properties
#@router.get("/teamquery/")
#async def teamquery(id: int):
#    return search_team(id)

@router.post("/", response_model= Team, status_code=status.HTTP_201_CREATED)
async def team(team: Team):
    if type(search_team("name", team.name)) == Team:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The team already exist")
    else:
        team_dict= dict(team)
        del team_dict["id"]

        id= db_client.teams.insert_one(team_dict).inserted_id
        new_team=team_schema(db_client.teams.find_one({"_id":id}))
        return Team(**new_team) # crea un usuarios de tipo User() con los datos de databases


@router.put("/", response_model= Team, status_code=status.HTTP_200_OK)
async def team(team: Team):

    team_dict= dict(team)
    del team_dict["id"]
    
    try:
        db_client.teams.find_one_and_replace({"_id": ObjectId(team.id)}, team_dict)

    except:
        return {"error": "the team was not updated successfully"}
    return search_team("_id", ObjectId(team.id))

    
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def team(id: str):

    found = db_client.teams.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="team not found")

#functions

def search_team(key: str, value):
    #manejo de errores
    try:
        return Team(**team_schema(db_client.teams.find_one({key:value})))
    except:
        return({"error": f"{key} not found"})
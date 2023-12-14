from fastapi import FastAPI
from routers import user, player, team, auth, auth_jwt, users_db,player_db,team_db,test
from fastapi.staticfiles import StaticFiles

#entorno FastAPI
app = FastAPI()

@app.get("/") # @something - this (@) is a decorator
async def root():
    return {"message": "Hello World"}

#TEST ROUTER!!!!!!!!!!!!!! ELIMINAR AL FINAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
app.include_router(test.router)
#FIN DE TEST ROUTER!!!!!!!!!!!!!! ELIMINAR AL FINAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#routers
app.include_router(user.router)
app.include_router(users_db.router)
app.include_router(player.router)
app.include_router(player_db.router)
app.include_router(team.router)
app.include_router(team_db.router)
app.include_router(auth.router)
app.include_router(auth_jwt.router)
app.mount("/static", StaticFiles(directory="static"), name="static") # with StaticFiles you could define a path on your directory to acces your statics files (images, documents...) 

# uvicorn main:app --reload /// COMMAND LINE - RUN UVICORN SERVER IN LOCAL HOST $ main: "main.py"; app: "[var] = FastAPI()"
#url root/docs /// swagger
#url root/redoc /// redocly
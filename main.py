from fastapi import FastAPI
import models 
from database import engine
from routers import recipes, auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(recipes.router)
app.include_router(auth.router)
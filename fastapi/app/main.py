from fastapi import FastAPI, Depends
from .models.db import get_database_connection
from .routers import ingredients, tags, recipes

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(
    ingredients.router, prefix="/ingredients", tags=["ingredients"], dependencies=[]
)
app.include_router(tags.router, prefix="/tags")
app.include_router(recipes.router, prefix="/recipes")

from fastapi import FastAPI, Depends
from .models import db
from .routers import ingredients, tags, recipes


app = FastAPI()

db.init_app(app)
app.include_router(
    ingredients.router, prefix="/ingredients", tags=["ingredients"], dependencies=[]
)
app.include_router(tags.router, prefix="/tags")
app.include_router(recipes.router, prefix="/recipes")

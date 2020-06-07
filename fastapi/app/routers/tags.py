from typing import List
from sqlalchemy.sql.expression import exists
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from databases import Database
from ..models.serializers import Tag, TagCreate, ErrorMessage
from ..models import db

NOT_FOUND_RESPONSE = {"message": "tag not found"}

router = APIRouter()

#######
# /tags
#######
@router.get("/", tags=["tags"], response_model=List[Tag])
async def get_tags(database: Database = Depends(db.get_database_connection)):
    query = db.tags.select()
    return await database.fetch_all(query)


@router.post("/", tags=["tags"], response_class=Tag)
async def create_tag(
    tag: TagCreate, database: Database = Depends(db.get_database_connection)
):
    query = db.ingredients.insert().values(value=tag.value, kind=tag.kind)
    created_tag_id = await database.execute(query)
    return {**tag.dict(), "id": created_tag_id}


#####################
# /tags/{tag_id: int}
#####################
@router.get(
    "/{tag_id}",
    tags=["tags"],
    response_model=Tag,
    responses={404: {"model": ErrorMessage}},
)
async def get_tag_detail(
    tag_id: int, database: Database = Depends(db.get_database_connection)
):
    query = db.tags.select().where(db.tags.c.id == tag_id)
    tag = await database.fetch_one(query)

    return tag if tag else JSONResponse(status_code=404, content=NOT_FOUND_RESPONSE)


@router.put(
    "/{tag_id}",
    tags=["tags"],
    response_model=Tag,
    responses={404: {"model": ErrorMessage}},
)
async def edit_tag(
    tag_id: int,
    tag: TagCreate,
    database: Database = Depends(db.get_database_connection),
):
    query = exists(db.tags.select().where(db.tags.c.id == tag_id))
    result = await database.execute(result)
    if result:
        query = (
            db.tags.update()
            .values(value=tag.value, kind=tag.kind)
            .where(db.tags.c.id == tag_id)
        )
        await database.execute(query)

        return {**tag.dict(), "id": tag_id}

    return JSONResponse(status_code=404, content=NOT_FOUND_RESPONSE)

from typing import List
from asyncpg.exceptions import IntegrityConstraintViolationError
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from ..serializers import Tag, TagCreate, ErrorMessage
from .. import models, utils

NOT_FOUND_RESPONSE = {"message": "tag not found"}

router = APIRouter()

#######
# /tags
#######
@router.get("/", tags=["tags"], response_model=List[Tag])
async def get_tags():
    tags = await models.Tag.query.gino.all()
    return tuple(tag.to_dict() for tag in tags)


@router.post(
    "/",
    tags=["tags"],
    response_model=Tag,
    responses={422: {"model": ErrorMessage}},
    status_code=201,
)
async def create_tag(tag: TagCreate):
    try:
        created_tag = await models.Tag.create(**tag.dict())

    except IntegrityConstraintViolationError as error:
        response = JSONResponse(content={"message": str(error)}, status_code=422)

    else:
        response = created_tag.to_dict()

    return response


#####################
# /tags/{tag_id: str}
#####################
@router.get(
    "/{tag_id}",
    tags=["tags"],
    response_model=Tag,
    responses={404: {"model": ErrorMessage}},
)
async def get_tag_detail(tag_id: str):
    tag = await models.Tag.get(tag_id)
    return (
        tag.to_dict()
        if tag
        else JSONResponse(status_code=404, content=NOT_FOUND_RESPONSE)
    )


@router.put(
    "/{tag_id}",
    tags=["tags"],
    response_model=Tag,
    responses={404: {"model": ErrorMessage}},
)
async def edit_tag(
    tag_id: str, tag: TagCreate,
):
    if not (db_tag := await models.Tag.get(tag_id)):
        return JSONResponse(status_code=404, content=NOT_FOUND_RESPONSE)

    try:
        await db_tag.update(**tag.dict()).apply()

    except IntegrityConstraintViolationError as error:
        response = JSONResponse(content={"message": str(error)}, status_code=422)

    else:
        response = db_tag.to_dict()

    return response

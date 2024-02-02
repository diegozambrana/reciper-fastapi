from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field 
from sqlalchemy.orm import Session

from database import get_db
from models import Recipe, Rating
from .auth import get_current_user

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Session, Depends(get_current_user)]


class RecipeCreate(BaseModel):
    name: str = Field(min_length=3, max_length=128)
    image: str
    description: str = Field(min_length=3, max_length=256)
    ingredients: str = Field(min_length=3, max_length=256)
    instructions: str = Field(min_length=3, max_length=256)


class RatingCreate(BaseModel):
    rating: int = Field(ge=1, le=5)


@router.get("/")
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return db.query(Recipe).filter(Recipe.owner_id == user.get('id')).all()


@router.post("/")
async def create_recipe(
    user: user_dependency,
    recipe: RecipeCreate,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    now = datetime.now(timezone.utc)
    formatted_now = now.isoformat()

    db_recipe = Recipe(
        **recipe.dict(),
        owner_id=user.get('id'),
        created_at=formatted_now,
        updated_at=formatted_now,
    )

    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.get("/{recipe_id}")
async def get_recipe(user: user_dependency, recipe_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id)\
        .filter(Recipe.owner_id == user.get('id')).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/{recipe_id}")
async def update_recipe(
    recipe_id: int,
    user: user_dependency,
    recipe: RecipeCreate,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id)\
        .filter(Recipe.owner_id == user.get('id')).first()

    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = recipe.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_recipe, key, value)

    db_recipe.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_recipe)

    return db_recipe


@router.delete("/{recipe_id}")
async def delete_recipe(user: user_dependency, recipe_id: int, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id)\
        .filter(Recipe.owner_id == user.get('id')).first()
    
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(recipe)
    db.commit()

    return {"message": "Recipe deleted successfully"}


@router.post("/{recipe_id}/rate")
async def rate_recipe(
    user: user_dependency,
    recipe_id: int,
    rating: RatingCreate,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    rating_obj = db.query(Rating).filter(Rating.recipe_id == recipe_id)\
        .filter(Rating.user_id == user.get('id')).first()
    
    if rating_obj is not None:
        rating_obj = Rating(
            **rating.dict(),
            recipe_id=recipe_id,
            user_id=user.get('id'),
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        db.add(rating_obj)
    else:
        rating_obj.rating = rating.rating
        rating_obj.updated_at = datetime.now(timezone.utc).isoformat()
        db.refresh(rating_obj)

    db.commit()

    return {"message": "Rating added successfully"}
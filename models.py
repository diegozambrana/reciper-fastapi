from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')


class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image = Column(String)
    description = Column(String)
    ingredients = Column(String)
    instructions = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(String)
    updated_at = Column(String)


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, index=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(String)
    updated_at = Column(String)


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, index=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(String)
    updated_at = Column(String)
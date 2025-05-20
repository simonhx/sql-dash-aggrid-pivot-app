from sqlalchemy import Column, Integer, String, Numeric, Text
from sqlalchemy.orm import declarative_base

# --- SQLAlchemy Base ---
# This Base will be used by all models in this file
Base = declarative_base()

# --- SQLAlchemy Model Definition ---
class Film(Base):
    __tablename__ = 'film' # The actual table name in your database

    film_id = Column(Integer, primary_key=True)
    title = Column(String(255)) # Assuming a max length for title
    description = Column(Text)
    release_year = Column(Integer)
    rental_rate = Column(Numeric(4, 2)) # Precision and scale for currency

    def __repr__(self):
        return f"<Film(film_id='{self.film_id}', title='{self.title}')>"

# If you had more models, you would define them here, all inheriting from the same Base.

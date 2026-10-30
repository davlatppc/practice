from alembic import context
from sqlalchemy import create_engine

import app.models
from app.database import DATABASE_URL, Base

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()

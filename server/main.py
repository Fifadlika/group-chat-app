from fastapi import FastAPI
from core.database import engine, Base
import models.user
from routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Group Chat App")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Server is running"}
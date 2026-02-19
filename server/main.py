from fastapi import FastAPI
from core.database import engine, Base
import models.user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Group Chat App")

@app.get("/")
def root():
    return {"message": "Server is running"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
import models.user
from routers import auth, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Group Chat App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # pls specify on prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Server is running"}
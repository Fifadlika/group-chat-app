from fastapi import FastAPI

app = FastAPI(title="Group Chat App")

@app.get("/")
def root():
    return {"message": "Server is running"}
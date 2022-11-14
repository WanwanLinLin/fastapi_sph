# -*- coding：utf-8 -*-
import uvicorn
from fastapi import FastAPI
# from modules import users_router
from db import Base, engine
from modules import users_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_router)


@app.get("/")
async def main():
    return {"message": "There will be a fastapi project"}


if __name__ == '__main__':
    uvicorn.run(app)
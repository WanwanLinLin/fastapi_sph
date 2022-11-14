# -*- coding：utf-8 -*-
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def main():
    return {"message": "There will be a fastapi project"}


if __name__ == '__main__':
    uvicorn.run(app)
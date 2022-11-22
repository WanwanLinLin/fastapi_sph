# encoding:utf-8
import uvicorn
from api import app


if __name__ == '__main__':
    uvicorn.run(app)

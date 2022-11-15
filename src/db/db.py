# -*- coding：utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@172.19.237.129:3306/sph_fastapi?charset=utf8"
# 出租屋的mysql
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:2298315584@127.0.0.1:3306/sph_fastapi?charset=utf8"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

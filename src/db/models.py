# -*- coding：utf-8 -*-
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db import Base


class FirstCategory(Base):
    __tablename__ = "FirstCategory"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), index=True)

    owner = relationship("SecondCategory", backref="FirstCategory")


class SecondCategory(Base):
    __tablename__ = "SecondCategory"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), index=True, )
    owner_id = Column(Integer, ForeignKey("FirstCategory.id"))

    owner = relationship("ThirdCategory", backref="SecondCategory")


class ThirdCategory(Base):
    __tablename__ = "ThirdCategory"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), index=True)
    owner_id = Column(Integer, ForeignKey("SecondCategory.id"))


if __name__ == '__main__':
    from db import SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    q = session.query(FirstCategory).filter(FirstCategory.id == 1).first()
    for i in q.owner:
        for j in i.owner:
            print(j.category_name)


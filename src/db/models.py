# -*- coding：utf-8 -*-
from db import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash


# 一级类目表
class FirstCategory(Base):
    __tablename__ = "FirstCategory"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), index=True)

    owner = relationship("SecondCategory", backref="FirstCategory")


# 二级类目表
class SecondCategory(Base):
    __tablename__ = "SecondCategory"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), index=True, )
    owner_id = Column(Integer, ForeignKey("FirstCategory.id"))

    owner = relationship("ThirdCategory", backref="SecondCategory")


# 三级类目表
class ThirdCategory(Base):
    __tablename__ = "ThirdCategory"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), index=True)
    owner_id = Column(Integer, ForeignKey("SecondCategory.id"))


# 超级管理员用户表
class AdminUser(Base):
    __tablename__ = "AdminUser"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=True, default=None)
    encrypt_password = Column(String(255), default="", nullable=False)
    level = Column(String(15), default="3", nullable=False)

    def set_password(self, password: str):
        self.encrypt_password = generate_password_hash(
            password, method="pbkdf2:sha512", salt_length=64
        )

    def check_password(self, value):
        return check_password_hash(self.encrypt_password, value)


if __name__ == '__main__':
    from db import SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    admin_user = AdminUser(username="Julia",
                           encrypt_password="linwan",
                           level="3")
    # 对管理员的密码进行加密
    admin_user.set_password("linwan")
    session.add(admin_user)
    session.commit()
    print("超级管理员创建成功！")
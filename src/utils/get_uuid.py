# -*- coding：utf-8 -*-
import uuid


def get_uuid():
    return uuid.uuid4()


if __name__ == '__main__':
    print(get_uuid())

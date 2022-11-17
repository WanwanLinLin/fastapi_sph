# -*- coding：utf-8 -*-
def success(data):

    return {
        "code": 200,
        "message": "Success",
        "data": data,
        "ok": True
    }


if __name__ == '__main__':
    print(success(None))
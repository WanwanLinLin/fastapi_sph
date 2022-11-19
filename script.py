# -*- coding：utf-8 -*-
# from datetime import datetime
#
# print(datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S"))

x = [{'categoryName': '图书、音像、电子书刊', 'categoryId': 1, 'categoryChild': [
    {'categoryName': '电子书刊', 'categoryId': 1, 'categoryChild': [{'categoryName': '电子书', 'categoryId': 1}]},
    {'categoryName': '岛国电影', 'categoryId': 2,
     'categoryChild': [{'categoryName': '人气女优', 'categoryId': 2}, {'categoryName': '波老师出道三十年作品集', 'categoryId': 8}]}]},
     {'categoryName': '外卖、美食', 'categoryId': 2, 'categoryChild': [{'categoryName': '不饿了么', 'categoryId': 3,
                                                                   'categoryChild': [
                                                                       {'categoryName': '美味家常菜', 'categoryId': 3},
                                                                       {'categoryName': '桂林特产', 'categoryId': 4}]},
                                                                  {'categoryName': '美美的团', 'categoryId': 4,
                                                                   'categoryChild': [{'categoryName': '美团优选（送货上门）',
                                                                                      'categoryId': 5}]}]},
     {'categoryName': '服装服饰', 'categoryId': 3, 'categoryChild': [{'categoryName': '尼克（Nike）', 'categoryId': 5,
                                                                  'categoryChild': [{'categoryName': '尼克2022纪念版专场',
                                                                                     'categoryId': 6}]},
                                                                 {'categoryName': '阿弟大四', 'categoryId': 6,
                                                                  'categoryChild': [{'categoryName': '阿弟大四桥单联名专场',
                                                                                     'categoryId': 7}]}]}]
import json
with open('result.json', 'w', encoding="utf-8") as f:
    json.dump(x, f)

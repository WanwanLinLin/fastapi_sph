import os

from concurrent.futures import ThreadPoolExecutor

task_list = ['python src/run.py',
             'python src/modules/goods_manage/goods_service.py',
             'python src/modules/ordinary_users/users_service.py',
             'python src/modules/trade_manage/trade_service.py']


def run_service(task_):
    os.system(task_)


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in task_list:
            executor.submit(run_service, i)

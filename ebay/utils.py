import time

from logger import log
import yaml

_config = yaml.load(open('./conf.yml', 'r', encoding='utf-8'))


def sleep(sleep_time=3):
    log.info("开始睡眠" + str(time.perf_counter()))
    time.sleep(sleep_time)
    log.info("睡眠结束，开启下次请求。。。" + str(time.perf_counter()))


def conf(*name):
    result = {}
    for index in range(len(name)):
        try:
            if index == 0:
                result = _config[name[0]]
                continue
            result = result[name[index]]
        except KeyError:
            log.error('config parameter [%s] not found', name[index])
            return None
    return result


if __name__ == '__main__':
    conf('123', '123')

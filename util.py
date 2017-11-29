#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import logging
import requests
from pprint import pprint

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt = '%a, %d %b %Y %H:%M:%S')
logger = logging.getLogger('util')

def dic_to_str(dict):
    # 将 key:value 形式的格式 转换为 key=value 的字符串类型, 各key=value对之间用 "," 分隔。
    result = ''
    count = 0
    for key in dict.keys():
        count += 1
        if count < len(dict):
            result += "{0}='{1}'".format(key,dict[key]) + ','
        else:
            result += "{0}='{1}'".format(key,dict[key])
    return result

def request_util(url, param):
    data = []

    logging.info("start GET %s?%s", url, param)
    response = requests.get(url, params=param)
    if response.status_code != requests.codes.ok:
        logging.error("GET %s?%s failed! The error code is: %s", url, param, response.status_code)
        return []
    logging.info("GET /api/v1/query?%s ok! Response code is = %s", param, response.status_code)
    results = response.json()
    logger.debug('The results of getting query are: %s', results)
    data = results['data']['result']

    return data


def cpu_cores(url, instance='10.110.13.217:9100'):
    '''计算CPU核数'''
    cpu_count = 0
    param = {
        "query": 'count(node_cpu{{instance="{0}", mode="system"}})'.format(instance),
    }
    result = request_util(url, param)
    cpu_count = result[0]['value'][1]
    logging.info("The CPU cores are : %s", cpu_count)
    return int(cpu_count)

def main():
    url = 'http://10.110.13.216:9200/api/v1/query'
    cpu_cores(url)

if __name__ == '__main__':
    main()
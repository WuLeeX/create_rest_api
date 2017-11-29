#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import requests
import json
import logging
import time
from pprint import pprint
from util import request_util, dic_to_str, cpu_cores

'''
Prometheus REST API 分为几部分：
Instant queries：        GET /api/v1/query
    curl 'http://localhost:9090/api/v1/query?query=up&time=2015-07-01T20:10:51.781Z'
Range queries：          GET /api/v1/query_range
    curl 'http://localhost:9090/api/v1/query_range?query=up&start=2015-07-01T20:10:30.781Z&end=2015-07-01T20:11:00.781Z&step=15s'
Querying metadata:       GET /api/v1/series
    curl -g 'http://localhost:9090/api/v1/series?match[]=up&match[]=process_start_time_seconds{job="prometheus"}'
Querying label values:   GET /api/v1/label/<label_name>/values
    curl http://localhost:9090/api/v1/label/job/values
Targets:                 GET /api/v1/targets
    curl http://localhost:9090/api/v1/targets
Alertmanagers:           GET /api/v1/alertmanagers
    curl http://localhost:9090/api/v1/alertmanagers
'''
'''
setting log level
'''
# LOG_FILE = 'D:\\Python\\Python_workspace\\log\\parse_json.log'
# logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')
logger = logging.getLogger('parse_json')


def instant_query(url, query, timestamp=time.time(), timeout='2m', **kwargs):
    '''
    :param url: Evaluation url, default to 'http://10.110.13.216:9200'
    :param query: query=<string>: Prometheus expression query string. like go_gc_duration_seconds{quantile="0"}
    :param timestamp: Evaluation timestamp. Optional. Defaults to current server time.
    :param timeout: Evaluation timeout. Optional. Defaults to 2 minutes
    :return: return a dict
    '''
    param = {
        'query': query + '{' + dic_to_str(kwargs) + '}',
        'timestamp': time,
        'timeout': timeout
    }
    url = url + '/api/v1/query'

    logger.info('GET /api/v1/query?%s', param)
    response = requests.get(url, params=param)
    if response.status_code != requests.codes.ok:
        logger.error('getting /api/v1/query?params failed ! , Please check it out ! The response code is: %s', response.status_code)
        return []
    results = response.json()
    logger.debug('The results of getting query are: %s', results)


    cores = 2
    query_result = results['data']['result']
    element_len = len(query_result)
    keys = []
    values = []
    metrics = {
        'query': param,
        'cpu': {
            'cpu0': {

            },
            'cpu1': {

            }
        }
    }

    # for i in range(element_len):
    #     for core in range(cores-1):
    #         if query_result[i]['metric']['cpu'] == 'cpu' + 'core':
    #             keys[core].append(query_result[i]['metric']['mode'])
    #             values[core].append(query_result[i]['value'][1])
    # pprint(dict(zip(keys,values)))


    pprint(query_result)
    return metrics

def range_query(url, query, interval=5*60, end=time.time(), step=15, timeout='2m'):
    '''
    :param url: Evaluation url, default to 'http://10.110.13.216:9200'
    :param query: query=<string>: Prometheus expression query string.
    :param interval: End timestamp - Start timestamp. Unit is second. Default to 5 minutes.
    :param end: start=<rfc3339 | unix_timestamp>: Start timestamp. Default to now.
    :param step: step=<duration>: Query resolution step width. Default to 15 seconds.
    :param timeout: timeout=<duration>: Evaluation timeout. Optional. Defaults to '2 minutes'
    :return: a dict
    '''
    param = {
        'query': query,
        'start': end - interval,
        'end': end,
        'step': step,
        'timeout': timeout
    }
    url = url + '/api/v1/query_range'

    logger.info('GET /api/v1/query_range?params')
    response = requests.get(url, params=param)
    if response.status_code != requests.codes.ok:
        logger.error('getting /api/v1/query_range?params failed ! , Please check it out ! The response code is: %s',
                     response.status_code)
        return []
    results = response.json()
    logger.debug('The results of getting query_range are: %s', results)
    pprint(results)

def querying_metadata(url, element, *args):
    '''
    :param url: Evaluation url, default to 'http://10.110.13.216:9200'
    :param element: params in the url,  At least one element must be provided.
    :param args: params in the url, it's a tuple, Optional
    :return: a dict
    '''
    logger.debug('args are %s', args)
    logger.debug('length of args are %s', len(args))

    if args is None:
        params = 'match[]=' + element
    else:
        params = 'match[]=' + element + '&'
        for value in args:
            try:
                if value == args[-1]:
                    params += 'match[]=' + value
                else:
                    params += params + 'match[]=' + value + '&'
            except ValueError:
                logger.error('param *args not correct')
    logger.debug('params are :%s ', params)

    url = url + '/api/v1/series'

    logger.info('GET /api/v1/series?params')
    response = requests.get(url, params=params)
    if response.status_code != requests.codes.ok:
        logger.error('getting /api/v1/series?params failed ! , Please check it out ! The response code is: %s',
                     response.status_code)
        return []
    results = response.json()
    logger.debug('The results of getting series are: %s', results)
    # pprint(results)

def querying_label_values(url, label_name):
    '''
    :param url: Evaluation url, default to 'http://10.110.13.216:9200'
    :param labelname:  a provided label name
    :return: a list of label values for a provided label name
    '''
    url = url + '/api/v1/label/' + label_name + '/values'

    logger.info('GET /api/v1/label/%s/values', label_name)
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        logger.error('getting /api/v1/label/%s/values failed ! , Please check it out ! The response code is: %s', label_name,
                     response.status_code)
        return []
    results = response.json()
    logger.debug('The results of getting label_name values are: %s', results)
    pprint(results)

def get_targets(url):
    '''
    :param url: Evaluation url, default to 'http://10.110.13.216:9200'
    :return: a dict
    '''
    url = url + '/api/v1/targets'

    logger.info('GET /api/v1/targets')
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        logger.error('getting /api/v1/targets failed ! , Please check it out ! The response code is: %s',
                     response.status_code)
        return []
    results = response.json()
    logger.debug('The results of getting targets are: %s', results)
    pprint(results)

def get_alertmanager(url):
    '''
        :param url: Evaluation url, default to 'http://10.110.13.216:9200'
        :return: a dict
    '''
    url = url + '/api/v1/alertmanagers'

    logger.info('GET /api/v1/alertmanagers')
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        logger.error('getting /api/v1/alertmanagers failed ! , Please check it out ! The response code is: %s',
                     response.status_code)
        return []
    results = response.json()
    logger.debug('The results of getting alertmanagers are: %s', results)
    pprint(results)

# def get_data(query, time='', timeout=''):
#
#     data = {}
#     url = 'http://10.110.13.216:9200/api/v1/query'
#     params = {
#         "query": query,
#         "time": time
#     }
#
#     req = requests.get(url, params)
#     if req.status_code == requests.codes.ok:
#         response = req.json()
#         status = response['status']
#         data = response['data']
#     else:
#         print(req.status_code)
#     return data

# def parse(para):
#     data = get_data(para)
#     type = data['resultType']
#     result = data['result']
#     final_result = result[0]['value'][1]
#     print("result type: ", type)
#     print(para, final_result)
#     pprint(result)
#     pprint(data)
#
#     a = requests.get(url='http://10.110.13.216:9200/api/v1/targets').json()
#     for i in range(len(a['data']['activeTargets'])):
#         print(a['data']['activeTargets'][i]['labels']['instance'])

def read_info():
    file = open('D:\\Python\\Python_workspace\\create_rest_api\\node_info.txt','r')
    for info in file:
        yield info
    file.close()

def hosts_info(url, timestamp=time.time(), timeout='2m'):
    results = {}
    node_info = read_info()

    url = url + '/api/v1/query'
    rlt_values = {}

    for info in node_info:
        query = info.strip('\n')
        param = {
            'query': query,
            'timestamp': timestamp,
            'timeout': timeout
        }

        data = request_util(url, param)

        for i in range(len(data)):
            rlt_values.setdefault(data[i]['metric']['instance'],data[i]['value'][1])
        results[query] = rlt_values
        logging.info('results is : %s', results)
    return results


def hosts_info_instance(url, timestamp=time.time(), timeout='2m', **kwargs):
    '''GET api/v1/hosts/<instance_name>'''
    results = {}
    node_info = read_info()

    url = url + '/api/v1/query'
    rlt_values = {}

    for info in node_info:
        query = info.strip('\n')
        param = {
            'query': query + '{' + dic_to_str(kwargs) + '}',
            'timestamp': timestamp,
            'timeout': timeout
        }
        data = request_util(url, param)

        for i in range(len(data)):
            rlt_values.setdefault(data[i]['metric']['instance'], data[i]['value'][1])
        results[query] = rlt_values
        logging.debug('host_info_instance results are : %s', results)
    return results

def hosts_node_cpus(url, timestamp=time.time(), timeout='2m'):

    node_info = read_info()
    rlt_values = {}
    results = {}

    url = url + '/api/v1/query'
    for info in node_info:
        if 'node_cpu' in info:
            query = info.strip('\n')
            param = {
                'query': query,
                'timestamp': timestamp,
                'timeout': timeout
            }
            logger.info('start GET /api/v1/query?%s', param)
            response = requests.get(url, params=param)
            if response.status_code != requests.codes.ok:
                logger.error(
                    'getting /api/v1/query?{0} failed ! , Please check it out ! The response code is: %s.'.format(param),
                    response.status_code)
                continue
            logger.info('GET /api/v1/query?%s ok! The status_code is %s', param, response.status_code)
            get_rlt = response.json()
            logger.info('The results of getting query are: %s', get_rlt)
            data = get_rlt['data']['result']

            for i in range(len(data)):
                rlt_values.setdefault(data[i]['metric']['instance'], data[i]['value'][1])
            results[query] = rlt_values
            logging.debug('results is : %s', results)
    return results


def single_host_cpu(url, instance, timestamp=time.time(), timeout='2m'):
    '''
    :param url: The url we want to query exactly.
    :param instance: a string format 'ip:port'
    :param timestamp: Unix timestamp, default to time.time()
    :param timeout: Query time out, default to 2 minutes
    :return: A dict contains the cpus info in the instance node.
    '''
    url = url + '/api/v1/query'
    param = {
        "query": "node_cpu{{ instance='{0}' }}".format(instance),
        "timestamp": timestamp,
        "timeout": timeout
    }

    data = request_util(url, param)

    logging.info("getting cpu cores...")
    cores = cpu_cores(url)
    logging.info("The Cores of CPU are: %s", cores)
    cpu_results = {
        "instance": instance,
        "cpu": {}
    }
    logging.info("Result of request data is %s", len(data))

    for i in range(cores):
        values = {}
        for index in range(len(data)):
            # 遍历整个请求结果，按照 cpu 进行分类
            # 判断属于哪个 cpu, 根据 mode 类型不同，将不同的 mode 及其 value 打包成一个 dict，结果传入 values
            if data[index]['metric']['cpu'] == 'cpu{0}'.format(i):
                values.setdefault(data[index]['metric']['mode'], data[index]['value'][1])
        # 不同的 cpu 对应一个 values 的 dict
        cpu_results['cpu']['cpu{0}'.format(i)] = values
    return cpu_results



def read_host_info():
    file = open('D:\\Python\\Python_workspace\\create_rest_api\\single_host_info.txt','r')
    for info in file:
        yield info
    file.close()

def single_host_info(url, instance, timestamp=time.time(), timeout='2m'):
    '''
    :param url: The url we want to query exactly.
    :param instance: a string format 'ip:port'
    :param timestamp: Unix timestamp, default to time.time()
    :param timeout: Query time out, default to 2 minutes
    :return: A dict contains the cpus info in the instance node.
    '''
    url = url + '/api/v1/query'
    data_results = {
        "href": "http://10.110.13.216:9200/api/v1/hosts/{0}?fields=metrics".format(instance),
        "instance": instance,
        "boot": {},
        "cpu": {},
        "filesystem": {},
        "disk": {},
        "load": {},
        "memory": {},
        "network": {},
        "procs": {}
    }
    single_host = read_host_info()
    single_output = ["disk", "load", "memory", "procs"]
    multi_output = ["cpu", "filesystem", "network"]


    for info in single_host:
        logging.info('Reading %s successfully.', info)
        query = info.strip('\n')
        param = {
            'query': query + "{{ instance='{0}' }}".format(instance),
            'timestamp': timestamp,
            'timeout': timeout
        }
        data = request_util(url, param)
        for key in single_output:
            # key 在 single_output 中，其输出是 key:{} 的方式
            if key in info:
                data_results[key].setdefault(data[0]['metric']['__name__'], data[0]['value'][1])

        if 'node_cpu' in info:
            # 判断有多少个网卡，按照 device 划分，因为 data 中的 device 有可能重复，所以将 device 放入集合去重
            cpu_elements = set()
            for index in range(len(data)):
                cpu_elements.add(data[index]['metric']['cpu'])
            #
            for element in cpu_elements:
                data_results['cpu'].setdefault(element, {})
                for index in range(len(data)):
                    # 遍历整个请求结果，按照 network 的 device 进行分类
                    # 判断属于哪个 device, 将不同的 device 及其 value 打包成一个 dict，结果传入 data_results['network'][element]
                    if data[index]['metric']['cpu'] == element:
                        data_results['cpu'][element].setdefault(data[index]['metric']['mode'],
                                                                data[index]['value'][1])

        elif 'node_network' in info:
            # 判断有多少个网卡，按照 device 划分，因为 data 中的 device 有可能重复，所以将 device 放入集合去重
            network_elements = set()
            for index in range(len(data)):
                network_elements.add(data[index]['metric']['device'])
            #
            for element in network_elements:
                data_results['network'].setdefault(element, {})
                for index in range(len(data)):
                    # 遍历整个请求结果，按照 network 的 device 进行分类
                    # 判断属于哪个 device, 将不同的 device 及其 value 打包成一个 dict，结果传入 data_results['network'][element]
                    if data[index]['metric']['device'] == element:
                        data_results['network'][element].setdefault(data[index]['metric']['__name__'],
                                                                    data[index]['value'][1])

        elif 'node_filesystem' in info:
            pprint(data)
            # data_results['filesystem'].setdefault(data[0]['metric']['__name__'], data[0]['value'][1])
            # 判断有多少个文件系统，按照 device 划分，因为 data 中的 device 有可能重复，所以将 device 放入集合去重
            fs_elements = set()
            for index in range(len(data)):
                fs_elements.add(data[index]['metric']['device'])
            #
            for element in fs_elements:
                data_results['filesystem'].setdefault(element, {})
                for index in range(len(data)):
                    # 遍历整个请求结果，按照 filesystem 的 device 进行分类
                    # 判断属于哪个 device, 将不同的 device 及其 value 打包成一个 dict，结果传入 data_result['filesystem'][element]
                    if data[index]['metric']['device'] == element:
                        data_results['filesystem'][element].setdefault(data[index]['metric']['__name__'],
                                                                       data[index]['value'][1])

        elif 'node_boot' in info:
            data_results['boot'].setdefault(data[0]['metric']['__name__'],
                                            time.time() - float(data[0]['value'][1]))
        else:
            pass
        # logging.info("Result of request data is %s", data)
    return data_results
        #
        # for key in multi_output:
        #     # pprint(subkey_sets)
        #     # key 在 multi_output 中，其输出是 key: { subkey1:{}, subkey2:{}, subkey3:{},..., }
        #     print(key)
        #     if key in info:
        #         # 获取 data 中所有的 subkey ，值有可能重复，所以将 subkey 放入集合去重
        #         for index in range(len(data)):
        #             if 'cpu' == key:
        #                 subkey_sets[key].add(data[index]['metric'][key])
        #             else:
        #                 subkey_sets[key].add(data[index]['metric']['device'])
        #         #
        #         print('sets are: ', subkey_sets)
        #         for element in subkey_sets[key]:
        #             data_results[key].setdefault(element, {})
        #             for index in range(len(data)):
        #                 # 遍历整个请求结果，按照 network 的 device 进行分类
        #                 # 判断属于哪个 device, 将不同的 device 及其 value 打包成一个 dict，结果传入 data_results['network'][element]
        #                 if data[index]['metric'][key] == element:
        #                     if 'cpu' == key:
        #                         data_results[key][element].setdefault(data[index]['metric']['mode'],
        #                                                               data[index]['value'][1])
        #                     else:
        #                         data_results[key][element].setdefault(data[index]['metric']['device'],
        #                                                               data[index]['value'][1])



def multi_data_output(data, data_results, key):
    subkey_sets = set()
    for index in range(len(data)):
        subkey_sets.add(data[index]['metric']['cpu'])
    #
    for element in subkey_sets:
        data_results[key].setdefault(element, {})
        for index in range(len(data)):
            # 遍历整个请求结果，按照 network 的 device 进行分类
            # 判断属于哪个 device, 将不同的 device 及其 value 打包成一个 dict，结果传入 data_results['network'][element]
            if data[index]['metric'][key] == element:
                data_results[key][element].setdefault(data[index]['metric']['mode'],
                                                        data[index]['value'][1])

'''
        elif 'node_cpu' in info:
            # 判断有多少个网卡，按照 device 划分，因为 data 中的 device 有可能重复，所以将 device 放入集合去重
            cpu_elements = set()
            for index in range(len(data)):
                cpu_elements.add(data[index]['metric']['cpu'])
            #
            for element in cpu_elements:
                data_results['cpu'].setdefault(element, {})
                for index in range(len(data)):
                    # 遍历整个请求结果，按照 network 的 device 进行分类
                    # 判断属于哪个 device, 将不同的 device 及其 value 打包成一个 dict，结果传入 data_results['network'][element]
                    if data[index]['metric']['cpu'] == element:
                        data_results['cpu'][element].setdefault(data[index]['metric']['mode'],
                                                                    data[index]['value'][1])

                        # pprint(data)
            # cores = cpu_cores(url, instance)
            # for i in range(cores):
            #     values = {}
            #     for index in range(len(data)):
            #         # 遍历整个请求结果，按照 cpu 进行分类
            #         # 判断属于哪个 cpu, 根据 mode 类型不同，将不同的 mode 及其 value 打包成一个 dict，结果传入 values
            #         if data[index]['metric']['cpu'] == 'cpu{0}'.format(i):
            #             values.setdefault(data[index]['metric']['mode'], data[index]['value'][1])
            #     # 不同的 cpu 对应一个 values 的 dict
            #     data_results['cpu']['cpu{0}'.format(i)] = values

        elif 'node_load' in info:
            data_results['load'].setdefault(data[0]['metric']['__name__'], data[0]['value'][1])

        elif 'node_disk' in info:
            data_results['disk'].setdefault(data[0]['metric']['__name__'], data[0]['value'][1])

        elif 'node_memory' in info:
            data_results['memory'].setdefault(data[0]['metric']['__name__'], data[0]['value'][1])

        elif 'node_network' in info:
            # 判断有多少个网卡，按照 device 划分，因为 data 中的 device 有可能重复，所以将 device 放入集合去重
            network_elements = set()
            for index in range(len(data)):
                network_elements.add(data[index]['metric']['device'])
            #
            for element in network_elements:
                data_results['network'].setdefault(element, {})
                for index in range(len(data)):
                # 遍历整个请求结果，按照 network 的 device 进行分类
                # 判断属于哪个 device, 将不同的 device 及其 value 打包成一个 dict，结果传入 data_results['network'][element]
                    if data[index]['metric']['device'] == element:
                        data_results['network'][element].setdefault(data[index]['metric']['__name__'], data[index]['value'][1])

        elif 'node_procs' in info:
            data_results['procs'].setdefault(data[0]['metric']['__name__'], data[0]['value'][1])

        elif 'node_filesystem' in info:
            pprint(data)
            # data_results['filesystem'].setdefault(data[0]['metric']['__name__'], data[0]['value'][1])
            # 判断有多少个文件系统，按照 device 划分，因为 data 中的 device 有可能重复，所以将 device 放入集合去重
            fs_elements = set()
            for index in range(len(data)):
                fs_elements.add(data[index]['metric']['device'])
            #
            for element in fs_elements:
                data_results['filesystem'].setdefault(element, {})
                for index in range(len(data)):
                    # 遍历整个请求结果，按照 filesystem 的 device 进行分类
                    # 判断属于哪个 device, 将不同的 device 及其 value 打包成一个 dict，结果传入 data_result['filesystem'][element]
                    if data[index]['metric']['device'] == element:
                        data_results['filesystem'][element].setdefault(data[index]['metric']['__name__'],
                                                                    data[index]['value'][1])
'''


def main():
    url = 'http://10.110.13.216:9200'
    # query = "node_cpu{instance='wlx-1-node', cpu='cpu0', mode='nice'}"
    # query = "avg without (cpu) (irate(node_cpu{instance='wlx-1-node', mode!='idle'}[5m]))"
    # parse(para)
    # print('another')
    # query = "node_cpu"
    # instant_query(url, query, instance='wlx-1-node')
    # range_query(url, query)
    # querying_metadata(url,'node_cpu','up')
    # querying_label_values(url, 'job')
    # get_targets(url)
    # get_alertmanager(url)

    # a = hosts_info(url)
    # with open('D:\\Python\\Python_workspace\\create_rest_api\\node_info_result.json','w') as file:
    #     file.write(json.dumps(a))
    #     file.close()

    # b = hosts_info_instance(url, instance='10.110.13.216:9100')
    # pprint(b)

    # c = hosts_node_cpus(url)
    # pprint(c)

    # d = single_host_cpu(url, instance='10.110.13.216:9100')
    # pprint(d)

    start = time.time()
    e = single_host_info(url, instance='10.110.13.216:9100')
    end1 = time.time()
    pprint(e)
    end2 = time.time()
    print('执行时间：', end2 - start)

if __name__ == '__main__':
    main()

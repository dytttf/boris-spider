# -*- coding: utf-8 -*-
"""
Created on 2018-08-13 11:43:01
---------
@summary:
---------
@author: Boris
@email:  boris_liu@foxmail.com
"""
import spider.setting as setting
from spider.buffer.request_buffer import RequestBuffer
from spider.db.redisdb import RedisDB
from spider.network.request import Request
from spider.utils.log import log


class HandleFailedRequests(object):
    """docstring for HandleFailedRequests"""

    def __init__(self, table_folder):
        super(HandleFailedRequests, self).__init__()
        self._table_folder = table_folder

        self._redisdb = RedisDB()
        self._request_buffer = RequestBuffer(self._table_folder)

        self._table_failed_request = setting.TAB_FAILED_REQUSETS.format(
            table_folder=table_folder
        )

    def get_failed_requests(self, count=100):
        failed_requests = self._redisdb.zget(self._table_failed_request, count=10000)
        failed_requests = [eval(failed_request) for failed_request in failed_requests]
        return failed_requests

    def reput_failed_requests_to_requests(self):
        log.debug("正在重置失败的requests...")
        total_count = 0
        while True:
            failed_requests = self.get_failed_requests()
            if not failed_requests:
                break

            for request in failed_requests:
                request["retry_times"] = 0
                request_obj = Request.from_dict(request)
                self._request_buffer.put_request(request_obj)

                total_count += 1

        self._request_buffer.flush()

        log.debug("重置%s条失败requests为待抓取requests" % total_count)


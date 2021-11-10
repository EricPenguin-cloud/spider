import time

import requests
import urllib3
import json
from logger import log
from bs4 import BeautifulSoup
from utils import sleep


class Dispatcher:

    def __init__(self, ip='', port='', timeout=15, useProxy=False):
        self.proxyIp = ip
        self.proxyPort = port
        self.timeout = timeout
        self.useProxy = useProxy

    def get(self, url, head, retry=1):
        return self.request(method="GET", url=url, body='', head=head, retry=retry, timeout=15)

    def request(self, method, url, body, head, retry=1, timeout=15):
        while retry > 0:
            try:
                current = time.time()
                log.info("requesting " + url)
                if self.useProxy:
                    pass
                else:
                    response = requests.request(method, url, data=body, headers=head, timeout=timeout)
                    log.info("request down,cost " + str(time.time() - current))
                    result_text = response.text
                    return result_text
            except AttributeError:
                log.error("AttributeError,retry " + str(retry))
                retry = retry - 1
                sleep()
            except urllib3.exceptions.MaxRetryError:
                log.error("urllib3.exceptions.MaxRetryError,retry " + str(retry))
                retry = retry - 1
                sleep()
            except urllib3.exceptions.ReadTimeoutError:
                log.error("urllib3.exceptions.ReadTimeoutError,retry " + str(retry))
                retry = retry - 1
                sleep()
            except requests.exceptions.ReadTimeout:
                log.error("requests.exceptions.ReadTimeout,retry " + str(retry))
                retry = retry - 1
                sleep()
            except requests.exceptions.Timeout:
                log.error("requests.exceptions.Timeout,retry " + str(retry))
                retry = retry - 1
                sleep()
            except requests.exceptions.ConnectionError:
                log.error("requests.exceptions.ConnectionError,retry " + str(retry))
                retry = retry - 1
                sleep()

        return ''

    def html(self, url, head, retry=1):
        response = self.get(url, head=head, retry=retry)
        return BeautifulSoup(response, features="html")

    def json(self, method, url, head, body='', timeout=15):
        return json.loads(self.request(method, url, body=body, head=head, timeout=timeout))

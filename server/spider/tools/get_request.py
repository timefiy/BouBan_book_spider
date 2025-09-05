import random
import time

import requests


def get_request(url, **kwargs):
    time.sleep(random.uniform(0.1, 2))
    user_agents = [
        # ... (user agents list)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2040.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
    ]

    headers = {
        'User-Agent': random.choice(user_agents)
    }

    # 代理
    # username = "15670595866"
    # password = "jUf4sd&ta%xVw5"
    # proxies = {
    #     "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password,
    #                                                     "proxy": '36.25.243.5:11768'},
    #     "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password,
    #                                                      "proxy": '36.25.243.5:11768'}
    # }

    max_retry = 3
    for attempt in range(max_retry):
        try:
            # [ ]: 代理问题
            response = requests.get(url, headers=headers, timeout=5)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"请求异常: {e}")

        if attempt < max_retry - 1:
            print(f"请求失败，正在重试... (第 {attempt + 1}/{max_retry} 次)")
            time.sleep(random.uniform(1, 2))

    print('多次请求失败')
    return None
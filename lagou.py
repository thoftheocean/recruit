# coding:utf-8
import requests
import time
from urllib import parse


class LaGou(object):
    @staticmethod
    def get_one_page(url, data, headers):
        try:
            response = requests.post(url=url, data=data, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print('异常：{}'.format(e))
            return {'success': False}

    @staticmethod
    def parse_one_page(datas):
        # {'success': False, 'msg': '您操作太频繁,请稍后再访问', 'clientIp': '182.139.76.28'}
        content = []
        jobs = datas['content']['positionResult']['result']
        if len(jobs) != 0:
            for job in jobs:
                job_info = {
                    'positionName': job['positionName'],
                    'city': job['city'],
                    'district': job['district'],
                    'companyFullName': job['companyFullName'],
                    'salary': job['salary'],
                    'workYear': job['workYear']}
                content.append(job_info)
            return content
        else:
            return None

    def get_all_job(self, job, city, total_page):
        content = []
        url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&city={}&needAddtionalResult=false'.format(city)
        headers = {
            'Host': 'www.lagou.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/jobs/list_{}?px=default&city={}'
                            .format(parse.quote(job), parse.quote(city)),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.139 Safari/537.36'
        }
        for page in range(1, int(total_page)):
            time.sleep(2)
            form_data = {
                'pn': str(page),
                'kd': job
            }
            while True:
                source = self.get_one_page(url=url, data=form_data, headers=headers)
                if not source['success']:
                    time.sleep(20)
                    continue
                else:
                    datas = self.parse_one_page(source)
                    if datas is not None:
                        print(source)
                        for data in datas:
                            content.append(data)
                        print(form_data)
                        break
                    else:
                        return content
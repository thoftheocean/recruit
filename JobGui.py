# coding:utf-8
import sys
import time

import requests
from urllib import parse
from lxml import etree
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication

from excel import w_excel


class ZhiLian(object):
    def __init__(self, city, job, total_page):
        self.city = city
        self.job = job
        self.total_page = total_page

    @staticmethod
    def get_one_page(method, url, data=None):
        if method == 'get':
            response = requests.get(url, params=data)
        else:
            response = requests.post(url, data=data)
        try:
            if response.status_code == 200:
                source = etree.HTML(response.content)
                return source
            else:
                return None
        except Exception as e:
            print('程序异常：{}'.format(e))
            return None

    @staticmethod
    def parse_one_page(source):
        datas = []
        try:
            table = source.xpath('//table[@class="newlist"]/tr[1]')
            for tr in table[1:]:
                job = tr.xpath('td[1]/div/a[1]')
                job = job[0].xpath('string(.)')
                feedback = tr.xpath('td[2]/span/text()')
                if len(feedback) == 0:
                    feedback = None
                else:
                    feedback = feedback[0]
                name = tr.xpath('td[3]/a[1]/text()')[0]
                salary = tr.xpath('td[4]/text()')[0]
                adress = tr.xpath('td[5]/text()')[0]
                data = {
                    'job': job,
                    'feedback': feedback,
                    'name': name,
                    'salary': salary,
                    'adress': adress}
                datas.append(data)
            return datas
        except Exception:
            return []

    def get_all_job(self):
        content = []
        url = 'http://sou.zhaopin.com/jobs/searchresult.ashx'
        for page_num in range(1, int(self.total_page)):
            form_data = {
                'jl': self.city,
                'kw': self.job,
                'p': str(page_num)}
            while True:
                print(form_data)
                source = self.get_one_page('get', url, data=form_data)

                if source is not None:
                    print(source)
                    datas = self.parse_one_page(source)
                    if len(datas) != 0:
                        for data in self.parse_one_page(source):
                            content.append(data)
                        break
                    else:
                        print('无该页面')
                        return content
                else:
                    time.sleep(10)
                    continue
        return content


class LaGou(object):
    def __init__(self, city, job, total_page):
        self.city = city
        self.job = job
        self.total_page = total_page

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

    def get_all_job(self):
        content = []
        url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&city={}&needAddtionalResult=false'.format(self.city)
        headers = {
            'Host': 'www.lagou.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/jobs/list_{}?px=default&city={}'
                            .format(parse.quote(self.job), parse.quote(self.city)),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.139 Safari/537.36'
        }
        for page in range(1, int(self.total_page)):
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
                        for data in datas:
                            content.append(data)
                        print(form_data)
                        break
                    else:
                        return content
        return content


class UiForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('职位抓取工具')
        self.resize(200, 100)
        lay = QFormLayout()
        self.setLayout(lay)

        Lab1 = QLabel('招聘网站')
        self.web = QLineEdit()

        Lab2 = QLabel('城市')
        self.city = QLineEdit()

        Lab3 = QLabel('职位')
        self.job = QLineEdit()

        Lab4 = QLabel('页数')
        self.page = QLineEdit()

        OkB = QPushButton('确定')
        CaB = QPushButton('退出')

        Lab0 = QLabel('程序状态')
        self.label = QLabel(self)
        self.label.setText('准备抓取数据')

        # 点击事件
        OkB.clicked.connect(self.buttonok)
        CaB.clicked.connect(QCoreApplication.instance().quit)

        lay.addRow(Lab0, self.label)
        lay.addRow(Lab1, self.web)
        lay.addRow(Lab2, self.city)
        lay.addRow(Lab3, self.job)
        lay.addRow(Lab4, self.page)
        lay.addRow(OkB, CaB)

    def buttonok(self):
        web = self.web.text()
        city = self.city.text()
        job = self.job.text()
        page = self.page.text()
        if '智联' in web:
            work = ZhiLian(city=city, job=job, total_page=page)
            datas = work.get_all_job()
            keys = ['职位', '反馈率', '公司', '薪资', '地点']
            w_excel(web=web, city=city, job=job, keys=keys, datas=datas)
        elif '拉钩' in web:
            print(web)
            work = LaGou(city=city, job=job, total_page=page)
            datas = work.get_all_job()

            keys = ['职位', '城市', '地区', '公司', '薪资', '经验']
            w_excel(web=web, city=city, job=job, keys=keys, datas=datas)
        self.label.setText('数据抓取完成')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    job = UiForm()
    job.show()
    sys.exit(app.exec_())
    # city = '成都'
    # job = 'python'
    # page = '30'
    # web = '智联'
    # work = ZhiLian(city=city, job=job, total_page=page)
    # datas = work.get_all_job()
    # keys = ['职位', '反馈率', '公司', '薪资', '地点']
    # w_excel(web=web, city=city, job=job, keys=keys, datas=datas)

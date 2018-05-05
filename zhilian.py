# coding:utf-8
import xlwt
import requests

from lxml import etree


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
                print('请求异常')
        except Exception as e:
            print('程序异常：{}'.format(e))

    @staticmethod
    def parse_one_page(source):
        datas = []
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

    def get_job_detail(self):
        datas = []
        url = 'http://sou.zhaopin.com/jobs/searchresult.ashx'
        for page_num in range(1, int(self.total_page)):
            data = {
                'jl': self.city,
                'kw': self.job,
                'p': str(page_num)}
            print(data)
            source = self.get_one_page('get', url, data=data)
            for one_data in self.parse_one_page(source):
                datas.append(one_data)
        return datas

    # def w_excel(self, datas):
    #     book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    #     sheet = book.add_sheet('sheet1', cell_overwrite_ok=True)
    #     row0 = ['职位', '反馈率', '公司', '薪资', '地点']
    #     # 生成标题
    #     for i in range(len(row0)):
    #         sheet.write(0, i, row0[i])
    #     # 添加数据
    #     for row_index, row in enumerate(datas):
    #         for col_index, col in enumerate(row.items()):
    #             sheet.write(row_index+1, col_index, col[1])
    #     path = '{}_{}.xls'.format(self.job, self.city)
    #     book.save(path)


# coding:utf-8
import xlwt


def w_excel(web, job, city, keys, datas):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('sheet1', cell_overwrite_ok=True)
    # 生成标题
    for i in range(len(keys)):
        sheet.write(0, i, keys[i])
    # 添加数据
    for row_index, row in enumerate(datas):
        for col_index, col in enumerate(row.items()):
            sheet.write(row_index + 1, col_index, col[1])
    path = '{}_{}_{}.xls'.format(web, job, city)
    book.save(path)
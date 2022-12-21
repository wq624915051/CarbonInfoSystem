import os
import xlrd
import xlwt
from common.custom.logger import my_logger
from common.custom.keywords_processor import split_keywords_with_comma


def read_ESG_from_excel(filepath):
    '''
    描述:从excel中读取ESG评级以及股权融资优势
    参数:
        filepath: Excel文件路径
    返回值:
        data:每个公司的对应年份股权融资以及ESG评级列表
    '''
    example_data = {
        "000001": {
            "公司代码": "000001",
            "公司简称": "平安银行",
            "年份记录": [2020, 2021],
            "2020": {"股权融资优势": 3, "ESG评级": 1},
            "2021": {"股权融资优势": 2, "ESG评级": 2}
        }
    }
    data = {}
    excel_data = xlrd.open_workbook(filename=filepath)
    esg_table = excel_data.sheets()[0]
    lines = len(esg_table.col(0))
    for row in range(3, lines):
        temp_dict = {} # 一个公司对应一个dict
        temp_dict["年份记录"] = []
        for col in range(0, len(esg_table.row_values(row))):
            if esg_table.cell_value(1, col) == "公司代码":
                temp_dict["公司代码"] = esg_table.cell_value(row, col)
            elif esg_table.cell_value(1, col) == "公司简称":
                temp_dict["公司简称"] = esg_table.cell_value(row, col)
            elif esg_table.cell_value(1, col) == "年份":
                if esg_table.cell_value(row, col) != '':
                    temp_dict["年份记录"].append(int(esg_table.cell_value(row, col)))
                    esg_dict = {
                        "股权融资优势": esg_table.cell_value(row, col+1),
                        "ESG评级": esg_table.cell_value(row, col+2)
                    }
                    temp_dict[int(esg_table.cell_value(row, col))] = esg_dict
        data[esg_table.cell_value(row, 0)] = temp_dict
    return data

def read_terms_from_excel(filepath, type):
    '''
    描述: 从excel读取词库
    参数:
        filepath: Excel文件路径
        type: 读取词库类型, type==0读取专有名词, type==1读取常用词
    返回值:
        terms: 词列表
    '''
    excel_data = xlrd.open_workbook(filename=filepath)
    term_table = excel_data.sheets()[type]
    terms = term_table.col_values(0)

    return terms

def read_indicators_from_excel1(filepath):
    '''
    描述：从碳信息披露Excel获取指标列表
    参数：
        filepath: Excel文件路径
    返回值:
        indicators: 指标列表
    '''
    excel_data = xlrd.open_workbook(filename=filepath, formatting_info=True)
    table = excel_data.sheets()[0]
    data = []  # 一级指标列表
    thrid_list = []
    sec_list = []
    first1_name = table.cell_value(1, 0)  # 一级指标名称
    first2_name = table.cell_value(1, 1)  # 具体指标名称
    scend_name = table.cell_value(1, 2)  # 二级指标名称
    lines = len(table.col(0))
    for row in range(1, lines):
        thrid_dict = {}
        for col in range(0, len(table.row_values(row))):
            if table.cell_value(0, col) == '三级指标':
                thrid_dict['三级指标名称'] = table.cell_value(row, col).strip()
                if thrid_dict['三级指标名称'] == "" and  row != lines-1:
                    # 如果三级指标名称为空，且不是最后一行，则跳过
                    continue
                thrid_dict['keywords'] = split_keywords_with_comma(table.cell_value(row, col + 1))
                if table.cell_value(row, col-1) != '' and row != 1:
                    # 如果二级指标名称不为空，代表其已经跳转到下一个二级指标，则将当前二级指标打包
                    sec_dict = {}
                    sec_dict['二级指标名称'] = scend_name
                    sec_dict['三级指标'] = thrid_list
                    sec_list.append(sec_dict)
                    scend_name = table.cell_value(row, col-1).strip()
                    thrid_list = []
                    thrid_list.append(thrid_dict)
                elif row == lines-1:
                    #由于最后一行下面没有数据，所以要做一个特殊判断，最后一行打包现有的数据
                    sec_dict = {}
                    if thrid_dict['三级指标名称'] != "":
                        thrid_list.append(thrid_dict)
                    sec_dict['二级指标名称'] = scend_name
                    sec_dict['三级指标'] = thrid_list
                    sec_list.append(sec_dict)
                    scend_name = table.cell_value(row, col-1).strip()
                else:
                    thrid_list.append(thrid_dict)
                if (table.cell_value(row, col-3) != '' and row != 1) or row == lines-1:
                    # 如果一级指标名称不为空，代表其已经跳转到下一个一级指标，则将当前一级指标打包
                    first_dic = {}
                    first_dic['一级指标'] = first1_name
                    first_dic['需求目的'] = first2_name
                    first_dic['二级指标'] = sec_list
                    first1_name = table.cell_value(row, col-3).strip()
                    first2_name = table.cell_value(row, col-2).strip()
                    sec_list = []
                    data.append(first_dic)
    return data

def read_indicators_from_excel2(filepath):
    '''
    描述：从碳中和发展Excel获取指标列表
    参数：
        filepath: Excel文件路径
    返回值:
        indicators: 指标列表
    '''
    excel_data = xlrd.open_workbook(filename=filepath, formatting_info=True)
    table = excel_data.sheets()[0]
    data = []  # 用来存储一级指标列表
    second_list = [] # 用来存储二级指标
    thrid_list = [] # 用来存储三级指标
    first_name = table.cell_value(1, 0).strip()  # 一级指标名称
    second_name = table.cell_value(1, 1).strip()  # 二级指标名称
    lines = len(table.col(0))
    # 遍历行
    for row in range(1, lines):
        thrid_dict = {}
        # 遍历行中的每一列
        for col in range(0, len(table.row_values(row))):
            if table.cell_value(0, col) == '三级指标':
                # 当前列的表头是 "三级指标"
                thrid_dict['三级指标名称'] = table.cell_value(row, col).strip()
                if thrid_dict['三级指标名称'] == "" and  row != lines-1:
                    # 当前行的三级指标名称为空，且不是最后一行，跳过
                    continue
                thrid_dict['keywords'] = split_keywords_with_comma(table.cell_value(row, col + 1))
                thrid_dict['计分方法分类（关键词+数字+字数）'] = table.cell_value(row, col + 2).strip()
                thrid_dict['终端采分方法'] = table.cell_value(row, col + 3).strip()
                thrid_dict['最高分'] = table.cell_value(row, col + 4)
                if table.cell_value(row, col-1) != '' and row != 1:
                    # 判断当前行前1个单元格(二级指标)是否为空，或者当前行是否是最后一行，若是，则这个二级指标结束
                    sec_dict = {}
                    sec_dict['二级指标名称'] = second_name
                    sec_dict['三级指标'] = thrid_list
                    second_list.append(sec_dict)
                    second_name = table.cell_value(row, col-1).strip()
                    thrid_list = []
                    thrid_list.append(thrid_dict)
                elif row == lines-1:
                    sec_dict = {}
                    if thrid_dict['三级指标名称'] != "":
                        thrid_list.append(thrid_dict)
                    sec_dict['二级指标名称'] = second_name
                    sec_dict['三级指标'] = thrid_list
                    second_list.append(sec_dict)
                else:
                    thrid_list.append(thrid_dict)
                if (table.cell_value(row, col-2) != '' and row != 1) or row == lines-1:
                    # 判断当前行前2个单元格(一级指标)是否为空，或者当前行是否是最后一行，若是，则这个一级指标结束
                    first_dic = {}
                    first_dic['一级指标'] = first_name
                    first_dic['二级指标'] = second_list
                    first_name = table.cell_value(row, col-2).strip()
                    second_list = []
                    data.append(first_dic)
    return data

def write_indicators_to_excel1(filepath, data):
    '''
    描述：将指标列表写入碳信息披露Excel
    参数：
        filepath: Excel文件路径
        data: 指标列表
    '''
    example_data = [
        {
            "一级指标": "一级指标",
            "需求目的": "需求目的",
            "二级指标": [
                {
                    "二级指标名称": "二级指标名称",
                    "三级指标": [
                        {
                            "三级指标名称": "三级指标名称",
                            "keywords": "碳排放，中和",
                            "文字内容": "碳排放碳排放碳排放碳排放",
                            "图片数量": 18,
                            "表格数量": 15,
                            "句子数量": 14,
                            "常用词数量": 30,
                            "专业词数量": 40,
                            "数字个数": 3,
                            "文字信息披露质量": "文字信息披露质量",
                            "最终得分": 30
                        }
                    ]
                },
            ]
        },
    ]
    # 一级/二级/三级指标位置指针
    first_begin = 1
    sed_begin = 1
    tri_begin = 1
    # 创建一个workbook对象，就相当于创建了一个Excel文件
    # encoding:设置编码，可写中文；style_compression:是否压缩，不常用
    workbook = xlwt.Workbook(encoding='utf-8')
    # 创建一个sheet对象，相当于创建一个sheet页
    # cell_overwrite_ok:是否可以覆盖单元格，默认为False
    worksheet = workbook.add_sheet('sheet2', cell_overwrite_ok=True)
    style = xlwt.XFStyle()
    font = xlwt.Font()
    borders = xlwt.Borders()
    alignment = xlwt.Alignment()
    font.name = '楷'
    font.height = 320
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    alignment.vert = 0x01
    alignment.horz = 0x02
    alignment.wrap = 1
    style.font = font
    style.borders = borders
    style.alignment = alignment
    worksheet.write(0, 0, '一级指标', style)
    worksheet.write(0, 1, '需求目的', style)
    worksheet.write(0, 2, '二级指标', style)
    worksheet.write(0, 3, '三级指标', style)
    worksheet.write(0, 4, '关键词', style)
    worksheet.write(0, 5, '文字内容', style)
    worksheet.write(0, 6, '图片数量', style)
    worksheet.write(0, 7, '表格数量', style)
    worksheet.write(0, 8, '句子数量', style)
    worksheet.write(0, 9, '常用词数量', style)
    worksheet.write(0, 10, '专业词数量', style)
    worksheet.write(0, 11, '数字个数', style)
    worksheet.write(0, 12, '文字信息披露质量', style)
    worksheet.write(0, 13, '最终得分', style)
    for index in range(0, 14):
        worksheet.col(index).width = 256*20
    for first_dict in data:  # 一个dict对应一个一级指标
        secend_list = first_dict['二级指标']  # 二级指标列表
        for secend_dict in secend_list:  # 一个dict对应一个二级指标
            thrid_list = secend_dict['三级指标']  # 三级指标列表
            for thrid_dict in thrid_list:  # 一个dict对应一个三级指标
                worksheet.write(tri_begin, 3, thrid_dict['三级指标名称'], style)
                worksheet.write(tri_begin, 4, thrid_dict['keywords'], style)
                worksheet.write(tri_begin, 5, thrid_dict['文字内容'], style)
                worksheet.write(tri_begin, 6, thrid_dict['图片数量'], style)
                worksheet.write(tri_begin, 7, thrid_dict['表格数量'], style)
                worksheet.write(tri_begin, 8, thrid_dict['句子数量'], style)
                worksheet.write(tri_begin, 9, thrid_dict['常用词数量'], style)
                worksheet.write(tri_begin, 10, thrid_dict['专业词数量'], style)
                worksheet.write(tri_begin, 11, thrid_dict['数字个数'], style)
                worksheet.write(tri_begin, 12, thrid_dict['文字信息披露质量'], style)
                worksheet.write(tri_begin, 13, thrid_dict['最终得分'], style)
                tri_begin += 1
            worksheet.write_merge(sed_begin, tri_begin-1,
                                  2, 2, secend_dict['二级指标名称'], style)
            sed_begin = tri_begin
        worksheet.write_merge(first_begin, sed_begin-1, 0,
                              0, first_dict['一级指标'], style)
        worksheet.write_merge(first_begin, sed_begin-1, 1,
                              1, first_dict['需求目的'], style)
        first_begin = sed_begin
    workbook.save(filepath)

def write_indicators_to_excel2(filepath, data):
    '''
    描述：将指标列表写入碳中和发展Excel
    参数：
        filepath: Excel文件路径
        data: 指标列表
    '''
    # 一级/二级/三级指标位置指针
    first_begin = 1
    sed_begin = 1
    tri_begin = 1
    # 创建一个workbook对象，就相当于创建了一个Excel文件
    # encoding:设置编码，可写中文；style_compression:是否压缩，不常用
    workbook = xlwt.Workbook(encoding='utf-8')
    # 创建一个sheet对象，相当于创建一个sheet页
    # cell_overwrite_ok:是否可以覆盖单元格，默认为False
    worksheet = workbook.add_sheet('sheet2', cell_overwrite_ok=True)
    style = xlwt.XFStyle()
    font = xlwt.Font()
    borders = xlwt.Borders()
    alignment = xlwt.Alignment()
    font.name = '楷'
    font.height = 320
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    alignment.vert = 0x01
    alignment.horz = 0x02
    alignment.wrap = 1
    style.font = font
    style.borders = borders
    style.alignment = alignment
    worksheet.write(0, 0, '一级指标', style)
    worksheet.write(0, 1, '二级指标', style)
    worksheet.write(0, 2, '三级指标', style)
    worksheet.write(0, 3, '关键词', style)
    worksheet.write(0, 4, '计分方法分类（关键词+数字+字数）', style)
    worksheet.write(0, 5, '终端采分点-衡量标准\方法', style)
    worksheet.write(0, 6, '最高分', style)
    worksheet.write(0, 7, '文字内容', style)
    worksheet.write(0, 8, '最终得分', style)
    for index in range(0, 9):
        worksheet.col(index).width = 256*20
    for first_dict in data:  # 一个dict对应一个一级指标
        secend_list = first_dict['二级指标']  # 二级指标列表
        for secend_dict in secend_list:  # 一个dict对应一个二级指标
            thrid_list = secend_dict['三级指标']  # 三级指标列表
            for thrid_dict in thrid_list:  # 一个dict对应一个三级指标
                worksheet.write(tri_begin, 2, thrid_dict['三级指标名称'], style)
                worksheet.write(tri_begin, 3, thrid_dict['keywords'], style)
                # 应对新增的三级指标的情况
                if '计分方法分类（关键词+数字+字数）' in thrid_dict:
                    worksheet.write(tri_begin, 4, thrid_dict['计分方法分类（关键词+数字+字数）'], style)
                if '终端采分方法' in thrid_dict:
                    worksheet.write(tri_begin, 5, thrid_dict['终端采分方法'], style)
                if '最高分' in thrid_dict:
                    worksheet.write(tri_begin, 6, thrid_dict['最高分'], style)
                worksheet.write(tri_begin, 7, thrid_dict['文字内容'], style)
                worksheet.write(tri_begin, 8, thrid_dict['最终得分'], style)
                tri_begin += 1
            worksheet.write_merge(sed_begin, tri_begin-1,
                                  1, 1, secend_dict['二级指标名称'], style)
            sed_begin = tri_begin
        worksheet.write_merge(first_begin, sed_begin-1, 0,
                              0, first_dict['一级指标'], style)
        first_begin = sed_begin
    workbook.save(filepath)

if __name__ == '__main__':
    data = read_indicators_from_excel2(os.path.join('D:\作业\研究生\研1\CarbonInfoSystem\data\企业碳中和发展评价指标体系.xls'))
    print(data)

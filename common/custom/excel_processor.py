import xlrd
import xlwt
from common.custom.keywords_processor import process_keywords

def read_indicators_from_excel(filepath):
    '''
    描述：从Excel获取指标列表
    参数：
        filepath: Excel文件路径
    返回值:
        indicators: 指标列表
    '''
    data = []  # 一级指标列表
    excel_data = xlrd.open_workbook(filename=filepath, formatting_info=True)
    table = excel_data.sheets()[0]
    merge = table.merged_cells #读出合并单元格,其形式为一个四元组(a,b,c,d) 分别代表起始与终止行/列
    for tupe0 in merge:#遍历合并单元格
        if tupe0[2] == 0 and tupe0[3] == 1:
            topic_temp = {}  # 指标主题和需求目的
            topic_temp["一级指标"] = table.cell_value(tupe0[0], tupe0[2])
            topic_temp["需求目的"] = table.cell_value(tupe0[0], tupe0[2] + 1)
            indicators_list = []  # 二级指标列表
            for tupe1 in merge:
                if tupe1[2] == 2 and tupe1[3] == 3 and tupe1[0] >= tupe0[0] and tupe1[1] <= tupe0[1]:
                    indicators_temp = {}  # 二级指标
                    indicators_temp["二级指标名称"] = table.cell_value(tupe1[0], tupe1[2])
                    last_indicator_list = []  # 三级指标列表
                    for index in range(tupe1[0], tupe1[1]):
                        last_indicator_temp = {}  # 三级指标
                        last_indicator_temp["三级指标名称"] = table.cell_value(index, tupe1[2] + 1)
                        last_indicator_temp["keywords"] = process_keywords(table.cell_value(index, tupe1[2] + 2))
                        last_indicator_list.append(last_indicator_temp)
                    indicators_temp["三级指标"] = last_indicator_list
                    indicators_list.append(indicators_temp)
            topic_temp["二级指标"] = indicators_list
            data.append(topic_temp)
    return data

def write_indicators_to_excel(filepath, data):
    '''
    描述：将指标列表写入Excel
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
                            "表格数量": 15
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
    workbook = xlwt.Workbook(encoding='utf-8')  # encoding:设置编码，可写中文；style_compression:是否压缩，不常用
    # 创建一个sheet对象，相当于创建一个sheet页
    worksheet = workbook.add_sheet('sheet2',cell_overwrite_ok=True) # cell_overwrite_ok:是否可以覆盖单元格，默认为False
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
    worksheet.write(0,0,'一级指标',style)
    worksheet.write(0,1,'需求目的',style)
    worksheet.write(0,2,'二级指标',style)
    worksheet.write(0,3,'三级指标',style)
    worksheet.write(0,4,'关键词',style)
    worksheet.write(0,5,'文字内容',style)
    worksheet.write(0,6,'图片数量',style)
    worksheet.write(0,7,'表格数量',style)
    for index in range(0,8):
        worksheet.col(index).width = 256*20
    for first_dict in data:#一个dict对应一个一级指标
        secend_list = first_dict['二级指标'] #二级指标列表
        for secend_dict in secend_list:#一个dict对应一个二级指标
            thrid_list = secend_dict['三级指标'] #三级指标列表
            for thrid_dict in thrid_list:#一个dict对应一个三级指标
                worksheet.write(tri_begin,3,thrid_dict['三级指标名称'],style)
                worksheet.write(tri_begin,4,thrid_dict['keywords'],style)
                worksheet.write(tri_begin,5,thrid_dict['文字内容'],style)
                worksheet.write(tri_begin,6,thrid_dict['图片数量'],style)
                worksheet.write(tri_begin,7,thrid_dict['表格数量'],style)
                tri_begin += 1
            worksheet.write_merge(sed_begin,tri_begin-1,2,2,secend_dict['二级指标名称'],style)
            sed_begin = tri_begin
        worksheet.write_merge(first_begin, sed_begin-1, 0, 0, first_dict['一级指标'],style)
        worksheet.write_merge(first_begin, sed_begin-1, 1, 1, first_dict['需求目的'],style)
        first_begin = sed_begin
    workbook.save(filepath)

# if __name__ == '__main__':
    
#     example_data = [
#         {
#             "一级指标": "一级指标",
#             "需求目的": "需求目的",
#             "二级指标": [
#                 {
#                     "二级指标名称": "二级指标名称",
#                     "三级指标": [
#                         {
#                             "三级指标名称": "三级指标名称",
#                             "keywords": "碳排放，中和",
#                             "文字内容": "碳排放碳排放碳排放碳排放",
#                             "图片数量": 18,
#                             "表格数量": 15
#                         },
#                         {
#                             "三级指标名称": "三级指标名称",
#                             "keywords": "碳排放，中和",
#                             "文字内容": "碳排放碳排放碳排放碳排放",
#                             "图片数量": 18,
#                             "表格数量": 15
#                         }
#                     ]
#                 },
#                 {
#                     "二级指标名称": "二级指标名称",
#                     "三级指标": [
#                         {
#                             "三级指标名称": "三级指标名称",
#                             "keywords": "碳排放，中和",
#                             "文字内容": "碳排放碳排放碳排放碳排放",
#                             "图片数量": 18,
#                             "表格数量": 15
#                         },
#                         {
#                             "三级指标名称": "三级指标名称",
#                             "keywords": "碳排放，中和",
#                             "文字内容": "碳排放碳排放碳排放碳排放",
#                             "图片数量": 18,
#                             "表格数量": 15
#                         }
#                     ]
#                 },
#             ]
#         },
#     ]
#     write_indicators_to_excel(data=example_data,filepath='test.xls')





    

import xlrd


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
    merge = table.merged_cells
    for tupe0 in merge:
        if tupe0[2] == 0 and tupe0[3] == 1:
            topic_temp = {}  # 指标主题和需求目的
            topic_temp["指标主题"] = table.cell_value(tupe0[0], tupe0[2])
            topic_temp["需求目的"] = table.cell_value(tupe0[0], tupe0[2] + 1)
            indicators_list = []  # 二级指标列表
            for tupe1 in merge:
                if tupe1[2] == 2 and tupe1[3] == 3 and tupe1[0] >= tupe0[0] and tupe1[1] <= tupe0[1]:
                    indicators_temp = {}  # 具体指标/二级指标
                    indicators_temp["具体指标名称"] = table.cell_value(tupe1[0], tupe1[2])
                    last_indicator_list = []  # 三级指标列表
                    for index in range(tupe1[0], tupe1[1]):
                        last_indicator_temp = {}  # 三级指标
                        last_indicator_temp["name"] = table.cell_value(index, tupe1[2] + 1)
                        last_indicator_temp["keywords"] = table.cell_value(index, tupe1[2] + 2)
                        last_indicator_list.append(last_indicator_temp)
                    indicators_temp["三级指标"] = last_indicator_list
                    indicators_list.append(indicators_temp)
            topic_temp["具体指标"] = indicators_list
            data.append(topic_temp)
    return data

def write_indicators_to_excel(filepath, data):
    '''
    描述：将指标列表写入Excel
    参数：
        filepath: Excel文件路径
        data: 指标列表
    '''
    
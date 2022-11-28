import os
import xlrd
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from common.base.base_respons import retJson

@csrf_exempt
def add_indicators(request):
    '''
    描述：添加三级指标
    方法：POST
    参数：
        name: 三级指标名称 
        type: 关键词上传类型 'file' | 'keywords'
        keywords: 关键词
        file: 关键词文件 (.txt文件 一行一个关键词)
    返回值:
        indicator: 新增三级指标
    '''
    indicator = {
        "指标主题": "新增的三级指标",
        "需求目的": "新增的三级指标",
        "具体指标": [
                {
                    "具体指标名称": "新增的三级指标",
                    "三级指标": [
                        {
                            "name": "新增的三级指标",
                            "key_words": "碳, 排放"
                        }
                    ]
                },
        ]
    }
    if request.method == 'GET':
        return retJson(code=0, msg="GET请求")
    elif request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')

        if type == 'file':
            file = request.FILES.get('file')
            if not file:
                return retJson(code=0, msg="请上传关键词文件")
            keywords = file.read().decode('utf-8')

        elif type == 'keywords':
            keywords = request.POST.get('keywords')
            if not keywords:
                return retJson(code=0, msg="请填写关键词")

        # 处理keywords
        keywords = keywords.replace(' ', ',')
        keywords = keywords.replace('，', ',')
        keywords = keywords.replace('、', ',')
        keywords = keywords.replace('\n', ',')
        keywords = keywords.replace('\r', ',')
        keywords = keywords.replace('\t', ',')
        keywords = keywords.replace(',,', ',')

        indicator["指标主题"] = name
        indicator["需求目的"] = name
        indicator["具体指标"][0]["具体指标名称"] = name
        indicator["具体指标"][0]["三级指标"][0]["name"] = name
        indicator["具体指标"][0]["三级指标"][0]["key_words"] = keywords

        return retJson(code=1, msg="success", data={"indicator": json.dumps(indicator, ensure_ascii=False)})


def system1_dataget(filename):
    data = []  # 一级指标列表
    excel_data = xlrd.open_workbook(filename=filename, formatting_info=True)
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


@csrf_exempt
def indicators(request):
    '''
    描述：获取指标列表
    方法：GET
    参数：
        system 
            说明: 
            system=1碳信息披露质量分析系统
            system=2企业碳中和发展分析系统
    返回值:
        indicators: 指标列表
    '''
    返回值示例 = [
        {
            "指标主题": "股东和投资者",
            "需求目的": "投资与融资决策依据；企业低碳战略及管理决策依据",
            "具体指标": [
                {
                    "具体指标名称": "碳排放风险与机遇",
                    "三级指标": [
                        {
                            "name": "碳减排过程中的风险识别与评估",
                            "key_words": "碳, xxx"
                        },
                        {
                            "name": "气候变化给企业带来的财务风险",
                            "key_words": "财务, xxx"
                        },
                    ]
                },
            ]
        },
    ]

    if request.method == 'GET':
        system = int(request.GET.get('system'))
        res = []
        if system == 1:
            filename = os.path.join(settings.BASE_DIR, "data", "碳信息披露质量指标体系.xls")
            res = system1_dataget(filename)
            return retJson(code=1, msg="success", data={"indicators": res})
        elif system == 2:

            return retJson(code=1, msg="success", data={"indicators": res})
    elif request.method == 'POST':
        return retJson(code=0, msg="POST请求")

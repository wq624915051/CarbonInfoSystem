import os
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from common.base.base_respons import retJson
from common.custom.excel_processor import read_indicators_from_excel
from common.custom.keywords_processor import split_keywords_with_comma

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
        "一级指标": "新增的一级指标",
        "需求目的": "新增的一级指标",
        "二级指标": [
                {
                    "二级指标名称": "新增的二级指标",
                    "三级指标": [
                        {
                            "三级指标名称": "新增的三级指标",
                            "keywords": "碳, 排放"
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
        
        else:
            return retJson(code=0, msg="关键词类型需为 'file' | 'keywords'")

        # 处理keywords
        keywords = split_keywords_with_comma(keywords)

        indicator["一级指标"] = name
        indicator["需求目的"] = name
        indicator["二级指标"][0]["二级指标名称"] = name
        indicator["二级指标"][0]["三级指标"][0]["三级指标名称"] = name
        indicator["二级指标"][0]["三级指标"][0]["keywords"] = keywords

        return retJson(code=1, msg="success", data={"indicator": indicator})


@csrf_exempt
def get_indicators(request):
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
            "一级指标": "股东和投资者",
            "需求目的": "投资与融资决策依据；企业低碳战略及管理决策依据",
            "二级指标": [
                {
                    "二级指标名称": "碳排放风险与机遇",
                    "三级指标": [
                        {
                            "三级指标名称": "碳减排过程中的风险识别与评估",
                            "keywords": "碳, xxx"
                        },
                        {
                            "三级指标名称": "气候变化给企业带来的财务风险",
                            "keywords": "财务, xxx"
                        },
                    ]
                },
            ]
        },
    ]

    if request.method == 'GET':
        system = int(request.GET.get('system'))
        if system == 1:
            filepath = os.path.join(settings.BASE_DIR, "data", "碳信息披露质量关键词.xls")
            res = read_indicators_from_excel(filepath)
            return retJson(code=1, msg="success", data={"indicators": res})
        elif system == 2:
            filepath = os.path.join(settings.BASE_DIR, "data", "企业碳中和发展评价指标体系.xls") # TODO
            res = read_indicators_from_excel(filepath)
            return retJson(code=1, msg="success", data={"indicators": res})
        else:
            return retJson(code=0, msg="参数只能为1或2")
    elif request.method == 'POST':
        return retJson(code=0, msg="POST请求")

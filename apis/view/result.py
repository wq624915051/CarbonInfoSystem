import os
import json
import datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from common.base.base_respons import retJson
from common.custom.myPDF import MyPDF
from common.custom.analysisPDF import AnalysisPDF

@csrf_exempt
def calculate(request):
    """
    描述：对之前上传每个PDF根据指标进行分析计算
    方法：POST
    参数：
        indicators: list[dict] 指标列表
        filepaths: list[string] pdf文件路径列表
        w1: int 贡献度1
        w2: int 贡献度2
        w3: int 贡献度3
    返回值:
        files_indicators: list[dict] 各个PDF文件的指标列表
    """

    files_indicators = [
        {
            "company": "龙湖",
            "filepath": "path/to/file",
            "indicators": [
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
            ],
        }
    ]

    if request.method == 'POST':
        try:
            # 获取参数
            received_json_data = json.loads(request.body.decode().replace("'", "\""))
            indicators = received_json_data.get('indicators')
            filepaths = received_json_data.get('filepaths')
            systemId = int(received_json_data.get('system'))
            w1 = float(received_json_data.get('w1'))
            w2 = float(received_json_data.get('w2'))
            w3 = float(received_json_data.get('w3'))
            
            ############
            # FOR TEST #
            # return retJson(code=1, msg="success", data={"files_indicators": files_indicators})
            # FOR TEST #
            ############

            # 判断filepaths中的文件是否存在
            for filepath in filepaths:
                if not os.path.exists(filepath):
                    return retJson(code=0, msg=f"文件 {filepath} 不存在")
            
            # 判断systemId是否为1或2
            if systemId not in [1, 2]:
                return retJson(code=0, msg="systemId参数错误, 只能为1或2")

            # 在media/downloads/下按时间生成文件夹, 用于存放分析结果Excel
            now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            excel_base_path = os.path.join(settings.MEDIA_ROOT, "downloads", now_time)
            if not os.path.exists(excel_base_path):
                os.makedirs(excel_base_path)

            # 遍历每个PDF文件，进行分析计算
            files_indicators = []
            for filepath in filepaths:
                analysis_pdf = AnalysisPDF(filepath, indicators, systemId, w1, w2, w3, excel_base_path)
                files_indicators.append(analysis_pdf.result)

            # 返回结果
            return retJson(code=1, msg="success", data={"files_indicators": files_indicators})
        except Exception as e:
            return retJson(code=0, msg="参数错误")
    elif request.method == 'GET':
        return retJson(code=0, msg="请求方式错误")

import os
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
                    "指标主题": "指标主题",
                    "需求目的": "需求目的",
                    "具体指标": [
                        {
                            "具体指标名称": "具体指标名称",
                            "三级指标": [
                                {
                                    "name": "三级指标名称",
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
        # 获取参数
        indicators = request.POST.get('indicators')
        filepaths = request.POST.get('filepaths')
        w1 = request.POST.get('w1')
        w2 = request.POST.get('w2')
        w3 = request.POST.get('w3')
        
        ############
        # FOR TEST #
        return retJson(code=1, msg="success", data={"files_indicators": files_indicators})
        # FOR TEST #
        ############

        # 在media/downloads/下按时间生成文件夹
        now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        excel_base_path = os.path.join(settings.MEDIA_ROOT, "downloads", now_time)
        if not os.path.exists(excel_base_path):
            os.makedirs(excel_base_path)

        # 遍历每个PDF文件
        files_indicators = []
        for filepath in filepaths:
            analysis_pdf = AnalysisPDF(filepath, indicators, w1, w2, w3, excel_base_path)
            files_indicators.append(analysis_pdf.result)

        # 返回结果
        return retJson(code=1, msg="success", data={"files_indicators": files_indicators})

    elif request.method == 'GET':
        return retJson(code=0, msg="请求方式错误")

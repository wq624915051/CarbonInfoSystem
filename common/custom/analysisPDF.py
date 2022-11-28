'''
AnalysisPDF类
对每个PDF进行分析
'''
import os
import datetime
from django.conf import settings

from common.custom.myPDF import MyPDF


class AnalysisPDF():
    '''
    描述：对每个PDF进行分析
    参数：
        filepath: string pdf文件路径
        indicators: list[dict] 指标列表
        w1: int 贡献度1
        w2: int 贡献度2
        w3: int 贡献度3
        excel_base_path: string excel文件存放路径
    '''

    def __init__(self, filepath, indicators, w1, w2, w3, excel_base_path) -> None:
        self.filepath = filepath
        self.indicators = indicators
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.excel_base_path = excel_base_path
        self.date = datetime.datetime.now().strftime('%Y%m%d')

        self.pdf = MyPDF(self.filepath, media_root=settings.MEDIA_ROOT) # 提取PDF内容存储到self.pdf.documnet_info

        self.example_result = {
            "company": "龙湖",
            "company_code": "123456",
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
                                    "key_words": "碳排放，中和",
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

        # 初始化结果
        self.result = {}

        # 获取公司名字
        self.company_name = self.get_company_name()
        self.result["company"] = self.company_name

        # 获取公司股票代码
        self.company_code = self.get_company_code()
        self.result["company_code"] = self.company_code

        # # 对每个指标进行分析, 结果保存到 self.indicators 中
        for indicator_level_1 in self.indicators:
            for indicator_level_2 in indicator_level_1["具体指标"]:
                for indicator_level_3 in indicator_level_2["三级指标"]:
                    # TODO
                    indicator_level_3["文字内容"] = ""
                    indicator_level_3["图片数量"] = 0
                    indicator_level_3["表格数量"] = 0

        self.result["indicators"] = self.indicators
        self.result["filepath"] = self.save_indicators()

    def get_company_name(self):
        '''
        描述：获取公司名字
        返回值：
            company_name: string 公司名字
        '''
        company = os.path.basename(self.filepath)
        company = company.split('.')[0]  # "股票代码_公司名称.pdf"
        company_name = company.split('_')[1]
        return company_name

    def get_company_code(self):
        '''
        描述：获取公司股票代码
        返回值：
            company: string 公司股票代码
        '''
        company = os.path.basename(self.filepath)
        company = company.split('.')[0]  # "股票代码_公司名称.pdf"
        company_code = company.split('_')[0]
        return company_code

    def save_indicators(self):
        '''
        描述：保存指标到EXCEL中
        返回值：
            filepath: string 保存的文件路径
        '''
        filename = f"{self.company_code}_{self.company_name}_{self.date}.xlsx"
        filepath = os.path.join(self.excel_base_path, filename)

        # TODO 保存 self.indicators 到filepath中

        return filepath

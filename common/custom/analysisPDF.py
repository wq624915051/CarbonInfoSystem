'''
AnalysisPDF类
对每个PDF进行分析
'''
import os
import datetime
from django.conf import settings

from common.custom.myPDF import MyPDF
from common.custom.excel_processor import write_indicators_to_excel
from common.custom.keywords_processor import get_paragraphs_with_keywords
from common.custom.keywords_processor import get_sentences_with_keywords

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

    def __init__(self, filepath, indicators, systemId, w1, w2, w3, excel_base_path) -> None:
        self.filepath = filepath
        self.indicators = indicators
        self.systemId = systemId
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.excel_base_path = excel_base_path
        self.date = datetime.datetime.now().strftime('%Y%m%d')

        self.pdf = MyPDF(self.filepath, media_root=settings.MEDIA_ROOT) # 提取PDF内容存储到self.pdf.document_info

        self.example_result = {
            "company": "龙湖",
            "company_code": "123456",
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

        # 初始化结果
        self.result = {}

        # 获取公司名字
        self.company_name = self.get_company_name()
        self.result["company"] = self.company_name

        # 获取公司股票代码
        self.company_code = self.get_company_code()
        self.result["company_code"] = self.company_code

        # Execl文件保存路径
        self.execl_filename = f"{self.company_code}_{self.company_name}_{self.date}.xls"
        self.execl_filepath = os.path.join(self.excel_base_path, self.execl_filename)

        # 每个指标进行分析, 结果保存到 self.indicators 中
        for indicator_level_1 in self.indicators:
            for indicator_level_2 in indicator_level_1["二级指标"]:
                for indicator_level_3 in indicator_level_2["三级指标"]:
                    indicator_level_3_name = indicator_level_3["三级指标名称"]
                    # 用,分割关键词
                    indicator_level_3_keywords = [keyword.strip() for keyword in indicator_level_3["keywords"].split(',')]
                    if self.systemId == 1:
                        # 筛选含有碳、环保、绿色的相关段落
                        self.relevant_pno_paragraphs = get_paragraphs_with_keywords(self.pdf.document_info, ["碳", "绿色", "环保"])
                        self.relevant_paragraphs = [item[1] for item in self.relevant_pno_paragraphs]
                        # 进行分析
                        content, image_count, table_count = self.analysis_with_keywords_system1(indicator_level_3_name, indicator_level_3_keywords)
                        indicator_level_3["文字内容"] = content
                        indicator_level_3["图片数量"] = image_count
                        indicator_level_3["表格数量"] = table_count
                    elif self.systemId == 2:
                        self.analysis_with_keywords_system2(indicator_level_3_name, indicator_level_3_keywords)
                    print(indicator_level_3)

        self.result["indicators"] = self.indicators
        self.result["filepath"] = self.execl_filepath
        # write_indicators_to_excel(self.execl_filepath, self.result["indicators"])

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

    def analysis_with_keywords_system1(self, name, keywords):
        '''
        描述：根据三级指标名称及关键词进行分析
        参数：
            name: string 指标名称
            keywords: list 关键词列表
        返回值：
            content: string 提取的文字内容
            image_count: int 图片数量
            table_count: int 表格数量
        '''
        if len(keywords) == 0:
            return "", 0, 0 # 关键词没有就空着
            
        if name == "高管致辞":
            # 获取高管致辞段落 及 段落中含有碳、环保、绿色的句子
            pno_paragraphs = get_paragraphs_with_keywords(self.pdf.document_info, ["致辞", "高管致辞", "董事长致辞", "董事长"])
            pno_sentences = get_sentences_with_keywords(pno_paragraphs, ["碳", "绿色", "环保"])
            
            sentences = [item[1] for item in pno_sentences]
            content = "\n".join(sentences)

            pno_list = [item[0] for item in pno_sentences] # 句子所在的页码
            pno_list = list(set(pno_list)) # 去重
            # 获取图片数量和表格数量
            image_count = sum([page_info["image_count"] for page_info in self.pdf.document_info if page_info["pno"] in pno_list])
            table_count = sum([page_info["table_count"] for page_info in self.pdf.document_info if page_info["pno"] in pno_list])
            return content, image_count, table_count

        elif name == "投入金额占营业总支出的比例":
            pass
        elif name == "减少的二氧化碳降低百分比":
            pass
        else:
            pass
        text = ""
        
        return text

    def analysis_with_keywords_system2(self, name, keywords):
        pass

if __name__ == "__main__":
    # 测试
    w1, w2, w3 = 1, 1, 1
    filepath = "D:/ALL/项目/碳信息披露/测试pdf/002916_深南电路_2021.PDF"
    excel_base_path = "D:/ALL/项目/碳信息披露/CarbonInfoSystem/media/ownloads/"
    
    indicators = [
            {
                "一级指标": "股东和投资者",
                "需求目的": "投资与融资决策依据；企业低碳战略及管理决策依据",
                "二级指标": [
                    {
                        "二级指标名称": "碳排放风险与机遇",
                        "三级指标": [
                            {
                                "三级指标名称": "碳减排过程中的风险识别与评估",
                                "keywords": "环境风险、环保风险、碳中和风险、能源风险、节能风险、风险"
                            },
                            {
                                "三级指标名称": "气候变化给企业带来的财务风险",
                                "keywords": "成本节约、财务风险、成本增加、价格、浮动"
                            },
                            {
                                "三级指标名称": "企业碳排放所受的政府管制风险",
                                "keywords": "政策风险、法律风险、法规风险"
                            },
                            {
                                "三级指标名称": "碳减排可能给企业带来的机遇",
                                "keywords": "机遇、成本节约、减少成本、降低成本、增加收入、应对"
                            },
                            {
                                "三级指标名称": "碳汇过程中的可逆性风险（如森林火灾等）",
                                "keywords": "森林火灾"
                            }
                        ]
                    }
                    ]
            }
            ]

    analysis_pdf = AnalysisPDF(filepath, indicators, w1, w2, w3, excel_base_path)


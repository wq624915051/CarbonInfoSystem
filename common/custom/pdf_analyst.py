'''
AnalysisPDF类
对每个PDF进行分析
'''
import os
import re
import sys
import jieba
import datetime
import numpy as np


from django.conf import settings
from common.base.base_respons import retJson
from common.custom.pdf_processor import PdfProcessor, clean_content
from common.custom.excel_processor import write_indicators_to_excel1
from common.custom.excel_processor import write_indicators_to_excel2
from common.custom.excel_processor import read_ESG_from_excel
from common.custom.excel_processor import read_terms_from_excel
from common.custom.keywords_processor import split_keywords
from common.custom.keywords_processor import get_sentences_count
from common.custom.keywords_processor import get_table_image_count
from common.custom.keywords_processor import get_paragraphs_with_keywords
from common.custom.keywords_processor import get_paragraphs_with_keywords_precisely
from common.custom.keywords_processor import get_sentences_with_keywords
from common.custom.keywords_processor import get_management_speech_paragraphs
from common.custom.utils import remove_duplicate, check_pno

class PdfAnalyst():
    '''
    描述：对每个PDF进行分析
    参数：
        filepath: string pdf文件路径
        indicators: list[dict] 指标列表
        systemId: int 系统ID
        w1: int 贡献度1
        w2: int 贡献度2
        w3: int 贡献度3
        excel_base_path: string excel文件存放路径
    '''

    def __init__(self, file, indicators, systemId, w1, w2, w3, excel_base_path) -> None:
        self.file = file
        self.indicators = indicators
        self.systemId = systemId
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.excel_base_path = excel_base_path # excel文件存放路径

        self.filepath = self.file["filepath"] # pdf文件路径

        # 先把页码变为字符串，方便后面空字符串的判断
        self.pno_start = str(self.file["pno_start"]) # 高管致辞开始页码
        self.pno_end = str(self.file["pno_end"]) # 高管致辞结束页码
        check_pno(self.pno_start, self.pno_end) # 判断页码是否合法

        self.date = datetime.datetime.now().strftime('%Y%m%d')

        self.pdf = PdfProcessor(self.filepath, media_root=settings.MEDIA_ROOT) # 提取PDF内容存储到self.pdf.document_info
        self.pdf.run()
        self.keywords_normal = ["碳", "绿色", "环保"]

        # 读取ESG数据
        filepath_ESG_data = os.path.join(settings.BASE_DIR, "data", "数据-股权融资优势和ESG评级.xls")
        self.ESG_data = read_ESG_from_excel(filepath_ESG_data)

        # 读取碳中和专业词
        filepath_professional_words = os.path.join(settings.BASE_DIR, "data", "所需表.xls")
        self.professional_words = read_terms_from_excel(filepath_professional_words, type=0)

        # 读取常用词汇
        filepath_common_words = os.path.join(settings.BASE_DIR, "data", "所需表.xls")
        self.common_words = read_terms_from_excel(filepath_common_words, type=1)

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

        # 记录句子出现的次数
        self.sentence_count_dict = {}

        # 获取公司股票代码、名字、年份
        self.company_code, self.company_name, self.year = self.get_company_code_name_year()
        self.result["company_code"] = self.company_code
        self.result["company"] = self.company_name
        self.result["year"] = self.year

        # Execl文件保存路径
        self.system_name = "碳信息披露" if self.systemId == 1 else "碳中和发展评价"
        self.execl_filename = f"{self.company_code}_{self.company_name}_{self.year}_{self.date}_{self.system_name}.xls"
        self.execl_filepath = os.path.join(self.excel_base_path, self.execl_filename)

        # 每个指标进行分析, 结果保存到 self.indicators 中
        for indicator_level_1 in self.indicators:
            for indicator_level_2 in indicator_level_1["二级指标"]:
                for indicator_level_3 in indicator_level_2["三级指标"]:
                    indicator_level_3_name = indicator_level_3["三级指标名称"]
                    """
                    用,分割关键词
                    句子中出现第一类关键词即可匹配
                    句子中必须同时出现第二、第三类关键词才能匹配
                    """
                    keywords_1, keywords_2, keywords_3 = split_keywords(indicator_level_3["keywords"])

                    if self.systemId == 1:
                        # 筛选含有碳、环保、绿色的相关段落
                        self.relevant_pno_paragraphs = get_paragraphs_with_keywords_precisely(
                            self.pdf.document_info, self.keywords_normal, sentence_number=5)
                        # 根据关键词进行分析
                        content, image_count, table_count, sentences_count = self.analysis_with_keywords_system1(indicator_level_3_name, keywords_1, keywords_2, keywords_3)
                        indicator_level_3["文字内容"] = content
                        indicator_level_3["图片数量"] = image_count
                        indicator_level_3["表格数量"] = table_count
                        indicator_level_3["句子数量"] = sentences_count
                        indicator_level_3["常用词数量"] = self.get_common_words_count(content)
                        indicator_level_3["专业词数量"] = self.get_professional_words_count(content)
                        indicator_level_3["数字个数"] = self.get_number_count(content)
                        indicator_level_3["文字信息披露质量"] = self.text_quality(indicator_level_3)
                        indicator_level_3["最终得分"] = self.get_final_score(indicator_level_3)
                    elif self.systemId == 2:
                        # 应对新增的三级指标的情况 三级指标计分方式
                        if "计分方法分类（关键词+数字+字数）" in indicator_level_3.keys():
                            indicator_level_3_method = indicator_level_3["计分方法分类（关键词+数字+字数）"].strip()
                        else:
                            indicator_level_3_method = "关键词"
                        # 筛选含有绿色 碳 温室气体 环保 能源的相关段落
                        self.relevant_pno_paragraphs = get_paragraphs_with_keywords_precisely(
                            self.pdf.document_info, ["绿色", "碳", "温室气体", "环保", "能源"], sentence_number=5)
                        # 根据关键词进行分析
                        content, score = self.analysis_with_keywords_system2(
                            indicator_level_3_name, indicator_level_3_method, keywords_1, keywords_2, keywords_3)
                        indicator_level_3["文字内容"] = content
                        indicator_level_3["最终得分"] = score

        self.result["indicators"] = self.indicators
        if self.systemId == 1:
            write_indicators_to_excel1(self.execl_filepath, self.result["indicators"])
        elif self.systemId == 2:
            write_indicators_to_excel2(self.execl_filepath, self.result["indicators"])
        
        # 获取相对路径
        relative_path = os.path.relpath(self.execl_filepath, settings.BASE_DIR)
        self.result["filepath"] = os.path.join(os.path.sep, relative_path)

    def get_company_code_name_year(self):
        '''
        描述：获取公司股票代码、公司名字、年份
        返回值：
            code: string 公司股票代码
            name: string 公司名字
            year: int 年份
        '''
        filename = os.path.basename(self.filepath).split('.')[0]  # "股票代码_公司名称_年份.pdf"
        code = filename.split('_')[0]
        name = filename.split('_')[1]
        year = int(filename.split('_')[2])
        return code, name, year

    def analysis_with_keywords_system1(self, name, keywords_1, keywords_2, keywords_3):
        '''
        描述：
            根据三级指标名称及关键词对碳信息披露进行分析
            句子中出现第一类关键词即可匹配
            句子中必须同时出现第二、第三类关键词才能匹配
        参数：
            name: string 指标名称
            keywords_1: list 第一类关键词列表
            keywords_2: list 第二类关键词列表
            keywords_3: list 第三类关键词列表
        返回值：
            content: string 提取的文字内容
            image_count: int 图片数量
            table_count: int 表格数量
            sentences_count: int 句子数量
        '''
        if len(keywords_1) == 0 and len(keywords_2) == 0 and len(keywords_3) == 0:
            return "", 0, 0, 0 # 关键词没有就空着
            
        if name == "高管致辞":
            # 获取高管致辞段落
            keywords_special = ["致辞", "高管致辞", "董事长致辞", "董事长"]
            # pno_paragraphs = get_paragraphs_with_keywords_precisely(self.pdf.document_info, keywords_special, sentence_number=30)
            pno_paragraphs = get_management_speech_paragraphs(self.pdf.document_info, self.pno_start, self.pno_end)
            # 段落中含有碳、环保、绿色的句子
            pno_sentences = get_sentences_with_keywords(pno_paragraphs, self.keywords_normal, keywords_2=[], keywords_type="single")
            # 高管致辞部分不需要去重
            sentences = remove_duplicate([item[1].strip() for item in pno_sentences])
            # 获取表格和图片数量
            table_count, image_count = get_table_image_count(self.pdf.document_info, self.keywords_normal, keywords_special, keywords_3=[], keywords_type="single", sentences=sentences)
        elif name == "减少的二氧化碳降低百分比":
            # 段落中含有 关键词 的句子
            keywords_1.append("二氧化碳排放下降")
            keywords_1.append("二氧化碳排放量下降")
            keywords_1.append("二氧化碳排放量减少")
            # 段落中含有 第一类关键词 的句子
            pno_sentences = get_sentences_with_keywords(self.relevant_pno_paragraphs, keywords_1, keywords_2=[], keywords_type="single")
            # 添加 段落中同时含有 第二类关键词和第三类关键词 的句子
            pno_sentences.extend(get_sentences_with_keywords(self.relevant_pno_paragraphs, keywords_2, keywords_3, keywords_type="double"))
            sentences = self.get_nonrepeated_sentences(pno_sentences) # 去除与之前指标相重复的句子

            # 获取表格和图片数量 第一类关键词
            table_count_1, image_count_1 = get_table_image_count(self.pdf.document_info, self.keywords_normal, keywords_1, keywords_3=[], keywords_type="single", sentences=sentences)
            
            # 获取表格和图片数量 第二类关键词和第三类关键词
            table_count_2, image_count_2 = get_table_image_count(self.pdf.document_info, self.keywords_normal, keywords_2, keywords_3, keywords_type="double", sentences=sentences)

            table_count = table_count_1 + table_count_2
            image_count = image_count_1 + image_count_2
            
        else:
            # 段落中含有 第一类关键词 的句子
            pno_sentences = get_sentences_with_keywords(self.relevant_pno_paragraphs, keywords_1, keywords_2=[], keywords_type="single")
            # 添加 段落中同时含有 第二类关键词和第三类关键词 的句子
            pno_sentences.extend(get_sentences_with_keywords(self.relevant_pno_paragraphs, keywords_2, keywords_3, keywords_type="double"))

            sentences = self.get_nonrepeated_sentences(pno_sentences) # 去除与之前指标相重复的句子    
            # 获取表格和图片数量
            table_count_1, image_count_1 = get_table_image_count(self.pdf.document_info, self.keywords_normal, keywords_1, keywords_3=[], keywords_type="single", sentences=sentences)
            table_count_2, image_count_2 = get_table_image_count(self.pdf.document_info, self.keywords_normal, keywords_2, keywords_3, keywords_type="double", sentences=sentences)
            table_count = table_count_1 + table_count_2
            image_count = image_count_1 + image_count_2

        
        content = "\n".join(sentences) # 拼接成字符串

        pno_list = [item[0] for item in pno_sentences] # 句子所在的页码
        pno_list = remove_duplicate(pno_list) # 页码去重

        # 获取图片数量和表格数量
        # image_count = sum([page_info["image_count"] for page_info in self.pdf.document_info if page_info["pno"] in pno_list])
        # table_count = sum([page_info["table_count"] for page_info in self.pdf.document_info if page_info["pno"] in pno_list])
        
        # 句子数量
        sentences_count = get_sentences_count(sentences)

        # 如果没有文字内容，则图片数量和表格数量为0
        if content.strip() == "":
            image_count = 0
            table_count = 0
            sentences_count = 0

        return content, image_count, table_count, sentences_count

    def analysis_with_keywords_system2(self, name, method, keywords_1, keywords_2, keywords_3):
        '''
        描述：根据三级指标名称及关键词对碳中和发展进行分析
        参数：
            name: string 指标名称
            keywords_1: list 第一类关键词列表
            keywords_2: list 第二类关键词列表
            keywords_3: list 第三类关键词列表
        返回值：
            content: string 提取的文字内容
            score: int 分数
        '''
        # 需要忽略的三级指标名称列表
        ignore_name_list = []
        
        if len(keywords_1) == 0 and len(keywords_2) == 0 and len(keywords_3) == 0:
            return "", ""
        if name in ignore_name_list:
            return "", ""
        if name == "碳信息披露时间（随年报披露、随披露社会责任报告或可持续发展报告、单独披露碳中和报告或路线图）":
            score = 1
            return "", score 
        if name == "高管有关双碳目标或碳减排的声明与承诺":
            # 获取高管致辞段落
            # pno_paragraphs = get_paragraphs_with_keywords_precisely(self.pdf.document_info, ["致辞", "高管致辞", "董事长致辞", "管理层致辞"], sentence_number=30)
            pno_paragraphs = get_management_speech_paragraphs(self.pdf.document_info, self.pno_start, self.pno_end)
            # 段落中含有碳、气候、节能、能源的句子
            pno_sentences = get_sentences_with_keywords(pno_paragraphs, ["碳", "气候", "节能", "能源"], keywords_2=[], keywords_type="single")
            # sentences = self.get_nonrepeated_sentences(pno_sentences) # 去除与之前指标相重复的句子
            sentences = remove_duplicate([item[1].strip() for item in pno_sentences])
            content = "\n".join(sentences) # 拼接成字符串
            score = 1 if len(sentences) else 0 # 有句子则得分1分
            return content, score

        elif name == "是否将此类气候变化流程纳入企业的整体风险管理系统或流程":
            # 获取“风险”段落
            pno_paragraphs = get_paragraphs_with_keywords_precisely(
                self.pdf.document_info, ["风险"], sentence_number=5)
            # 段落中含有管理机制、制度、流程、整体、气候变化、能源的句子
            pno_sentences = get_sentences_with_keywords(pno_paragraphs, ["管理机制", "制度", "流程", "整体", "气候变化", "能源"], keywords_2=[], keywords_type="single")
            # sentences = self.get_nonrepeated_sentences(pno_sentences) # 去除与之前指标相重复的句子
            sentences = remove_duplicate([item[1].strip() for item in pno_sentences])
            content = "\n".join(sentences) # 拼接成字符串
            score = 1 if len(sentences) else 0 # 有句子则得分1分
            return content, score

        elif name == "利益相关者沟通中识别了与双碳目标或低碳有关的利益相关者及其期望":
            # 获取“利益相关者”段落
            pno_paragraphs = get_paragraphs_with_keywords_precisely(
                self.pdf.document_info, ["利益相关者"], sentence_number=5)
            # 段落中含有碳、气候变化、节能、能源的句子
            pno_sentences = get_sentences_with_keywords(pno_paragraphs, ["碳", "气候变化", "节能", "能源"], keywords_2=[], keywords_type="single")
            # sentences = self.get_nonrepeated_sentences(pno_sentences) # 去除与之前指标相重复的句子
            sentences = remove_duplicate([item[1].strip() for item in pno_sentences])
            content = "\n".join(sentences) # 拼接成字符串
            score = 1 if len(sentences) else 0 # 有句子则得分1分
            return content, score

        elif name == "采取一致的方法学对长期的碳排放情况进行比较":
            # 获取“碳排放”段落
            pno_paragraphs = get_paragraphs_with_keywords_precisely(
                self.pdf.document_info, ["碳排放"], sentence_number=5)
            # 获取去年和前年的年份
            last_year, last_last_year = str(self.year - 1), str(self.year - 2)
            # 段落中含有去年和前年的句子
            pno_sentences = get_sentences_with_keywords(pno_paragraphs, [last_year, last_last_year], keywords_2=[], keywords_type="single")
            # sentences = self.get_nonrepeated_sentences(pno_sentences) # 去除与之前指标相重复的句子
            sentences = remove_duplicate([item[1].strip() for item in pno_sentences])
            content = "\n".join(sentences) # 拼接成字符串
            score = 1 if len(sentences) else 0 # 有句子则得分1分
            return content, score

        elif name == "企业投资成本":
            if self.company_code in self.ESG_data.keys():
                if self.year in self.ESG_data[self.company_code]["年份记录"]:
                    score = self.ESG_data[self.company_code][self.year]["股权融资优势"]
                    return "", score
                else:
                    score = 0
                    return f"{self.company_code}_{self.company_name}_{self.year}.PDF 未找到此年的股权融资优势数据", score
                    # raise Exception(f"{self.company_code}_{self.company_name}_{self.year}.PDF 未找到此年的股权融资优势数据")
            else:
                score = 0
                return f"{self.company_code}_{self.company_name}_{self.year}.PDF 未找到此企业的股权融资优势数据", score
                # raise Exception(f"{self.company_code}_{self.company_name}_{self.year}.PDF 未找到此企业的股权融资优势数据")

        elif name == "wind ESG评级":
            if self.company_code in self.ESG_data.keys():
                if self.year in self.ESG_data[self.company_code]["年份记录"]:
                    score = self.ESG_data[self.company_code][self.year]["ESG评级"]
                    return "", score
                else:
                    score = 0
                    return f"{self.company_code}_{self.company_name}_{self.year}.PDF 未找到此年的Wind ESG评级数据", score
                    # raise Exception(f"{self.company_code}_{self.company_name}_{self.year}.PDF 未找到此年的Wind ESG评级数据")
            else:
                score = 0
                return f"{self.company_code}_{self.company_name}_{self.year}.PDF 未找到此企业的Wind ESG评级数据", score
                # raise Exception(f"{self.company_code}_{self.company_name}_{self.year}.PDF 未找到此企业的Wind ESG评级数据")

        elif "充分披露了企业碳排放相关信息" in name:
            "充分披露了企业碳排放相关信息（即完整披露确碳、减碳、抵碳的核心题项）"
            # 计算前三个一级指标的平均分
            score_list = []
            for indicator_level_1 in self.indicators:
                for indicator_level_2 in indicator_level_1["二级指标"]:
                    for indicator_level_3 in indicator_level_2["三级指标"]:
                        if "最终得分" in indicator_level_3.keys():
                            score_list.append(float(indicator_level_3["最终得分"]))
            score = np.average(score_list)
            return "", score

        elif name == "企业披露的碳排放量涵盖了组织边界和运营边界以内的总排放量":
            score_var1 = self.indicators[0]["二级指标"][0]["三级指标"][0]["最终得分"]
            score_var2 = self.indicators[0]["二级指标"][0]["三级指标"][1]["最终得分"]
            score = 1 if (score_var1 != 0 or score_var2 != 0) else 0
            return "", score
        
        elif "使用数字进行信息披露的程度" in name:
            "使用数字进行信息披露的程度（披露了范围一、范围二、范围三的碳排放量或者能源消耗量（电、煤、石油天然气等）的具体值）"
            # 范围一
            range_1_key_2 = ["范围一", "范畴一"]
            range_1_key_3 = ["二氧化碳当量", "排放量", "直接"]
            # 范围二
            range_2_key_2 = ["范围二", "范畴二"]
            range_2_key_3 = ["二氧化碳当量", "间接", "外购"]
            # 范围三
            range_3_key_2 = ["范围三", "范畴三"]
            range_3_key_3 = ["二氧化碳当量"]
            # 能源消耗量
            energy_key_1 = ["能源消耗量", "能源消耗密度", "能源消费量", "总能耗", "综合能耗"]

            range_1 = get_sentences_with_keywords(self.relevant_pno_paragraphs, range_1_key_2, range_1_key_3, keywords_type="double")
            range_2 = get_sentences_with_keywords(self.relevant_pno_paragraphs, range_2_key_2, range_2_key_3, keywords_type="double")
            range_3 = get_sentences_with_keywords(self.relevant_pno_paragraphs, range_3_key_2, range_3_key_3, keywords_type="double")
            energy = get_sentences_with_keywords(self.relevant_pno_paragraphs, energy_key_1, keywords_2=[], keywords_type="single")

            range_1_num = len(remove_duplicate([item[1].strip() for item in range_1]))
            range_2_num = len(remove_duplicate([item[1].strip() for item in range_2]))
            range_3_num = len(remove_duplicate([item[1].strip() for item in range_3]))
            energy_num = len(remove_duplicate([item[1].strip() for item in energy]))

            range_1_score = 1 if range_1_num > 0 else 0
            range_2_score = 1 if range_2_num > 0 else 0
            range_3_score = 1 if range_3_num > 0 else 0
            energy_score = 1 if energy_num > 0 else 0

            score = range_1_score + range_2_score + range_3_score
            if score != 0:
                return "", score + 1
            elif energy_score == 1:
                return "", 1
            else:
                return "", 0

        else:
            # 段落中含有 第一类关键词 的句子
            pno_sentences = get_sentences_with_keywords(self.relevant_pno_paragraphs, keywords_1, keywords_2=[], keywords_type="single")
            # 添加 段落中同时含有 第二类关键词和第三类关键词 的句子
            pno_sentences.extend(get_sentences_with_keywords(self.relevant_pno_paragraphs, keywords_2, keywords_3, keywords_type="double"))
            # sentences = self.get_nonrepeated_sentences(pno_sentences) # 去除与之前指标相重复的句子
            sentences = remove_duplicate([item[1].strip() for item in pno_sentences])
            content = "\n".join(sentences) # 拼接成字符串
            if method == "关键词":
                if name == "确定碳排放核算责任的运营边界（依据范围一、范围二、范围三界定）":
                    ''' 涵盖了几个范围得几分 '''
                    range_1 = get_sentences_with_keywords(self.relevant_pno_paragraphs, ["范围一", "范畴一"], keywords_2=[], keywords_type="single")
                    range_2 = get_sentences_with_keywords(self.relevant_pno_paragraphs, ["范围二", "范畴二"], keywords_2=[], keywords_type="single")
                    range_3 = get_sentences_with_keywords(self.relevant_pno_paragraphs, ["范围三", "范畴三"], keywords_2=[], keywords_type="single")
                    score = sum([bool(lst) for lst in (range_1, range_2, range_3)])
                    return content, score

                elif name == "通过温室气体管理体系（ISO14064）认证、产品碳足迹认证（ISO 14067）、能源管理体系（ISO50001）认证、环境管理体系（ISO14001）认证的情况":
                    # 有多少句子则得分多少分，最多4分
                    score = len(sentences) if len(sentences)<=4 else 4 
                    return content, score

                else:
                    score = 1 if len(sentences) else 0 # 有句子则得分1分
                    return content, score

            elif method == "关键词+数字":
                if name == "是否设定碳达峰、碳中和年份":
                    # 如果筛选出来的文本内含有以下数字，则得分1分
                    year_list = [2025, 2030, 2045, 2050, 2060]
                    for year in year_list:
                        if str(year) in content:
                            return content, 1
                    return content, 0
                return content, ""

            elif method == "关键词+数字+字数":
                ''' 定量描述，赋值为3；详细定性，赋值为2；简单定性，赋值为1；无描述，赋值为0 '''
                number_count = self.get_number_count(content)
                if number_count:
                    score = 3
                elif len(sentences) and len(content) > 15:
                    score = 2
                elif len(sentences) and len(content) > 0:
                    score = 1
                else:
                    score = 0
                return content, score

    def get_common_words_count(self, content):
        '''
        描述：统计常用词数量
        参数：
            content: string 文本内容
        返回值：
            count: int 常用词数量
        '''
        words = jieba.lcut(content) 
        count = 0
        for word in self.common_words: #直接遍历一遍即可
            if word in words:
                count += 1
        # count_list = [content.count(word) for word in self.common_words] # 统计单词出现的次数
        # count_list = [word in content for word in self.common_words] # 统计单词是否出现
        return count
    
    def get_professional_words_count(self, content):
        '''
        描述：统计专业词数量
        参数：
            content: string 文本内容
        返回值：
            count: int 专业词数量
        '''
        words = jieba.lcut(content)
        count = 0
        for word in self.professional_words:
            if word in words:
                count += 1
        # count_list = [content.count(word) for word in self.professional_words] # 统计单词出现的次数
        # count_list = [word in content for word in self.professional_words] # 统计单词是否出现
        return count

    def get_number_count(self, content):
        """
        描述：统计数字数量
        参数：
            content: string 文本内容
        返回值：    
            count: int 数字数量
        """
        # 去除无用数字
        content = self.remove_useless_number(content)
        # 去除字符串开头的数字
        content = re.sub(r"^\d+", "", content)
        # 匹配所有数字
        numbers = re.findall(r"\d+\.?\d*", content)
        return len(numbers)   

    def remove_useless_number(self, content):
        '''
        描述：去除无用的数字
        参数：
            content: string 文本内容
        返回值：
            content: string 去除无用数字后的文本内容
        '''
        # 去除所有年份
        content = re.sub(r"(19\d{2}|20\d{2})年", "", content)
        content = re.sub(r"(\d+)月", "", content)
        content = re.sub(r"(\d+)日", "", content)
        content = re.sub(r"(\d+)号", "", content)
        # 去除所有日期 yyyy-./mm-./dd, mm-./dd-./yyyy
        content = re.sub(r"\d{4}[-|.|/]+\d+[-|.|/]+\d+|\d+[-|.|/]+\d+[-|.|/]+\d{4}", "", content)
        content = re.sub(r"([0-9]{4})-(0[1-9]|1[0-2])-(0[1-3]|1[0-2])", "", content)
        content = re.sub(r"(19\d{2}|20\d{2})\-(19\d{2}|20\d{2})", "", content)
        # 去除所有ISO开头的数字
        content = re.sub(r"ISO(\d+\.?\d*)", "", content)
        # 去除所有章节号，例如1.
        content = re.sub(r"\d\.", "", content)
        # 去除电话号码、邮编
        content = re.sub(r"\(\d{4}\)[0-9]{8}", "", content)
        content = re.sub(r"邮编：\d{7}", "", content)
        content = re.sub(r"[\w!#$%&'*+/=?^_`{|}~.-]+@[a-zA-Z\d.-]+\.[a-zA-Z]{2,}", "", content)
        return content    
    
    def text_quality(self, indicator_level_3):
        '''
        描述：
            文字信息披露质量=常用词数量/句子数量+碳中和专业术语数量+数字数量
        参数：
            indicator_level_3: dict 指标3级指标
        返回值：    
            res: float 文本质量
        '''
        if indicator_level_3["句子数量"] != 0:
            res = indicator_level_3["常用词数量"] / indicator_level_3["句子数量"] 
        else:
            res = 0
        res += indicator_level_3["专业词数量"] + indicator_level_3["数字个数"]
        return res

    def get_final_score(self, indicator_level_3):
        """
        描述：
            最终得分 = w1 * 文字信息披露质量 + w2 * 图片数量 + w3 * 表格数量
        参数：
            indicator_level_3: dict 指标3级指标
        返回值：
            score: float 最终得分
        """
        score = self.w1 * indicator_level_3["文字信息披露质量"]   
        score += self.w2 * indicator_level_3["图片数量"]      
        score += self.w3 * indicator_level_3["表格数量"]      
        return score

    def get_nonrepeated_sentences(self, pno_sentences):
        """
        描述:   
            检查sentences中的句子是否在self.sentence_count_dict中出现
            如果出现过，就不再添加到nonrepeated_sentences中
            如果没有出现过，就添加到nonrepeated_sentences中，并且在self.sentence_count_dict中添加该句子
        参数：
            sentences: list 句子列表
        返回值：        
            nonrepeated_sentences: list 不重复的句子列表
        """
        # 去重
        sentences = remove_duplicate([item[1].strip() for item in pno_sentences])
        
        nonrepeated_sentences = []
        for sentence in sentences:
            if sentence in self.sentence_count_dict.keys():
                self.sentence_count_dict[sentence] += 1
            else:
                self.sentence_count_dict[sentence] = 1
                nonrepeated_sentences.append(sentence)
        return nonrepeated_sentences
        

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

    analysis_pdf = PdfAnalyst(filepath, indicators, w1, w2, w3, excel_base_path)


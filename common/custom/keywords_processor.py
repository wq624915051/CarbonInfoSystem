import re
from itertools import product

from common.custom.pdf_processor import clean_content

def preprocess_keywords(keywords_str):
    """
    描述：
        预处理关键词
        把"气候、环保、碳、（政策风险、……、出台）"的形式处理成
        "气候、环保、碳、（政策风险）、……、（出台）"的形式
    参数：
        keywords_str: str 关键词
    返回值：
        keywords: str 关键词
    """
    keywords_str = keywords_str.replace("（", "(").replace("）", ")")
    # 判断是否有括号
    if "(" in keywords_str and ")" in keywords_str:
        if keywords_str.count("(") == 1 and keywords_str.count(")") == 1 and keywords_str.index("(") < keywords_str.index(")"):
            # 使用正则表达式匹配（）中的内容
            pattern = re.compile(r"\((.*?)\)")
            keywords_1 = pattern.findall(keywords_str)
            if len(keywords_1) != 1:
                raise Exception(f"关键词 {keywords_str} 中的括号有问题")
            
            keywords_1 = keywords_1[0] # 获取括号中的内容
            keywords_2 = "".join(keywords_str.split(f"({keywords_1})"))

            # 把关键词用逗号分隔
            keywords_1 = split_keywords_with_comma(keywords_1)
            keywords_2 = split_keywords_with_comma(keywords_2)

            # 把关键词用括号括起来
            keywords_1_list = [f"({word})" for word in keywords_1.split(",")]
            keywords_1_str = ",".join(keywords_1_list)
            res_keywords = split_keywords_with_comma(f"{keywords_2},{keywords_1_str}")
            return res_keywords
        else:
                raise Exception(f"关键词 {keywords_str} 中的括号有问题")
    # 如果左右括号只出现一个，则抛出异常
    elif ("(" in keywords_str) ^ (")" in keywords_str):
        raise Exception(f"关键词 {keywords_str} 中的括号不匹配")
    else:
        return split_keywords_with_comma(keywords_str)

def split_keywords(keywords):
    """
    描述:
        把关键词分成2种形式
        把'环境风险,环保风险,(转型),(识别)'分成2个List: 
        第一类关键词：不包含括号的关键词 ['环境风险', '环保风险']
        第二类关键词：包含括号的关键词 ['转型', '识别']
    参数：
        keywords: str 关键词
    返回值：
        keywords_1: list 第一类关键词
        keywords_2: list 第二类关键词   
    """
    
    keyword_list = keywords.split(',')

    # 第一类关键词
    keywords_1= [item for item in keyword_list if '(' not in item]
    # 第二类关键词, 并去除括号
    keywords_2 = [item.replace('(', '').replace(')', '') for item in keyword_list if '(' in item]

    # 去除空字符串
    keywords_1 = [keyword.strip() for keyword in keywords_1 if keyword != '']
    keywords_2 = [keyword.strip() for keyword in keywords_2 if keyword != '']

    return keywords_1, keywords_2

def split_keywords_with_comma(keywords):
    """
    描述：处理关键词，把关键词用逗号分隔
    参数：
        keywords: 关键词
    返回值：
        处理后的关键词
    """
    # 去除前后的空格
    keywords = keywords.strip()
    keywords = keywords.replace(' ', ',')
    keywords = keywords.replace('，', ',')
    keywords = keywords.replace('、', ',')
    keywords = keywords.replace('；', ',')
    keywords = keywords.replace(';', ',')
    keywords = keywords.replace('\n', ',')
    keywords = keywords.replace('\r', ',')
    keywords = keywords.replace('\t', ',')
    keywords = keywords.replace(',,', ',')
    return keywords

def get_paragraphs_with_keywords(document_info, keywords):
    """
    描述: 
        获取含有特定词语的段落
        这个段落实际是一整页的文本内容
    参数:
        document_info: 文档信息
        keywords: list[特定词语]
    返回值:
        result: List[(段落所在的页码, 段落文本内容)]
    """
    result = [] # 保存结果(pno, paragraph)

    for idx, page_info in enumerate(document_info):
        content = page_info["content"] # 获取每一页的文本内容
        content = clean_content(content) # 去除换行符、回车符、制表符、章节号
        for word in keywords:
            if word in content:
                result.append((page_info["pno"], content))
    result = list(set(result)) # 去重
    return result

def get_management_speech_paragraphs(document_info, pno_start, pno_end):
    """
    描述: 
        获取document_info中[pno_start: pno_end]的页面的文本内容
        pno_start, pno_end是1开始计数的左闭右闭区间
        因此需要转换为[pno_start-1: pno_end]
    参数:
        document_info: 文档信息
        pno_start: 起始页码
        pno_end: 结束页码
    返回值:
        result: List[(段落所在的页码, 段落文本内容)]
    """
    if pno_start.strip() == "" and pno_end.strip() == "":
        return [] # 没有高管致辞内容
    
    # 转换为整数
    pno_start, pno_end = int(pno_start), int(pno_end)

    if pno_start < 1:
        raise ValueError("pno_start can not less than 1")

    if pno_start > pno_end:
        raise ValueError("pno_start can not large than pno_end")
    
    if pno_end > len(document_info):
        raise ValueError("pno_end can not large than pdf page length")

    result = [] # 保存结果(pno, paragraph)
    for page_info in document_info[pno_start-1: pno_end]:
        content = page_info["content"] # 获取每一页的文本内容
        content = clean_content(content) # 去除换行符、回车符、制表符、章节号
        result.append((page_info["pno"], content))
    result = list(set(result)) # 去重
    return result

def get_paragraphs_with_keywords_precisely(document_info, keywords, sentence_number=5):
    """
    描述: 
        获取含有特定词语的段落
        这个段落实际是特定词语所在的句子的前后一共 sentence_number 句话
    参数:
        document_info: 文档信息
        keywords: list[特定词语]
    返回值:
        result: List[(段落所在的页码, 段落文本内容)]
    """
    pattern = r'[^。!！?？]*[。!！?？]' # 定义正则表达式，用于匹配句子
    result = [] # 保存结果(pno, paragraph)
    for idx_page, page_info in enumerate(document_info):
        content = page_info["content"] # 获取每一页的文本内容
        content = clean_content(content) # 去除换行符、回车符、制表符、章节号
        for word in keywords:
            # 如果当前页的内容中包含关键词，则进行下一步处理
            if word in content:
                sentences = re.findall(pattern, content) # 使用正则表达式查找所有句子
                for idx_sentences, sentence in enumerate(sentences):
                    if word in sentence:
                        """
                        如果关键词在句子中，则把句子的前后一共五句话保存下来
                        如果句子的前面不足两句话，则从上一页的末尾开始
                        如果句子的后面不足两句话，则从下一页的开头开始
                        """
                        start = idx_sentences - (sentence_number // 2)
                        end = idx_sentences + (sentence_number - sentence_number // 2)
                        previous_sentences = [] # 保存前面页的句子
                        next_sentences = [] # 保存后面页的句子
                        if start < 0:
                            previous_sentences_num = 0 - start # 上一页需要的句子数
                            if idx_page > 0:
                                previous_page_info = document_info[idx_page - 1] # 上一页的信息
                                previous_content = previous_page_info["content"] # 上一页的文本内容
                                previous_content = clean_content(previous_content)
                                previous_sentences = re.findall(pattern, previous_content) # 上一页的所有句子
                                previous_sentences = previous_sentences[-previous_sentences_num:] # 从上一页的末尾n个开始
                            start = 0 # 从当前页的第一句开始
                        if end > len(sentences):
                            next_sentences_num = end - len(sentences) # 下一页需要的句子数
                            if idx_page < len(document_info) - 1:
                                next_page_info = document_info[idx_page + 1] # 下一页的信息
                                next_content = next_page_info["content"] # 下一页的文本内容
                                next_content = clean_content(next_content)
                                next_sentences = re.findall(pattern, next_content) # 下一页的所有句子
                                next_sentences = next_sentences[:next_sentences_num] # 从下一页的开头n个开始
                            end = len(sentences) # 到当前页的最后一句结束
                        current_sentences = sentences[start: end] # 保存当前页句子
                        paragraph = " ".join(previous_sentences + current_sentences + next_sentences) # 拼接成段落
                        result.append((page_info["pno"], paragraph)) # 保存结果

    result = list(set(result)) # 去重
    return result

def get_sentences_with_keywords(pno_paragraphs, keywords_1, keywords_2):
    """
    描述: 在筛选出来的段落中找到关键词所在的句（以句号划分）
    参数:
        pno_paragraphs: List[(pno, paragraph)]
        keywords: List[关键词]
    返回值:
        sentences: List[(句子所在的页码, 句子)]
    """
    # 如果只有一个关键词，则把第二个关键词设置为空, 防止product的结果为空
    keywords_1 = [""]  if len(keywords_1) == 0 else keywords_1
    keywords_2 = [""]  if len(keywords_2) == 0 else keywords_2
    
    pattern = r'[^。!！?？]*[。!！?？]' # 定义正则表达式，用于匹配句子
    result_sentences = [] # 保存结果
    for pno, paragraph in pno_paragraphs:
        # 使用正则表达式查找所有句子的位置
        sentences = re.findall(pattern, paragraph)
        for sentence in sentences:
            for (word_1, word_2) in list(product(keywords_1, keywords_2)):
                if word_1 in sentence and word_2 in sentence:
                    sentence = sentence.strip() # 去除首尾空格
                    result_sentences.append((pno, sentence))

    result_sentences = list(set(result_sentences)) # 去重
    return result_sentences

def get_table_image_count(document_info, keywords_1, keywords_2, keywords_3):
    """
    描述：
        获取表格和图片数量
    参数：
        document_info: dict 文档信息
        keywords_1: list 关键词
        keywords_2: list 关键词
        keywords_3: list 关键词
    返回值：
        table_count: int 表格数量
        image_count: int 图片数量
    """

    # 如果只有一个关键词，则把第二个关键词设置为空, 防止product的结果为空
    keywords_1 = [""]  if len(keywords_1) == 0 else keywords_1
    keywords_2 = [""]  if len(keywords_2) == 0 else keywords_2
    keywords_3 = [""]  if len(keywords_3) == 0 else keywords_3

    table_count = 0
    image_count = 0
    founded_list  = [] # 用于存储已经匹配到的句子
    for idx_page, page_info in enumerate(document_info):
        content = page_info["content"] # 获取每一页的文本内容
        content = clean_content(content) # 去除换行符、回车符、制表符、章节号
        for (word_1, word_2, word_3) in list(product(keywords_1, keywords_2, keywords_3)):
            # 如果当前页的内容中包含关键词1和关键词2，则进行下一步处理
            if word_1 in content and word_2 in content and word_3 in content:
                structure = page_info["new_structure"] # 获取每一页的结构化信息
                for idx_item, item in enumerate(structure):
                    # 如果当前句子的内容中包含关键词1和关键词2，且当前句子没有被匹配过，则进行下一步处理
                    if word_1 in item["content"]  and word_2 in content and (idx_page, idx_item) not in founded_list:
                        founded_list.append((idx_page, idx_item))
                        table_count += item["table_count"]
                        image_count += item["image_count"]
    return table_count, image_count
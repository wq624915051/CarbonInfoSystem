import re
from common.custom.pdf_processor import clean_content

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

def get_sentences_with_keywords(pno_paragraphs, keywords):
    """
    描述: 在筛选出来的段落中找到关键词所在的句（以句号划分）
    参数:
        pno_paragraphs: List[(pno, paragraph)]
        keywords: List[关键词]
    返回值:
        sentences: List[(句子所在的页码, 句子)]
    """
    pattern = r'[^。!！?？]*[。!！?？]' # 定义正则表达式，用于匹配句子
    result_sentences = [] # 保存结果
    for pno, paragraph in pno_paragraphs:
        # 使用正则表达式查找所有句子的位置
        sentences = re.findall(pattern, paragraph)
        for sentence in sentences:
            for keyword in keywords:
                if keyword in sentence:
                    sentence = sentence.strip() # 去除首尾空格
                    result_sentences.append((pno, sentence))

    result_sentences = list(set(result_sentences)) # 去重
    return result_sentences
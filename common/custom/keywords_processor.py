import re

def split_keywords_with_comma(keywords):
    """
    描述：处理关键词，把关键词用逗号分隔
    参数：
        keywords: 关键词
    返回值：
        处理后的关键词
    """
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
    描述: 获取含有特定词语的段落
    参数:
        document_info: 文档信息
        word: list[特定词语]
    返回值:
        result: List[(段落所在的页码, 段落文本内容)]
    """
    result = [] # 保存结果(pno, paragraph)
    for page_info in document_info:
        content = page_info["content"] # 获取每一页的文本内容
        # 去除换行符、回车符、制表符
        content = content.replace('\n', '').replace('\r', '').replace('\t', '')
        for word in keywords:
            if word in content:
                result.append((page_info["pno"], content))
    result = list(set(result)) # 去重
    return result

# 在筛选出来的段落中找到关键词所在的句（以句号划分）
def get_sentences_with_keywords(pno_paragraphs, keywords):
    """
    描述: 在筛选出来的段落中找到关键词所在的句（以句号划分）
    参数:
        pno_paragraphs: List[(pno, paragraph)]
        keywords: List[关键词]
    返回值:
        sentences: List[(句子所在的页码, 句子)]
    """
    pattern = r'[^。!！?？]*[。!！?？]' # 定义正则表达式，用于匹配句子的位置
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
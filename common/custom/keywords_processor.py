

def process_keywords(keywords):
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
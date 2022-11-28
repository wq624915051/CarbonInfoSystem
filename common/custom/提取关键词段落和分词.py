'''
同学你好！能和你们商量个事情嘛，
就是里面不是第一步是按碳、绿色、环保先筛选出相关段落嘛，
你们能不能筛出来之后把这个所有段（所有报告）存下来然后做个分词处理
（就是把段/句分成词，类似jieba的分词处理）
然后把分词能不能给我们一份，
我们想拿这个对一下我们的关键词
'''

res = [{
    "name": "平安银行：2021年社会责任报告.PDF",
    "碳_段落": [
        "这是一个段落",
        "这是另一个段落"
    ],
    "碳_分词": [
        "这是一个分词",
        "这是另一个分词"
    ],
    "绿色_段落": [],
    "绿色_分词": [],
    "环保_段落": [],
    "环保_分词": [],
    "碳_绿色_环保_分词": []
}]



import os
import sys
import json
import jieba
if True:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from common.custom.myPDF import MyPDF


# 获取含有特定词语的段落
def get_paragraphs_with_words(documnet_info, word):
    paragraphs = []
    for page_info in documnet_info:
        content = page_info["content"]
        if word in content:
            paragraphs.append(content)
    return paragraphs

# 对段落进行分词，并去重
def get_words_from_paragraphs(paragraphs):
    words = []
    for paragraph in paragraphs:
        words += jieba.lcut(paragraph)
    words = list(set(words))
    return words

if __name__ == '__main__':
    pdf_files_dir = "D:\ALL\项目\碳信息披露\测试pdf\\"
    media_root = "D:\ALL\项目\碳信息披露\CarbonInfoSystem\media"

    for file in os.listdir(pdf_files_dir)[1:]:
        file_path = os.path.join(pdf_files_dir, file)

        print(f"{'='*10}\n{file}")
        my_pdf = MyPDF(file_path, media_root)
        documnet_info = my_pdf.documnet_info
        
        # 获取含有特定词语的段落
        paragraphs_carbon = get_paragraphs_with_words(documnet_info, "碳")
        paragraphs_green = get_paragraphs_with_words(documnet_info, "绿色")
        paragraphs_envir = get_paragraphs_with_words(documnet_info, "环保")

        # 对段落进行分词，并去重
        words_carbon = get_words_from_paragraphs(paragraphs_carbon)
        words_green = get_words_from_paragraphs(paragraphs_green)
        words_envir = get_words_from_paragraphs(paragraphs_envir)

        # 合并所有分词
        words_all = words_carbon + words_green + words_envir
        words_all = list(set(words_all))

        company = file.replace(".PDF", "")
        res = {
                "name": company,
                "碳_段落": paragraphs_carbon,
                "碳_分词": words_carbon,
                "绿色_段落": paragraphs_green,
                "绿色_分词": words_green,
                "环保_段落": paragraphs_envir,
                "环保_分词": words_envir,
                "碳_绿色_环保_分词": words_all
                }

        # 保存结果
        filepath = os.path.join("common\custom", f"test.{company}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=4)
    
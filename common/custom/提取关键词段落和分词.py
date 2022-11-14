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
from common.custom.myPDF import MyPDF

pdf_files_dir = "D:\ALL\项目\碳信息披露\测试pdf\\"
media_root = "D:\ALL\项目\碳信息披露\CarbonInfoSystem\media"


for file in os.listdir(pdf_files_dir):
    file_path = os.path.join(pdf_files_dir, file)
    my_pdf = MyPDF(file_path, media_root)
    documnet_info = my_pdf.documnet_info

    break

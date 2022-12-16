# {
#     "000001":{
#         "公司代码":"000001",
#         "公司简称":"平安银行",
#         "年份记录":[2020,2021],
#         "2020":{"股权融资优势":3,"ESG评级":1},
#         "2021":{"股权融资优势":2,"ESG评级":2}
#     }
# }
import xlrd

excel_path = 'D:\作业\研究生\研1\CarbonInfoSystem\data\所需表.xls'
excel_data = xlrd.open_workbook(filename=excel_path)
Professional_terms = excel_data

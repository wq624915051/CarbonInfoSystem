import os
import logging
import datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from common.base.base_respons import retJson
from common.custom.logger import my_logger

@csrf_exempt
def upload_pdfs(request):
    """
    描述：上传pdf文件, 重命名后保存到本地, 并返回文件路径
    方法：POST
    参数：
        files: pdf文件列表
    返回值:
        filepaths: list[string] pdf文件路径列表
    """
    if request.method == 'GET':
        return retJson(code=0, msg="GET请求")
    elif request.method == 'POST':
        try:
            files = request.FILES.getlist('files')
            if not files:
                return retJson(code=0, msg="请上传pdf文件")
            
            # 检查文件名是否符合 "股票代码_公司名称_年份.pdf"
            for file in files:
                file_name = file.name
                if not file_name.lower().endswith('.pdf'):
                    return retJson(code=0, msg="文件类型错误, 只能上传pdf文件")
                if len(file_name.split('_')) != 3:
                    return retJson(code=0, msg="文件命名格式错误, 请按照'股票代码_公司名称_年份.pdf'命名")

            # 创建以now命名的文件夹用于保存pdf
            now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            pdf_dir = os.path.join(settings.MEDIA_ROOT, "uploads", now)
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)

            filepaths = []
            for file in files:
                file_name = file.name
                file_path = os.path.join(pdf_dir, file_name)
                filepaths.append(file_path)
                with open(file_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
            return retJson(code=1, msg="success", data={"filepaths": filepaths})
        except Exception as e:
            my_logger.error(f"{str(logging.exception(e))}")
            return retJson(code=0, msg=str(e))
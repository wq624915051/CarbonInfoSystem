'''
MyPDF类
用于提取PDF文件中的文本、表格、图片等信息
'''
import os
import fitz

from common.custom.ocr import MyOCR


class PdfProcessor():
    '''
    描述：
        PdfProcessor类，利用PaddleOCR用于提取PDF文件中的文本、图像、表格
    参数：
        filepath: PDF文件路径
        media_root: 保存图片的路径
    成员变量：
        document_info: list(page_info)
        page_info: {
            "pno": 页码,
            "type": 页面类型,
            "content": 页面内容
        }
    '''
    def __init__(self, filepath, media_root) -> None:
        self.filepath = filepath # PDF文件路径
        self.documnet = fitz.open(filepath) # PyMuPdf打开PDF文件
        self.media_root = media_root # 保存图片的路径
        self.pdf_ocr = MyOCR()

        self.document_info = [] # PDF每一页的信息
        for pno, page in enumerate(self.documnet):
            page_info = {"pno": pno} # 页面信息

            # 把页面保存为图片
            img_save_path = os.path.join(self.media_root, 'temp_images', f"images_{pno}.png")
            page.get_pixmap().save(img_save_path) 

            # 利用paddleocr进行版面分析和文字提取
            structure = self.pdf_ocr.get_structure(img_save_path) # 速度比较慢
            page_info["content"] = self.get_content(structure) # 页面内容
            page_info["image_count"] = self.get_image_count(structure) # 图片数量
            page_info["table_count"] = self.get_table_count(structure) # 表格数量

            self.document_info.append(page_info) # 添加到文档信息中
        
        self.delete_images(os.path.join(self.media_root, 'temp_images')) # 删除临时图片

    def get_content(self, structure):
        """
        描述：获取文本内容
        参数：
            structure: 版面分析结果 List[Dict]
        返回值：
            content: 文本内容
        """
        content = ""
        for item in structure:
            if item["type"] == "text":
                for line in item["res"]:
                    content += line["text"]
        return content

    def get_image_count(self, structure):
        """
        描述：获取图片数量
        参数：
            structure: 版面分析结果 List[Dict]
        返回值：
            image_count: 图片数量
        """
        image_count = 0
        for item in structure:
            if item["type"] == "figure":
                image_count += 1
        return image_count
    
    def get_table_count(self, structure):
        """
        描述：获取表格数量
        参数：
            structure: 版面分析结果 List[Dict]
        返回值：
            table_count: 表格数量
        """
        table_count = 0
        for item in structure:
            if item["type"] == "table":
                table_count += 1
        return table_count

    def delete_images(self, del_path):
        '''
        描述：
            批量删除图片
        参数：
            del_path: 删除路径
        '''
        for file in os.listdir(del_path):
            if file == ".gitkeep":
                continue
            else:
                os.remove(os.path.join(del_path, file))
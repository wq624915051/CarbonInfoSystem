'''
MyPDF类
用于提取PDF文件中的文本
'''
import os
import json
import time
import fitz
import pdfplumber
import numpy as np 
from PIL import Image
from django.conf import settings

from common.custom.ocr import MyOCR

class MyPDF():
    '''
    描述：MyPDF类，用于提取PDF文件中的文本、图像、表格
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
        self.filepath = filepath
        self.documnet = fitz.open(filepath)
        self.pdfplumber = pdfplumber.open(filepath)
        self.media_root = media_root # 保存图片的路径
        self.pdf_ocr = MyOCR()

        self.document_info = [] # PDF每一页的信息
        for pno, page in enumerate(self.documnet):
            page_info = page.get_text("dict") # 该页的信息
            page_info["pno"] = pno # 页码
            page_type = self.judge_page_type(page_info) # 页面类型
            page_info["type"] = page_type
            if page_type == "text":
                # 获取页面的文本内容
                content = self.get_textpage_content_by_pymupdf(page_info)
                page_info["content"] = content

                # 通过pdfplumber获取图片
                pdfplumber_page = self.pdfplumber.pages[pno]
                images = pdfplumber_page.images # 获取图片
                page_info["image_count"] = len(images) # 图片数量
                
                # 通过pdfplumber获取表格
                tables = pdfplumber_page.extract_tables() # 获取表格
                page_info["table_count"] = len(tables) # 表格数量
            elif page_type == "image":
                img_list = page.get_images()  # 提取该页中的所有img
                image = img_list[0]  # 只取第一张图片

                # 保存图片
                img_save_path = os.path.join(self.media_root, 'temp_images', f"images_{pno}.png")
                self.save_image_page(image, img_save_path)  

                # page_info["content"] = self.get_image_content_by_Tesseract(img_save_path) 

                # 利用paddleocr进行版面分析和文字提取
                structure = self.pdf_ocr.get_structure(img_save_path) # 速度比较慢
                page_info["content"] = self.pdf_ocr.get_ocr_result(structure) # 页面内容
                page_info["image_count"] = self.pdf_ocr.get_image_count(structure) # 图片数量
                page_info["table_count"] = self.pdf_ocr.get_table_count(structure) # 表格数量

                # 方式一：逐个删除图片
                # self.delete_image(img_save_path)
            
            # 方式二：批量删除图片
            self.delete_images(os.path.join(self.media_root, 'temp_images'))  

            self.document_info.append(page_info)
    
    def judge_page_type(self, page_info: dict):
        '''
        描述：
            判断pdf页面类型为可解析的文本类型还是图片类型
            如果一个page里面只有图片块，没有文本块，那么就是图片类型
            否则是文本类型
        参数：
            page_info: dict 页面信息page_info = page.get_text("dict")
        返回值：
            text: 可解析的文本类型
            image: 图片类型
        '''
        blocks = page_info["blocks"]  # PDF页面的块
        imgblocks = [b for b in blocks if b["type"] == 1]  # 图片块
        textblocks = [b for b in blocks if b["type"] == 0]  # 文本块
        imgblocks_len = len(imgblocks)  # 图片块的数量
        textblocks_len = len(textblocks)  # 文本块的数量
        if imgblocks_len == 1 and textblocks_len == 0:
            return "image"  # 只有图片块，没有文本块
        else:
            return "text"
    
    def get_textpage_content_by_pdfplumber_directly(self, page):
        """
        描述： 
            通过pdfplumber直接获取页面的文本内容
        参数：
            page: 页面
        返回值：    
            content: 页面的文本内容
        """
        return page.extract_text()

    def get_textpage_content_by_pymupdf_directly(self, page):
        """
        描述：
            通过pymupdf直接获取页面的文本内容
        参数：
            page: 页面
        返回值：    
            content: 页面的文本内容
        """
        return page.get_text("text")

    def get_textpage_content_by_pymupdf(self, page_info):
        '''
        描述: 
            获取页面的文本内容
        参数：
            page_info: 页面信息
        返回值：
            content: 页面的文本内容
        '''
        content = ""
        blocks = page_info["blocks"]  # PDF页面的块
        for block in blocks:
            # 图片块，跳过
            if block["type"] == 1:
                continue

            lines = block["lines"]
            for line in lines:
                spans = line["spans"]
                for span in spans:
                    content += span["text"]
            content += "\n"
        return content

    def save_image_page(self, image, save_path):
        '''
        描述：
            保存图片类型的页面
        参数：
            image: 图片
            save_path: 保存路径
        '''
        # image转pixmap
        pix = fitz.Pixmap(self.documnet, image[0])

        # 如果差值大于等于4，需要转化后才能保存为png
        if pix.n - pix.alpha >= 4:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        pix.save(save_path)  # 存储图片
        pix = None  # 释放Pixmap资源

    def delete_image(self, del_path):
        '''
        描述：
            逐个删除图片
        参数：
            del_path: 删除路径
        '''
        os.remove(del_path)    
    
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

    def get_image_content_by_Tesseract(self, img_path):
        '''
        描述：使用 Tesseract 识别, 提取文字
        参数：
            img_path: 图片路径
        返回值：
            content: 识别出的文字
        '''
        img = Image.open(img_path)
        img_gray = img.convert('L')  # 灰度化
        # 二值化 (二值化后效果不好, 仍使用灰度图 img_gray)
        avg_gray = np.average(np.array(img_gray)) # 取所有像素点灰度的平均值
        img_binary = img_gray.point(lambda x: 0 if x < avg_gray else 255)

        # 使用 Tesseract 识别
        content = ""
        return content

    def get_pdf_content(self):
        '''
        描述：
            获取pdf文件的文本内容
        返回值：
            content: pdf文件的文本内容
        '''
        content_list = [page["content"] for page in self.document_info]
        content = "\n".join(content_list)
        return content
        
if __name__ =="__main__":
    filepath = "D:\ALL\项目\碳信息披露\测试pdf\\600018-2021-可持续.PDF"
    media_root = "D:\ALL\项目\碳信息披露\CarbonInfoSystem\media"
    pdf = MyPDF(filepath, media_root=media_root)

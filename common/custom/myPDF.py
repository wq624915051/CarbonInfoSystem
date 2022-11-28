'''
MyPDF类
用于提取PDF文件中的文本
'''
import os
import json
import time
import fitz
import pytesseract
import  numpy as np 
from PIL import Image
from django.conf import settings


class MyPDF():
    def __init__(self, filepath, media_root) -> None:
        self.filepath = filepath
        self.documnet = fitz.open(filepath)
        self.media_root = media_root # 保存图片的路径

        self.documnet_info = []
        for pno, page in enumerate(self.documnet):
            page_info = page.get_text("dict")
            page_info["pno"] = pno
            page_type = self.judge_page_type(page_info)
            page_info["type"] = page_type
            if page_type == "text":
                # 整合文本
                content = self.get_textpage_content(page_info)
                page_info["content"] = content
            elif page_type == "image":
                img_list = page.get_images()  # 提取该页中的所有img
                image = img_list[0]  # 只取第一张图片

                # 保存图片
                img_save_path = os.path.join(self.media_root, 'temp_images', f"images_{pno}.png")
                self.save_image_page(image, img_save_path)  

                # 获取图片中的文本
                content =  self.get_image_content(img_save_path) 
                page_info["content"] = content
                
                # 删除图片
                self.delete_image(img_save_path)  

            self.documnet_info.append(page_info)
    
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
    
    def get_textpage_content(self, page_info):
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
            删除图片
        参数：
            del_path: 删除路径
        '''
        os.remove(del_path)

    def get_image_content(self, img_save_path):
        '''
        描述：使用 Tesseract 识别, 提取文字
        参数：
            img_save_path: 图片路径
        返回值：
            content: 识别出的文字
        '''
        img = Image.open(img_save_path)
        img_gray = img.convert('L')  # 灰度化
        # 二值化 (二值化后效果不好, 仍使用灰度图 img_gray)
        avg_gray = np.average(np.array(img_gray)) # 取所有像素点灰度的平均值
        img_binary = img_gray.point(lambda x: 0 if x < avg_gray else 255)

        # 使用 Tesseract 识别
        content = pytesseract.image_to_string(img_gray, lang='chi_sim')
        return content

    def get_pdf_content(self):
        '''
        描述：
            获取pdf文件的文本内容
        返回值：
            content: pdf文件的文本内容
        '''
        content_list = [page["content"] for page in self.documnet_info]
        content = "\n".join(content_list)
        return content

if __name__ =="__main__":
    filepath = "D:\ALL\项目\碳信息披露\测试pdf\\600018-2021-可持续.PDF"
    media_root = "D:\ALL\项目\碳信息披露\CarbonInfoSystem\media"
    pdf = MyPDF(filepath, media_root=media_root)

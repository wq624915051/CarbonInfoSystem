'''
PdfProcessor类
用于提取PDF文件中的文本、表格、图片等信息
'''
import os
import re
import fitz
import datetime
import pdfplumber
import numpy as np
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
        self.pdfplumber = pdfplumber.open(filepath) # pdfplumber打开PDF文件
        self.media_root = media_root # 保存图片的路径
        self.pdf_ocr = MyOCR()
        self.zoom_x = 2.0 # 缩放比例
        self.zoom_y = 2.0 # 缩放比例
        self.mat = fitz.Matrix(self.zoom_x, self.zoom_y) # 缩放矩阵
        self.y_threshold = 300 # y轴阈值

        self.document_info = [] # PDF每一页的信息
        self.img_save_paths = [] # 保存图片的路径
        for pno, page in enumerate(self.documnet):
            if page.width < page.height:
                page_info = self.single_page(pno, page) # 单页
            else:
                page_info = self.double_page(pno, page) # 双页

            self.document_info.append(page_info) # 添加到文档信息中
        
        self.delete_images(self.img_save_paths) # 删除临时图片
        self.pdfplumber.close() # 关闭pdfplumber

    def single_page(self, pno, page):
        '''
        描述：
            单页PDF处理
        参数:
            pno: 页码
            page: PyMuPdf的Page对象
        返回值：
            page_info: 页面信息
        '''
        # 保存PDF页面图片
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        img_save_path = os.path.join(self.media_root, 'temp_images', f"images_{pno}_{now}.png")
        page.get_pixmap(matrix=self.mat).save(img_save_path)
        self.img_save_paths.append(img_save_path)

        # 利用 PPStructure 和 paddleocr 进行版面分析和文字提取
        structure = self.pdf_ocr.get_structure(img_save_path) # 速度比较慢

        error_axis_x = 50 if True else 5 # TODO 单栏双栏判断

        page_info = {"pno": pno} # 页面信息
        page_info["content"] = self.get_content_by_PaddleOCR(structure, img_save_path, error_axis_x) # 页面内容 by PaddleOCR [速度慢]
        page_info["image_count"] = self.get_image_count(structure) # 图片数量
        page_info["table_count"] = self.get_table_count(structure) # 表格数量
        page_info["new_structure"] = self.get_image_table_count(structure) # 每一块下方的图片数量和表格数量

        return page_info

    def double_page(self, pno, page):
        '''
        描述：
            双页PDF处理
        参数:
            pno: 页码
            page: PyMuPdf的Page对象
        返回值：
            page_info: 页面信息
        '''
        # PDF页面图片存储路径
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        img_left_save_path = os.path.join(self.media_root, 'temp_images', f"images_left_{pno}_{now}.png")
        img_right_save_path = os.path.join(self.media_root, 'temp_images', f"images_right_{pno}_{now}.png")
        self.img_save_paths.append(img_left_save_path)
        self.img_save_paths.append(img_right_save_path)

        rect = page.rect # 页面矩形
        middle_top_point = fitz.Point((rect.br[0] + rect.tl[0]) * 0.5, rect.tl[1]) # 中线上点
        middle_bottom_point = fitz.Point((rect.br[0] + rect.tl[0]) * 0.5, rect.br[1]) # 中线下点
        clip_left = fitz.Rect(rect.tl, middle_bottom_point) # 左边矩形
        clip_right = fitz.Rect(middle_top_point, rect.br) # 右边矩形
        
        # 保存图片
        page.get_pixmap(matrix=self.mat, clip=clip_left).save(img_left_save_path)
        page.get_pixmap(matrix=self.mat, clip=clip_right).save(img_right_save_path) 

        # 利用 PPStructure 和 paddleocr 进行版面分析和文字提取
        structure_left = self.pdf_ocr.get_structure(img_left_save_path)
        structure_right = self.pdf_ocr.get_structure(img_right_save_path)

        error_axis_x_left = 50 if True else 5 # TODO 单栏双栏判断
        error_axis_x_right = 50 if True else 5 # TODO 单栏双栏判断

        content = self.get_content_by_PaddleOCR(structure_left, img_left_save_path, error_axis_x_left)
        content += self.get_content_by_PaddleOCR(structure_right, img_right_save_path, error_axis_x_right)
        image_count = self.get_image_count(structure_left) + self.get_image_count(structure_right)
        table_count = self.get_table_count(structure_left) + self.get_table_count(structure_right)
        new_structure = self.get_image_table_count(structure_left) + self.get_image_table_count(structure_right)

        page_info = {
            "pno": pno,
            "content": content,
            "image_count": image_count,
            "table_count": table_count,
            "new_structure": new_structure
        } 
        return page_info

    def get_content_by_PPStructure(self, structure):
        """
        描述：
            使用 PPStructure 获取文本内容
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
        content = clean_content(content)
        return content

    def get_content_by_PaddleOCR(self, structure, img_save_path, error_axis_x=50):
        """
        描述：
            使用 PaddleOCR + PPStructure 获取文本内容
            精度高，速度慢
        参数：
            structure: 版面分析结果 List[Dict]
        返回值：
            content: 文本内容
        """
        # 获取paddle ocr的识别结果
        ocr_result = self.pdf_ocr.get_ocr_result(img_save_path)

        # 获取文字部分的Bbox
        text_bboxes = self.get_text_bboxes(structure)

        content = ""
        # 遍历已排序完成的structure的text_bboxes
        for text_bbox in text_bboxes:
            block_res = [] # 存放块中的内容
            for line in ocr_result:
                # 提取line的bbox [左上x, 左上y, 右下x, 右下y]
                bbox = [line[0][0][0], line[0][0][1], line[0][2][0], line[0][2][1]]
                # 判断line的bbox是否在text_bbox中
                flag = self.is_in_bboxes(bbox, [text_bbox], error_axis_x=error_axis_x, error_axis_y=2)
                if flag:
                    block_res.append(line)
            
            # 对块内的内容按Y轴排序
            block_res = sorted(block_res, key=lambda x: ((x[0][0][1] + x[0][2][1])*0.5))
            content += "".join([line[1][0] for line in block_res])
    
        content = clean_content(content)
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

    def get_image_table_count(self, structure):
        '''
        描述：
            获取每一个文字块下方的图片数量和表格数量
        参数：  
            structure: 版面分析结果 List[Dict]
        返回值：    
            new_structure: 新的版面结构 List[Dict]
            Dict结构： {
                "content": 文字块内容,
                "image_count": 文字块下方的图片数量,
                "table_count": 文字块下方的表格数量
            }
        '''
        # 新的版面结构，包含每一块的类型、y坐标、[内容]
        new_structure = []
        for item in structure:
            axis_y_top  = item["bbox"][1]
            axis_y_bottom = item["bbox"][3]
            axis_y_mean = np.mean([axis_y_top, axis_y_bottom])
            tmp = {"type": item["type"], "axis_y_top": axis_y_top,
                    "axis_y_bottom": axis_y_bottom, "axis_y_mean": axis_y_mean}
            if item["type"] == "text":
                content = "".join([line["text"] for line in item["res"]])
                tmp["content"] = content
                new_structure.append(tmp)
            elif item["type"]  in ["table", "figure"]:
                new_structure.append(tmp)
        
        # 遍历每一块，获取阈值内的图片数量和表格数量
        y_threshold = self.y_threshold # y坐标的阈值
        for i, item in enumerate(new_structure):
            if item["type"] == "text":
                item["image_count"] = 0
                item["table_count"] = 0
                for j in range(i+1, len(new_structure)):
                    if new_structure[j]["axis_y_top"] - item["axis_y_bottom"] < y_threshold:
                        # 如果下一块的顶部y坐标与当前块的底部y坐标的差小于阈值，则计数
                        if new_structure[j]["type"] == "figure":
                            item["image_count"] += 1
                        elif new_structure[j]["type"] == "table":
                            item["table_count"] += 1
                    else:
                        # 如果下一块的顶部y坐标与当前块的底部y坐标的差大于阈值，则跳出循环
                        break
        
        # 保留text类型的 content、image_count、table_count字段
        res_structure = [{k: item[k] for k in ["content", "image_count", "table_count"]} for item in new_structure if item["type"] == "text"]

        return res_structure

    def get_text_bboxes(self, structure):
        """
        描述：获取文字的Bbox
        参数：
            content: 文字提取结果 List
        返回值：    
            bboxs: 文字的Bbox List
            Bbox: [左上角x，左上角y，右下角x，右下角y]
        """
        bboxs = []
        for line in structure:
            if line["type"] == "text":
                bboxs.append(line["bbox"])
        return bboxs

    def is_in_bboxes(self, bbox, bboxes, error_axis_x=50, error_axis_y=2):
        """
        描述：判断bbox是否在bboxes中
        参数：
            bbox: Bbox [左上角x，左上角y，右下角x，右下角y]
            bboxes: Bbox List
            error_axis_x: x轴允许误差
            error_axis_y: y轴允许误差
        返回值：
            True: 在bboxes中
            False: 不在bboxes中
        """
        # 添加允许误差
        bbox = [bbox[0]+error_axis_x, bbox[1]+error_axis_y, bbox[2]-error_axis_x, bbox[3]-error_axis_y]
        for box in bboxes:
            if bbox[0] >= box[0] - error_axis_x and bbox[1] >= box[1] - error_axis_y and bbox[2] <= box[2] + error_axis_x and bbox[3] <= box[3] + error_axis_y:
                return True
        return False

    def delete_images(self, filepaths):
        '''
        描述：
            批量删除图片
        参数：
            filepaths: List 文件路径
        '''
        for file in filepaths:
            os.remove(file)

def clean_content(content):
    """
    描述：
        从文本中去除换行符、回车符、制表符、章节号
    参数：
        content: 文本内容
    返回值：    
        content: 处理后的文本内容
    """
    # 去除换行符、回车符、制表符
    content = content.replace('\n', '').replace('\r', '')
    content = content.replace('\t', '').replace(' ', '')
    # 去除所有章节号，例如4.3.1
    content = re.sub(r"\d+\.?\d*\.\d+\.?\d*\.\d+\.?\d*","", content)
    return content
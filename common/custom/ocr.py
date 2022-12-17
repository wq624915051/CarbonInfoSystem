import os
import cv2
from paddleocr import PPStructure
from paddleocr import draw_structure_result
from paddleocr import save_structure_res

class MyOCR():
    """
    描述: 利用paddleocr进行版面分析和文字提取
    """
    def __init__(self, table=False, ocr=True, show_log=False, image_orientation=False) -> None:
        self.pdf_engine = PPStructure(table=table, ocr=ocr, show_log=show_log, image_orientation=image_orientation)
    
    def get_structure(self, img_path):
        """
        描述：进行版面分析和文字提取
        参数：
            img_path: 图片路径
        返回值：
            structure: 版面分析结果 List[Dict]
        """
        img = cv2.imread(img_path)
        structure = self.pdf_engine(img)
        return structure
    
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
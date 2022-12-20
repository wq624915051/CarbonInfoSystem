import os
import sys
import cv2
from paddleocr import PPStructure
from paddleocr import draw_structure_result
from paddleocr import save_structure_res

from common.custom.utils import cv2imread
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
            dict 里各个字段说明如下：
                type: 文本类型，包括 text, table, figure, title, footer
                bbox: 文本框坐标，[左上角x，左上角y，右下角x，右下角y]
                res: 文本内容，type为text时，res为List[Dict]，包含每行的文本内容，每行的文本内容为Dict，包含text和confidence字段，分别表示文本内容和置信度
        
        """
        img = cv2imread(img_path)
        structure = self.pdf_engine(img)
        # 根据structure的字典内的bbox的左上角y坐标，对structure进行排序
        structure.sort(key=lambda x: x["bbox"][1])
        return structure
import os
import sys
import cv2
from itertools import chain
from paddleocr import PPStructure
from paddleocr import PaddleOCR
from paddleocr import draw_structure_result
from paddleocr import save_structure_res

from common.custom.utils import cv2imread
class MyOCR():
    """
    描述: 利用paddleocr进行版面分析和文字提取
    """
    def __init__(self, table=False, ocr=True, show_log=False, image_orientation=False, use_angle_cls=False, use_gpu=False) -> None:
        self.pdf_engine = PPStructure(table=table, ocr=ocr, show_log=show_log, image_orientation=image_orientation, use_gpu=use_gpu)
        self.ocr_engine = PaddleOCR(use_angle_cls=use_angle_cls, lang="ch", use_gpu=use_gpu)
    
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
        
        # 计算每个item的中心点坐标
        for item in structure:
            middle_point = ((item["bbox"][0] + item["bbox"][2])*0.5, (item["bbox"][1] + item["bbox"][3])*0.5)
            item["middle_point"] = middle_point

        """
        根据每个item的中心点坐标，对structure进行排序
        先按y轴升序，y轴相同按x轴升序
        x轴、y轴坐标都除以100，根据百位数字进行排序
        """
        structure = sorted(structure, key=lambda x: ((x["middle_point"][1] // 100), (x["middle_point"][0] // 100)))
        return structure
    
    def get_ocr_result(self, img_path):
        '''
        描述：获取paddle ocr的识别结果
        参数：
            img_path: 图片路径
        返回值：    
            result: 文字提取结果 List[item]
            item: [[[左上x, 左上y], [右上x, 右上y], [右下x, 右下y], [左下x, 左下y]], (文本, 置信度)]
        '''
        results = self.ocr_engine.ocr(img_path, cls=False)
        result = list(chain(*results))

        return result
import cv2
import numpy as np

def cv2imread(img_path):
    # 读取图像，解决imread不能读取中文路径的问题  
    return cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)


def remove_duplicate(list_1):
    # 去重后还是原list顺序
    return sorted(set(list_1), key=list_1.index)

def check_pno(pno_start, pno_end):
    """
    判断页码是否合法
    """
    # 判断是否为数字
    if not pno_start.isdigit() or not pno_end.isdigit():
        raise ValueError("pno_start and pno_end must be digit")

    # 转换为整数
    pno_start, pno_end = int(pno_start), int(pno_end)

    if pno_start < 1:
        raise ValueError("pno_start can not less than 1")

    if pno_start > pno_end:
        raise ValueError("pno_start can not large than pno_end")

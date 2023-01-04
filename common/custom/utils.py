import cv2
import numpy as np

def cv2imread(img_path):
    # 读取图像，解决imread不能读取中文路径的问题  
    return cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)


def remove_duplicate(list_1):
    # 去重后还是原list顺序
    return sorted(set(list_1), key=list_1.index)

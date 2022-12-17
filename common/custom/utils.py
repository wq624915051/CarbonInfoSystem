import cv2
import numpy as np

def cv2imread(img_path):
    # 读取图像，解决imread不能读取中文路径的问题  
    return cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)
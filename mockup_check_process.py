#-*- coding:utf-8 -*-
from PIL import Image
import numpy as np
from PIL import ImageDraw
import cv2
import io
import requests


def rgb2xy(rgb):
    r,g,b,_ = rgb
    index = r * 256 * 256 + g * 256 + b
    x = index / 2048
    y = index % 2048
    return x,y

def get_rectangle(im):
    im_data = np.asarray(im)
    xy_res = im_data[:, :, 3].nonzero()
    points_dict = {}
    for y, x in zip(xy_res[0].tolist(), xy_res[1].tolist()):
        color = str(im_data[y, x].tolist())
        if color in points_dict:
            points_dict[color].append([x, y])
        else:
            points_dict[color] = [[x, y]]

    points_points_dict = {}
    for k in points_dict:
        avg_x = int(np.average([p[0] for p in points_dict[k]]))
        avg_y = int(np.average([p[1] for p in points_dict[k]]))
        points_points_dict[str(rgb2xy(eval(k)))] = (avg_x, avg_y)

    dict = {}
    for k in points_points_dict:
        x, y = eval(k)
        if x % 1 == 0 and y % 1 == 0 or True:
            dict[k] = points_points_dict[k]
    print len(dict)

    x_lst = sorted(set([eval(i)[0] for i in dict.keys()]))
    y_lst = sorted(set([eval(i)[1] for i in dict.keys()]))
    rect_lst = []
    for i in range(len(x_lst)-1):
        for j in range(len(y_lst)-1):
            p1 = (x_lst[i],y_lst[j])
            p2 = (x_lst[i+1],y_lst[j])
            p3 = (x_lst[i],y_lst[j+1])
            p4 = (x_lst[i+1],y_lst[j+1])
            rect_lst.append([[p1,p2,p3,p4],[dict[str(p1)],dict[str(p2)],dict[str(p3)],dict[str(p4)]]])
    print "rect_len:",len(rect_lst)
    return rect_lst

import traceback
def process(im):
    try:
        rect_lst = get_rectangle(im)
        texture_coord = []
        vertext_coord = []
        for i in rect_lst:
            material_rect,output_rect = i
            a1 = [(i[0]/2048.0,i[1]/2048.0) for i in material_rect[:3]]
            b1 = output_rect[:3]
            a2 = [(i[0]/2048.0,i[1]/2048.0) for i in material_rect[1:]]
            b2 = output_rect[1:]
            texture_coord.extend(np.array(a1).reshape(-1).tolist())
            texture_coord.extend(np.array(a2).reshape(-1).tolist())
            vertext_coord.extend(np.array(b1).reshape(-1).tolist())
            vertext_coord.extend(np.array(b2).reshape(-1).tolist())
        return {"status":0,"message":True}
    except Exception:
	traceback.print_exc()
        return {"status":-1,"message":False}


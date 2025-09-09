#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import cg_algorithms as alg
import numpy as np
from PIL import Image


if __name__ == '__main__':
    # 读取命令行的参数
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    item_dict = {}
    pen_color = np.zeros(3, np.uint8)
    width = 0
    height = 0

    with open(input_file, 'r') as fp:
        # 从文件中读取命令
        line = fp.readline()
        while line:
            # 将命令按照空格分割参数
            line = line.strip().split(' ')
            # 读取命令的内容，按照不同情况处理
            if line[0] == 'resetCanvas':
                width = int(line[1])
                height = int(line[2])
                item_dict = {}
            # 绘制在这个分支里
            # 其他的分支只是保存图元对象
            # 未填写完整
            elif line[0] == 'saveCanvas':
                save_name = line[1]
                canvas = np.zeros([height, width, 3], np.uint8)
                canvas.fill(255)
                # 注意到此处的参数为：类型，控制点，算法，颜色
                # 不存在多余算法的被保存为 ""
                for item_type, p_list, algorithm, color in item_dict.values():
                    if item_type == 'line':
                        pixels = alg.draw_line(p_list, algorithm)
                        for x, y in pixels:
                            canvas[height - 1 - y, x] = color  # 根据Pillow版本而定，最终输出的视觉结果需要以画布左上角为坐标原点
                    elif item_type == 'polygon':
                        pass
                    elif item_type == 'ellipse':
                        pass
                    elif item_type == 'curve':
                        pass
                Image.fromarray(canvas).save(os.path.join(output_dir, save_name + '.bmp'), 'bmp')
            elif line[0] == 'setColor':
                pen_color[0] = int(line[1])
                pen_color[1] = int(line[2])
                pen_color[2] = int(line[3])
            elif line[0] == 'drawLine':
                item_id = line[1]
                x0 = int(line[2])
                y0 = int(line[3])
                x1 = int(line[4])
                y1 = int(line[5])
                algorithm = line[6]
                item_dict[item_id] = ['line', [[x0, y0], [x1, y1]], algorithm, np.array(pen_color)]
            elif line[0] == 'drawPolygon':
                item_id = line[1]
                dots = []
                sizeofargs = len(line)
                for i in range(2, sizeofargs - 1, 2):
                    dots.append([int(line[i]), int(line[i + 1])])
                algorithm = line[sizeofargs - 1]
                item_dict[item_id] = ['Polygon', dots, algorithm, np.array(pen_color)]        
            elif line[0] == 'drawEllipse':
                item_id = line[1]
                x0 = int(line[2])
                y0 = int(line[3])
                x1 = int(line[4])
                y1 = int(line[5])
                item_dict[item_id] = ['ellipse', [[x0, y0], [x1, y1]], "", np.array(pen_color)]
            elif line[0] == 'drawCurve':
                # 命令格式: drawCurve id x0 y0 x1 y1 x2 y2 ... algorithm
                item_id = line[1]
                dots = []
                sizeofargs = len(line)
                # 提取控制点坐标（从索引2开始，到倒数第二个元素结束，步长2）
                for i in range(2, sizeofargs - 1, 2):
                    dots.append([int(line[i]), int(line[i + 1])])
                algorithm = line[sizeofargs - 1]
                item_dict[item_id] = ['curve', dots, algorithm, np.array(pen_color)]
            # 存储平移参数：类型、偏移量
            elif line[0] == 'translate':
                # 命令格式: translate id dx dy
                item_id = line[1]
                dx = int(line[2])
                dy = int(line[3])
                item_dict[item_id] = ['translate', dx, dy]
            # 存储旋转参数：类型、旋转中心、角度
            elif line[0] == 'rotate':
                # 命令格式: rotate id x y r
                item_id = line[1]
                x = int(line[2])    # 旋转中心x坐标
                y = int(line[3])    # 旋转中心y坐标
                r = int(line[4])    # 旋转角度（度）
                item_dict[item_id] = ['rotate', x, y, r]
            # 存储缩放参数：类型、缩放中心、比例
            elif line[0] == 'scale':
                # 命令格式: scale id x y s
                item_id = line[1]
                x = int(line[2])    # 缩放中心x坐标
                y = int(line[3])    # 缩放中心y坐标
                s = float(line[4])  # 缩放比例（支持浮点）
                item_dict[item_id] = ['scale', x, y, s]
            # 存储裁剪参数：类型、窗口坐标、算法
            elif line[0] == 'clip':
                # 命令格式: clip id x0 y0 x1 y1 algorithm
                item_id = line[1]
                x0 = int(line[2])   # 裁剪窗口左上角x
                y0 = int(line[3])   # 裁剪窗口左上角y
                x1 = int(line[4])   # 裁剪窗口右下角x
                y1 = int(line[5])   # 裁剪窗口右下角y
                algorithm = line[6] # 裁剪算法
                item_dict[item_id] = ['clip', [[x0, y0], [x1, y1]], algorithm]
            # 读取下一个命令
            line = fp.readline()


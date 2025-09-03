#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))
        x_inc = dx / steps
        y_inc = dy / steps
        # 当前点坐标（使用临时变量，避免修改原始起点）
        x, y = x0, y0
        for _ in range(int(steps) + 1):
            # 对坐标进行四舍五入取整
            result.append((round(x), round(y)))
            x += x_inc
            y += y_inc
    elif algorithm == 'Bresenham':
        # 计算坐标差值
        dx = x1 - x0
        dy = y1 - y0
        # 确定步进方向
        x_step = 1 if dx > 0 else -1 if dx < 0 else 0
        y_step = 1 if dy > 0 else -1 if dy < 0 else 0
        # 取绝对值，便于比较和计算
        dx_abs = abs(dx)
        dy_abs = abs(dy)
        x, y = x0, y0
        result.append((x, y))
        # 处理特殊情况：垂直线
        if dx_abs == 0:
            # 沿y轴步进
            for _ in range(dy_abs):
                y += y_step
                result.append((x, y))
            return result
        # 处理特殊情况：水平线
        if dy_abs == 0:
            # 沿x轴步进
            for _ in range(dx_abs):
                x += x_step
                result.append((x, y))
            return result
        # 通用情况：根据斜率绝对值决定步进方向
        if dx_abs > dy_abs:
            # 斜率绝对值小于1，沿x轴步进
            p = 2 * dy_abs - dx_abs
            for _ in range(dx_abs):
                x += x_step
                if p >= 0:
                    y += y_step
                    p += 2 * (dy_abs - dx_abs)
                else:
                    p += 2 * dy_abs
                result.append((x, y))
        else:
            # 斜率绝对值大于等于1，沿y轴步进
            p = 2 * dx_abs - dy_abs
            for _ in range(dy_abs):
                y += y_step
                if p >= 0:
                    x += x_step
                    p += 2 * (dx_abs - dy_abs)
                else:
                    p += 2 * dx_abs
                result.append((x, y))
        return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    # 解析包围框坐标
    (x0, y0), (x1, y1) = p_list
    # 计算椭圆中心
    center_x = (x0 + x1) // 2
    center_y = (y0 + y1) // 2
    # 计算长半轴和短半轴（取绝对值确保为正）
    a = abs(x1 - x0) // 2  # x方向半轴
    b = abs(y1 - y0) // 2  # y方向半轴
    # 特殊情况处理：若半轴为0，绘制一个点
    if a == 0 and b == 0:
        return [[center_x, center_y]]
    if a == 0:  # 退化为垂直线
        return [[center_x, y] for y in range(min(y0, y1), max(y0, y1) + 1)]
    if b == 0:  # 退化为水平线
        return [[x, center_y] for x in range(min(x0, x1), max(x0, x1) + 1)]
    result = []
    x, y = 0, b  # 从第一象限起点开始
    # 计算初始决策变量（区域1）
    a_sq = a * a
    b_sq = b * b
    d1 = b_sq - a_sq * b + (a_sq // 4)
    two_a_sq = 2 * a_sq
    two_b_sq = 2 * b_sq
    # 区域1：x为主方向步进，直到2*b²*x >= 2*a²*y（斜率绝对值<=1的区域）
    while two_b_sq * x <= two_a_sq * y:
        # 添加8个对称点（考虑椭圆中心偏移）
        result.extend([
            [center_x + x, center_y + y],
            [center_x - x, center_y + y],
            [center_x + x, center_y - y],
            [center_x - x, center_y - y]
        ])
        # 更新决策变量和坐标
        if d1 < 0:
            # 中点在椭圆内，选择y不变
            d1 += two_b_sq * (x + 1)
        else:
            # 中点在椭圆外，选择y减1
            d1 += two_b_sq * (x + 1) - two_a_sq * (y - 1)
            y -= 1
        x += 1
    # 计算区域2的初始决策变量
    d2 = b_sq * (x + 0.5) ** 2 + a_sq * (y - 1) ** 2 - a_sq * b_sq
    d2 = int(round(d2))  # 转换为整数运算
    # 区域2：y为主方向步进，直到y < 0（斜率绝对值>1的区域）
    while y >= 0:
        # 添加8个对称点（考虑椭圆中心偏移）
        result.extend([
            [center_x + x, center_y + y],
            [center_x - x, center_y + y],
            [center_x + x, center_y - y],
            [center_x - x, center_y - y]
        ])
        # 更新决策变量和坐标
        if d2 > 0:
            # 中点在椭圆外，选择x不变
            d2 += two_a_sq * (1 - y)
        else:
            # 中点在椭圆内，选择x加1
            d2 += two_b_sq * (x + 1) + two_a_sq * (1 - y)
            x += 1
        y -= 1
    # 去除可能重复的点（当a或b为0时可能出现）并排序
    # 转换为元组去重，再转回列表
    unique_points = list({tuple(p) for p in result})
    # 按x,y坐标排序，使结果更直观
    unique_points.sort()
    # 转回列表的列表形式
    return [list(p) for p in unique_points]


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    pass


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for [x, y] in p_list:
        result.append([x + dx, y + dy])
    return result

def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for [x_n, y_n] in p_list:
        # 平移到缩放中心，消除缩放偏移
        x_n -= x
        y_n -= y 
        # 按比例缩放
        x_n *= s
        y_n *= s
        # 平移回原位置
        x_n += x
        y_n += y
        result.append([round(x_n), round(y_n)])
    return result


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    result = []
    # 解析端点坐标
    (x0, y0), (x1, y1) = p_list
    if algorithm == 'Cohen-Sutherland':
        # 对端点进行编码
        byte1 = 0x0
        byte2 = 0x0
        if x0 < x_min: byte1 = byte1 | 0x1
        if x0 > x_max: byte1 = byte1 | 0x2
        if y0 < y_min: byte1 = byte1 | 0x4
        if y0 > y_max: byte1 = byte1 | 0x8
        if x1 < x_min: byte2 = byte2 | 0x1
        if x1 > x_max: byte2 = byte2 | 0x2
        if y1 < y_min: byte2 = byte2 | 0x4
        if y1 > y_max: byte2 = byte2 | 0x8
        # 完全在窗口内
        if (byte1 == 0) and (byte2 == 0): return [[x0, y0], [x1, y1]]
        # 完全在窗口外
        elif (byte1 & byte2) != 0: return []
        # 部分在窗口内
        else:
            # 特判：垂直线的情况，无法计算斜率
            if x1 - x0 == 0:
                if y0 < y_min: result.append([x0, y_min])
                elif y0 > y_max: result.append([x0, y_max])
                else: result.append([x0, y0])
                if y1 < y_min: result.append([x1, y_min])
                elif y1 > y_max: result.append([x1, y_max])
                else: result.append([x1, y1])
                return result
            # 计算斜率
            k = (y1 - y0) / (x1 - x0)
            # 首先看第一个端点是否在窗口内
            if byte1 == 0: result.append([x0, y0])
            else:
                pass
            # 再处理第二个端点是否在窗口内
            
    elif algorithm == 'Liang-Barsky':
        pass

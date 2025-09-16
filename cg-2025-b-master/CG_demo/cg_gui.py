#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import math
import cg_algorithms as alg
from typing import Optional, List, Tuple
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QGraphicsItem, QListWidget, QHBoxLayout, QVBoxLayout, QWidget,
    QPushButton, QComboBox, QLineEdit, QLabel, QColorDialog, QFileDialog,
    QStyleOptionGraphicsItem, QStatusBar
)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPen, QImage, QPixmap
from PyQt5.QtCore import QRectF, Qt, QPointF


class MyItem(QGraphicsItem):
    """自定义图元类，支持多种图元类型绘制"""
    def __init__(self, item_id: str, item_type: str, p_list: list, 
                 algorithm: str = '', color: Tuple[int, int, int] = (0, 0, 0), 
                 parent: QGraphicsItem = None):
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型：line/polygon/ellipse/curve
        self.p_list = p_list        # 顶点/控制点列表
        self.algorithm = algorithm  # 绘制算法
        self.color = color          # 颜色(RGB)
        self.selected = False       # 是否选中

    def boundingRect(self) -> QRectF:
        """定义图元边界（用于碰撞检测和重绘）"""
        if not self.p_list:
            return QRectF()
        xs = [p[0] for p in self.p_list]
        ys = [p[1] for p in self.p_list]
        return QRectF(min(xs)-2, min(ys)-2, max(xs)-min(xs)+4, max(ys)-min(ys)+4)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None) -> None:
        """绘制图元（调用核心算法生成像素）"""
        # 设置画笔颜色
        painter.setPen(QPen(QColor(*self.color), 1))
        if self.selected:
            # 选中状态绘制红色边框
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))

        # 根据图元类型调用对应算法
        if self.item_type == 'line':
            pixels = alg.draw_line(self.p_list, self.algorithm)
        elif self.item_type == 'polygon':
            pixels = alg.draw_polygon(self.p_list, self.algorithm)
        elif self.item_type == 'ellipse':
            pixels = alg.draw_ellipse(self.p_list)
        elif self.item_type == 'curve':
            pixels = alg.draw_curve(self.p_list, self.algorithm)
        else:
            return

        # 绘制所有像素点
        for (x, y) in pixels:
            painter.drawPoint(x, y)


class MyCanvas(QGraphicsView):
    """画布类，处理鼠标交互和图元管理"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 800, 600)  # 默认画布大小

        # 状态管理
        self.current_state = "idle"  # idle/drawing/editing
        self.current_draw_type = None  # line/polygon/ellipse/curve
        self.current_algorithm = None  # 绘制算法
        self.current_color = (0, 0, 0)  # 默认黑色
        self.current_item_id = None    # 当前图元ID

        # 临时数据
        self.temp_points = []          # 绘制临时点
        self.selected_item = None      # 选中的图元
        self.edit_start_pos = None     # 编辑起始位置
        self.preview_item = None       # 预览图元

        # 关联图元列表
        self.list_widget = None

    def set_list_widget(self, list_widget):
        """关联图元列表组件"""
        self.list_widget = list_widget
        self.list_widget.itemClicked.connect(self.on_list_item_clicked)

    def start_drawing(self, draw_type: str, algorithm: str, item_id: str):
        """开始绘制图元"""
        self.current_state = "drawing"
        self.current_draw_type = draw_type
        self.current_algorithm = algorithm
        self.current_item_id = item_id
        self.temp_points = []
        self.statusBar.showMessage(f"绘制{draw_type}（算法：{algorithm}），点击添加点，右键结束")

    def set_color(self, color: Tuple[int, int, int]):
        """设置当前画笔颜色"""
        self.current_color = color
        self.statusBar.showMessage(f"颜色设置为：R={color[0]}, G={color[1]}, B={color[2]}")

    def reset_canvas(self, width: int, height: int):
        """重置画布"""
        self.scene.clear()
        # 清除所有临时状态（关键修复）
        self.temp_points = []
        self.selected_item = None
        self.preview_item = None
        self.current_state = "idle"
        # 更新列表和场景
        if self.list_widget:
            self.list_widget.clear()
        self.setSceneRect(0, 0, width, height)
        self.scene.update()  # 强制刷新
        self.statusBar.showMessage(f"画布重置为 {width}x{height}")

    def save_canvas(self, path: str):
        """保存画布为图片"""
        img = QImage(self.sceneRect().size().toSize(), QImage.Format_RGB32)
        painter = QPainter(img)
        self.scene.render(painter)
        img.save(path)
        self.statusBar.showMessage(f"画布已保存至 {path}")

    def start_editing(self, operation: str):
        """开始编辑操作（平移/旋转/缩放）"""
        if not self.selected_item:
            self.statusBar.showMessage("请先选中一个图元")
            return
        self.current_state = "editing"
        self.edit_operation = operation
        self.statusBar.showMessage(f"编辑：{operation}，拖动鼠标完成操作")

    def on_list_item_clicked(self, item):
        """图元列表项点击事件"""
        item_id = item.text()
        # 取消之前的选中状态
        if self.selected_item:
            self.selected_item.selected = False
            self.selected_item.update()
            self.selected_item = None  # 显式置空
        # 选中新图元
        for scene_item in self.scene.items():
            if isinstance(scene_item, MyItem) and scene_item.id == item_id:
                self.selected_item = scene_item
                self.selected_item.selected = True
                self.selected_item.update()
                break
        self.scene.update()  # 刷新场景

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.pos())
        x, y = int(pos.x()), int(pos.y())

        if event.button() == Qt.LeftButton:
            if self.current_state == "drawing":
                # 收集绘制点
                self.temp_points.append([x, y])
                # 实时预览（线段/椭圆只需2个点）
                if self.current_draw_type in ["line", "ellipse"] and len(self.temp_points) == 2:
                    self.finish_drawing()
            elif self.current_state == "editing":
                # 记录编辑起始位置
                self.edit_start_pos = (x, y)
            else:  # idle状态：点击选中图元
                self.select_item(pos)

        elif event.button() == Qt.RightButton and self.current_state == "drawing":
            # 右键结束多边形/曲线绘制（至少需要2个点）
            if len(self.temp_points) >= 2:
                self.finish_drawing()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.current_state == "drawing" and len(self.temp_points) == 1:
            # 实时预览（线段/椭圆）
            pos = self.mapToScene(event.pos())
            x, y = int(pos.x()), int(pos.y())
            # 移除上一次预览（关键修复：确保预览图元被彻底移除）
            if self.preview_item:
                self.scene.removeItem(self.preview_item)
                self.preview_item = None  # 显式置空，避免引用残留
            # 生成预览图元
            preview_points = self.temp_points + [[x, y]]
            self.preview_item = MyItem(
                id="preview",
                item_type=self.current_draw_type,
                p_list=preview_points,
                algorithm=self.current_algorithm,
                color=(128, 128, 128)  # 灰色预览
            )
            self.scene.addItem(self.preview_item)

        elif self.current_state == "editing" and self.edit_start_pos and self.selected_item:
            # 实时编辑（平移/旋转/缩放）
            pos = self.mapToScene(event.pos())
            x, y = int(pos.x()), int(pos.y())
            dx = x - self.edit_start_pos[0]
            dy = y - self.edit_start_pos[1]

            # 调用核心算法更新图元
            if self.edit_operation == "translate":
                new_points = alg.translate(self.selected_item.p_list, dx, dy)
            elif self.edit_operation == "rotate":
                # 以初始点击位置为旋转中心
                cx, cy = self.edit_start_pos
                angle = math.atan2(dy, dx) * 180 / math.pi  # 计算旋转角度
                new_points = alg.rotate(self.selected_item.p_list, cx, cy, angle)
            elif self.edit_operation == "scale":
                cx, cy = self.edit_start_pos
                scale = 1.0 + (dx + dy) / 100  # 简单缩放因子计算
                new_points = alg.scale(self.selected_item.p_list, cx, cy, scale)
            else:
                return

            # 更新图元后强制刷新
            self.selected_item.p_list = new_points
            self.selected_item.update()  # 更新单个图元
            self.scene.update()  # 强制刷新整个场景（关键修复）
            self.edit_start_pos = (x, y)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.current_state == "editing":
            self.current_state = "idle"
            self.statusBar.showMessage("编辑完成")
        super().mouseReleaseEvent(event)

    def finish_drawing(self):
        """完成绘制并添加图元到画布"""
        # 移除预览
        if self.preview_item:
            self.scene.removeItem(self.preview_item)
            self.preview_item = None

        # 创建图元
        item = MyItem(
            item_id=self.current_item_id,
            item_type=self.current_draw_type,
            p_list=self.temp_points,
            algorithm=self.current_algorithm,
            color=self.current_color
        )
        self.scene.addItem(item)

        # 添加到图元列表
        if self.list_widget:
            self.list_widget.addItem(self.current_item_id)

        # 重置状态
        self.current_state = "idle"
        self.statusBar.showMessage(f"图元 {self.current_item_id} 绘制完成")

    def select_item(self, scene_pos: QPointF):
        """通过鼠标位置选中图元"""
        # 取消之前的选中
        if self.selected_item:
            self.selected_item.selected = False
            self.selected_item.update()
            self.selected_item = None

        # 查找点击位置的图元
        for item in self.scene.items(scene_pos):
            if isinstance(item, MyItem):
                self.selected_item = item
                self.selected_item.selected = True
                self.selected_item.update()
                # 更新列表选中状态
                if self.list_widget:
                    for i in range(self.list_widget.count()):
                        if self.list_widget.item(i).text() == item.id:
                            self.list_widget.setCurrentRow(i)
                            break
                self.statusBar.showMessage(f"选中图元：{item.id}")
                break


class MainWindow(QMainWindow):
    """主窗口类，整合UI组件"""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("计算机图形学绘图系统")
        self.setGeometry(100, 100, 1000, 700)

        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")

        # 画布
        self.canvas = MyCanvas(self)
        self.canvas.statusBar = self.statusBar  # 关联状态栏

        # 图元列表
        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(150)
        self.list_widget.setWindowTitle("图元列表")
        self.canvas.set_list_widget(self.list_widget)

        # 控制面板
        control_panel = self.create_control_panel()

        # 布局
        main_layout = QHBoxLayout()
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.canvas, 5)
        main_layout.addWidget(self.list_widget, 1)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_control_panel(self):
        """创建控制面板（按钮、输入框等）"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 图元ID输入
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("图元ID")
        layout.addWidget(QLabel("图元ID:"))
        layout.addWidget(self.id_input)

        # 绘制控制
        layout.addWidget(QLabel("绘制图元:"))
        
        # 线段
        line_layout = QHBoxLayout()
        self.line_btn = QPushButton("线段")
        self.line_alg = QComboBox()
        self.line_alg.addItems(["DDA", "Bresenham"])
        line_layout.addWidget(self.line_btn)
        line_layout.addWidget(self.line_alg)
        layout.addLayout(line_layout)
        self.line_btn.clicked.connect(lambda: self.start_draw("line"))

        # 多边形
        poly_layout = QHBoxLayout()
        self.poly_btn = QPushButton("多边形")
        self.poly_alg = QComboBox()
        self.poly_alg.addItems(["DDA", "Bresenham"])
        poly_layout.addWidget(self.poly_btn)
        poly_layout.addWidget(self.poly_alg)
        layout.addLayout(poly_layout)
        self.poly_btn.clicked.connect(lambda: self.start_draw("polygon"))

        # 椭圆
        self.ellipse_btn = QPushButton("椭圆")
        layout.addWidget(self.ellipse_btn)
        self.ellipse_btn.clicked.connect(lambda: self.start_draw("ellipse"))

        # 曲线
        curve_layout = QHBoxLayout()
        self.curve_btn = QPushButton("曲线")
        self.curve_alg = QComboBox()
        self.curve_alg.addItems(["Bezier", "B-spline"])
        curve_layout.addWidget(self.curve_btn)
        curve_layout.addWidget(self.curve_alg)
        layout.addLayout(curve_layout)
        self.curve_btn.clicked.connect(lambda: self.start_draw("curve"))

        # 颜色选择
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.clicked.connect(self.choose_color)
        layout.addWidget(self.color_btn)

        # 编辑控制
        layout.addWidget(QLabel("编辑操作:"))
        edit_layout = QHBoxLayout()
        self.translate_btn = QPushButton("平移")
        self.rotate_btn = QPushButton("旋转")
        self.scale_btn = QPushButton("缩放")
        edit_layout.addWidget(self.translate_btn)
        edit_layout.addWidget(self.rotate_btn)
        edit_layout.addWidget(self.scale_btn)
        layout.addLayout(edit_layout)
        self.translate_btn.clicked.connect(lambda: self.canvas.start_editing("translate"))
        self.rotate_btn.clicked.connect(lambda: self.canvas.start_editing("rotate"))
        self.scale_btn.clicked.connect(lambda: self.canvas.start_editing("scale"))

        # 画布控制
        canvas_layout = QHBoxLayout()
        self.reset_btn = QPushButton("重置画布")
        self.save_btn = QPushButton("保存画布")
        canvas_layout.addWidget(self.reset_btn)
        canvas_layout.addWidget(self.save_btn)
        layout.addLayout(canvas_layout)
        self.reset_btn.clicked.connect(self.reset_canvas_dialog)
        self.save_btn.clicked.connect(self.save_canvas_dialog)

        layout.addStretch()
        return panel

    def start_draw(self, draw_type: str):
        """开始绘制图元（获取ID和算法）"""
        item_id = self.id_input.text().strip()
        if not item_id:
            self.statusBar.showMessage("请输入图元ID")
            return

        # 获取对应算法
        if draw_type == "line":
            algorithm = self.line_alg.currentText()
        elif draw_type == "polygon":
            algorithm = self.poly_alg.currentText()
        elif draw_type == "curve":
            algorithm = self.curve_alg.currentText()
        else:  # ellipse不需要算法
            algorithm = ""

        self.canvas.start_drawing(draw_type, algorithm, item_id)

    def choose_color(self):
        """选择颜色对话框"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_color((color.red(), color.green(), color.blue()))

    def reset_canvas_dialog(self):
        """重置画布对话框"""
        from PyQt5.QtWidgets import QInputDialog
        width, ok1 = QInputDialog.getInt(self, "画布宽度", "请输入宽度(100-1000):", 800, 100, 1000)
        if ok1:
            height, ok2 = QInputDialog.getInt(self, "画布高度", "请输入高度(100-1000):", 600, 100, 1000)
            if ok2:
                self.canvas.reset_canvas(width, height)

    def save_canvas_dialog(self):
        """保存画布对话框"""
        path, _ = QFileDialog.getSaveFileName(self, "保存画布", "", "BMP文件 (*.bmp)")
        if path:
            self.canvas.save_canvas(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
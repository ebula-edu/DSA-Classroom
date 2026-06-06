import math
import json
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer, QLineF, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import (QPainter, QColor, QFont, QPen, QBrush, QPainterPath,
                           QPolygonF, QKeyEvent, QTransform, QImage, QPixmap)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGraphicsEllipseItem, QGraphicsRectItem,
                             QGraphicsPathItem, QGraphicsTextItem, QButtonGroup,
                             QColorDialog, QInputDialog, QSlider, QLabel,
                             QFileDialog, QMessageBox, QGraphicsPixmapItem,
                             QApplication)
from gui.icons import VectorIconProvider

# Clean White Classroom theme
COLOR_WHITEBOARD_BG = QColor("#ffffff")
COLOR_GRID = QColor("#e0e0e0")
COLOR_STICKY_BG = QColor("#fffde7") # Soft pastel yellow
COLOR_STICKY_TEXT = QColor("#000000")

class GravityStackItem(QGraphicsRectItem):
    """
    A visual bucket container that elements can drop into.
    """
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.setBrush(QBrush(QColor(240, 240, 240, 150)))
        self.setPen(QPen(QColor("#007acc"), 3))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(0)
        self.type_name = "stack_container"

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            scene = self.scene()
            if scene:
                for item in scene.items():
                    if hasattr(item, "type_name") and item.type_name == "connection_line":
                        item.update_path()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRect(r)
        
        # Label
        painter.setPen(QPen(QColor("#555555")))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(r.adjusted(10, 10, 0, 0), Qt.AlignTop | Qt.AlignLeft, "STACK BUCKET")


class CSBlockItem(QGraphicsRectItem):
    """
    Representing blocks like Array Blocks, Stack Nodes, etc.
    """
    def __init__(self, x, y, val_str="X", is_node=False, parent=None):
        super().__init__(-35, -20, 70, 40, parent)
        self.setPos(x, y)
        self.val_str = val_str
        self.is_node = is_node
        
        self.setBrush(QBrush(QColor("#007acc")))
        self.setPen(QPen(QColor("#005995"), 2))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(2)
        
        self.velocity_y = 0.0
        self.type_name = "cs_block"

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            scene = self.scene()
            if scene:
                for item in scene.items():
                    if hasattr(item, "type_name") and item.type_name == "connection_line":
                        item.update_path()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(r, 4, 4)
        
        if self.is_node:
            sep_x = r.right() - 20
            painter.drawLine(sep_x, r.top(), sep_x, r.bottom())
            
            painter.setPen(QPen(Qt.white))
            painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
            painter.drawText(r.adjusted(0, 0, -20, 0), Qt.AlignCenter, self.val_str)
            
            painter.setFont(QFont("Arial", 12))
            painter.drawText(QRectF(sep_x, r.top(), 20, r.height()), Qt.AlignCenter, "▪")
        else:
            painter.setPen(QPen(Qt.white))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            painter.drawText(r, Qt.AlignCenter, self.val_str)

    def mouseDoubleClickEvent(self, event):
        new_val, ok = QInputDialog.getText(None, "Edit Value", "Enter element value:", text=self.val_str)
        if ok and new_val:
            self.val_str = new_val
            self.update()
        super().mouseDoubleClickEvent(event)


class StickyNoteItem(QGraphicsRectItem):
    """
    A sticky note block.
    """
    def __init__(self, x, y, text_str="Sticky Note", parent=None):
        super().__init__(-60, -60, 120, 120, parent)
        self.setPos(x, y)
        self.text_str = text_str
        self.setBrush(QBrush(COLOR_STICKY_BG))
        self.setPen(QPen(QColor("#d4af37"), 1.5))
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(1)
        self.type_name = "sticky_note"

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            scene = self.scene()
            if scene:
                for item in scene.items():
                    if hasattr(item, "type_name") and item.type_name == "connection_line":
                        item.update_path()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        # shadow
        painter.fillRect(r.translated(4, 4), QColor(0, 0, 0, 40))
        # paper
        painter.fillRect(r, self.brush().color())
        painter.setPen(self.pen())
        painter.drawRect(r)
        
        # text
        painter.setPen(QPen(COLOR_STICKY_TEXT))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(r.adjusted(10, 10, -10, -10), Qt.AlignLeft | Qt.TextWordWrap, self.text_str)

    def mouseDoubleClickEvent(self, event):
        text, ok = QInputDialog.getMultiLineText(None, "Edit Sticky Note", "Enter content:", self.text_str)
        if ok:
            self.text_str = text
            self.update()
        super().mouseDoubleClickEvent(event)

class ConnectionLineItem(QGraphicsPathItem):
    """
    A connection line or arrow between two shapes (CSBlockItem, StickyNoteItem, GravityStackItem).
    Updates its geometry dynamically as shapes are dragged.
    """
    def __init__(self, start_pt, end_pt, start_item=None, end_item=None, is_arrow=False, color=Qt.black, width=3, parent=None):
        super().__init__(parent)
        self.start_pt = start_pt
        self.end_pt = end_pt
        self.start_item = start_item
        self.end_item = end_item
        self.is_arrow = is_arrow
        self.color = color
        self.width = width
        self.type_name = "connection_line"
        
        self.setPen(QPen(self.color, self.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(-1) # Render behind shapes
        
        self.update_path()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            delta = value - QPointF(0, 0)
            if delta != QPointF(0, 0):
                self.start_pt += delta
                self.end_pt += delta
                self.update_path()
            return QPointF(0, 0)
        return super().itemChange(change, value)
        
    def update_path(self):
        p1 = self.start_item.sceneBoundingRect().center() if self.start_item else self.start_pt
        p2 = self.end_item.sceneBoundingRect().center() if self.end_item else self.end_pt
        
        if p1 == p2:
            self.setPath(QPainterPath())
            return
            
        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        
        if self.is_arrow:
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            angle = math.atan2(dy, dx)
            arrow_size = 12
            
            if self.end_item:
                offset = 25.0
                if hasattr(self.end_item, "type_name"):
                    if self.end_item.type_name == "cs_block":
                        offset = 25.0
                    elif self.end_item.type_name == "sticky_note":
                        offset = 60.0
                    elif self.end_item.type_name == "stack_container":
                        offset = 60.0
                p2 = p2 - QPointF(offset * math.cos(angle), offset * math.sin(angle))
                
                path = QPainterPath()
                path.moveTo(p1)
                path.lineTo(p2)
                
            ap1 = p2 - QPointF(arrow_size * math.cos(angle - math.pi / 6), arrow_size * math.sin(angle - math.pi / 6))
            ap2 = p2 - QPointF(arrow_size * math.cos(angle + math.pi / 6), arrow_size * math.sin(angle + math.pi / 6))
            
            path.moveTo(p2)
            path.lineTo(ap1)
            path.lineTo(ap2)
            path.closeSubpath()
            
        self.setPath(path)


class WhiteboardView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setStyleSheet("background-color: transparent; border: none;")
        
        self.drawing_mode = "select"
        self.current_color = Qt.black
        self.current_pen_width = 3
        
        self.current_path_item = None
        self.preview_shape_item = None
        self.start_point = QPointF()
        self.start_item = None
        self.bg_theme = "light"
        
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setInteractive(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        self.resizing_item = None
        self.resizing_line = None
        self.resizing_line_endpoint = None
        self.resize_start_pos = QPointF()
        self.resize_start_rect = None
        self.resize_start_scale = 1.0
        self.resize_start_font_size = 14

    def drawBackground(self, painter, rect):
        bg_color = QColor("#ffffff") if self.bg_theme == "light" else QColor("#121212")
        painter.fillRect(rect, bg_color)
        
        grid_color = QColor("#e0e0e0") if self.bg_theme == "light" else QColor("#2d2d2d")
        pen = QPen(grid_color, 1)
        painter.setPen(pen)
        
        grid_size = 50
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        
        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += grid_size
            
        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += grid_size

    def set_drawing_mode(self, mode):
        self.drawing_mode = mode
        if mode == "select":
            self.setDragMode(QGraphicsView.RubberBandDrag)
            for item in self.scene().items():
                if not isinstance(item, ConnectionLineItem):
                    item.setFlag(QGraphicsItem.ItemIsMovable, True)
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        else:
            self.setDragMode(QGraphicsView.NoDrag)
            self.scene().clearSelection()

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.start_point = scene_pos
        
        focused_item = self.scene().focusItem()
        if isinstance(focused_item, QGraphicsTextItem):
            if not focused_item.toPlainText().strip() or focused_item.toPlainText() == "Type here...":
                self.scene().removeItem(focused_item)
                
        # Click-resize detection in Select mode
        if self.drawing_mode == "select" and event.button() == Qt.LeftButton:
            # 1. Check freestanding connection line endpoints
            for item in self.scene().selectedItems():
                if hasattr(item, "type_name") and item.type_name == "connection_line":
                    p1 = item.start_item.sceneBoundingRect().center() if item.start_item else item.start_pt
                    p2 = item.end_item.sceneBoundingRect().center() if item.end_item else item.end_pt
                    if not item.start_item and math.hypot(scene_pos.x() - p1.x(), scene_pos.y() - p1.y()) < 15:
                        self.resizing_line = item
                        self.resizing_line_endpoint = "start"
                        self.resizing_line_had_movable = bool(item.flags() & QGraphicsItem.ItemIsMovable)
                        if self.resizing_line_had_movable:
                            item.setFlag(QGraphicsItem.ItemIsMovable, False)
                        if hasattr(self.parent(), "save_undo_state"):
                            self.parent().save_undo_state()
                        event.accept()
                        return
                    if not item.end_item and math.hypot(scene_pos.x() - p2.x(), scene_pos.y() - p2.y()) < 15:
                        self.resizing_line = item
                        self.resizing_line_endpoint = "end"
                        self.resizing_line_had_movable = bool(item.flags() & QGraphicsItem.ItemIsMovable)
                        if self.resizing_line_had_movable:
                            item.setFlag(QGraphicsItem.ItemIsMovable, False)
                        if hasattr(self.parent(), "save_undo_state"):
                            self.parent().save_undo_state()
                        event.accept()
                        return
                        
            # 2. Check shape bottom-right corners
            for item in self.scene().selectedItems():
                if item.zValue() >= 0:
                    rect = item.sceneBoundingRect()
                    br = rect.bottomRight()
                    if math.hypot(scene_pos.x() - br.x(), scene_pos.y() - br.y()) < 15:
                        self.resizing_item = item
                        self.resize_start_pos = scene_pos
                        if isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)):
                            self.resize_start_rect = item.rect()
                        elif isinstance(item, QGraphicsTextItem):
                            self.resize_start_font_size = item.font().pointSize()
                        else:
                            self.resize_start_scale = item.scale()
                        self.resizing_item_had_movable = bool(item.flags() & QGraphicsItem.ItemIsMovable)
                        if self.resizing_item_had_movable:
                            item.setFlag(QGraphicsItem.ItemIsMovable, False)
                        if hasattr(self.parent(), "save_undo_state"):
                            self.parent().save_undo_state()
                        self.viewport().setCursor(Qt.SizeFDiagCursor)
                        event.accept()
                        return
        
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and self.drawing_mode == "pan"):
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().mousePressEvent(event)
            return

        if self.drawing_mode in ("pen", "marker", "highlighter"):
            path = QPainterPath()
            path.moveTo(scene_pos)
            
            width = self.current_pen_width
            color = QColor(self.current_color)
            
            if self.drawing_mode == "marker":
                width = width * 2
            elif self.drawing_mode == "highlighter":
                width = width * 4
                color.setAlpha(100)
                
            self.current_path_item = QGraphicsPathItem()
            self.current_path_item.setPath(path)
            self.current_path_item.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.current_path_item.setZValue(1)
            self.scene().addItem(self.current_path_item)
            
        elif self.drawing_mode in ("rect", "circle", "line", "arrow"):
            self.start_item = None
            clicked_items = self.scene().items(scene_pos)
            for item in clicked_items:
                if hasattr(item, "type_name") and item.type_name in ("cs_block", "sticky_note", "stack_container"):
                    self.start_item = item
                    break
                    
            if self.drawing_mode == "rect":
                self.preview_shape_item = QGraphicsRectItem()
                self.preview_shape_item.setPen(QPen(self.current_color, self.current_pen_width))
            elif self.drawing_mode == "circle":
                self.preview_shape_item = QGraphicsEllipseItem()
                self.preview_shape_item.setPen(QPen(self.current_color, self.current_pen_width))
            elif self.drawing_mode in ("line", "arrow"):
                self.preview_shape_item = QGraphicsPathItem()
                self.preview_shape_item.setPen(QPen(self.current_color, self.current_pen_width))
                
            self.preview_shape_item.setZValue(1)
            self.scene().addItem(self.preview_shape_item)
            self.update_preview_shape(scene_pos)
            
        elif self.drawing_mode == "text":
            item = QGraphicsTextItem("Type here...")
            item.setDefaultTextColor(self.current_color)
            item.setFont(QFont("Arial", 14))
            item.setPos(scene_pos)
            item.setFlag(QGraphicsItem.ItemIsMovable)
            item.setFlag(QGraphicsItem.ItemIsSelectable)
            item.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.scene().addItem(item)
            item.setFocus()
            
            cursor = item.textCursor()
            cursor.select(cursor.SelectionType.Document)
            item.setTextCursor(cursor)
            
            if hasattr(self.parent(), "save_undo_state"):
                self.parent().save_undo_state()
            
        elif self.drawing_mode == "eraser":
            self.erase_at(scene_pos)
            
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        
        # 1. Handle active line resizing
        if self.resizing_line:
            if self.resizing_line_endpoint == "start":
                self.resizing_line.start_pt = scene_pos
            else:
                self.resizing_line.end_pt = scene_pos
            self.resizing_line.update_path()
            event.accept()
            return
            
        # 2. Handle active item resizing
        if self.resizing_item:
            dx = scene_pos.x() - self.resize_start_pos.x()
            dy = scene_pos.y() - self.resize_start_pos.y()
            
            if isinstance(self.resizing_item, (QGraphicsRectItem, QGraphicsEllipseItem)):
                r = self.resize_start_rect
                if hasattr(self.resizing_item, "type_name"):
                    if self.resizing_item.type_name == "cs_block":
                        w = max(20.0, r.width() + dx * 2)
                        h = max(15.0, r.height() + dy * 2)
                        self.resizing_item.setRect(-w/2, -h/2, w, h)
                    elif self.resizing_item.type_name == "sticky_note":
                        w = max(40.0, r.width() + dx * 2)
                        h = max(40.0, r.height() + dy * 2)
                        self.resizing_item.setRect(-w/2, -h/2, w, h)
                    elif self.resizing_item.type_name == "stack_container":
                        w = max(40.0, r.width() + dx)
                        h = max(40.0, r.height() + dy)
                        self.resizing_item.setRect(r.x(), r.y(), w, h)
                else:
                    w = max(10.0, r.width() + dx)
                    h = max(10.0, r.height() + dy)
                    self.resizing_item.setRect(r.x(), r.y(), w, h)
            elif isinstance(self.resizing_item, QGraphicsTextItem):
                new_sz = max(6, min(120, int(self.resize_start_font_size + dy * 0.2)))
                font = self.resizing_item.font()
                font.setPointSize(new_sz)
                self.resizing_item.setFont(font)
            elif isinstance(self.resizing_item, QGraphicsPixmapItem):
                w_orig = self.resizing_item.pixmap().width()
                if w_orig > 0:
                    new_scale = max(0.05, self.resize_start_scale * (1.0 + dx / (w_orig * self.resize_start_scale)))
                    self.resizing_item.setScale(new_scale)
            elif isinstance(self.resizing_item, QGraphicsPathItem):
                new_scale = max(0.05, self.resize_start_scale * (1.0 + dx / 100.0))
                self.resizing_item.setScale(new_scale)
                
            # Trigger path updates on connection lines
            for item in self.scene().items():
                if hasattr(item, "type_name") and item.type_name == "connection_line":
                    item.update_path()
            event.accept()
            return
            
        # 3. Handle hover cursor changes
        if self.drawing_mode == "select" and self.dragMode() == QGraphicsView.RubberBandDrag:
            hover_resize = False
            for item in self.scene().selectedItems():
                if hasattr(item, "type_name") and item.type_name == "connection_line":
                    p1 = item.start_item.sceneBoundingRect().center() if item.start_item else item.start_pt
                    p2 = item.end_item.sceneBoundingRect().center() if item.end_item else item.end_pt
                    if (not item.start_item and math.hypot(scene_pos.x() - p1.x(), scene_pos.y() - p1.y()) < 15) or \
                       (not item.end_item and math.hypot(scene_pos.x() - p2.x(), scene_pos.y() - p2.y()) < 15):
                        hover_resize = True
                        break
            if not hover_resize:
                for item in self.scene().selectedItems():
                    if item.zValue() >= 0:
                        rect = item.sceneBoundingRect()
                        br = rect.bottomRight()
                        if math.hypot(scene_pos.x() - br.x(), scene_pos.y() - br.y()) < 15:
                            hover_resize = True
                            break
            if hover_resize:
                self.viewport().setCursor(Qt.SizeFDiagCursor)
            else:
                self.viewport().setCursor(Qt.ArrowCursor)

        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            super().mouseMoveEvent(event)
            return
            
        if self.drawing_mode in ("pen", "marker", "highlighter") and self.current_path_item:
            path = self.current_path_item.path()
            path.lineTo(scene_pos)
            self.current_path_item.setPath(path)
            
        elif self.drawing_mode in ("rect", "circle", "line", "arrow") and self.preview_shape_item:
            self.update_preview_shape(scene_pos)
            
        elif self.drawing_mode == "eraser" and event.buttons() & Qt.LeftButton:
            self.erase_at(scene_pos)
            
        else:
            super().mouseMoveEvent(event)
            
        for item in self.scene().items():
            if isinstance(item, ConnectionLineItem):
                item.update_path()

    def mouseReleaseEvent(self, event):
        if self.resizing_item or self.resizing_line:
            if self.resizing_item and getattr(self, "resizing_item_had_movable", False):
                self.resizing_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            if self.resizing_line and getattr(self, "resizing_line_had_movable", False):
                self.resizing_line.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.resizing_item = None
            self.resizing_line = None
            self.viewport().setCursor(Qt.ArrowCursor)
            event.accept()
            return
            
        scene_pos = self.mapToScene(event.pos())
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.RubberBandDrag if self.drawing_mode == "select" else QGraphicsView.NoDrag)
            super().mouseReleaseEvent(event)
            return

        if self.drawing_mode in ("pen", "marker", "highlighter"):
            if self.current_path_item:
                self.current_path_item.setFlag(QGraphicsItem.ItemIsSelectable)
                self.current_path_item = None
                if hasattr(self.parent(), "save_undo_state"):
                    self.parent().save_undo_state()
        elif self.drawing_mode in ("rect", "circle", "line", "arrow") and self.preview_shape_item:
            if self.drawing_mode in ("line", "arrow"):
                self.scene().removeItem(self.preview_shape_item)
                
                end_item = None
                released_items = self.scene().items(scene_pos)
                for item in released_items:
                    if hasattr(item, "type_name") and item.type_name in ("cs_block", "sticky_note", "stack_container"):
                        if item != self.start_item:
                            end_item = item
                            break
                              
                is_arrow = (self.drawing_mode == "arrow")
                conn = ConnectionLineItem(self.start_point, scene_pos, self.start_item, end_item, is_arrow=is_arrow, color=self.current_color, width=self.current_pen_width)
                self.scene().addItem(conn)
                self.preview_shape_item = None
            else:
                self.preview_shape_item.setFlag(QGraphicsItem.ItemIsSelectable)
                self.preview_shape_item.setFlag(QGraphicsItem.ItemIsMovable)
                self.preview_shape_item = None
                
            if hasattr(self.parent(), "save_undo_state"):
                self.parent().save_undo_state()
        else:
            super().mouseReleaseEvent(event)
            if self.drawing_mode == "select" and event.button() == Qt.LeftButton:
                if hasattr(self.parent(), "save_undo_state"):
                    self.parent().save_undo_state()

    def wheelEvent(self, event):
        # Scale selected items with Shift + Wheel
        if event.modifiers() == Qt.ShiftModifier:
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            for item in self.scene().selectedItems():
                if hasattr(item, "type_name") and item.type_name == "connection_line":
                    item.width = max(1, min(30, item.width * factor))
                    item.setPen(QPen(item.color, item.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.update_path()
                elif isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)):
                    r = item.rect()
                    if hasattr(item, "type_name") and item.type_name in ("cs_block", "sticky_note"):
                        w = max(20.0, r.width() * factor)
                        h = max(15.0, r.height() * factor)
                        item.setRect(-w/2, -h/2, w, h)
                    else:
                        w = max(10.0, r.width() * factor)
                        h = max(10.0, r.height() * factor)
                        item.setRect(r.x(), r.y(), w, h)
                elif isinstance(item, QGraphicsTextItem):
                    font = item.font()
                    sz = max(6, min(120, int(font.pointSize() * factor)))
                    font.setPointSize(sz)
                    item.setFont(font)
                elif isinstance(item, QGraphicsPixmapItem):
                    item.setScale(item.scale() * factor)
                elif isinstance(item, QGraphicsPathItem):
                    item.setScale(item.scale() * factor)
            # Update paths for connection lines
            for item in self.scene().items():
                if hasattr(item, "type_name") and item.type_name == "connection_line":
                    item.update_path()
            if hasattr(self.parent(), "save_undo_state"):
                self.parent().save_undo_state()
            event.accept()
            return

        # Zoom support
        factor = 1.15 if event.angleDelta().y() > 0 else 0.85
        self.scale(factor, factor)

    def update_preview_shape(self, end_point):
        if not self.preview_shape_item:
            return
        rect = QRectF(self.start_point, end_point).normalized()
        
        if self.drawing_mode == "rect":
            self.preview_shape_item.setRect(rect)
        elif self.drawing_mode == "circle":
            self.preview_shape_item.setRect(rect)
        elif self.drawing_mode == "line":
            path = QPainterPath()
            path.moveTo(self.start_point)
            path.lineTo(end_point)
            self.preview_shape_item.setPath(path)
        elif self.drawing_mode == "arrow":
            path = QPainterPath()
            path.moveTo(self.start_point)
            path.lineTo(end_point)
            
            dx = end_point.x() - self.start_point.x()
            dy = end_point.y() - self.start_point.y()
            angle = math.atan2(dy, dx)
            
            arrow_size = 12
            ap1 = end_point - QPointF(arrow_size * math.cos(angle - math.pi/6), arrow_size * math.sin(angle - math.pi/6))
            ap2 = end_point - QPointF(arrow_size * math.cos(angle + math.pi/6), arrow_size * math.sin(angle + math.pi/6))
            
            path.moveTo(end_point)
            path.lineTo(ap1)
            path.lineTo(ap2)
            path.closeSubpath()
            self.preview_shape_item.setPath(path)

    def remove_item_safely(self, item):
        if hasattr(self.parent(), "remove_item_safely"):
            self.parent().remove_item_safely(item)
        else:
            try:
                self.scene().removeItem(item)
            except Exception:
                pass

    def erase_at(self, pos):
        erase_rect = QRectF(pos.x() - 15, pos.y() - 15, 30, 30)
        items = self.scene().items(erase_rect)
        for item in list(items):
            if item != self.current_path_item and item != self.preview_shape_item:
                self.remove_item_safely(item)

    def keyPressEvent(self, event):
        # Clipboard paste support (Ctrl+V)
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            if mime_data.hasImage():
                pixmap = clipboard.pixmap()
                if not pixmap.isNull():
                    if hasattr(self.parent(), "save_undo_state"):
                        self.parent().save_undo_state()
                    item = QGraphicsPixmapItem(pixmap)
                    center = self.mapToScene(self.viewport().rect().center())
                    item.setPos(center.x() - pixmap.width() / 2, center.y() - pixmap.height() / 2)
                    item.setFlag(QGraphicsItem.ItemIsMovable)
                    item.setFlag(QGraphicsItem.ItemIsSelectable)
                    item.type_name = "pixmap"
                    self.scene().addItem(item)
                    event.accept()
                    return

        # Keyboard shortcuts - Delete selected items
        if event.key() == Qt.Key_Delete:
            for item in list(self.scene().selectedItems()):
                self.remove_item_safely(item)
        else:
            super().keyPressEvent(event)


class WhiteboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        
        # Physics timer (60 FPS)
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self.run_physics_tick)
        self.physics_enabled = False
        
        # Undo/Redo checkpoint stacks
        self.undo_stack = []
        self.redo_stack = []
        self.is_undoing_redoing = False
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. MAIN TOOLBAR WIDGET
        self.toolbar_widget = QWidget()
        self.toolbar_widget.setObjectName("WhiteboardToolbar")
        self.toolbar_widget.setFixedHeight(48)
        toolbar = QHBoxLayout(self.toolbar_widget)
        toolbar.setContentsMargins(10, 0, 10, 0)
        toolbar.setSpacing(6)
        
        # Modes Button Group
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        modes = [
            ("select", "Select", "view_2d"),
            ("pen", "Pen", "pen"),
            ("marker", "Marker", "marker"),
            ("highlighter", "Highlight", "highlighter"),
            ("eraser", "Eraser", "eraser"),
            ("text", "Text", "text_tool"),
            ("rect", "Rect", "rect_tool"),
            ("circle", "Circle", "circle_tool"),
            ("line", "Line", "line_tool"),
            ("arrow", "Arrow", "arrow_tool")
        ]
        
        for mode_id, text, icon_name in modes:
            btn = QPushButton(f" {text}")
            btn.setIcon(VectorIconProvider.get_icon(icon_name, "#007acc"))
            btn.setCheckable(True)
            if mode_id == "select":
                btn.setChecked(True)
                
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #555555;
                    border: 1px solid transparent;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(0, 122, 204, 0.1);
                    color: #007acc;
                }
                QPushButton:checked {
                    background-color: #007acc;
                    color: white;
                    border: 1px solid #005995;
                }
            """)
            self.btn_group.addButton(btn)
            toolbar.addWidget(btn)
            
            def make_slot(m):
                return lambda: self.view.set_drawing_mode(m)
            btn.clicked.connect(make_slot(mode_id))
            
        # Color picker button
        self.btn_color = QPushButton()
        self.btn_color.setToolTip("Pick drawing color")
        self.btn_color.setStyleSheet("background-color: black; border-radius: 4px; border: 1px solid #ccc; width: 32px; height: 24px;")
        self.btn_color.clicked.connect(self.choose_color)
        toolbar.addWidget(self.btn_color)
        
        toolbar.addSpacing(10)
        
        # Undo/Redo Buttons
        self.btn_undo = QPushButton(" Undo")
        self.btn_undo.setIcon(VectorIconProvider.get_icon("step_backward", "#555555", 14))
        self.btn_undo.setStyleSheet("""
            QPushButton { background-color: transparent; color: #555555; border: none; padding: 4px 8px; font-size: 11px; }
            QPushButton:hover { background-color: rgba(0,0,0,0.05); border-radius: 4px; }
        """)
        self.btn_undo.clicked.connect(self.undo)
        
        self.btn_redo = QPushButton(" Redo")
        self.btn_redo.setIcon(VectorIconProvider.get_icon("step_forward", "#555555", 14))
        self.btn_redo.setStyleSheet("""
            QPushButton { background-color: transparent; color: #555555; border: none; padding: 4px 8px; font-size: 11px; }
            QPushButton:hover { background-color: rgba(0,0,0,0.05); border-radius: 4px; }
        """)
        self.btn_redo.clicked.connect(self.redo)
        
        toolbar.addWidget(self.btn_undo)
        toolbar.addWidget(self.btn_redo)
        
        toolbar.addSpacing(10)
        
        # Shape insertion items (keeping them on toolbar is handy!)
        cs_shapes = [
            ("block", "CS Node", "block_tool", "#007acc"),
            ("stack", "Stack Box", "stack_tool", "#007acc"),
            ("sticky", "Sticky", "sticky_tool", "#d4af37")
        ]
        for shape_id, text, icon_name, color_hex in cs_shapes:
            btn = QPushButton(f" {text}")
            btn.setIcon(VectorIconProvider.get_icon(icon_name, color_hex))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {color_hex};
                    border: 1px solid transparent;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 122, 204, 0.1);
                    border: 1px solid {color_hex};
                }}
            """)
            def make_cs_slot(s):
                return lambda: self.add_cs_item(s)
            btn.clicked.connect(make_cs_slot(shape_id))
            toolbar.addWidget(btn)
            
        toolbar.addStretch()
        
        # Collapsible Settings Drawer Toggle Button
        self.btn_drawer_toggle = QPushButton(" Options Drawer")
        self.btn_drawer_toggle.setIcon(VectorIconProvider.get_icon("folder", "#007acc", 16))
        self.btn_drawer_toggle.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: 1px solid #005995;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        self.btn_drawer_toggle.clicked.connect(self.toggle_drawer)
        toolbar.addWidget(self.btn_drawer_toggle)
        
        layout.addWidget(self.toolbar_widget)
        
        # 2. MAIN CONTENT AREA (View + Drawer)
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # View
        self.view = WhiteboardView(self.scene, self)
        content_layout.addWidget(self.view, 1)
        
        # Collapsible Drawer
        self.drawer = QWidget()
        self.drawer.setObjectName("WhiteboardDrawer")
        self.drawer.setFixedWidth(230)
        self.drawer.setHidden(True)
        
        drawer_layout = QVBoxLayout(self.drawer)
        drawer_layout.setContentsMargins(15, 15, 15, 15)
        drawer_layout.setSpacing(14)
        
        # Title
        lbl_drawer_title = QLabel("WHITEBOARD SETTINGS")
        lbl_drawer_title.setStyleSheet("font-weight: bold; font-size: 10px; color: #858585; letter-spacing: 1px;")
        drawer_layout.addWidget(lbl_drawer_title)
        
        # Theme Button
        self.btn_theme = QPushButton(" Whiteboard Theme: LIGHT")
        self.btn_theme.setIcon(VectorIconProvider.get_icon("whiteboard", "#007acc"))
        self.btn_theme.clicked.connect(self.toggle_theme)
        drawer_layout.addWidget(self.btn_theme)
        
        # Physics Button
        self.btn_physics = QPushButton(" Physics: OFF")
        self.btn_physics.setCheckable(True)
        self.btn_physics.setIcon(VectorIconProvider.get_icon("view_3d", "#007acc"))
        self.btn_physics.clicked.connect(self.toggle_physics_state)
        drawer_layout.addWidget(self.btn_physics)
        
        # Brush Size Slider Layout
        size_layout = QVBoxLayout()
        size_layout.setSpacing(4)
        lbl_size = QLabel("Brush Size:")
        lbl_size.setStyleSheet("font-size: 11px;")
        
        self.slider_size = QSlider(Qt.Horizontal)
        self.slider_size.setRange(2, 25)
        self.slider_size.setValue(3)
        self.slider_size.valueChanged.connect(self.change_brush_size)
        
        size_layout.addWidget(lbl_size)
        size_layout.addWidget(self.slider_size)
        drawer_layout.addLayout(size_layout)
        
        drawer_layout.addSpacing(5)
        
        # Actions section divider
        lbl_actions = QLabel("BOARD ACTIONS")
        lbl_actions.setStyleSheet("font-weight: bold; font-size: 10px; color: #858585; letter-spacing: 1px; margin-top: 10px;")
        drawer_layout.addWidget(lbl_actions)
        
        # Import Screenshot / Image file
        self.btn_import_img = QPushButton(" Import Image File")
        self.btn_import_img.setIcon(VectorIconProvider.get_icon("folder", "#007acc"))
        self.btn_import_img.clicked.connect(self.import_image_dialog)
        drawer_layout.addWidget(self.btn_import_img)
        
        # Save Board
        self.btn_save = QPushButton(" Save Board (.dsa-wb)")
        self.btn_save.setIcon(VectorIconProvider.get_icon("pptx", "#4ec9b0"))
        self.btn_save.clicked.connect(self.save_board_dialog)
        drawer_layout.addWidget(self.btn_save)
        
        # Load Board
        self.btn_load = QPushButton(" Load Board (.dsa-wb)")
        self.btn_load.setIcon(VectorIconProvider.get_icon("folder", "#007acc"))
        self.btn_load.clicked.connect(self.load_board_dialog)
        drawer_layout.addWidget(self.btn_load)
        
        # Clear All
        self.btn_clear = QPushButton(" Clear Canvas")
        self.btn_clear.setIcon(VectorIconProvider.get_icon("clear", "#ff5555"))
        self.btn_clear.clicked.connect(lambda: self.clear_whiteboard(force=False))
        drawer_layout.addWidget(self.btn_clear)
        
        drawer_layout.addStretch()
        content_layout.addWidget(self.drawer)
        
        layout.addWidget(content_widget, 1)
        
        # Apply theme stylesheet (defaults to LIGHT)
        self.apply_whiteboard_theme("light")

    def toggle_drawer(self):
        self.drawer.setHidden(not self.drawer.isHidden())

    def toggle_theme(self):
        if self.view.bg_theme == "light":
            self.apply_whiteboard_theme("dark")
        else:
            self.apply_whiteboard_theme("light")

    def apply_whiteboard_theme(self, theme):
        self.view.bg_theme = theme
        if theme == "light":
            self.btn_theme.setText(" Whiteboard Theme: LIGHT")
            self.drawer.setStyleSheet("""
                QWidget#WhiteboardDrawer {
                    background-color: #f5f5f5;
                    border-left: 1px solid #cccccc;
                }
                QLabel {
                    color: #333333;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
            self.toolbar_widget.setStyleSheet("background-color: #f5f5f5; border-bottom: 1px solid #cccccc;")
        else:
            self.btn_theme.setText(" Whiteboard Theme: DARK")
            self.drawer.setStyleSheet("""
                QWidget#WhiteboardDrawer {
                    background-color: #252526;
                    border-left: 1px solid #3c3c3c;
                }
                QLabel {
                    color: #cccccc;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #333333;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)
            self.toolbar_widget.setStyleSheet("background-color: #252526; border-bottom: 1px solid #3c3c3c;")
            
        # Ensure readability: Convert pure black items to white in dark mode, and vice-versa
        for item in self.scene.items():
            if isinstance(item, QGraphicsTextItem):
                col = item.defaultTextColor()
                if theme == "dark" and (col == Qt.black or col.name() == "#000000"):
                    item.setDefaultTextColor(Qt.white)
                elif theme == "light" and (col == Qt.white or col.name() == "#ffffff"):
                    item.setDefaultTextColor(Qt.black)
            elif isinstance(item, ConnectionLineItem):
                col = item.color
                if theme == "dark" and (col == Qt.black or col == QColor("#000000")):
                    item.color = Qt.white
                    item.setPen(QPen(Qt.white, item.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.update_path()
                elif theme == "light" and (col == Qt.white or col == QColor("#ffffff")):
                    item.color = Qt.black
                    item.setPen(QPen(Qt.black, item.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.update_path()
            elif isinstance(item, QGraphicsPathItem):
                pen = item.pen()
                col = pen.color()
                if theme == "dark" and (col == Qt.black or col.name() == "#000000"):
                    pen.setColor(Qt.white)
                    item.setPen(pen)
                elif theme == "light" and (col == Qt.white or col.name() == "#ffffff"):
                    pen.setColor(Qt.black)
                    item.setPen(pen)
            elif isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)) and not hasattr(item, "type_name"):
                pen = item.pen()
                col = pen.color()
                if theme == "dark" and (col == Qt.black or col.name() == "#000000"):
                    pen.setColor(Qt.white)
                    item.setPen(pen)
                elif theme == "light" and (col == Qt.white or col.name() == "#ffffff"):
                    pen.setColor(Qt.black)
                    item.setPen(pen)
                    
        self.view.viewport().update()

    def toggle_physics_state(self):
        enabled = self.btn_physics.isChecked()
        self.toggle_physics(enabled)

    def import_image_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.save_undo_state()
                item = QGraphicsPixmapItem(pixmap)
                center = self.view.mapToScene(self.view.viewport().rect().center())
                item.setPos(center.x() - pixmap.width() / 2, center.y() - pixmap.height() / 2)
                item.setFlag(QGraphicsItem.ItemIsMovable)
                item.setFlag(QGraphicsItem.ItemIsSelectable)
                item.type_name = "pixmap"
                self.scene.addItem(item)

    def choose_color(self):
        color = QColorDialog.getColor(self.view.current_color, self, "Pick Drawing Color")
        if color.isValid():
            self.view.current_color = color
            self.btn_color.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px; border: 1px solid #ccc; width: 40px;")

    def change_brush_size(self, val):
        self.view.current_pen_width = val

    def add_cs_item(self, item_type):
        center = self.view.mapToScene(self.view.viewport().rect().center())
        
        if item_type == "block":
            text, ok = QInputDialog.getText(self, "Add Node", "Node value:", text="10")
            val = text if (ok and text) else "10"
            item = CSBlockItem(center.x(), center.y(), val_str=val, is_node=True)
            self.scene.addItem(item)
        elif item_type == "stack":
            item = GravityStackItem(center.x() - 60, center.y() - 100, 120, 200)
            self.scene.addItem(item)
        elif item_type == "sticky":
            text, ok = QInputDialog.getMultiLineText(self, "Add Sticky", "Sticky text:", "Write note...")
            val = text if ok else "Write note..."
            item = StickyNoteItem(center.x(), center.y(), text_str=val)
            self.scene.addItem(item)

    def serialize_board(self):
        def serialize_pen(pen):
            return {
                "color": pen.color().name(QColor.HexArgb),
                "width": pen.widthF(),
                "style": int(pen.style())
            }

        def serialize_brush(brush):
            return {
                "color": brush.color().name(QColor.HexArgb),
                "style": int(brush.style())
            }

        def serialize_path(path):
            elements = []
            for i in range(path.elementCount()):
                el = path.elementAt(i)
                t = 0
                if str(el.type).endswith("LineToElement") or int(el.type) == 1:
                    t = 1
                elif str(el.type).endswith("CurveToElement") or int(el.type) == 2:
                    t = 2
                elif str(el.type).endswith("CurveToDataElement") or int(el.type) == 3:
                    t = 3
                elements.append((t, el.x, el.y))
            return elements

        items_data = []
        for item in self.scene.items():
            if item.zValue() == -10:  # Skip background grid lines
                continue
                
            data = {}
            data["id"] = str(id(item))
            
            if hasattr(item, "type_name"):
                data["type"] = item.type_name
                data["x"] = item.x()
                data["y"] = item.y()
                if item.type_name == "cs_block":
                    data["val"] = item.val_str
                    data["is_node"] = item.is_node
                elif item.type_name == "sticky_note":
                    data["text"] = item.text_str
                elif item.type_name == "stack_container":
                    r = item.rect()
                    data["rect"] = [r.x(), r.y(), r.width(), r.height()]
                elif item.type_name == "connection_line":
                    data["start_item_id"] = str(id(item.start_item)) if item.start_item else None
                    data["end_item_id"] = str(id(item.end_item)) if item.end_item else None
                    data["start_pt"] = [item.start_pt.x(), item.start_pt.y()]
                    data["end_pt"] = [item.end_pt.x(), item.end_pt.y()]
                    data["is_arrow"] = item.is_arrow
                    data["color"] = item.color.name(QColor.HexArgb) if isinstance(item.color, QColor) else str(item.color)
                    data["width"] = item.width
                elif item.type_name == "pixmap":
                    pixmap = item.pixmap()
                    ba = QByteArray()
                    buf = QBuffer(ba)
                    buf.open(QIODevice.WriteOnly)
                    pixmap.save(buf, "PNG")
                    data["image_data"] = ba.toBase64().data().decode("utf-8")
            elif isinstance(item, QGraphicsPixmapItem):
                data["type"] = "pixmap"
                data["x"] = item.x()
                data["y"] = item.y()
                pixmap = item.pixmap()
                ba = QByteArray()
                buf = QBuffer(ba)
                buf.open(QIODevice.WriteOnly)
                pixmap.save(buf, "PNG")
                data["image_data"] = ba.toBase64().data().decode("utf-8")
            elif isinstance(item, QGraphicsPathItem):
                data["type"] = "path"
                data["x"] = item.x()
                data["y"] = item.y()
                data["pen"] = serialize_pen(item.pen())
                data["brush"] = serialize_brush(item.brush())
                data["path_elements"] = serialize_path(item.path())
            elif isinstance(item, QGraphicsRectItem):
                data["type"] = "rect"
                data["x"] = item.x()
                data["y"] = item.y()
                r = item.rect()
                data["rect"] = [r.x(), r.y(), r.width(), r.height()]
                data["pen"] = serialize_pen(item.pen())
                data["brush"] = serialize_brush(item.brush())
            elif isinstance(item, QGraphicsEllipseItem):
                data["type"] = "circle"
                data["x"] = item.x()
                data["y"] = item.y()
                r = item.rect()
                data["rect"] = [r.x(), r.y(), r.width(), r.height()]
                data["pen"] = serialize_pen(item.pen())
                data["brush"] = serialize_brush(item.brush())
            elif isinstance(item, QGraphicsTextItem):
                data["type"] = "text"
                data["x"] = item.x()
                data["y"] = item.y()
                data["text"] = item.toPlainText()
                data["color"] = item.defaultTextColor().name()
                data["font_size"] = item.font().pointSize()
                data["font_family"] = item.font().family()
                
            if data:
                items_data.append(data)
        return items_data

    def deserialize_board(self, items_data):
        self.clear_whiteboard()
        id_to_item_map = {}
        connection_items_data = []
        
        for item_data in items_data:
            i_type = item_data.get("type")
            item_id = item_data.get("id")
            x = item_data.get("x", 0.0)
            y = item_data.get("y", 0.0)
            
            if i_type == "connection_line":
                connection_items_data.append(item_data)
                continue
                
            item = None
            if i_type == "cs_block":
                val = item_data.get("val", "10")
                is_node = item_data.get("is_node", False)
                item = CSBlockItem(x, y, val_str=val, is_node=is_node)
                self.scene.addItem(item)
            elif i_type == "sticky_note":
                text = item_data.get("text", "")
                item = StickyNoteItem(x, y, text_str=text)
                self.scene.addItem(item)
            elif i_type == "stack_container":
                r_list = item_data.get("rect", [0, 0, 120, 200])
                item = GravityStackItem(r_list[0], r_list[1], r_list[2], r_list[3])
                item.setPos(x, y)
                self.scene.addItem(item)
            elif i_type == "pixmap":
                img_base64 = item_data.get("image_data", "")
                if img_base64:
                    ba = QByteArray.fromBase64(img_base64.encode("utf-8"))
                    img = QImage.fromData(ba)
                    pixmap = QPixmap.fromImage(img)
                    item = QGraphicsPixmapItem(pixmap)
                    item.setPos(x, y)
                    item.setFlag(QGraphicsItem.ItemIsMovable)
                    item.setFlag(QGraphicsItem.ItemIsSelectable)
                    item.type_name = "pixmap"
                    self.scene.addItem(item)
            elif i_type == "path":
                item = QGraphicsPathItem()
                item.setPos(x, y)
                
                path_elements = item_data.get("path_elements", [])
                path = QPainterPath()
                for t, px, py in path_elements:
                    if t == 0:
                        path.moveTo(px, py)
                    elif t == 1:
                        path.lineTo(px, py)
                item.setPath(path)
                
                pen_data = item_data.get("pen", {})
                pen = QPen(QColor(pen_data.get("color", "#000000")), pen_data.get("width", 3))
                pen.setStyle(Qt.PenStyle(pen_data.get("style", 1)))
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                item.setPen(pen)
                
                brush_data = item_data.get("brush", {})
                brush = QBrush(QColor(brush_data.get("color", "#000000")))
                brush.setStyle(Qt.BrushStyle(brush_data.get("style", 0)))
                item.setBrush(brush)
                
                item.setFlag(QGraphicsItem.ItemIsSelectable)
                item.setFlag(QGraphicsItem.ItemIsMovable)
                self.scene.addItem(item)
            elif i_type in ("rect", "circle"):
                r_list = item_data.get("rect", [0, 0, 100, 100])
                if i_type == "rect":
                    item = QGraphicsRectItem(r_list[0], r_list[1], r_list[2], r_list[3])
                else:
                    item = QGraphicsEllipseItem(r_list[0], r_list[1], r_list[2], r_list[3])
                item.setPos(x, y)
                
                pen_data = item_data.get("pen", {})
                pen = QPen(QColor(pen_data.get("color", "#000000")), pen_data.get("width", 2))
                pen.setStyle(Qt.PenStyle(pen_data.get("style", 1)))
                item.setPen(pen)
                
                brush_data = item_data.get("brush", {})
                brush = QBrush(QColor(brush_data.get("color", "#000000")))
                brush.setStyle(Qt.BrushStyle(brush_data.get("style", 0)))
                item.setBrush(brush)
                
                item.setFlag(QGraphicsItem.ItemIsSelectable)
                item.setFlag(QGraphicsItem.ItemIsMovable)
                self.scene.addItem(item)
            elif i_type == "text":
                text = item_data.get("text", "")
                item = QGraphicsTextItem(text)
                item.setPos(x, y)
                item.setDefaultTextColor(QColor(item_data.get("color", "#000000")))
                font = QFont(item_data.get("font_family", "Arial"), item_data.get("font_size", 14))
                item.setFont(font)
                item.setFlag(QGraphicsItem.ItemIsSelectable)
                item.setFlag(QGraphicsItem.ItemIsMovable)
                item.setTextInteractionFlags(Qt.TextEditorInteraction)
                self.scene.addItem(item)
                
            if item and item_id:
                id_to_item_map[item_id] = item
                
        for conn_data in connection_items_data:
            start_item_id = conn_data.get("start_item_id")
            end_item_id = conn_data.get("end_item_id")
            start_pt_arr = conn_data.get("start_pt", [0, 0])
            end_pt_arr = conn_data.get("end_pt", [0, 0])
            is_arrow = conn_data.get("is_arrow", False)
            color_hex = conn_data.get("color", "#000000")
            width = conn_data.get("width", 3)
            
            start_item = id_to_item_map.get(start_item_id) if start_item_id else None
            end_item = id_to_item_map.get(end_item_id) if end_item_id else None
            start_pt = QPointF(start_pt_arr[0], start_pt_arr[1])
            end_pt = QPointF(end_pt_arr[0], end_pt_arr[1])
            
            conn = ConnectionLineItem(start_pt, end_pt, start_item, end_item, is_arrow=is_arrow, color=QColor(color_hex), width=width)
            self.scene.addItem(conn)

    def save_board_dialog(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Whiteboard", "", "DSA Whiteboard (*.dsa-wb)")
        if path:
            try:
                data = self.serialize_board()
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save whiteboard:\n{e}")

    def load_board_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Whiteboard", "", "DSA Whiteboard (*.dsa-wb)")
        if path:
            self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.deserialize_board(data)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Could not load whiteboard:\n{e}")

    def remove_item_safely(self, item):
        # Remove connection lines first if this is a shape
        if hasattr(item, "type_name") and item.type_name in ("cs_block", "sticky_note", "stack_container"):
            conns_to_remove = []
            for other in list(self.scene.items()):
                if hasattr(other, "type_name") and other.type_name == "connection_line":
                    if other.start_item == item or other.end_item == item:
                        conns_to_remove.append(other)
            for conn in conns_to_remove:
                try:
                    conn.start_item = None
                    conn.end_item = None
                    self.scene.removeItem(conn)
                except Exception:
                    pass
        try:
            self.scene.removeItem(item)
        except Exception:
            pass

    def clear_whiteboard(self, force=False):
        if not force:
            reply = QMessageBox.question(
                self, "Confirm Clear", 
                "Are you sure you want to clear the whiteboard canvas?", 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        self.save_undo_state()
        self.scene.clearSelection()
        
        # Remove connection lines first to avoid dangling references
        for item in list(self.scene.items()):
            if hasattr(item, "type_name") and item.type_name == "connection_line":
                try:
                    item.start_item = None
                    item.end_item = None
                    self.scene.removeItem(item)
                except Exception:
                    pass
                    
        # Now remove everything else safely
        for item in list(self.scene.items()):
            try:
                self.scene.removeItem(item)
            except Exception:
                pass

    def save_undo_state(self):
        if self.is_undoing_redoing:
            return
        state = self.serialize_board()
        self.undo_stack.append(state)
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        self.is_undoing_redoing = True
        self.redo_stack.append(self.serialize_board())
        prev_state = self.undo_stack.pop()
        self.deserialize_board(prev_state)
        self.is_undoing_redoing = False

    def redo(self):
        if not self.redo_stack:
            return
        self.is_undoing_redoing = True
        self.undo_stack.append(self.serialize_board())
        next_state = self.redo_stack.pop()
        self.deserialize_board(next_state)
        self.is_undoing_redoing = False

    def toggle_physics(self, enabled):
        self.physics_enabled = enabled
        if enabled:
            self.physics_timer.start(16)
            self.btn_physics.setText(" Physics: ON")
            for item in self.scene.items():
                if isinstance(item, CSBlockItem):
                    item.velocity_y = 0.0
        else:
            self.physics_timer.stop()
            self.btn_physics.setText(" Physics: OFF")

    def run_physics_tick(self):
        buckets = []
        blocks = []
        for item in self.scene.items():
            if isinstance(item, GravityStackItem):
                buckets.append(item)
            elif isinstance(item, CSBlockItem):
                blocks.append(item)
                
        for block in blocks:
            if block.isSelected() and self.view.drawing_mode == "select":
                continue
                
            pos = block.scenePos()
            target_bucket = None
            for b in buckets:
                b_rect = b.sceneBoundingRect()
                if pos.x() >= b_rect.left() and pos.x() <= b_rect.right():
                    if pos.y() <= b_rect.bottom():
                        target_bucket = b
                        break
                        
            if target_bucket:
                b_rect = target_bucket.sceneBoundingRect()
                block.velocity_y += 0.8
                new_y = pos.y() + block.velocity_y
                
                bottom_limit = b_rect.bottom() - 20
                closest_node_y = bottom_limit
                for other in blocks:
                    if other == block: continue
                    other_pos = other.scenePos()
                    if abs(other_pos.x() - pos.x()) < 50:
                        if other_pos.y() > pos.y() and other_pos.y() - 40 < closest_node_y:
                            closest_node_y = other_pos.y() - 40
                            
                if new_y >= closest_node_y:
                    block.setPos(pos.x(), closest_node_y)
                    block.velocity_y = 0
                else:
                    block.setPos(pos.x(), new_y)
            else:
                block.velocity_y = 0.0

        # Repel overlapping nodes
        for i, b1 in enumerate(blocks):
            p1 = b1.scenePos()
            for j in range(i + 1, len(blocks)):
                b2 = blocks[j]
                p2 = b2.scenePos()
                dx = p2.x() - p1.x()
                dy = p2.y() - p1.y()
                dist = math.hypot(dx, dy)
                if dist < 80:
                    angle = math.atan2(dy, dx)
                    force = (80 - dist) * 0.1
                    if not b1.isSelected():
                        b1.setPos(p1.x() - force * math.cos(angle), p1.y() - force * math.sin(angle))
                    if not b2.isSelected():
                        b2.setPos(p2.x() + force * math.cos(angle), p2.y() + force * math.sin(angle))

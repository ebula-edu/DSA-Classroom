from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QPointF, QRectF

class VectorIconProvider:
    @staticmethod
    def get_icon(name, color_hex="#d4d4d4", size=32):
        """
        Paints a vector path onto a transparent QPixmap and returns it as a QIcon.
        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(color_hex)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        
        # Center coordinates
        c = size / 2.0
        scale = size / 32.0 # Design coordinate system is 32x32
        
        # Scale all painter calls
        painter.scale(scale, scale)
        
        path = QPainterPath()
        
        if name == "play":
            path.moveTo(9, 6)
            path.lineTo(25, 16)
            path.lineTo(9, 26)
            path.closeSubpath()
            painter.drawPath(path)
            
        elif name == "pause":
            path.addRect(8, 6, 5, 20)
            path.addRect(19, 6, 5, 20)
            painter.drawPath(path)
            
        elif name == "step_forward":
            path.moveTo(6, 6)
            path.lineTo(20, 16)
            path.lineTo(6, 26)
            path.closeSubpath()
            path.addRect(22, 6, 4, 20)
            painter.drawPath(path)
            
        elif name == "step_backward":
            path.moveTo(26, 6)
            path.lineTo(12, 16)
            path.lineTo(26, 26)
            path.closeSubpath()
            path.addRect(6, 6, 4, 20)
            painter.drawPath(path)
            
        elif name == "folder":
            # Draw folder outline shape
            path.moveTo(4, 6)
            path.lineTo(12, 6)
            path.lineTo(15, 10)
            path.lineTo(28, 10)
            path.lineTo(28, 26)
            path.lineTo(4, 26)
            path.closeSubpath()
            
            # Inner hollow cut-out for outline look
            inner = QPainterPath()
            inner.moveTo(6, 12)
            inner.lineTo(26, 12)
            inner.lineTo(26, 24)
            inner.lineTo(6, 24)
            inner.closeSubpath()
            
            path = path.subtracted(inner)
            painter.drawPath(path)
            
        elif name == "pdf":
            # Page with a folded corner and PDF text
            path.moveTo(6, 4)
            path.lineTo(20, 4)
            path.lineTo(26, 10)
            path.lineTo(26, 28)
            path.lineTo(6, 28)
            path.closeSubpath()
            
            # Hollow inner
            inner = QPainterPath()
            inner.moveTo(8, 6)
            inner.lineTo(19, 6)
            inner.lineTo(19, 11)
            inner.lineTo(24, 11)
            inner.lineTo(24, 26)
            inner.lineTo(8, 26)
            inner.closeSubpath()
            path = path.subtracted(inner)
            painter.drawPath(path)
            
            # Draw PDF text inside
            painter.setPen(QPen(color, 1))
            painter.setFont(QFont("Arial", 6, QFont.Bold))
            painter.drawText(QRectF(9, 14, 14, 8), Qt.AlignCenter, "PDF")
            
        elif name == "pptx":
            # Slides screen icon
            path.moveTo(4, 6)
            path.lineTo(28, 6)
            path.lineTo(28, 22)
            path.lineTo(4, 22)
            path.closeSubpath()
            
            inner = QPainterPath()
            inner.addRect(6, 8, 20, 12)
            path = path.subtracted(inner)
            
            # Draw stand
            path.moveTo(14, 22)
            path.lineTo(12, 27)
            path.lineTo(20, 27)
            path.lineTo(18, 22)
            path.closeSubpath()
            
            painter.drawPath(path)
            
            # P letter inside
            painter.setPen(QPen(color, 1))
            painter.setFont(QFont("Arial", 7, QFont.Bold))
            painter.drawText(QRectF(6, 8, 20, 12), Qt.AlignCenter, "P")
            
        elif name == "docx":
            # Page icon with doc lines
            path.moveTo(6, 4)
            path.lineTo(20, 4)
            path.lineTo(26, 10)
            path.lineTo(26, 28)
            path.lineTo(6, 28)
            path.closeSubpath()
            
            inner = QPainterPath()
            inner.moveTo(8, 6)
            inner.lineTo(19, 6)
            inner.lineTo(19, 11)
            inner.lineTo(24, 11)
            inner.lineTo(24, 26)
            inner.lineTo(8, 26)
            inner.closeSubpath()
            
            path = path.subtracted(inner)
            painter.drawPath(path)
            
            # Draw Doc lines
            painter.setPen(QPen(color, 1.5))
            painter.drawLine(11, 14, 21, 14)
            painter.drawLine(11, 18, 21, 18)
            painter.drawLine(11, 22, 17, 22)
            
        elif name == "python":
            # Snake-like shapes for python
            # Top snake
            path.moveTo(16, 4)
            path.cubicTo(10, 4, 10, 8, 10, 12)
            path.lineTo(12, 12)
            path.cubicTo(12, 10, 12, 8, 16, 8)
            path.lineTo(22, 8)
            path.cubicTo(26, 8, 26, 12, 26, 12)
            path.lineTo(26, 14)
            path.cubicTo(26, 18, 22, 18, 18, 18)
            path.lineTo(16, 18)
            path.lineTo(16, 16)
            path.lineTo(10, 16)
            path.lineTo(10, 20)
            path.cubicTo(10, 26, 18, 26, 18, 26)
            path.lineTo(20, 26)
            path.cubicTo(26, 26, 28, 24, 28, 20)
            path.lineTo(28, 16)
            path.cubicTo(28, 10, 24, 4, 16, 4)
            
            # Bottom snake (mirror/rotated)
            path2 = QPainterPath()
            path2.moveTo(16, 28)
            path2.cubicTo(22, 28, 22, 24, 22, 20)
            path2.lineTo(20, 20)
            path2.cubicTo(20, 22, 20, 24, 16, 24)
            path2.lineTo(10, 24)
            path2.cubicTo(6, 24, 6, 20, 6, 20)
            path2.lineTo(6, 18)
            path2.cubicTo(6, 14, 10, 14, 14, 14)
            path2.lineTo(16, 14)
            path2.lineTo(16, 16)
            path2.lineTo(22, 16)
            path2.lineTo(22, 12)
            path2.cubicTo(22, 6, 14, 6, 14, 6)
            path2.lineTo(12, 6)
            path2.cubicTo(6, 6, 4, 8, 4, 12)
            path2.lineTo(4, 16)
            path2.cubicTo(4, 22, 8, 28, 16, 28)
            
            path.addPath(path2)
            painter.drawPath(path)
            
        elif name == "whiteboard":
            # Drawing board or paint palette outline
            path.addRoundedRect(QRectF(4, 6, 24, 20), 4, 4)
            inner = QPainterPath()
            inner.addRect(6, 8, 20, 16)
            path = path.subtracted(inner)
            
            # Add palette thumbhole or easel feet
            path.moveTo(8, 26)
            path.lineTo(6, 29)
            path.lineTo(10, 29)
            path.closeSubpath()
            
            path.moveTo(24, 26)
            path.lineTo(22, 29)
            path.lineTo(26, 29)
            path.closeSubpath()
            
            painter.drawPath(path)

        elif name == "view_2d":
            # Simple 2D square
            path.addRoundedRect(QRectF(6, 6, 20, 20), 2, 2)
            inner = QPainterPath()
            inner.addRect(8, 8, 16, 16)
            path = path.subtracted(inner)
            painter.drawPath(path)
            
        elif name == "view_3d":
            # Isometric 3D box wireframe
            painter.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
            # Projected cube lines
            # Top face
            painter.drawLine(16, 4, 26, 10)
            painter.drawLine(26, 10, 16, 16)
            painter.drawLine(16, 16, 6, 10)
            painter.drawLine(6, 10, 16, 4)
            
            # Vertical edges
            painter.drawLine(6, 10, 6, 22)
            painter.drawLine(26, 10, 26, 22)
            painter.drawLine(16, 16, 16, 28)
            
            # Bottom face
            painter.drawLine(6, 22, 16, 28)
            painter.drawLine(16, 28, 26, 22)
            
        elif name == "pen":
            # Diagonal pen path
            path.moveTo(26, 4)
            path.lineTo(28, 6)
            path.lineTo(12, 22)
            path.lineTo(8, 24)
            path.lineTo(10, 20)
            path.closeSubpath()
            painter.drawPath(path)
            
        elif name == "marker":
            # Thick marker path
            path.moveTo(24, 4)
            path.lineTo(28, 8)
            path.lineTo(16, 24)
            path.lineTo(12, 24)
            path.lineTo(12, 20)
            path.closeSubpath()
            painter.drawPath(path)
            
        elif name == "highlighter":
            # Wide tilted rectangle
            path.moveTo(22, 6)
            path.lineTo(26, 10)
            path.lineTo(14, 26)
            path.lineTo(8, 26)
            path.lineTo(8, 20)
            path.closeSubpath()
            painter.drawPath(path)
            
        elif name == "eraser":
            # Block eraser shape
            path.addRoundedRect(QRectF(6, 10, 20, 12), 2, 2)
            # Slash division for holder
            painter.drawPath(path)
            painter.setPen(QPen(QColor("#252526"), 1.5))
            painter.drawLine(14, 10, 14, 22)
            
        elif name == "text_tool":
            # Large letter T
            path.addRect(6, 6, 20, 4)
            path.addRect(14, 10, 4, 16)
            painter.drawPath(path)
            
        elif name == "rect_tool":
            path.addRect(6, 8, 20, 16)
            inner = QPainterPath()
            inner.addRect(8, 10, 16, 12)
            path = path.subtracted(inner)
            painter.drawPath(path)
            
        elif name == "circle_tool":
            path.addEllipse(QRectF(6, 6, 20, 20))
            inner = QPainterPath()
            inner.addEllipse(QRectF(8, 8, 16, 16))
            path = path.subtracted(inner)
            painter.drawPath(path)
            
        elif name == "line_tool":
            painter.setPen(QPen(color, 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(6, 26, 26, 6)
            
        elif name == "arrow_tool":
            # Arrow line
            painter.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(6, 26, 22, 10)
            # Arrow head
            path.moveTo(24, 8)
            path.lineTo(16, 8)
            path.lineTo(24, 16)
            path.closeSubpath()
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawPath(path)
            
        elif name == "sticky_tool":
            # Note sheet with folder tab
            path.moveTo(6, 6)
            path.lineTo(20, 6)
            path.lineTo(26, 12)
            path.lineTo(26, 26)
            path.lineTo(6, 26)
            path.closeSubpath()
            
            # Inner hollow cut-out
            inner = QPainterPath()
            inner.addRect(8, 8, 16, 16)
            path = path.subtracted(inner)
            painter.drawPath(path)
            
        elif name == "clear":
            # Trash can outline
            path.addRect(6, 8, 20, 2) # Top lid
            path.addRect(14, 5, 4, 3) # Handle
            path.moveTo(8, 10)
            path.lineTo(10, 28)
            path.lineTo(22, 28)
            path.lineTo(24, 10)
            path.closeSubpath()
            
            inner = QPainterPath()
            inner.addRect(10, 12, 12, 14)
            path = path.subtracted(inner)
            
            painter.drawPath(path)
            
        elif name == "block_tool":
            # Cube block
            path.addRoundedRect(QRectF(6, 6, 20, 20), 3, 3)
            inner = QPainterPath()
            inner.addRect(9, 9, 14, 14)
            path = path.subtracted(inner)
            painter.drawPath(path)
            
        elif name == "stack_tool":
            # U-shaped bucket
            path.moveTo(6, 6)
            path.lineTo(6, 26)
            path.lineTo(26, 26)
            path.lineTo(26, 6)
            path.lineTo(22, 6)
            path.lineTo(22, 22)
            path.lineTo(10, 22)
            path.lineTo(10, 6)
            path.closeSubpath()
            painter.drawPath(path)
            
        painter.end()
        return QIcon(pixmap)

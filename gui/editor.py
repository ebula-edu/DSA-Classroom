import sys
from PySide6.QtCore import QRect, QSize, Qt, QRegularExpression
from PySide6.QtGui import (QColor, QFont, QPainter, QSyntaxHighlighter,
                           QTextCharFormat, QTextFormat, QKeySequence)
from PySide6.QtWidgets import (QPlainTextEdit, QTextEdit, QWidget)

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Color palette (VS Code dark theme style)
        keyword_color = QColor("#569cd6")
        builtins_color = QColor("#4ec9b0")
        string_color = QColor("#ce9178")
        comment_color = QColor("#6a9955")
        number_color = QColor("#b5cea8")
        func_color = QColor("#dcdcaa")
        class_color = QColor("#4ec9b0")

        # Rules
        def make_format(color, bold=False, italic=False):
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            if bold:
                fmt.setFontWeight(QFont.Bold)
            if italic:
                fmt.setFontItalic(True)
            return fmt

        # Keywords
        keywords = [
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else",
            "except", "finally", "for", "from", "global", "if", "import",
            "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
            "return", "try", "while", "with", "yield"
        ]
        
        for word in keywords:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.highlighting_rules.append((pattern, make_format(keyword_color, bold=True)))

        # Builtins (common functions and data types)
        builtins = [
            "print", "len", "range", "str", "int", "float", "list", "dict", "set",
            "tuple", "min", "max", "sum", "append", "pop", "insert", "sorted",
            "abs", "enumerate", "zip", "map", "filter", "any", "all", "open"
        ]
        for word in builtins:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.highlighting_rules.append((pattern, make_format(builtins_color)))

        # Numbers
        self.highlighting_rules.append((QRegularExpression(r"\b[0-9]+\b"), make_format(number_color)))

        # Function Definitions
        self.highlighting_rules.append((QRegularExpression(r"\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)\b"), make_format(func_color)))

        # Class Definitions
        self.highlighting_rules.append((QRegularExpression(r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)\b"), make_format(class_color, bold=True)))

        # Single-line Comments
        self.highlighting_rules.append((QRegularExpression(r"#[^\n]*"), make_format(comment_color, italic=True)))

        # Strings
        self.highlighting_rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), make_format(string_color)))
        self.highlighting_rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), make_format(string_color)))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Style & Font
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Highlighter
        self.highlighter = PythonHighlighter(self.document())

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        # Dark theme styling
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }
        """)

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#282828")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))
        # Draw thin separator line
        painter.setPen(QColor("#3c3c3c"))
        painter.drawLine(event.rect().width() - 1, 0, event.rect().width() - 1, event.rect().height())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                # Right align numbers
                rect = QRect(0, top, self.line_number_area.width() - 8, self.fontMetrics().height())
                painter.drawText(rect, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def keyPressEvent(self, event):
        # Auto indent on Enter key
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            current_line = cursor.block().text()
            
            # Count leading whitespace
            indent = ""
            for char in current_line:
                if char.isspace():
                    indent += char
                else:
                    break
                    
            if current_line.endswith(':'):
                indent += "    " # Auto indent 4 spaces
                
            super().keyPressEvent(event)
            self.insertPlainText(indent)
        else:
            super().keyPressEvent(event)

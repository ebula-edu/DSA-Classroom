import os
import time
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat, QTextFormat, QIcon, QPixmap
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
                             QTextBrowser, QTextEdit, QPushButton, QSlider, QLabel, 
                             QCheckBox, QMessageBox, QFileDialog, QInputDialog, QMenu)

from gui.sidebar import ResourceExplorer
from gui.editor import CodeEditor
from gui.presentation import PresentationTab
from gui.visualizer import VisualizerWidget
from gui.whiteboard import WhiteboardWidget
from gui.icons import VectorIconProvider
from engine.execution_engine import ExecutionEngine
from engine.data_structure_parser import DataStructureParser

class ComplexityTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_custom_context_menu)
        
    def show_custom_context_menu(self, pos):
        menu = self.createStandardContextMenu(pos)
        
        # Add table editing actions if the cursor is inside a table
        cursor = self.textCursor()
        table = cursor.currentTable()
        if table:
            menu.addSeparator()
            
            act_add_row = menu.addAction("Insert Row Below")
            act_del_row = menu.addAction("Delete Current Row")
            act_add_col = menu.addAction("Insert Column Right")
            act_del_col = menu.addAction("Delete Current Column")
            
            action = menu.exec(self.mapToGlobal(pos))
            if action == act_add_row:
                cell = table.cellAt(cursor)
                row = cell.row()
                table.insertRows(row + 1, 1)
            elif action == act_del_row:
                cell = table.cellAt(cursor)
                row = cell.row()
                table.removeRows(row, 1)
            elif action == act_add_col:
                cell = table.cellAt(cursor)
                col = cell.column()
                table.insertColumns(col + 1, 1)
            elif action == act_del_col:
                cell = table.cellAt(cursor)
                col = cell.column()
                table.removeColumns(col, 1)
        else:
            menu.addSeparator()
            act_insert_table = menu.addAction("Insert New Table...")
            action = menu.exec(self.mapToGlobal(pos))
            if action == act_insert_table:
                rows, ok1 = QInputDialog.getInt(self, "Insert Table", "Number of rows:", value=3, min=1, max=100)
                cols, ok2 = QInputDialog.getInt(self, "Insert Table", "Number of columns:", value=4, min=1, max=20)
                if ok1 and ok2:
                    cursor.insertTable(rows, cols)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSA Classroom - Offline Visual Teaching Studio")
        self.resize(1280, 850)
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "dsa-classroom-logo.png")
        self.setWindowIcon(QIcon(logo_path))
        
        self.engine = ExecutionEngine()
        self.parser = DataStructureParser()
        
        # State variables
        self.timeline = []
        self.current_step_idx = -1
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.autoplay_step)
        
        self.hidden_output_mode = False
        self.hidden_variables_mode = False
        self.hidden_vars_set = set()
        
        # Countdown Timer variables (45 minutes default)
        self.class_time_remaining = 45 * 60
        self.class_timer = QTimer(self)
        self.class_timer.timeout.connect(self.tick_class_timer)
        self.class_timer_running = False
        
        self.init_ui()
        self.apply_dark_theme()
        
        # Load a default code template
        self.editor.setPlainText("""# DSA Demo: Bubble Sort
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                # Swap elements
                temp = arr[j]
                arr[j] = arr[j+1]
                arr[j+1] = temp
                print(f"Swapped {arr[j]} and {arr[j+1]}")

numbers = [5, 2, 8, 1, 3]
print("Original:", numbers)
bubble_sort(numbers)
print("Sorted:", numbers)
""")
        # Initialize visibility of controls
        self.switch_mode(1)

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. TOP HEADER TOOLBAR
        toolbar = QWidget()
        toolbar.setObjectName("TopToolbar")
        toolbar.setFixedHeight(50)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 0, 10, 0)
        toolbar_layout.setSpacing(6)
        
        # Logo branding widget
        lbl_logo = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "dsa-classroom-logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            lbl_logo.setPixmap(logo_pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        toolbar_layout.addWidget(lbl_logo)
        
        # Collapsible Sidebar Toggle
        self.btn_toggle_sidebar = QPushButton(" Sidebar")
        self.btn_toggle_sidebar.setIcon(VectorIconProvider.get_icon("folder", "#007acc"))
        self.btn_toggle_sidebar.setCheckable(True)
        self.btn_toggle_sidebar.setChecked(True)
        self.btn_toggle_sidebar.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:checked {
                background-color: #007acc;
                border: 1px solid #005995;
            }
        """)
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        toolbar_layout.addWidget(self.btn_toggle_sidebar)
        
        toolbar_layout.addSpacing(10)
        
        # Mode selector buttons
        self.btn_presentation = QPushButton(" Presentation")
        self.btn_coding = QPushButton(" Coding")
        self.btn_visualization = QPushButton(" Visualizer")
        self.btn_whiteboard = QPushButton(" Whiteboard")
        
        self.btn_presentation.setIcon(VectorIconProvider.get_icon("pdf", "#007acc"))
        self.btn_coding.setIcon(VectorIconProvider.get_icon("python", "#4ec9b0"))
        self.btn_visualization.setIcon(VectorIconProvider.get_icon("view_3d", "#ffb86c"))
        self.btn_whiteboard.setIcon(VectorIconProvider.get_icon("whiteboard", "#ce9178"))
        
        self.btn_presentation.setCheckable(True)
        self.btn_coding.setCheckable(True)
        self.btn_visualization.setCheckable(True)
        self.btn_whiteboard.setCheckable(True)
        
        self.btn_coding.setChecked(True)
        
        for btn in (self.btn_presentation, self.btn_coding, self.btn_visualization, self.btn_whiteboard):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #cccccc;
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: #ffffff;
                    background-color: #2d2d2d;
                }
                QPushButton:checked {
                    color: #007acc;
                    border-bottom: 2px solid #007acc;
                    background-color: #2a2d2e;
                }
            """)
            
        self.btn_presentation.clicked.connect(lambda: self.switch_mode(0))
        self.btn_coding.clicked.connect(lambda: self.switch_mode(1))
        self.btn_visualization.clicked.connect(lambda: self.switch_mode(2))
        self.btn_whiteboard.clicked.connect(lambda: self.switch_mode(3))
        
        toolbar_layout.addWidget(self.btn_presentation)
        toolbar_layout.addWidget(self.btn_coding)
        toolbar_layout.addWidget(self.btn_visualization)
        toolbar_layout.addWidget(self.btn_whiteboard)
        
        toolbar_layout.addSpacing(20)
        
        # Execution controls (dynamic visibility)
        self.btn_run = QPushButton(" Run")
        self.btn_pause = QPushButton(" Pause")
        self.btn_prev = QPushButton(" Step Back")
        self.btn_next = QPushButton(" Step Fwd")
        self.btn_3d_toggle = QPushButton(" 3D View")
        
        self.btn_run.setIcon(VectorIconProvider.get_icon("play", "#4ec9b0"))
        self.btn_pause.setIcon(VectorIconProvider.get_icon("pause", "#ff5555"))
        self.btn_prev.setIcon(VectorIconProvider.get_icon("step_backward", "#858585"))
        self.btn_next.setIcon(VectorIconProvider.get_icon("step_forward", "#858585"))
        self.btn_3d_toggle.setIcon(VectorIconProvider.get_icon("view_3d", "#ffb86c"))
        self.btn_3d_toggle.setCheckable(True)
        self.btn_3d_toggle.clicked.connect(self.toggle_3d_view)
        
        for btn in (self.btn_run, self.btn_pause, self.btn_prev, self.btn_next, self.btn_3d_toggle):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
                QPushButton:checked {
                    background-color: #007acc;
                    border: 1px solid #005995;
                }
            """)
            
        self.btn_run.clicked.connect(self.run_code)
        self.btn_pause.clicked.connect(self.pause_code)
        self.btn_prev.clicked.connect(self.prev_step)
        self.btn_next.clicked.connect(self.next_step)
        
        toolbar_layout.addWidget(self.btn_run)
        toolbar_layout.addWidget(self.btn_pause)
        toolbar_layout.addWidget(self.btn_prev)
        toolbar_layout.addWidget(self.btn_next)
        toolbar_layout.addWidget(self.btn_3d_toggle)
        
        # Play Speed Slider
        self.lbl_speed_tag = QLabel("Speed:")
        self.lbl_speed_tag.setStyleSheet("color: #cccccc; font-size: 11px;")
        toolbar_layout.addWidget(self.lbl_speed_tag)
        
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(200, 2000)
        self.slider_speed.setValue(1000)
        self.slider_speed.setFixedWidth(60)
        self.slider_speed.valueChanged.connect(self.change_play_speed)
        toolbar_layout.addWidget(self.slider_speed)
        
        # Step Slider Scrubber
        self.lbl_step_info = QLabel("Step: 0/0")
        self.lbl_step_info.setStyleSheet("color: #cccccc; font-weight: bold; margin-left: 5px;")
        toolbar_layout.addWidget(self.lbl_step_info)
        
        self.slider_step = QSlider(Qt.Horizontal)
        self.slider_step.setEnabled(False)
        self.slider_step.valueChanged.connect(self.jump_to_step)
        toolbar_layout.addWidget(self.slider_step)
        
        # List of widgets to hide/show dynamically
        self.execution_widgets = [
            self.btn_run, self.btn_pause, self.btn_prev, self.btn_next, 
            self.btn_3d_toggle, self.lbl_speed_tag, self.slider_speed, 
            self.lbl_step_info, self.slider_step
        ]
        
        toolbar_layout.addSpacing(20)
        
        # Classroom Countdown Timer Widget
        self.lbl_timer = QLabel("Remaining: 45:00")
        self.lbl_timer.setStyleSheet("color: #ffb86c; font-weight: bold; font-family: Consolas; font-size: 12px; padding: 2px;")
        self.btn_timer_toggle = QPushButton()
        self.btn_timer_toggle.setIcon(VectorIconProvider.get_icon("play", "#ffb86c", 16))
        self.btn_timer_toggle.setStyleSheet("background-color: transparent; border: none;")
        self.btn_timer_toggle.clicked.connect(self.toggle_class_timer)
        self.lbl_timer.mouseDoubleClickEvent = self.set_class_timer_duration
        
        toolbar_layout.addWidget(self.lbl_timer)
        toolbar_layout.addWidget(self.btn_timer_toggle)
        
        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)
        
        # 2. MAIN SPLITTER (Sidebar | Workspace)
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)
        main_layout.addWidget(self.main_splitter, 1)
        
        # Sidebar Explorer
        self.sidebar = ResourceExplorer()
        self.sidebar.setMinimumWidth(180)
        self.sidebar.setMaximumWidth(600)
        self.sidebar.file_selected.connect(self.open_file)
        self.main_splitter.addWidget(self.sidebar)
        
        # Workspace Tab Widget (We hide the actual tab bar)
        self.workspace_tabs = QTabWidget()
        self.workspace_tabs.tabBar().hide()
        self.main_splitter.addWidget(self.workspace_tabs)
        
        self.main_splitter.setSizes([200, 1000])
        
        # --- TAB 1: PRESENTATION VIEW ---
        self.presentation_tab = PresentationTab()
        self.workspace_tabs.addTab(self.presentation_tab, "Presentation")
        
        # --- TAB 2: CODING VIEW ---
        coding_widget = QWidget()
        coding_layout = QHBoxLayout(coding_widget)
        coding_layout.setContentsMargins(0, 0, 0, 0)
        
        coding_splitter = QSplitter(Qt.Horizontal)
        coding_splitter.setCollapsible(0, False)
        coding_splitter.setCollapsible(1, False)
        coding_layout.addWidget(coding_splitter)
        
        # Left Panel: Code Editor
        self.editor = CodeEditor()
        coding_splitter.addWidget(self.editor)
        
        # Right Panel: Visualization & Execution Panels
        right_panel = QSplitter(Qt.Vertical)
        right_panel.setCollapsible(0, False)
        right_panel.setCollapsible(1, False)
        coding_splitter.addWidget(right_panel)
        
        # Top right: Visualizer Canvas
        self.visualizer = VisualizerWidget()
        self.visualizer.btn_copy_wb.clicked.connect(lambda: self.copy_visualizer_to_whiteboard(self.visualizer))
        right_panel.addWidget(self.visualizer)
        
        # Bottom right: Tabs for Variables, Console, and Complexity Reference
        self.bottom_panel = QTabWidget()
        self.bottom_panel.setObjectName("BottomPanel")
        right_panel.addWidget(self.bottom_panel)
        
        # Tab A: Variable Inspector Table
        var_widget = QWidget()
        var_layout = QVBoxLayout(var_widget)
        var_layout.setContentsMargins(5, 5, 5, 5)
        
        var_toolbar = QHBoxLayout()
        self.chk_hidden_vars = QCheckBox("Quiz: Hidden Variables Mode")
        self.chk_hidden_vars.setStyleSheet("color: #ffb86c; font-weight: bold;")
        self.chk_hidden_vars.stateChanged.connect(self.toggle_hidden_vars)
        
        self.btn_clear_vars_log = QPushButton("Clear History Logs")
        self.btn_clear_vars_log.setIcon(VectorIconProvider.get_icon("clear", "#ff5555"))
        self.btn_clear_vars_log.setStyleSheet("background-color: #4a1c1c; color: #ff5555; border-radius: 3px; font-size: 10px; padding: 3px 6px;")
        self.btn_clear_vars_log.clicked.connect(self.clear_variables_log)
        
        var_toolbar.addWidget(self.chk_hidden_vars)
        var_toolbar.addStretch()
        var_toolbar.addWidget(self.btn_clear_vars_log)
        
        var_layout.addLayout(var_toolbar)
        
        # Splitter to divide current variables table and persistent updates log
        var_panel_splitter = QSplitter(Qt.Vertical)
        var_layout.addWidget(var_panel_splitter)
        
        self.tbl_variables = QTableWidget(0, 3)
        self.tbl_variables.setHorizontalHeaderLabels(["Variable", "Type", "Value"])
        self.tbl_variables.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_variables.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                gridline-color: #3c3c3c;
                border: 1px solid #3c3c3c;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #cccccc;
                padding: 4px;
                border: 1px solid #3c3c3c;
            }
        """)
        self.tbl_variables.horizontalHeader().setStretchLastSection(True)
        self.tbl_variables.cellDoubleClicked.connect(self.toggle_individual_variable_visibility)
        var_panel_splitter.addWidget(self.tbl_variables)
        
        # Persistent Variable assignment log
        self.vars_history_log = QTextBrowser()
        self.vars_history_log.setStyleSheet("""
            QTextBrowser {
                background-color: #1a1a1a;
                color: #858585;
                font-family: 'Consolas';
                font-size: 9pt;
                border: 1px dashed #3c3c3c;
            }
        """)
        self.vars_history_log.setHtml("<span style='color: #858585;'>[ Variable History Log - Step updates will accumulate here ]</span>")
        var_panel_splitter.addWidget(self.vars_history_log)
        
        self.bottom_panel.addTab(var_widget, "📋 Variable Inspector")
        
        # Tab B: Execution Console
        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(5, 5, 5, 5)
        
        console_toolbar = QHBoxLayout()
        self.chk_hidden_output = QCheckBox("Quiz: Hidden Output Mode")
        self.chk_hidden_output.setStyleSheet("color: #ffb86c; font-weight: bold;")
        self.chk_hidden_output.stateChanged.connect(self.toggle_hidden_output)
        
        self.btn_reveal_output = QPushButton("Reveal Output")
        self.btn_reveal_output.setStyleSheet("""
            QPushButton {
                background-color: #ffb86c;
                color: black;
                border: none;
                border-radius: 3px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ffc98c;
            }
        """)
        self.btn_reveal_output.clicked.connect(self.reveal_output_manually)
        self.btn_reveal_output.setVisible(False)
        
        self.btn_clear_console = QPushButton("Clear Console")
        self.btn_clear_console.setIcon(VectorIconProvider.get_icon("clear", "#ff5555"))
        self.btn_clear_console.setStyleSheet("background-color: #4a1c1c; color: #ff5555; border-radius: 3px; font-size: 10px; padding: 3px 6px;")
        self.btn_clear_console.clicked.connect(self.clear_console_log)
        
        console_toolbar.addWidget(self.chk_hidden_output)
        console_toolbar.addWidget(self.btn_reveal_output)
        console_toolbar.addStretch()
        console_toolbar.addWidget(self.btn_clear_console)
        console_layout.addLayout(console_toolbar)
        
        self.console = QTextBrowser()
        self.console.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                font-family: 'Consolas';
                font-size: 11pt;
            }
        """)
        console_layout.addWidget(self.console)
        
        self.bottom_panel.addTab(console_widget, "💻 Console Output")
        
        # Tab C: Complexity Cheat Sheet Helper
        self.complexity_widget = ComplexityTextEdit()
        self.complexity_widget.setStyleSheet("""
            ComplexityTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
        """)
        
        # Load persistent complexity cheat sheet HTML
        default_complexity_html = """
        <h3 style="color: #007acc; border-bottom: 1px solid #3c3c3c; padding-bottom: 4px; margin-top:0px;">DSA Complexity Cheat Sheet</h3>
        <p style="color: #858585; font-size: 9pt; margin-bottom: 10px;">Tip: Click anywhere inside the table or text below to edit, add, or remove complexities. Edits are auto-saved.</p>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; border-color: #3c3c3c; width: 100%; color: #cccccc; font-family: Segoe UI; font-size: 9pt;">
          <tr style="background-color: #252526; color: #ffffff;">
            <th>Structure / Algorithm</th>
            <th>Average Time</th>
            <th>Worst Time</th>
            <th>Space Complexity</th>
          </tr>
          <tr>
            <td><b>Array / Python List Lookups</b></td>
            <td style="color:#4ec9b0">O(1)</td>
            <td style="color:#4ec9b0">O(1)</td>
            <td>O(N)</td>
          </tr>
          <tr>
            <td><b>Linear Search</b></td>
            <td>O(N)</td>
            <td>O(N)</td>
            <td style="color:#4ec9b0">O(1)</td>
          </tr>
          <tr>
            <td><b>Binary Search</b></td>
            <td style="color:#ffb86c">O(log N)</td>
            <td style="color:#ffb86c">O(log N)</td>
            <td style="color:#4ec9b0">O(1)</td>
          </tr>
          <tr>
            <td><b>Stack (Push/Pop)</b></td>
            <td style="color:#4ec9b0">O(1)</td>
            <td style="color:#4ec9b0">O(1)</td>
            <td style="color:#4ec9b0">O(1)</td>
          </tr>
          <tr>
            <td><b>Queue (Enqueue/Dequeue)</b></td>
            <td style="color:#4ec9b0">O(1)</td>
            <td style="color:#4ec9b0">O(1)</td>
            <td style="color:#4ec9b0">O(1)</td>
          </tr>
          <tr>
            <td><b>Singly Linked List Insertion</b></td>
            <td style="color:#4ec9b0">O(1)</td>
            <td style="color:#4ec9b0">O(1)</td>
            <td style="color:#4ec9b0">O(1)</td>
          </tr>
          <tr>
            <td><b>Hash Table / Dict (Access)</b></td>
            <td style="color:#4ec9b0">O(1)</td>
            <td>O(N)</td>
            <td>O(N)</td>
          </tr>
          <tr>
            <td><b>BST / AVL Insertion & Search</b></td>
            <td style="color:#ffb86c">O(log N)</td>
            <td>O(N) (AVL: O(log N))</td>
            <td>O(N)</td>
          </tr>
          <tr>
            <td><b>Bubble / Selection / Insertion Sort</b></td>
            <td>O(N^2)</td>
            <td>O(N^2)</td>
            <td style="color:#4ec9b0">O(1)</td>
          </tr>
        </table>
        """
        
        path = os.path.expanduser("~/.dsa_classroom_complexity.html")
        loaded_html = default_complexity_html
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded_html = f.read()
            except:
                pass
        
        self.complexity_widget.setHtml(loaded_html)
        self.complexity_widget.textChanged.connect(self.save_complexity_sheet)
        self.bottom_panel.addTab(self.complexity_widget, "📊 Complexity Cheat-Sheet")
        
        # Set proportions
        coding_splitter.setSizes([450, 750])
        right_panel.setSizes([450, 250])
        var_panel_splitter.setSizes([150, 100])
        
        self.workspace_tabs.addTab(coding_widget, "Coding")
        
        # --- TAB 3: VISUALIZATION MODE (Full focus on visual animations) ---
        self.fullscreen_visualizer = VisualizerWidget()
        self.fullscreen_visualizer.btn_copy_wb.clicked.connect(lambda: self.copy_visualizer_to_whiteboard(self.fullscreen_visualizer))
        self.workspace_tabs.addTab(self.fullscreen_visualizer, "Visualizer")
        
        # --- TAB 4: WHITEBOARD MODE ---
        self.whiteboard = WhiteboardWidget()
        self.workspace_tabs.addTab(self.whiteboard, "Whiteboard")

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget#TopToolbar {
                background-color: #252526;
                border-bottom: 1px solid #3c3c3c;
            }
            QSplitter::handle {
                background-color: #2d2d2d;
            }
            QSplitter::handle:horizontal {
                width: 6px;
            }
            QSplitter::handle:vertical {
                height: 6px;
            }
            QSplitter::handle:hover {
                background-color: #007acc;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #858585;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        """)

    # --- COLLAPSIBLE SIDEBAR LOGIC ---
    def toggle_sidebar(self, checked):
        self.sidebar.setHidden(not checked)

    # --- CONTEXT-AWARE TOOLBAR LOGIC ---
    def switch_mode(self, tab_idx):
        self.workspace_tabs.setCurrentIndex(tab_idx)
        
        self.btn_presentation.setChecked(tab_idx == 0)
        self.btn_coding.setChecked(tab_idx == 1)
        self.btn_visualization.setChecked(tab_idx == 2)
        self.btn_whiteboard.setChecked(tab_idx == 3)
        
        # Hide/Show execution controls based on Active Mode
        # Only show controls in Coding (1) and Visualizer (2)
        show_controls = tab_idx in (1, 2)
        for w in self.execution_widgets:
            w.setVisible(show_controls)

    def toggle_3d_view(self, checked):
        self.visualizer.set_3d_mode(checked)
        self.fullscreen_visualizer.set_3d_mode(checked)
        self.update_step_ui()

    # --- COUNTDOWN CLASS TIMER LOGIC ---
    def toggle_class_timer(self):
        if self.class_timer_running:
            self.class_timer.stop()
            self.class_timer_running = False
            self.btn_timer_toggle.setIcon(VectorIconProvider.get_icon("play", "#ffb86c", 16))
        else:
            self.class_timer.start(1000) # fire every second
            self.class_timer_running = True
            self.btn_timer_toggle.setIcon(VectorIconProvider.get_icon("pause", "#ffb86c", 16))

    def tick_class_timer(self):
        if self.class_time_remaining > 0:
            self.class_time_remaining -= 1
            mins = self.class_time_remaining // 60
            secs = self.class_time_remaining % 60
            self.lbl_timer.setText(f"Remaining: {mins:02d}:{secs:02d}")
        else:
            self.class_timer.stop()
            self.class_timer_running = False
            self.btn_timer_toggle.setIcon(VectorIconProvider.get_icon("play", "#ffb86c", 16))
            QMessageBox.information(self, "Class Time Up", "The countdown timer has completed!")

    def set_class_timer_duration(self, event):
        duration, ok = QInputDialog.getInt(self, "Set Timer", "Enter class timer duration (minutes):", value=45, min=1, max=180)
        if ok:
            self.class_time_remaining = duration * 60
            self.lbl_timer.setText(f"Remaining: {duration:02d}:00")
            if self.class_timer_running:
                self.class_timer.stop()
                self.class_timer_running = False
                self.btn_timer_toggle.setIcon(VectorIconProvider.get_icon("play", "#ffb86c", 16))

    # --- PERSISTENT LOGS CONTROL ---
    def clear_console_log(self):
        self.console.clear()

    def clear_variables_log(self):
        self.vars_history_log.clear()
        self.vars_history_log.setHtml("<span style='color: #858585;'>[ Log cleared ]</span>")

    def open_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".py":
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.setPlainText(content)
                self.switch_mode(1)
            except Exception as e:
                QMessageBox.critical(self, "Read Error", f"Could not read python script:\n{e}")
        elif ext in (".pdf", ".pptx", ".ppt", ".docx", ".doc"):
            self.presentation_tab.load_file(path)
            self.switch_mode(0)
        elif ext == ".dsa-wb":
            self.switch_mode(3)
            self.whiteboard.load_file(path)

    # --- CODE EXECUTION LOGIC ---
    def run_code(self):
        self.play_timer.stop()
        code = self.editor.toPlainText()
        
        # Append starting header to Persistent Console
        timestamp = time.strftime("%H:%M:%S")
        self.console.append(f"<span style='color:#007acc;'>--- Script Run started at {timestamp} ---</span>")
        
        res = self.engine.run_code(code)
        
        if res.get("error"):
            err_msg = res.get("error")
            self.timeline = res.get("timeline", [])
            self.console.append(f"<span style='color:#ff5555;'>Error occurred: {err_msg}</span>\n")
            if self.timeline:
                step = self.timeline[-1]
                self.console.append(step["output"])
            self.bottom_panel.setCurrentIndex(1)
            return
            
        self.timeline = res.get("timeline", [])
        
        if not self.timeline:
            self.console.append("Execution finished with no tracked frames.\n")
            self.slider_step.setEnabled(False)
            return
            
        self.slider_step.setEnabled(True)
        self.slider_step.setRange(0, len(self.timeline) - 1)
        self.slider_step.setValue(0)
        
        self.current_step_idx = 0
        
        # Append start header to Persistent Variable Log
        self.vars_history_log.append(f"<span style='color:#007acc;'>--- Run variables trace at {timestamp} ---</span>")
        
        self.update_step_ui()
        self.play_timer.start(self.slider_speed.value())

    def pause_code(self):
        self.play_timer.stop()

    def autoplay_step(self):
        if self.current_step_idx < len(self.timeline) - 1:
            self.current_step_idx += 1
            self.slider_step.setValue(self.current_step_idx)
        else:
            self.play_timer.stop()

    def prev_step(self):
        self.play_timer.stop()
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            self.slider_step.setValue(self.current_step_idx)

    def next_step(self):
        self.play_timer.stop()
        if self.current_step_idx < len(self.timeline) - 1:
            self.current_step_idx += 1
            self.slider_step.setValue(self.current_step_idx)

    def jump_to_step(self, value):
        if 0 <= value < len(self.timeline):
            self.current_step_idx = value
            self.update_step_ui()

    def update_step_ui(self):
        if not self.timeline or self.current_step_idx == -1:
            return
            
        step = self.timeline[self.current_step_idx]
        
        # 1. Status label
        self.lbl_step_info.setText(f"Step: {self.current_step_idx + 1}/{len(self.timeline)} (Line {step['line']})")
        
        # 2. Highlight code
        self.highlight_editor_line(step["line"])
        
        # 3. Parse variables and feed visualizers
        locals_snapshot = step.get("locals", {})
        parsed_state = self.parser.parse_state(locals_snapshot)
        
        self.visualizer.render_state(parsed_state, quiz_mode=self.hidden_variables_mode)
        self.fullscreen_visualizer.render_state(parsed_state, quiz_mode=self.hidden_variables_mode)
        
        # 4. Update variable table & Append to Persistent Log
        self.tbl_variables.setRowCount(0)
        
        # Build a string log for this step's variable changes
        step_var_log = []
        for name, val_dict in locals_snapshot.items():
            row = self.tbl_variables.rowCount()
            self.tbl_variables.insertRow(row)
            
            self.tbl_variables.setItem(row, 0, QTableWidgetItem(name))
            
            var_type = val_dict.get("type", "primitive")
            if var_type == "object":
                var_type = val_dict.get("class", "object")
            self.tbl_variables.setItem(row, 1, QTableWidgetItem(var_type))
            
            val_str = self.get_formatted_val_string(val_dict)
            
            # Show/Hide modes
            if self.hidden_variables_mode or name in self.hidden_vars_set:
                item = QTableWidgetItem("[ Hidden (Double Click Reveal) ]")
                item.setForeground(QColor("#ffb86c"))
                step_var_log.append(f"{name} = [ Hidden ]")
            else:
                item = QTableWidgetItem(val_str)
                step_var_log.append(f"{name} = {val_str}")
                
            self.tbl_variables.setItem(row, 2, item)
            
        # Append step variables log to history browser
        if step_var_log:
            var_entries = ", ".join(step_var_log)
            self.vars_history_log.append(f"<span style='color:#a6e22e;'>[Step {self.current_step_idx + 1}]</span> {var_entries}")
            self.vars_history_log.moveCursor(QTextCursor.End)
            
        # 5. Append step output to console
        output_txt = step.get("output", "")
        if self.hidden_output_mode:
            # Clear console and show overlay placeholder if output hidden
            self.console.setHtml("<span style='color: #ffb86c;'>[ Output Hidden by Teacher - Class Quiz Mode ]</span>")
            self.btn_reveal_output.setVisible(True)
        else:
            # In persistent mode, display current accumulated output
            self.console.setPlainText(output_txt)
            self.btn_reveal_output.setVisible(False)
            self.console.moveCursor(QTextCursor.End)

    def get_formatted_val_string(self, val_dict):
        v_type = val_dict.get("type")
        if v_type == "primitive":
            return str(val_dict.get("value"))
        elif v_type == "ref":
            return f"Node(Ref {val_dict.get('id')})"
        elif v_type in ("list", "tuple", "set"):
            inner = [self.get_formatted_val_string(x) for x in val_dict.get("value", [])]
            brackets = ("[", "]") if v_type == "list" else (("(", ")") if v_type == "tuple" else ("{", "}"))
            return f"{brackets[0]}{', '.join(inner)}{brackets[1]}"
        elif v_type == "dict":
            inner = [f"'{k}': {self.get_formatted_val_string(v)}" for k, v in val_dict.get("value", {}).items()]
            return "{" + ", ".join(inner) + "}"
        elif v_type == "object":
            return f"{val_dict.get('class')}(id={val_dict.get('id')})"
        return str(val_dict)

    def highlight_editor_line(self, line_num):
        self.editor.blockSignals(True)
        self.editor.highlight_current_line()
        
        selections = self.editor.extraSelections()
        selection = QTextEdit.ExtraSelection()
        
        line_color = QColor(255, 184, 108, 40) 
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        
        doc = self.editor.document()
        block = doc.findBlockByLineNumber(line_num - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            selection.cursor = cursor
            selections.append(selection)
            self.editor.setTextCursor(cursor)
            self.editor.ensureCursorVisible()
            
        self.editor.setExtraSelections(selections)
        self.editor.blockSignals(False)

    # --- QUIZ / HIDDEN MODES LOGIC ---
    def toggle_hidden_output(self, state):
        self.hidden_output_mode = (state == Qt.Checked.value or state == True)
        self.update_step_ui()

    def reveal_output_manually(self):
        if self.timeline and self.current_step_idx != -1:
            step = self.timeline[self.current_step_idx]
            self.console.setPlainText(step.get("output", ""))

    def toggle_hidden_vars(self, state):
        self.hidden_variables_mode = (state == Qt.Checked.value or state == True)
        self.update_step_ui()

    def toggle_individual_variable_visibility(self, row, col):
        item_name = self.tbl_variables.item(row, 0)
        if not item_name: return
        name = item_name.text()
        
        if name in self.hidden_vars_set:
            self.hidden_vars_set.remove(name)
        else:
            self.hidden_vars_set.add(name)
        self.update_step_ui()

    def change_play_speed(self, value):
        if self.play_timer.isActive():
            self.play_timer.stop()
            self.play_timer.start(value)

    def copy_visualizer_to_whiteboard(self, visualizer_widget):
        if not visualizer_widget.active_items:
            QMessageBox.information(self, "Copy to Whiteboard", "No visual elements to copy.")
            return
            
        reply = QMessageBox.question(
            self, "Clear Canvas?",
            "Clear whiteboard canvas before copying visual structure?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.No
        )
        if reply == QMessageBox.Cancel:
            return
            
        if reply == QMessageBox.Yes:
            self.whiteboard.clear_whiteboard(force=True)
            
        # We need to save undo state on whiteboard
        self.whiteboard.save_undo_state()
        
        # Keep track of mapping: visualizer_key -> whiteboard_item
        vis_to_wb_map = {}
        
        # Add CSBlockItems
        from gui.whiteboard import CSBlockItem, ConnectionLineItem
        for key, item in visualizer_widget.active_items.items():
            pos = item.scenePos()
            # Create block item at same scene pos
            wb_item = CSBlockItem(pos.x(), pos.y(), val_str=item.val_str, is_node=True)
            self.whiteboard.scene.addItem(wb_item)
            vis_to_wb_map[key] = wb_item
            
        # Add ConnectionLineItems
        for start_key, end_key, label, z_val, color_hex in visualizer_widget.current_edges:
            start_wb = vis_to_wb_map.get(start_key)
            end_wb = vis_to_wb_map.get(end_key)
            if start_wb and end_wb:
                # Whiteboard connection line
                conn = ConnectionLineItem(
                    QPointF(0, 0), QPointF(0, 0),
                    start_item=start_wb,
                    end_item=end_wb,
                    is_arrow=True,
                    color=Qt.black,
                    width=3
                )
                self.whiteboard.scene.addItem(conn)
                
        # Trigger an update on all whiteboard items to refresh connection paths
        for item in self.whiteboard.scene.items():
            if isinstance(item, ConnectionLineItem):
                item.update_path()
                
        # Switch to Whiteboard mode
        self.switch_mode(3)
        QMessageBox.information(self, "Success", "Visual structure copied to whiteboard.")

    def save_complexity_sheet(self):
        html = self.complexity_widget.toHtml()
        path = os.path.expanduser("~/.dsa_classroom_complexity.html")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
        except:
            pass

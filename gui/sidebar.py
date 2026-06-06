import os
from PySide6.QtCore import Qt, Signal, QFileSystemWatcher
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QLabel, QFileDialog)
from gui.icons import VectorIconProvider

class ResourceExplorer(QWidget):
    # Emitted when a file is selected (double-clicked)
    file_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_dir = None
        self.watcher = QFileSystemWatcher()
        self.watcher.directoryChanged.connect(self.reload_explorer)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header / Choose Folder Button
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("EXPLORER")
        self.lbl_title.setStyleSheet("font-weight: bold; color: #858585; font-size: 10px; letter-spacing: 1px;")
        
        self.btn_open = QPushButton("Open Folder")
        self.btn_open.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        self.btn_open.clicked.connect(self.choose_folder)
        
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_open)
        
        layout.addLayout(header_layout)
        
        # Selected Directory display
        self.lbl_dir = QLabel("No teaching folder selected")
        self.lbl_dir.setWordWrap(True)
        self.lbl_dir.setStyleSheet("color: #858585; font-size: 10px; padding: 2px;")
        layout.addWidget(self.lbl_dir)

        # File Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                color: #cccccc;
                border: none;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
            QTreeWidget::item:selected {
                background-color: #37373d;
                color: #ffffff;
            }
        """)
        
        # Double click to open files
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.tree)
        
        # Build category buckets
        self.categories = {
            "PDFs": {"exts": [".pdf"], "icon_name": "pdf", "color": "#007acc", "item": None},
            "PowerPoints": {"exts": [".pptx", ".ppt"], "icon_name": "pptx", "color": "#ffb86c", "item": None},
            "Word Files": {"exts": [".docx", ".doc"], "icon_name": "docx", "color": "#569cd6", "item": None},
            "Python Files": {"exts": [".py"], "icon_name": "python", "color": "#4ec9b0", "item": None},
            "Whiteboards": {"exts": [".dsa-wb"], "icon_name": "whiteboard", "color": "#ce9178", "item": None}
        }
        
        self.rebuild_category_roots()

    def rebuild_category_roots(self):
        self.tree.clear()
        for name, data in self.categories.items():
            root_item = QTreeWidgetItem(self.tree)
            root_item.setText(0, name)
            root_item.setIcon(0, VectorIconProvider.get_icon(data["icon_name"], data["color"]))
            root_item.setData(0, Qt.UserRole, "root")
            root_item.setFlags(root_item.flags() & ~Qt.ItemIsSelectable) # Make root non-selectable
            data["item"] = root_item

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Teaching Directory", "")
        if folder:
            self.set_teaching_directory(folder)

    def set_teaching_directory(self, folder_path):
        if self.selected_dir:
            # Remove old directory from watcher
            try:
                self.watcher.removePath(self.selected_dir)
            except:
                pass
                
        self.selected_dir = os.path.abspath(folder_path)
        self.lbl_dir.setText(self.selected_dir)
        
        # Add to watcher
        self.watcher.addPath(self.selected_dir)
        
        self.reload_explorer()

    def reload_explorer(self, *args):
        if not self.selected_dir or not os.path.exists(self.selected_dir):
            return
            
        # Temporarily block signals to avoid noise
        self.tree.blockSignals(True)
        
        # Clear child items under categories
        for name, data in self.categories.items():
            root = data["item"]
            # Remove all children
            for i in reversed(range(root.childCount())):
                root.removeChild(root.child(i))
                
        # Scan folder
        try:
            for entry in os.scandir(self.selected_dir):
                if entry.is_file():
                    ext = os.path.splitext(entry.name)[1].lower()
                    
                    # Match categories
                    for cat_name, cat_data in self.categories.items():
                        if ext in cat_data["exts"]:
                            child = QTreeWidgetItem(cat_data["item"])
                            child.setText(0, entry.name)
                            child.setIcon(0, VectorIconProvider.get_icon(cat_data["icon_name"], "#cccccc"))
                            # Store full file path
                            child.setData(0, Qt.UserRole, entry.path)
                            break
        except Exception as e:
            print(f"Error reading directory: {e}")
            
        # Expand categories that have files
        for name, data in self.categories.items():
            root = data["item"]
            if root.childCount() > 0:
                root.setExpanded(True)
                
        self.tree.blockSignals(False)

    def on_item_double_clicked(self, item, column):
        path = item.data(0, Qt.UserRole)
        # Verify it's a file path and not a "root" category item
        if path and path != "root":
            self.file_selected.emit(path)

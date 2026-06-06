import math
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPolygonF
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem, 
                             QGraphicsSimpleTextItem, QGraphicsRectItem, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QGraphicsTextItem)

# Modern HSL-tailored colors
COLOR_BG = QColor("#1e1e1e")
COLOR_NODE_BG = QColor("#007acc")
COLOR_NODE_BORDER = QColor("#005995")
COLOR_TEXT = QColor("#ffffff")
COLOR_INDEX = QColor("#858585")
COLOR_ARROW = QColor("#ce9178")
COLOR_POINTER = QColor("#4ec9b0")
COLOR_BORDER = QColor("#3c3c3c")
COLOR_PANEL_BG = QColor("#252526")

class ArrowItem(QGraphicsItem):
    def __init__(self, start_pos, end_pos, label="", z_depth=0, color_hex="#ce9178", parent=None):
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.label = label
        self.color = QColor(color_hex)
        self.setZValue(z_depth - 1)

    def boundingRect(self):
        return QRectF(self.start_pos, self.end_pos).normalized().adjusted(-30, -30, 30, 30)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(self.color, 2)
        painter.setPen(pen)
        
        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()
        angle = math.atan2(dy, dx)
        
        # Adjust arrowhead stop point based on node radius
        shortened_end = QPointF(
            self.end_pos.x() - 18 * math.cos(angle),
            self.end_pos.y() - 18 * math.sin(angle)
        )
        
        painter.drawLine(self.start_pos, shortened_end)
        
        # Arrowhead triangle
        arrow_size = 8
        arrow_p1 = shortened_end - QPointF(
            arrow_size * math.cos(angle - math.pi / 6),
            arrow_size * math.sin(angle - math.pi / 6)
        )
        arrow_p2 = shortened_end - QPointF(
            arrow_size * math.cos(angle + math.pi / 6),
            arrow_size * math.sin(angle + math.pi / 6)
        )
        
        arrowhead = QPolygonF([shortened_end, arrow_p1, arrow_p2])
        painter.setBrush(QBrush(self.color))
        painter.drawPolygon(arrowhead)
        
        if self.label:
            painter.setPen(QPen(COLOR_POINTER, 1))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            mid_point = (self.start_pos + shortened_end) / 2.0
            painter.drawText(mid_point + QPointF(5, -5), self.label)


class DraggableNodeItem(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, val_str, node_id, z_depth=1, base_color=COLOR_NODE_BG, parent=None):
        super().__init__(-radius, -radius, radius * 2, radius * 2, parent)
        self.radius = radius
        self.val_str = val_str
        self.node_id = node_id
        self.pointers = []
        self.base_color = base_color
        self.target_pos = QPointF(x, y)
        
        self.setPos(x, y)
        self.setBrush(QBrush(base_color))
        self.setPen(QPen(COLOR_NODE_BORDER, 2))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(z_depth)

    def add_pointer(self, pointer_name):
        if pointer_name not in self.pointers:
            self.pointers.append(pointer_name)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            scene = self.scene()
            if scene:
                for view in scene.views():
                    if hasattr(view, "widget") and view.widget:
                        view.widget.update_arrows()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Value text
        painter.setPen(QPen(COLOR_TEXT))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        fm = painter.fontMetrics()
        tx = -fm.horizontalAdvance(self.val_str) / 2
        ty = fm.ascent() - fm.height() / 2
        painter.drawText(QPointF(tx, ty), self.val_str)
        
        # Pointers
        if self.pointers:
            ptr_str = ", ".join(self.pointers)
            painter.setPen(QPen(COLOR_POINTER))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            fm_p = painter.fontMetrics()
            ptx = -fm_p.horizontalAdvance(ptr_str) / 2
            pty = -self.radius - 4
            painter.drawText(QPointF(ptx, pty), ptr_str)


class VisualizerView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setStyleSheet("background-color: #1e1e1e; border: 1px solid #3c3c3c; border-radius: 4px;")
        
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.widget = None
        self.last_mouse_pos = QPointF()
        
    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale(1.15, 1.15)
            else:
                self.scale(1.0 / 1.15, 1.0 / 1.15)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if self.widget and self.widget.is_3d_mode and event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        if self.widget and self.widget.is_3d_mode and event.buttons() & Qt.LeftButton:
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()
            self.last_mouse_pos = event.pos()
            
            # Rotate instantly on mouse dragging
            self.widget.yaw += dx * 0.015
            self.widget.pitch += dy * 0.015
            self.widget.render_current_state(instant_pos=True)
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if self.widget and self.widget.is_3d_mode:
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mouseReleaseEvent(event)


class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_3d_mode = False
        self.yaw = 0.6
        self.pitch = 0.4
        self.parsed_state = {}
        self.quiz_mode = False
        
        # Item registry for transitions
        self.active_items = {}
        self.arrow_items = []
        self.current_edges = []
        self.extra_scene_items = []
        
        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_tick)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Info header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.lbl_title = QLabel("Execution Visualization Canvas")
        self.lbl_title.setStyleSheet("color: #d4d4d4; font-weight: bold; font-size: 13px;")
        
        self.lbl_hint = QLabel("(Ctrl + Mouse Wheel to zoom; Left-drag to pan; Step to see smooth swapping)")
        self.lbl_hint.setStyleSheet("color: #858585; font-size: 11px;")
        
        header_layout.addWidget(self.lbl_title)
        header_layout.addWidget(self.lbl_hint)
        header_layout.addStretch()
        
        from gui.icons import VectorIconProvider
        self.btn_copy_wb = QPushButton(" Copy to Whiteboard")
        self.btn_copy_wb.setIcon(VectorIconProvider.get_icon("whiteboard", "#ffb86c", 16))
        self.btn_copy_wb.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        header_layout.addWidget(self.btn_copy_wb)
        
        layout.addLayout(header_layout)
        
        # Graphics View
        self.view = VisualizerView(self)
        self.view.widget = self
        layout.addWidget(self.view)
        
        # Show empty state initially
        self.render_state({})

    def set_3d_mode(self, enabled):
        self.is_3d_mode = enabled
        if enabled:
            self.lbl_hint.setText("(Left-drag to rotate in 3D; Ctrl + Scroll to zoom)")
            self.view.setDragMode(QGraphicsView.NoDrag)
        else:
            self.lbl_hint.setText("(Left-drag to pan canvas; Ctrl + Scroll to zoom)")
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)
            
    def is_state_empty(self, parsed_state):
        if not parsed_state:
            return True
        has_data = (
            parsed_state.get("primitives") or
            parsed_state.get("arrays") or
            parsed_state.get("stacks") or
            parsed_state.get("queues") or
            parsed_state.get("linked_lists") or
            parsed_state.get("trees") or
            parsed_state.get("graphs") or
            parsed_state.get("dicts")
        )
        return not has_data

    def render_current_state(self, instant_pos=False):
        if self.parsed_state:
            self.render_state(self.parsed_state, instant_pos, quiz_mode=self.quiz_mode)

    def render_state(self, parsed_state, instant_pos=False, quiz_mode=None):
        """
        Clears scene, registers targets, and triggers the smooth interpolation layout.
        """
        if quiz_mode is not None:
            self.quiz_mode = quiz_mode
        self.parsed_state = parsed_state
        self.current_edges.clear()
        
        # Clean up old extra elements to prevent graphics leaks
        for item in self.extra_scene_items:
            try:
                self.view.scene.removeItem(item)
            except Exception:
                pass
        self.extra_scene_items.clear()
        
        # Specs dictionary holding everything we need to draw in the new frame
        # key -> {x, y, z, type, val, radius, pointers, color, is_box}
        specs = {}
        
        # Collect coordinates and specs depending on mode
        if self.is_3d_mode:
            self.collect_3d_specs(parsed_state, specs)
        else:
            self.collect_2d_specs(parsed_state, specs, self.quiz_mode)
            
        # Apply quiz mode masking to specs
        if self.quiz_mode:
            for spec in specs.values():
                spec["val"] = "?"
                
        # If the state is empty, draw a placeholder
        if self.is_state_empty(parsed_state):
            placeholder = QGraphicsTextItem()
            placeholder.setHtml("""
                <div style='text-align: center; color: #858585; font-family: Segoe UI;'>
                    <h2 style='color: #007acc; margin-bottom: 5px;'>Offline DSA Visualizer</h2>
                    <p style='margin: 0; font-size: 12px;'>Run a python script with tracked data structures to visualize.</p>
                    <p style='margin-top: 5px; font-size: 11px; color: #666666;'>Supported: Variables, Arrays, Lists, Stacks, Queues, Linked Lists, Trees, Graphs, Dicts</p>
                </div>
            """)
            rect = placeholder.boundingRect()
            placeholder.setPos(-rect.width() / 2, -rect.height() / 2)
            self.view.scene.addItem(placeholder)
            self.extra_scene_items.append(placeholder)
            self.view.centerOn(0, 0)
            
        # Match specs against registry
        touched_keys = set()
        for key, spec in specs.items():
            touched_keys.add(key)
            tx, ty = spec["x"], spec["y"]
            r = spec.get("radius", 18)
            
            # Shading and layout variables
            z_val = int(1000 - spec.get("z", 0))
            base_col = spec.get("color", COLOR_NODE_BG)
            
            # Check if item already exists in registry
            if key in self.active_items:
                item = self.active_items[key]
                item.target_pos = QPointF(tx, ty)
                item.setZValue(z_val)
                item.val_str = spec["val"]
                item.pointers = spec["pointers"]
                item.setBrush(QBrush(base_col))
                item.update()
                
                # If rotation dragging or instant coordinates requested
                if instant_pos:
                    item.setPos(item.target_pos)
            else:
                # Create new item
                if spec.get("is_box", False):
                    item = DraggableNodeItem(tx, ty, r, spec["val"], key, z_val, base_col)
                else:
                    item = DraggableNodeItem(tx, ty, r, spec["val"], key, z_val, base_col)
                    
                for ptr in spec["pointers"]:
                    item.add_pointer(ptr)
                    
                item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
                self.view.scene.addItem(item)
                self.active_items[key] = item
                
        # Remove dead items from registry
        for key in list(self.active_items.keys()):
            if key not in touched_keys:
                item = self.active_items.pop(key)
                try:
                    self.view.scene.removeItem(item)
                except:
                    pass
                    
        # Update edges and run animation tick
        self.update_arrows()
        
        if not instant_pos:
            self.animation_timer.start(16) # 60 FPS transitions
        else:
            self.update_arrows()

    def animate_tick(self):
        moving = False
        for key, item in list(self.active_items.items()):
            if hasattr(item, "target_pos"):
                curr_pos = item.pos()
                target = item.target_pos
                dx = target.x() - curr_pos.x()
                dy = target.y() - curr_pos.y()
                dist = math.hypot(dx, dy)
                if dist > 0.4:
                    new_pos = curr_pos + QPointF(dx * 0.22, dy * 0.22) # smooth interpolation speed
                    item.setPos(new_pos)
                    moving = True
                else:
                    item.setPos(target)
                    
        self.update_arrows()
        if not moving:
            self.animation_timer.stop()

    def update_arrows(self):
        """
        Clears previous arrows and draws new ones pointing exactly to current node positions.
        """
        for arrow in self.arrow_items:
            try:
                self.view.scene.removeItem(arrow)
            except:
                pass
        self.arrow_items.clear()
        
        for start_key, end_key, label, z_val, color_hex in self.current_edges:
            if start_key in self.active_items and end_key in self.active_items:
                start_item = self.active_items[start_key]
                end_item = self.active_items[end_key]
                
                arrow = ArrowItem(start_item.pos(), end_item.pos(), label, z_val, color_hex)
                self.view.scene.addItem(arrow)
                self.arrow_items.append(arrow)

    # --- 3D PERSPECTIVE CALCULATOR ---
    def project_3d_point(self, x, y, z, cx=400, cy=300):
        cos_y, sin_y = math.cos(self.yaw), math.sin(self.yaw)
        x1 = x * cos_y - z * sin_y
        z1 = x * sin_y + z * cos_y
        
        cos_x, sin_x = math.cos(self.pitch), math.sin(self.pitch)
        y2 = y * cos_x - z1 * sin_x
        z2 = y * sin_x + z1 * cos_x
        
        d = 400.0
        depth = z2 + d
        if depth < 10: depth = 10
        scale = d / depth
        scale = max(0.2, min(scale, 2.0))
        
        px = x1 * scale + cx
        py = -y2 * scale + cy
        return px, py, scale, z2

    # --- COLLECT 3D SPECS ---
    def collect_3d_specs(self, parsed_state, specs):
        cx, cy = 400, 300
        pointers = parsed_state.get("pointers", {})
        
        # 1. 3D Trees (Alternate cone projection)
        trees = parsed_state.get("trees", {})
        for name, tree_data in trees.items():
            tree_nodes = tree_data.get("nodes", {})
            root_id = tree_data.get("root_id")
            if not root_id or root_id not in tree_nodes:
                continue
                
            coords = {}
            def layout_3d_tree(n_id, x, y, z, depth):
                if not n_id or n_id not in tree_nodes:
                    return
                node = tree_nodes[n_id]
                coords[n_id] = (x, y, z)
                sep = 140.0 / (1.4 ** depth)
                if depth % 2 == 0:
                    layout_3d_tree(node["left_id"], x - sep, y - 60, z, depth + 1)
                    layout_3d_tree(node["right_id"], x + sep, y - 60, z, depth + 1)
                else:
                    layout_3d_tree(node["left_id"], x, y - 60, z - sep, depth + 1)
                    layout_3d_tree(node["right_id"], x, y - 60, z + sep, depth + 1)
                    
            layout_3d_tree(root_id, 0, 150, 0, 0)
            
            for n_id, pos in coords.items():
                node = tree_nodes[n_id]
                px, py, scale, z2 = self.project_3d_point(pos[0], pos[1], pos[2], cx, cy)
                
                # Sizing & Fading
                shaded_col = self.get_depth_shaded_color(z2, COLOR_NODE_BG)
                
                specs[str(n_id)] = {
                    "x": px, "y": py, "z": z2, "val": str(node["val"]),
                    "radius": 18 * scale, "pointers": [p_name for p_name, p_id in pointers.items() if p_id == n_id],
                    "color": shaded_col
                }
                
                # Add edges to be drawn later
                for child_k in ("left_id", "right_id"):
                    child_id = node[child_k]
                    if child_id and child_id in coords:
                        avg_z = (z2 + pos[2]) / 2.0
                        self.current_edges.append((str(n_id), str(child_id), "", int(1000 - avg_z), "#6a9955"))

        # 2. 3D Graphs (Fibonacci Sphere Layout)
        graphs = parsed_state.get("graphs", {})
        for name, graph_data in graphs.items():
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            num = len(nodes)
            r = 150.0
            
            coords = {}
            for idx, node in enumerate(nodes):
                if num > 1:
                    y = r * (1.0 - 2.0 * idx / (num - 1))
                    rad = math.sqrt(max(0.0, r**2 - y**2))
                    theta = idx * math.pi * (3.0 - math.sqrt(5.0))
                    x = rad * math.cos(theta)
                    z = rad * math.sin(theta)
                else:
                    x, y, z = 0, 0, 0
                    
                pos = (x, y - 50, z)
                coords[node] = pos
                px, py, scale, z2 = self.project_3d_point(x, y - 50, z, cx, cy)
                shaded_col = self.get_depth_shaded_color(z2, QColor("#4ec9b0"))
                
                key = f"graph_{name}_{node}"
                specs[key] = {
                    "x": px, "y": py, "z": z2, "val": node,
                    "radius": 18 * scale, "pointers": [],
                    "color": shaded_col
                }
                
            for u, v in edges:
                if u in coords and v in coords:
                    avg_z = (coords[u][2] + coords[v][2]) / 2.0
                    self.current_edges.append((f"graph_{name}_{u}", f"graph_{name}_{v}", "", int(1000 - avg_z), "#ce9178"))

        # 3. 3D Linked Lists (Helix spiral layout)
        linked_lists = parsed_state.get("linked_lists", {})
        for name, ll_data in linked_lists.items():
            ll_nodes = ll_data.get("nodes", {})
            head_id = ll_data.get("head_id")
            
            coords = {}
            visited = set()
            curr_id = head_id
            idx = 0
            while curr_id and curr_id in ll_nodes and curr_id not in visited:
                visited.add(curr_id)
                node_info = ll_nodes[curr_id]
                
                angle = idx * 0.7
                x = 120.0 * math.cos(angle)
                z = 120.0 * math.sin(angle)
                y = 120.0 - idx * 40.0
                
                pos = (x - 150, y, z)
                coords[curr_id] = pos
                px, py, scale, z2 = self.project_3d_point(pos[0], pos[1], pos[2], cx, cy)
                shaded_col = self.get_depth_shaded_color(z2, QColor("#ce9178"))
                
                specs[str(curr_id)] = {
                    "x": px, "y": py, "z": z2, "val": str(node_info["val"]),
                    "radius": 18 * scale, "pointers": [p_name for p_name, p_id in pointers.items() if p_id == curr_id],
                    "color": shaded_col
                }
                
                next_id = node_info["next_id"]
                if next_id:
                    pass
                curr_id = next_id
                idx += 1
                
            # Helix Edges
            visited.clear()
            curr_id = head_id
            while curr_id and curr_id in ll_nodes and curr_id not in visited:
                visited.add(curr_id)
                node_info = ll_nodes[curr_id]
                next_id = node_info["next_id"]
                if next_id and next_id in coords:
                    avg_z = (coords[curr_id][2] + coords[next_id][2]) / 2.0
                    self.current_edges.append((str(curr_id), str(next_id), "", int(1000 - avg_z), "#ce9178"))
                curr_id = next_id

        # 4. 3D Arrays
        arrays = parsed_state.get("arrays", {})
        idx_offset_y = -100
        for name, elements in arrays.items():
            arr_coords = []
            for i, val in enumerate(elements):
                x = -200 + i * 50
                y = idx_offset_y
                z = -100
                pos = (x, y, z)
                arr_coords.append(pos)
                
                px, py, scale, z2 = self.project_3d_point(x, y, z, cx, cy)
                shaded_col = self.get_depth_shaded_color(z2, QColor("#858585"))
                
                key = f"arr_{name}_{i}"
                specs[key] = {
                    "x": px, "y": py, "z": z2, "val": str(val),
                    "radius": 18 * scale, "pointers": [p_name for p_name, p_val in pointers.items() if p_val == i],
                    "color": shaded_col, "is_box": True
                }
            for i in range(len(arr_coords) - 1):
                self.current_edges.append((f"arr_{name}_{i}", f"arr_{name}_{i+1}", "", 900, "#858585"))
            idx_offset_y -= 60

    def get_depth_shaded_color(self, z, base_color):
        norm_depth = (z + 200.0) / 400.0
        norm_depth = max(0.0, min(1.0, norm_depth))
        return QColor(
            int(base_color.red() * (1.0 - norm_depth) + 30 * norm_depth),
            int(base_color.green() * (1.0 - norm_depth) + 30 * norm_depth),
            int(base_color.blue() * (1.0 - norm_depth) + 30 * norm_depth)
        )

    # --- COLLECT 2D SPECS (Flat positions for smooth sliding) ---
    def collect_2d_specs(self, parsed_state, specs, quiz_mode=False):
        scene_y = 50
        pointers = parsed_state.get("pointers", {})
        
        # 1. Primitives display
        primitives = parsed_state.get("primitives", {})
        if primitives:
            # We draw primitives as normal overlaid text boxes (not animated to avoid clutter)
            self.draw_primitives_2d(primitives, 50, scene_y, quiz_mode)
            scene_y += 100
            
        # 2. Arrays
        arrays = parsed_state.get("arrays", {})
        for name, elements in arrays.items():
            cell_w = 50
            arr_x = 130
            for idx, val in enumerate(elements):
                key = f"arr_{name}_{idx}"
                specs[key] = {
                    "x": arr_x + idx * cell_w + 25,
                    "y": scene_y + 20,
                    "z": 0,
                    "val": str(val),
                    "radius": 18,
                    "pointers": [p_name for p_name, p_val in pointers.items() if p_val == idx],
                    "color": COLOR_NODE_BG,
                    "is_box": True
                }
            # Add connections/edges for array cells so they form a row
            for idx in range(len(elements) - 1):
                self.current_edges.append((f"arr_{name}_{idx}", f"arr_{name}_{idx+1}", "", 999, "#005995"))
            scene_y += 120
            
        # 3. Stacks
        stacks = parsed_state.get("stacks", {})
        stack_x = 50
        max_stack_h = 0
        for name, elements in stacks.items():
            cell_h = 30
            base_y = scene_y + 40
            num_elements = len(elements)
            stack_h = max(4, num_elements) * cell_h + 10
            
            # draw stack container outline
            self.draw_stack_bounds_2d(name, stack_x, base_y, stack_h)
            
            for idx, val in enumerate(elements):
                y_pos = base_y + stack_h - (idx + 1) * cell_h
                key = f"stack_{name}_{idx}"
                specs[key] = {
                    "x": stack_x + 35,
                    "y": y_pos + 15,
                    "z": 0,
                    "val": str(val),
                    "radius": 15,
                    "pointers": [],
                    "color": COLOR_NODE_BG
                }
            stack_x += 180
            max_stack_h = max(max_stack_h, stack_h)
        if stacks:
            scene_y += max_stack_h + 80
            
        # 4. Queues
        queues = parsed_state.get("queues", {})
        for name, elements in queues.items():
            cell_w = 50
            q_x = 130
            num_elements = len(elements)
            queue_w = max(5, num_elements) * cell_w
            
            # Draw queue outline bounds
            self.draw_queue_bounds_2d(name, q_x, scene_y, queue_w)
            
            for idx, val in enumerate(elements):
                x_pos = q_x + queue_w - (idx + 1) * cell_w
                key = f"queue_{name}_{idx}"
                
                ptrs = []
                if idx == 0: ptrs.append("Front")
                if idx == num_elements - 1: ptrs.append("Rear")
                
                specs[key] = {
                    "x": x_pos + 25,
                    "y": scene_y + 20,
                    "z": 0,
                    "val": str(val),
                    "radius": 16,
                    "pointers": ptrs,
                    "color": COLOR_NODE_BG
                }
            scene_y += 120
            
        # 5. Linked Lists
        linked_lists = parsed_state.get("linked_lists", {})
        for name, ll_data in linked_lists.items():
            nodes_dict = ll_data.get("nodes", {})
            head_id = ll_data.get("head_id")
            node_w = 70
            curr_x = 130
            visited = set()
            curr_id = head_id
            
            while curr_id and curr_id in nodes_dict and curr_id not in visited:
                visited.add(curr_id)
                node_info = nodes_dict[curr_id]
                
                specs[str(curr_id)] = {
                    "x": curr_x + 35,
                    "y": scene_y + 20,
                    "z": 0,
                    "val": str(node_info["val"]),
                    "radius": 18,
                    "pointers": [p_name for p_name, p_id in pointers.items() if p_id == curr_id],
                    "color": COLOR_NODE_BG
                }
                
                next_id = node_info["next_id"]
                if next_id:
                    self.current_edges.append((str(curr_id), str(next_id), "", 999, "#ce9178"))
                curr_id = next_id
                curr_x += node_w + 50
            scene_y += 140
            
        # 6. Trees
        trees = parsed_state.get("trees", {})
        for name, tree_data in trees.items():
            nodes = tree_data.get("nodes", {})
            root_id = tree_data.get("root_id")
            if not root_id or root_id not in nodes:
                continue
                
            def get_subtree_width(node_id):
                if not node_id or node_id not in nodes: return 0
                node = nodes[node_id]
                left_w = get_subtree_width(node["left_id"])
                right_w = get_subtree_width(node["right_id"])
                return max(left_w + right_w + 60, 50)
                
            def layout_2d_tree(node_id, x, y, dx):
                if not node_id or node_id not in nodes: return
                node = nodes[node_id]
                
                specs[str(node_id)] = {
                    "x": x,
                    "y": y,
                    "z": 0,
                    "val": str(node["val"]),
                    "radius": 18,
                    "pointers": [p_name for p_name, p_id in pointers.items() if p_id == node_id],
                    "color": COLOR_NODE_BG
                }
                
                left_id = node["left_id"]
                right_id = node["right_id"]
                
                if left_id:
                    layout_2d_tree(left_id, x - dx, y + 60, dx / 2)
                    self.current_edges.append((str(node_id), str(left_id), "", 999, "#ce9178"))
                if right_id:
                    layout_2d_tree(right_id, x + dx, y + 60, dx / 2)
                    self.current_edges.append((str(node_id), str(right_id), "", 999, "#ce9178"))
                    
            root_dx = get_subtree_width(root_id) / 2
            layout_2d_tree(root_id, 350, scene_y + 30, root_dx)
            scene_y += 250
            
        # 7. Graphs
        graphs = parsed_state.get("graphs", {})
        for name, graph_data in graphs.items():
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            if not nodes: continue
            
            radius = 20
            graph_radius = 80
            cx = 300
            cy = scene_y + 100
            
            for idx, node in enumerate(nodes):
                angle = 2 * math.pi * idx / len(nodes)
                nx = cx + graph_radius * math.cos(angle)
                ny = cy + graph_radius * math.sin(angle)
                
                key = f"graph_{name}_{node}"
                specs[key] = {
                    "x": nx,
                    "y": ny,
                    "z": 0,
                    "val": node,
                    "radius": radius,
                    "pointers": [],
                    "color": QColor("#4ec9b0")
                }
                
            for u, v in edges:
                self.current_edges.append((f"graph_{name}_{u}", f"graph_{name}_{v}", "", 999, "#ce9178"))
            scene_y += 300
            
        # 8. Dicts
        dicts = parsed_state.get("dicts", {})
        for name, dict_items in dicts.items():
            # Draw standard 2D dict buckets (no animation for simplicity)
            self.draw_dict_2d(dict_items, 50, scene_y, quiz_mode)
            scene_y += 120

    # Draw methods for 2D container lines (not animated nodes)
    def draw_stack_bounds_2d(self, name, x, y, h):
        cell_w = 60
        # Draw stack container boundary lines
        pen = QPen(COLOR_BORDER, 3)
        l1 = self.view.scene.addLine(x, y, x, y + h, pen)
        l2 = self.view.scene.addLine(x + cell_w + 10, y, x + cell_w + 10, y + h, pen)
        l3 = self.view.scene.addLine(x, y + h, x + cell_w + 10, y + h, pen)
        self.extra_scene_items.extend([l1, l2, l3])
        
        lbl = QGraphicsSimpleTextItem(name)
        lbl.setBrush(QBrush(COLOR_INDEX))
        lbl.setFont(QFont("Arial", 10, QFont.Bold))
        lbl.setPos(x + 10, y - 20)
        self.view.scene.addItem(lbl)
        self.extra_scene_items.append(lbl)

    def draw_queue_bounds_2d(self, name, x, y, w):
        cell_h = 40
        pen = QPen(COLOR_BORDER, 3)
        l1 = self.view.scene.addLine(x, y, x + w, y, pen)
        l2 = self.view.scene.addLine(x, y + cell_h, x + w, y + cell_h, pen)
        self.extra_scene_items.extend([l1, l2])
        
        lbl = QGraphicsSimpleTextItem(f"{name}:")
        lbl.setBrush(QBrush(COLOR_INDEX))
        lbl.setFont(QFont("Arial", 11, QFont.Bold))
        lbl.setPos(x - 80, y + 10)
        self.view.scene.addItem(lbl)
        self.extra_scene_items.append(lbl)

    def draw_primitives_2d(self, primitives, start_x, start_y):
        lbl = QGraphicsSimpleTextItem("Variables:")
        lbl.setBrush(QBrush(COLOR_INDEX))
        lbl.setFont(QFont("Arial", 11, QFont.Bold))
        lbl.setPos(start_x, start_y)
        self.view.scene.addItem(lbl)
        self.extra_scene_items.append(lbl)
        
        curr_x = start_x
        curr_y = start_y + 25
        for name, val in primitives.items():
            text_str = f" {name} = {val} "
            font = QFont("Consolas", 11, QFont.Bold)
            text_item = QGraphicsSimpleTextItem(text_str)
            text_item.setBrush(QBrush(COLOR_TEXT))
            text_item.setFont(font)
            
            text_rect = text_item.boundingRect()
            rect_item = QGraphicsRectItem(curr_x, curr_y, text_rect.width() + 10, text_rect.height() + 8)
            rect_item.setBrush(QBrush(QColor("#2d2d2d")))
            rect_item.setPen(QPen(COLOR_BORDER, 1))
            
            text_item.setPos(curr_x + 5, curr_y + 4)
            self.view.scene.addItem(rect_item)
            self.view.scene.addItem(text_item)
            self.extra_scene_items.extend([rect_item, text_item])
            
            curr_x += text_rect.width() + 25
            if curr_x > 800:
                curr_x = start_x
                curr_y += 35

    def draw_primitives_2d(self, primitives, start_x, start_y, quiz_mode=False):
        lbl = QGraphicsSimpleTextItem("Variables:")
        lbl.setBrush(QBrush(COLOR_INDEX))
        lbl.setFont(QFont("Arial", 11, QFont.Bold))
        lbl.setPos(start_x, start_y)
        self.view.scene.addItem(lbl)
        self.extra_scene_items.append(lbl)
        
        curr_x = start_x
        curr_y = start_y + 25
        for name, val in primitives.items():
            val_display = "?" if quiz_mode else val
            text_str = f" {name} = {val_display} "
            font = QFont("Consolas", 11, QFont.Bold)
            text_item = QGraphicsSimpleTextItem(text_str)
            text_item.setBrush(QBrush(COLOR_TEXT))
            text_item.setFont(font)
            
            text_rect = text_item.boundingRect()
            rect_item = QGraphicsRectItem(curr_x, curr_y, text_rect.width() + 10, text_rect.height() + 8)
            rect_item.setBrush(QBrush(QColor("#2d2d2d")))
            rect_item.setPen(QPen(COLOR_BORDER, 1))
            
            text_item.setPos(curr_x + 5, curr_y + 4)
            self.view.scene.addItem(rect_item)
            self.view.scene.addItem(text_item)
            self.extra_scene_items.extend([rect_item, text_item])
            
            curr_x += text_rect.width() + 25
            if curr_x > 800:
                curr_x = start_x
                curr_y += 35

    def draw_dict_2d(self, dict_items, start_x, start_y, quiz_mode=False):
        cell_w, cell_h = 100, 30
        curr_x = start_x
        curr_y = start_y
        
        for k, v in dict_items.items():
            rect_k = QGraphicsRectItem(curr_x, curr_y, cell_w, cell_h)
            rect_k.setBrush(QBrush(COLOR_PANEL_BG))
            rect_k.setPen(QPen(COLOR_BORDER, 1))
            self.view.scene.addItem(rect_k)
            self.extra_scene_items.append(rect_k)
            
            lbl_k = QGraphicsSimpleTextItem(str(k))
            lbl_k.setFont(QFont("Segoe UI", 9, QFont.Bold))
            lbl_k.setBrush(QBrush(COLOR_POINTER))
            lbl_k.setPos(curr_x + 5, curr_y + (cell_h - lbl_k.boundingRect().height()) / 2)
            self.view.scene.addItem(lbl_k)
            self.extra_scene_items.append(lbl_k)
            
            rect_v = QGraphicsRectItem(curr_x + cell_w, curr_y, cell_w, cell_h)
            rect_v.setBrush(QBrush(COLOR_NODE_BG))
            rect_v.setPen(QPen(COLOR_NODE_BORDER, 1))
            self.view.scene.addItem(rect_v)
            self.extra_scene_items.append(rect_v)
            
            val_display = "?" if quiz_mode else v
            lbl_v = QGraphicsSimpleTextItem(str(val_display))
            lbl_v.setFont(QFont("Segoe UI", 9, QFont.Bold))
            lbl_v.setBrush(QBrush(COLOR_TEXT))
            lbl_v.setPos(curr_x + cell_w + 5, curr_y + (cell_h - lbl_v.boundingRect().height()) / 2)
            self.view.scene.addItem(lbl_v)
            self.extra_scene_items.append(lbl_v)
            
            curr_x += (cell_w * 2) + 20
            if curr_x > 800:
                curr_x = start_x
                curr_y += cell_h + 10

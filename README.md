<img width="2255" height="1271" alt="dsa" src="https://github.com/user-attachments/assets/38187a77-827e-4eeb-876e-f85d3ed9d69a" />

# DSA Classroom - Offline Visual Teaching Studio

An offline, zero-cloud desktop application designed specifically for computer science professors to teach **Data Structures and Algorithms (DSA)** in university lecture halls.

Combining the functionality of **VS Code**, **Microsoft PowerPoint**, **Visualgo**, and **Microsoft Whiteboard** into a single offline tool, it has no cloud dependencies, subscriptions, accounts, or setup requirements.

---

## Table of Contents
1. [Key Philosophies](#key-philosophies)
2. [Supported DSA Modules & Data Structures](#supported-dsa-modules--data-structures)
3. [Core Feature Walkthrough](#core-feature-walkthrough)
   - [Folder-Based Explorer](#folder-based-explorer)
   - [Presentation Tab & PDF Annotator](#presentation-tab--pdf-annotator)
   - [Interactive Execution Visualizer](#interactive-execution-visualizer)
   - [Whiteboard Studio](#whiteboard-studio)
   - [DSA Complexity Cheat Sheet Editor](#dsa-complexity-cheat-sheet-editor)
4. [Keyboard and Mouse Shortcut Reference](#keyboard-and-mouse-shortcut-reference)
5. [Installation and Running from Source](#installation-and-running-from-source)
6. [Compiling to Standalone Windows EXE](#compiling-to-standalone-windows-exe)
7. [Technical Architecture](#technical-architecture)
8. [Screenshots](#screenshots)

---

## Key Philosophies

* **100% Offline & Private**: The app collects zero telemetry, requires no login, and runs entirely locally. Ideal for classroom environments with unreliable internet.
* **Direct Teaching Integration**: The app indexes a standard filesystem directory on the professor's machine containing existing slides, text documents, and Python code, immediately making them teachable without import conversion overhead.
* **Unified Workspace**: Seamless switching between PDF/PPT presentations, code editing, real-time code visual tracing, and the whiteboard.

---

## Supported DSA Modules & Data Structures

The application natively supports, parses, and visualizes standard Python data types and custom data structure implementations:
* **Primitive Types**: Python variables (`int`, `float`, `str`, `bool`, `None`).
* **Linear Structures**: Fixed-size arrays, Python dynamic lists, Stacks (LIFO), Queues (FIFO), and circular buffers.
* **Linked Structures**: Singly Linked Lists, Doubly Linked Lists.
* **Key-Value Maps**: Hash Tables, Python dictionaries.
* **Tree Structures**: Binary Trees, Binary Search Trees (BST), AVL Trees.
* **Graphs**: Adjacency lists, adjacency matrices, BFS traversal, DFS traversal.
* **Algorithms**: Linear Search, Binary Search, Sorting Algorithms (Bubble, Selection, Insertion, Merge, Quick, Heap), and recursion tree tracing.

---

## Core Feature Walkthrough

### 📁 Folder-Based Explorer
Instead of importing slides or documents individually, the professor selects a local teaching directory (e.g., `C:\Teaching\DSA\`). The explorer automatically scans and organizes files into:
* **PDFs**: Syllabus, handouts, slides.
* **PowerPoints**: `.pptx` and `.ppt` slideshows.
* **Word Files**: `.docx` and `.doc` lecture guides.
* **Python Files**: Runnable teaching scripts.
* **Whiteboards**: Saved whiteboard layouts (`.dsa-wb`).

Double-clicking any file instantly switches to its associated view tab. The sidebar is fully resizable using grabbable splitter handles.

### 📝 Presentation Tab & PDF Annotator
Opens PDF, PowerPoint, and Word documents directly.
* **Annotation overlay**: Draw red annotations or yellow highlights directly over the slide pages.
* **Laser Pointer**: Toggles a glowing red indicator following the cursor for visual lecture focus.
* **Page controls**: Seamless slide navigation via toolbar buttons, arrow keys, `Spacebar`, or `PageUp`/`PageDown`.

### 💻 Interactive Execution Visualizer
Runs Python code step-by-step with synchronized 2D/3D visualizations.
* **Settrace Tracing**: Executes compiled Python code locally inside a monitored background thread. The engine captures stdout/stderr and logs all variable states at every line.
* **60 FPS Swapping Animations**: Instantly displays positional variable updates (such as sorting swaps or pointer shifts) using smooth graphical animations.
* **📋 Copy to Whiteboard**: Convert the current visual structure (nodes as blocks, pointers as connection lines) into the whiteboard canvas in one click to write annotations directly on top of the structure.
* **Quiz Modes**: Hides variables or masks visualizer node labels to `?` to interactive-test student comprehension during line-by-step executions.
* **Live Speed Slider**: Adjust script playback intervals (200ms to 2000ms) on the fly during active execution.
* **2D / 3D projected viewports**: Toggle between a flat 2D workspace and a draggable, zoomable 3D perspective viewport.

### 🎨 Whiteboard Studio
A complete digital whiteboard designed for computer science classrooms.
* **Collapsible Options Drawer**: Toggles on the right to keep the canvas toolbar clean. Hosts save/load functions, canvas clearing, theme pickers, brush size sliders, physics switches, and manual image imports.
* **Snap Connection Lines**: Drag a line/arrow tool between whiteboard blocks (CS Nodes, Stacks, Sticky Notes) to lock them. Moving shapes stretches the connection lines automatically at 60 FPS.
* **Connection Line Drag-Moving**: Click and drag a connection line to move it, or drag its endpoints individually to reconnect or redirect.
* **Gravity Stacking Physics**: Turn on Physics to activate gravity. CS Blocks will stack cleanly inside Stack Bucket containers and repel each other to avoid overlap.
* **Clipboard Screenshots**: Copy a screenshot (e.g. `Ctrl+Alt+PrintScreen`) and paste (`Ctrl+V`) it directly onto the whiteboard canvas.
* **In-place Text Editor**: Select the Text tool and click any coordinate to begin typing notes directly without annoying pop-up inputs.
* **Automatic Theme Adaptation**: Switching the whiteboard theme between light and dark automatically flips stroke colors (e.g., black lines turn white on dark background and vice-versa) to ensure continuous readability.

### 📊 DSA Complexity Cheat Sheet Editor
A persistent reference guide is built into the execution tab.
* **Custom Rich Text Context Menu**: Right-click anywhere in the table to insert/delete table rows or columns, or create new tables entirely.
* **Auto-Saving**: Any edits or updates are automatically saved to `~/.dsa_classroom_complexity.html` and persist across application restarts.

---

## Keyboard and Mouse Shortcut Reference

### Presentation Tab
* `Right Arrow` / `Down Arrow` / `Space` / `PageDown`: Next page / slide
* `Left Arrow` / `Up Arrow` / `Backspace` / `PageUp`: Previous page / slide
* `Ctrl + Mouse Scroll`: Zoom in / Zoom out slide view

### Visualizer / Code Editor Tab
* `Ctrl + F5` / Run Button: Start executing the Python script
* `Space` / Play Button: Play / Pause step autoplay
* `F10` / Next Button: Step forward
* `F9` / Prev Button: Step backward

### Whiteboard Canvas
* `Middle Mouse Drag` / `Space + Left Mouse Drag`: Pan the canvas view
* `Mouse Scroll Wheel`: Zoom in / Zoom out of the canvas coordinate center
* `Shift + Mouse Scroll Wheel` (while items selected): Resize selected items (blocks, circles, text font sizes, images, path scales, and line stroke widths)
* `Delete`: Delete all selected items from the canvas
* `Ctrl + V`: Paste image/screenshot from system clipboard onto the canvas
* `Left Click + Drag (Select tool)`: Select multiple whiteboard items simultaneously or drag a selected shape

---

## Installation and Running from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/ebula-edu/DSA-Classroom.git
   cd DSA-Classroom
   ```
2. Install the required dependencies (ensure Python 3.10+ is installed):
   ```bash
   pip install PySide6 Pillow
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## Technical Architecture

* **UI Framework**: PySide6 (Python Qt6 bindings) styled with custom stylesheet styles and modern Fusion style rendering.
* **Code Tracing Engine**: Standard `sys.settrace()` execution monitoring. Variable extraction utilizes recursive parsing to serialize graph-like objects (e.g. Nodes referencing other Nodes) and nested collections.
* **Thread-Safe Streams**: Standard output/error redirected using a custom multi-threaded router class `ThreadRedirector`. It safely routes stream writes to thread-specific execution buffers without interfering with Qt's core logging system or deadlocking the main event loop when streams are `None` (as in compiled `--noconsole` executables).
* **Whiteboard Drawing Canvas**: Customized `QGraphicsScene` / `QGraphicsView` architecture. Handles custom item boundaries, selection states, custom serialization (exported to JSON `.dsa-wb` file formats, including base64 image streams), and custom event handling.

## Screenshots
### Home
<img width="1920" height="1056" alt="image" src="https://github.com/user-attachments/assets/a325e1ac-603b-4c81-8e8c-f94b36d0903e" />
<img width="1920" height="1057" alt="image" src="https://github.com/user-attachments/assets/3285b224-235f-4266-af63-ffd10f27ac55" />
<img width="1920" height="1056" alt="image" src="https://github.com/user-attachments/assets/0caf88b3-53b2-40ac-8be7-d297b54fc54f" />
<img width="1920" height="1056" alt="image" src="https://github.com/user-attachments/assets/da352fe6-c6d6-4397-903b-3895a6ec1741" />
<img width="1920" height="1055" alt="image" src="https://github.com/user-attachments/assets/afb90846-9bf6-4c52-8349-ad7b7b40585e" />

### Visualizations
<img width="1920" height="1056" alt="image" src="https://github.com/user-attachments/assets/fab2b475-60ab-465d-a2b1-9a2a8df2d615" />
<img width="1920" height="1058" alt="image" src="https://github.com/user-attachments/assets/6b3c32af-c5d2-4ed2-8aff-c71dbe6a2afc" />


### Whiteboards
<img width="1920" height="1056" alt="image" src="https://github.com/user-attachments/assets/bf36e5b5-35cb-4ceb-8169-ab0799ab33e2" />


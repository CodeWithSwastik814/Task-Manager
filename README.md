# 📝 Task Manager

A lightweight Python task management app with both a **CLI** and a polished **PyQt6 GUI** featuring a dark animated interface.

---

## ✨ Features

- ➕ Add tasks with **High / Medium / Low** priority
- ✅ Mark tasks as complete
- 🗑️ Delete tasks with confirmation
- 🔍 Search tasks by keyword
- 🎛️ Filter tasks by priority level
- 📂 Switch between Incomplete, Completed, and All views
- 💾 Auto-save via local `tasks.json` file
- 🎨 Animated dark-theme GUI with floating orb background

---

## 🖼️ Interface

The GUI (`Ui.py`) is built with **PyQt6** and features:

- Glass-morphism panel design
- Animated floating orb background (rendered via `QPainter`)
- Color-coded priority badges — 🔴 High · 🟡 Medium · 🟢 Low
- Live search and filter controls
- Smooth dark Fusion palette

---

## 📁 Project Structure

```
task-manager/
│
├── task_manager.py   # Core logic + CLI interface
├── Ui.py             # PyQt6 GUI frontend
└── tasks.json        # Auto-generated save file (created on first run)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PyQt6

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/task-manager.git
cd task-manager

# Install dependencies
pip install PyQt6
```

### Running the App

```bash
# Launch the GUI
python Ui.py

# Or use the CLI version
python task_manager.py
```

---

## 🖥️ CLI Usage

```
=== Task Manager ===

--- Menu ---
  1. Add Tasks
  2. Show Incomplete
  3. Complete a Task
  4. Delete a Task
  5. Show All Tasks
  6. Filter by Priority
  7. Search Tasks
  8. Quit
```

---

## 💾 Data Storage

Tasks are saved automatically to `tasks.json` in the project directory:

```json
{
  "incomplete": [
    { "name": "Buy groceries", "priority": "high" }
  ],
  "complete": [
    { "name": "Read docs", "priority": "low" }
  ]
}
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3 | Core language |
| PyQt6 | GUI framework |
| JSON | Local data persistence |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

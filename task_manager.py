import json
import os

SAVE_FILE = "tasks.json"

incomplete_tasks = []
complete_tasks = []

PRIORITIES = ["high", "medium", "low"]
PRIORITY_LABEL = {"high": "[HIGH]", "medium": "[MED] ", "low": "[LOW] "}


# -- JSON STORAGE --------------------------------------------------------------

def load_tasks():
    """Load tasks from JSON file on startup."""
    global incomplete_tasks, complete_tasks
    if not os.path.exists(SAVE_FILE):
        return
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        incomplete_tasks = data.get("incomplete", [])
        complete_tasks = data.get("complete", [])
        print(f"Tasks loaded from {SAVE_FILE}.")
    except (json.JSONDecodeError, KeyError):
        print("Warning: Could not read save file. Starting fresh.")


def save_tasks():
    """Save tasks to JSON file."""
    data = {
        "incomplete": incomplete_tasks,
        "complete": complete_tasks,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)


# -- DISPLAY HELPERS -----------------------------------------------------------

def format_task(task):
    """Format a task dict into a display string."""
    label = PRIORITY_LABEL.get(task.get("priority", "medium"), "[MED] ")
    return f"{label} {task['name']}"


def show_incomplete(tasks=None):
    """Print incomplete tasks. Optionally pass a filtered subset."""
    source = tasks if tasks is not None else incomplete_tasks
    if not source:
        print("  (none)")
        return
    for i, task in enumerate(source, start=1):
        print(f"  {i}. {format_task(task)}")


def show_all_tasks():
    print("\n--- All Tasks ---")
    print("Incomplete:")
    show_incomplete()
    print("Completed:")
    if complete_tasks:
        for i, task in enumerate(complete_tasks, start=1):
            print(f"  {i}. {format_task(task)}")
    else:
        print("  (none)")


# -- CORE FEATURES -------------------------------------------------------------

def pick_priority():
    """Prompt user to choose a priority level."""
    print("  Priority: 1) High  2) Medium  3) Low")
    choice = input("  Choose priority (default = medium): ").strip()
    return {"1": "high", "2": "medium", "3": "low"}.get(choice, "medium")


def add_tasks():
    while True:
        name = input("Enter task name (or 'stop' to finish): ").strip()
        if name.lower() == "stop":
            break
        if not name:
            continue
        priority = pick_priority()
        incomplete_tasks.append({"name": name, "priority": priority})
        save_tasks()
        print(f'  Task "{name}" [{priority}] added.')

# -- COMPLETE TASK ------------------------------------------------------

def complete_task():
    print("\nIncomplete Tasks:")
    show_incomplete()
    if not incomplete_tasks:
        return

    while True:
        comp = input("Enter task number to complete (or 'stop'): ").strip()
        if comp.lower() == "stop":
            break
        if not comp.isdigit():
            print("Please enter a valid number.")
            continue
        index = int(comp) - 1
        if 0 <= index < len(incomplete_tasks):
            done = incomplete_tasks.pop(index)
            complete_tasks.append(done)
            save_tasks()
            print(f'  Task "{done["name"]}" marked as complete.')
            print("\nRemaining:")
            show_incomplete()
            if not incomplete_tasks:
                print("All tasks completed!")
                break
        else:
            print(f"Invalid number. Enter 1–{len(incomplete_tasks)}.")

# -- DELETE TASK ------------------------------------------------------

def delete_task():
    print("\nIncomplete Tasks:")
    show_incomplete()
    if not incomplete_tasks:
        return

    x = input("Enter task number to delete: ").strip()
    if not x.isdigit():
        print("Please enter a valid number.")
        return
    index = int(x) - 1
    if 0 <= index < len(incomplete_tasks):
        removed = incomplete_tasks.pop(index)
        save_tasks()
        print(f'  Task "{removed["name"]}" deleted.')
    else:
        print(f"Invalid number. Enter 1–{len(incomplete_tasks)}.")


# -- PRIORITY FILTER ------------------------------------------------------

def filter_by_priority():
    print("\n  Filter by: 1) High  2) Medium  3) Low")
    choice = input("  Choose: ").strip()
    level = {"1": "high", "2": "medium", "3": "low"}.get(choice)
    if not level:
        print("Invalid choice.")
        return
    filtered = [t for t in incomplete_tasks if t.get("priority") == level]
    print(f"\nIncomplete tasks with [{level.upper()}] priority:")
    if filtered:
        for i, task in enumerate(filtered, start=1):
            print(f"  {i}. {task['name']}")
    else:
        print("  (none)")


# -- SEARCH ---------------------------------------------------------------

def search_tasks():
    keyword = input("Search keyword: ").strip().lower()
    if not keyword:
        return

    inc_matches = [t for t in incomplete_tasks if keyword in t["name"].lower()]
    com_matches = [t for t in complete_tasks   if keyword in t["name"].lower()]

    print(f"\nResults for '{keyword}':")
    print("  Incomplete:")
    if inc_matches:
        for t in inc_matches:
            print(f"    - {format_task(t)}")
    else:
        print("    (none)")

    print("  Completed:")
    if com_matches:
        for t in com_matches:
            print(f"    - {format_task(t)}")
    else:
        print("    (none)")


# -- MAIN ----------------------------------------------------------------------

def main():
    load_tasks()
    print("=== Task Manager ===")

    menu = {
        "1": ("Add Tasks",           add_tasks),
        "2": ("Show Incomplete",     lambda: (print("\nIncomplete Tasks:"), show_incomplete())),
        "3": ("Complete a Task",     complete_task),
        "4": ("Delete a Task",       delete_task),
        "5": ("Show All Tasks",      show_all_tasks),
        "6": ("Filter by Priority",  filter_by_priority),
        "7": ("Search Tasks",        search_tasks),
        "8": ("Quit",                None),
    }

    while True:
        print("\n--- Menu ---")
        for key, (label, _) in menu.items():
            print(f"  {key}. {label}")

        choice = input("Choose an option: ").strip()
        if choice == "8":
            save_tasks()
            print("Tasks saved. Goodbye!")
            break
        elif choice in menu:
            menu[choice][1]()
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
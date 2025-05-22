#!/bin/bash
# Container Farm Control System - Student Activity Logger
# This script sets up activity logging for student interactions
# Install in SCRIPTS_DIR

INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"
LOGS_DIR="${INSTALL_DIR}/logs"

# Create logs directory if it doesn't exist
mkdir -p "${LOGS_DIR}/student_logs"

# Create a function for Mycodo to call on dashboard actions
cat > "${SCRIPTS_DIR}/log_activity.py" << 'EOF'
#!/usr/bin/env python3
"""
Log student actions in the Mycodo dashboard
This is called by Mycodo's action system

Usage: Called via Mycodo Actions with parameters:
    python3 /opt/container-farm-control/scripts/log_activity.py "student_name" "action" "details"
"""

import sys
import os
import datetime
import json

def log_activity(student_name, action, details=""):
    """Log a student activity to the appropriate files"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = "/opt/container-farm-control/logs/student_logs"
    
    # Ensure the directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Get project info
    project_name = "Container Farm"
    try:
        with open("/opt/container-farm-control/configs/project_name.txt", "r") as f:
            project_name = f.read().strip()
    except:
        pass
    
    # Create student's log file if it doesn't exist
    student_file = os.path.join(log_dir, f"{student_name.replace(' ', '_').lower()}.txt")
    if not os.path.exists(student_file):
        with open(student_file, "w") as f:
            f.write(f"Activity Log for {student_name} - {project_name}\n")
            f.write("=" * 50 + "\n\n")
    
    # Write to student's log file
    with open(student_file, "a") as f:
        f.write(f"{timestamp} - {action}: {details}\n")
    
    # Also write to a consolidated log file
    with open(os.path.join(log_dir, "all_activities.txt"), "a") as f:
        f.write(f"{timestamp} - {student_name} - {action}: {details}\n")
    
    # Write to JSON for data analysis
    json_file = os.path.join(log_dir, "activities.json")
    activities = []
    
    # Load existing data if present
    if os.path.exists(json_file):
        try:
            with open(json_file, "r") as f:
                activities = json.load(f)
        except:
            activities = []
    
    # Add new activity
    activities.append({
        "timestamp": timestamp,
        "student": student_name,
        "action": action,
        "details": details
    })
    
    # Save updated data
    with open(json_file, "w") as f:
        json.dump(activities, f, indent=2)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: log_activity.py student_name action [details]")
        sys.exit(1)
    
    student_name = sys.argv[1]
    action = sys.argv[2]
    details = sys.argv[3] if len(sys.argv) > 3 else ""
    
    log_activity(student_name, action, details)
EOF

chmod +x "${SCRIPTS_DIR}/log_activity.py"

# Create hook for Mycodo to log button clicks and other actions
# This is a configuration that will be imported by Mycodo
cat > "${CONFIG_DIR}/activity_logging_actions.json" << EOF
{
  "actions": [
    {
      "name": "Log Light Toggle",
      "trigger": "output_change",
      "output_id": "light_relay",
      "action_type": "execute_python_code",
      "python_code": "import subprocess; subprocess.call(['/usr/bin/python3', '/opt/container-farm-control/scripts/log_activity.py', '$VIEWER_NAME', 'Toggled Lights', 'New state: $OUTPUT_STATE'])"
    },
    {
      "name": "Log Water Toggle",
      "trigger": "output_change",
      "output_id": "pump_relay",
      "action_type": "execute_python_code",
      "python_code": "import subprocess; subprocess.call(['/usr/bin/python3', '/opt/container-farm-control/scripts/log_activity.py', '$VIEWER_NAME', 'Toggled Water Pump', 'New state: $OUTPUT_STATE'])"
    },
    {
      "name": "Log Note Added",
      "trigger": "note_add",
      "action_type": "execute_python_code",
      "python_code": "import subprocess; subprocess.call(['/usr/bin/python3', '/opt/container-farm-control/scripts/log_activity.py', '$VIEWER_NAME', 'Added Note', '$NOTE_TEXT'[:50]])"
    }
  ]
}
EOF

# Create student authentication script (for future implementation)
cat > "${SCRIPTS_DIR}/student_login.py" << 'EOF'
#!/usr/bin/env python3
"""
Simple student login system that logs the student name for activity tracking
This is a placeholder for more robust authentication
"""

import sys
import os
import time
import json

STUDENTS_FILE = "/opt/container-farm-control/configs/students.json"

def load_students():
    """Load student list from JSON file"""
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    
    # Default empty student list
    return {"students": []}

def save_students(students_data):
    """Save student list to JSON file"""
    with open(STUDENTS_FILE, "w") as f:
        json.dump(students_data, f, indent=2)

def add_student(name, grade=None, id=None):
    """Add a new student to the tracking system"""
    students_data = load_students()
    
    # Check if student already exists
    for student in students_data["students"]:
        if student["name"].lower() == name.lower():
            print(f"Student {name} already exists!")
            return False
    
    # Create new student entry
    new_student = {
        "name": name,
        "grade": grade,
        "id": id or str(int(time.time())),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    students_data["students"].append(new_student)
    save_students(students_data)
    print(f"Added student: {name}")
    return True

def list_students():
    """List all registered students"""
    students_data = load_students()
    
    if not students_data["students"]:
        print("No students registered yet.")
        return
    
    print("\nRegistered Students:")
    print("=" * 40)
    for i, student in enumerate(students_data["students"], 1):
        print(f"{i}. {student['name']} (Grade: {student.get('grade', 'N/A')})")
    print("")

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  student_login.py add NAME [GRADE] [ID]  - Add a new student")
        print("  student_login.py list                   - List all registered students")
        return
    
    command = sys.argv[1].lower()
    
    if command == "add" and len(sys.argv) >= 3:
        name = sys.argv[2]
        grade = sys.argv[3] if len(sys.argv) > 3 else None
        id = sys.argv[4] if len(sys.argv) > 4 else None
        add_student(name, grade, id)
    
    elif command == "list":
        list_students()
    
    else:
        print("Unknown command or missing arguments.")
        print("Usage:")
        print("  student_login.py add NAME [GRADE] [ID]  - Add a new student")
        print("  student_login.py list                   - List all registered students")

if __name__ == "__main__":
    main()
EOF

chmod +x "${SCRIPTS_DIR}/student_login.py"

# Create a simple dashboard widget to select current student
# This is more advanced and would be implemented with a full JavaScript widget

echo "Student Activity Logger installed successfully."
echo "To add students, run: sudo python3 ${SCRIPTS_DIR}/student_login.py add 'Student Name' 'Grade'"
echo "Activities will be logged to: ${LOGS_DIR}/student_logs/"

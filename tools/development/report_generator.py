#!/usr/bin/env python3
"""
Container Farm Control System - Stakeholder Report Generator
Creates professional reports for stakeholders with project information,
growth data, photos, and impact metrics.

This tool combines:
- Project description and goals
- Growth data and charts
- Photo documentation
- System performance metrics

Usage:
    python3 generate_report.py --basic       # Generate basic report
    python3 generate_report.py --full        # Generate comprehensive report
    python3 generate_report.py --educational # Generate education-focused report
    python3 generate_report.py --therapy     # Generate therapy-focused report
    python3 generate_report.py --custom      # Interactive custom report
"""

import os
import sys
import json
import argparse
import shutil
import datetime
import glob
import re
import zipfile
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("report_generator")

# Base directories
INSTALL_DIR = "/opt/container-farm-control"
CONFIG_DIR = os.path.join(INSTALL_DIR, "configs")
SCRIPTS_DIR = os.path.join(INSTALL_DIR, "scripts")
DOCS_DIR = os.path.join(INSTALL_DIR, "docs")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backups")
PHOTO_DIR = os.path.join(INSTALL_DIR, "photo_log")
REPORT_DIR = os.path.join(INSTALL_DIR, "reports")

# Ensure report directory exists
os.makedirs(REPORT_DIR, exist_ok=True)

# Function to load project configuration
def load_project_config():
    """Load project configuration from files"""
    config = {
        "project_name": "Container Farm",
        "location": "Unknown",
        "operator": "Unknown",
        "user_role": "general",
        "goal": "general",
        "system_type": "basic_monitoring",
        "date_created": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    
    # Try to load from individual files
    try:
        if os.path.exists(os.path.join(CONFIG_DIR, "project_name.txt")):
            with open(os.path.join(CONFIG_DIR, "project_name.txt"), "r") as f:
                config["project_name"] = f.read().strip()
                
        if os.path.exists(os.path.join(CONFIG_DIR, "location.txt")):
            with open(os.path.join(CONFIG_DIR, "location.txt"), "r") as f:
                config["location"] = f.read().strip()
                
        if os.path.exists(os.path.join(CONFIG_DIR, "operator.txt")):
            with open(os.path.join(CONFIG_DIR, "operator.txt"), "r") as f:
                config["operator"] = f.read().strip()
                
        if os.path.exists(os.path.join(CONFIG_DIR, "user_role.txt")):
            with open(os.path.join(CONFIG_DIR, "user_role.txt"), "r") as f:
                config["user_role"] = f.read().strip()
                
        if os.path.exists(os.path.join(CONFIG_DIR, "primary_goal.txt")):
            with open(os.path.join(CONFIG_DIR, "primary_goal.txt"), "r") as f:
                config["goal"] = f.read().strip()
                
        if os.path.exists(os.path.join(CONFIG_DIR, "selected_config.txt")):
            with open(os.path.join(CONFIG_DIR, "selected_config.txt"), "r") as f:
                config["system_type"] = f.read().strip()
                
        # Try to load learning goal for educational/therapy projects
        if os.path.exists(os.path.join(CONFIG_DIR, "learning_goal.txt")):
            with open(os.path.join(CONFIG_DIR, "learning_goal.txt"), "r") as f:
                config["learning_goal"] = f.read().strip()
                
    except Exception as e:
        logger.warning(f"Error loading project configuration: {e}")
    
    # Alternately, try to load from config.sh
    if os.path.exists(os.path.join(CONFIG_DIR, "config.sh")):
        try:
            with open(os.path.join(CONFIG_DIR, "config.sh"), "r") as f:
                config_text = f.read()
                
                # Extract values using regex
                project_name_match = re.search(r'PROJECT_NAME="([^"]*)"', config_text)
                if project_name_match:
                    config["project_name"] = project_name_match.group(1)
                    
                location_match = re.search(r'PROJECT_LOCATION="([^"]*)"', config_text)
                if location_match:
                    config["location"] = location_match.group(1)
                    
                operator_match = re.search(r'OPERATOR="([^"]*)"', config_text)
                if operator_match:
                    config["operator"] = operator_match.group(1)
                    
                role_match = re.search(r'USER_ROLE="([^"]*)"', config_text)
                if role_match:
                    config["user_role"] = role_match.group(1)
                    
                goal_match = re.search(r'PRIMARY_GOAL="([^"]*)"', config_text)
                if goal_match:
                    config["goal"] = goal_match.group(1)
                    
                type_match = re.search(r'SYSTEM_TYPE="([^"]*)"', config_text)
                if type_match:
                    config["system_type"] = type_match.group(1)
        except Exception as e:
            logger.warning(f"Error parsing config.sh: {e}")
    
    return config

# Function to load project description
def load_project_description():
    """Load project description from about_project.txt or create one"""
    if os.path.exists(os.path.join(DOCS_DIR, "about_project.txt")):
        try:
            with open(os.path.join(DOCS_DIR, "about_project.txt"), "r") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Error reading project description: {e}")
    
    # Create a basic description if none exists
    config = load_project_config()
    description = f"""===================================
ABOUT THIS CONTAINER FARM
===================================

Project: {config['project_name']}
Location: {config['location']}
Operator: {config['operator']}
User Role: {config['user_role']}
Primary Goal: {config['goal']}
System Type: {config['system_type']}
Installation Date: {config['date_created']}

This system was set up using the Open-Source Closed Environment framework,
developed to preserve autonomy and access to local control systems.

CORE PRINCIPLES:
- Data sovereignty and local control
- User autonomy and transparency
- Ethical and sustainable growing practices
"""
    
    # Add extra details based on user role
    if config['user_role'] == 'educator' or config['goal'] == 'educational':
        description += """
EDUCATIONAL FOCUS:
This system is designed to support classroom learning by:
- Providing hands-on experience with plant growth cycles
- Demonstrating environmental science principles
- Allowing data collection and analysis
- Supporting inquiry-based learning
"""
    elif config['user_role'] == 'agritherapist' or config['user_role'] == 'therapist':
        description += """
THERAPEUTIC FOCUS:
This system is specifically configured to support therapeutic practice, providing:
- Accessible interfaces for diverse participant needs
- Documentation tools for therapy session progress
- Visual tracking of plant growth for participant engagement
- Multi-sensory growing experiences
"""
    
    return description

# Function to get system performance metrics
def get_system_metrics():
    """
    Gather system performance metrics
    This would ideally pull from Mycodo, but we'll simulate for now
    """
    # Simulated metrics - in production would connect to Mycodo database
    return {
        "system_uptime": "27 days, 4 hours",
        "temperature_avg": "23.5°C",
        "humidity_avg": "63.2%",
        "water_usage": "12.4 liters",
        "energy_usage": "8.2 kWh",
        "light_hours": "14 hours/day",
        "alerts": "2 temperature warnings, 1 humidity warning",
        "maintenance": "Last performed: 2023-04-12"
    }

# Function to find and copy photos
def gather_photos(max_photos=15):
    """
    Find and copy photos for the report
    Returns the list of copied photo paths
    """
    photo_dir = os.path.join(REPORT_DIR, "temp", "photos")
    os.makedirs(photo_dir, exist_ok=True)
    
    # Find photos
    photos = []
    
    # Check for photo_log directory
    if os.path.exists(PHOTO_DIR):
        # Get jpg files, sorted by date (newest first)
        jpg_files = sorted(
            glob.glob(os.path.join(PHOTO_DIR, "*.jpg")),
            key=os.path.getmtime,
            reverse=True
        )
        
        # Filter out thumbnail files
        jpg_files = [f for f in jpg_files if "thumb" not in os.path.basename(f)]
        
        # Take the newest max_photos
        jpg_files = jpg_files[:max_photos]
        
        # Copy photos to report directory
        for i, photo in enumerate(jpg_files):
            dest = os.path.join(photo_dir, f"photo_{i+1}{os.path.splitext(photo)[1]}")
            shutil.copy2(photo, dest)
            photos.append(dest)
    
    return photos

# Function to generate the report HTML
def generate_html_report(report_type="basic"):
    """
    Generate HTML report
    
    Args:
        report_type: Type of report to generate (basic, full, educational, therapy)
        
    Returns:
        Path to the generated HTML file
    """
    # Create temporary directory for report files
    temp_dir = os.path.join(REPORT_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Load configuration
    config = load_project_config()
    description = load_project_description()
    metrics = get_system_metrics()
    
    # Gather photos
    photos = gather_photos(max_photos=10)
    
    # Determine report filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = os.path.join(temp_dir, f"{config['project_name'].replace(' ', '_')}_{report_type}_report.html")
    
    # Get extra content based on report type
    extra_content = ""
    if report_type == "educational":
        if os.path.exists(os.path.join(DOCS_DIR, "lesson_plans")):
            lesson_plans = glob.glob(os.path.join(DOCS_DIR, "lesson_plans", "markdown", "*.md"))
            if lesson_plans:
                extra_content += "<h2>Available Lesson Plans</h2>\n<ul>\n"
                for plan in lesson_plans[:5]:  # Show up to 5 lesson plans
                    plan_name = os.path.splitext(os.path.basename(plan))[0]
                    extra_content += f"<li>{plan_name.replace('_', ' ').title()}</li>\n"
                extra_content += "</ul>\n"
    
    elif report_type == "therapy":
        # Add therapy-specific content like session logs if available
        if "learning_goal" in config:
            extra_content += f"<h2>Therapeutic Goal</h2>\n<p>{config['learning_goal']}</p>\n"
        
        # Check if we have any therapy log files
        if os.path.exists(os.path.join(INSTALL_DIR, "logs", "therapy_logs")):
            therapy_logs = glob.glob(os.path.join(INSTALL_DIR, "logs", "therapy_logs", "*.txt"))
            if therapy_logs:
                extra_content += "<h2>Recent Therapy Sessions</h2>\n<ul>\n"
                for log in sorted(therapy_logs, key=os.path.getmtime, reverse=True)[:5]:
                    log_date = datetime.datetime.fromtimestamp(os.path.getmtime(log)).strftime("%Y-%m-%d")
                    log_name = os.path.splitext(os.path.basename(log))[0]
                    extra_content += f"<li>{log_date}: {log_name.replace('_', ' ').title()}</li>\n"
                extra_content += "</ul>\n"
    
    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['project_name']} - Stakeholder Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #2c7d3d;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        h1, h2, h3 {{
            color: #2c7d3d;
        }}
        .section {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .metric-card {{
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
            background-color: white;
        }}
        .metric-card h3 {{
            margin-top: 0;
            color: #2c7d3d;
        }}
        .photo-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .photo-item {{
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
            background-color: white;
        }}
        .photo-item img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .photo-caption {{
            padding: 10px;
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
            color: #666;
        }}
        .pre {{
            white-space: pre-wrap;
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{config['project_name']}</h1>
        <p>Stakeholder Report - Generated {datetime.datetime.now().strftime("%Y-%m-%d")}</p>
    </div>
    
    <div class="section">
        <h2>Project Overview</h2>
        <p><strong>Location:</strong> {config['location']}</p>
        <p><strong>Operator:</strong> {config['operator']}</p>
        <p><strong>Type:</strong> {config['system_type'].replace('_', ' ').title()}</p>
        <p><strong>Primary Goal:</strong> {config['goal'].replace('_', ' ').title()}</p>
        <p><strong>User Role:</strong> {config['user_role'].replace('_', ' ').title()}</p>
    </div>
    
    <div class="section">
        <h2>Project Description</h2>
        <div class="pre">{description}</div>
    </div>
"""

    # Add photos if available
    if photos:
        html_content += """    <div class="section">
        <h2>Growth Documentation</h2>
        <div class="photo-grid">
"""
        for i, photo in enumerate(photos):
            photo_date = datetime.datetime.fromtimestamp(os.path.getmtime(photo)).strftime("%Y-%m-%d")
            photo_rel_path = os.path.relpath(photo, temp_dir)
            html_content += f"""            <div class="photo-item">
                <img src="{photo_rel_path}" alt="Plant Photo {i+1}">
                <div class="photo-caption">Photo taken: {photo_date}</div>
            </div>
"""
        html_content += """        </div>
    </div>
"""

    # Add system metrics
    html_content += """    <div class="section">
        <h2>System Performance</h2>
        <div class="metrics">
"""

    for key, value in metrics.items():
        display_name = key.replace("_", " ").title()
        html_content += f"""            <div class="metric-card">
                <h3>{display_name}</h3>
                <p>{value}</p>
            </div>
"""

    html_content += """        </div>
    </div>
"""

    # Add extra content based on report type
    if extra_content:
        html_content += f"""    <div class="section">
        <h2>Additional Information</h2>
        {extra_content}
    </div>
"""

    # Add footer
    html_content += f"""    <div class="footer">
        <p>This report was automatically generated by the Container Farm Control System.</p>
        <p>Report Type: {report_type.title()} | Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
</body>
</html>"""

    # Write HTML to file
    with open(html_file, "w") as f:
        f.write(html_content)
    
    return html_file

# Function to create PDF from HTML
def convert_to_pdf(html_file):
    """
    Convert HTML report to PDF if possible
    
    Args:
        html_file: Path to HTML file
        
    Returns:
        Path to PDF file or None if conversion fails
    """
    pdf_file = html_file.replace(".html", ".pdf")
    
    # Try using wkhtmltopdf if available
    if shutil.which("wkhtmltopdf"):
        try:
            subprocess.run(["wkhtmltopdf", html_file, pdf_file], check=True)
            logger.info(f"PDF report generated: {pdf_file}")
            return pdf_file
        except Exception as e:
            logger.warning(f"Error generating PDF with wkhtmltopdf: {e}")
    
    # Try using weasyprint if available
    try:
        from weasyprint import HTML
        HTML(html_file).write_pdf(pdf_file)
        logger.info(f"PDF report generated: {pdf_file}")
        return pdf_file
    except ImportError:
        logger.warning("WeasyPrint not installed, skipping PDF generation")
    except Exception as e:
        logger.warning(f"Error generating PDF with WeasyPrint: {e}")
    
    # Couldn't generate PDF
    logger.warning("PDF generation failed. To enable PDF reports, install wkhtmltopdf or WeasyPrint")
    return None

# Function to create report zip file
def create_report_zip(html_file, pdf_file=None):
    """
    Create a zip file containing the report and any supporting files
    
    Args:
        html_file: Path to HTML report file
        pdf_file: Optional path to PDF report file
        
    Returns:
        Path to the created zip file
    """
    # Determine zip file path
    config = load_project_config()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{config['project_name'].replace(' ', '_')}_{timestamp}_report.zip"
    zip_path = os.path.join(REPORT_DIR, zip_filename)
    
    # Create zip file
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        # Add HTML report
        zip_file.write(html_file, arcname=os.path.basename(html_file))
        
        # Add PDF report if available
        if pdf_file and os.path.exists(pdf_file):
            zip_file.write(pdf_file, arcname=os.path.basename(pdf_file))
        
        # Add photos
        photos_dir = os.path.join(os.path.dirname(html_file), "photos")
        if os.path.exists(photos_dir):
            for photo in os.listdir(photos_dir):
                photo_path = os.path.join(photos_dir, photo)
                if os.path.isfile(photo_path):
                    zip_file.write(photo_path, arcname=os.path.join("photos", photo))
        
        # Add project description
        about_project = os.path.join(DOCS_DIR, "about_project.txt")
        if os.path.exists(about_project):
            zip_file.write(about_project, arcname="about_project.txt")
        
        # Add system summary
        summary_file = os.path.join(INSTALL_DIR, "project_summary.txt")
        if os.path.exists(summary_file):
            zip_file.write(summary_file, arcname="project_summary.txt")
    
    logger.info(f"Report zip file created: {zip_path}")
    return zip_path

# Main function to generate report
def generate_report(report_type="basic", cleanup=True):
    """
    Generate a stakeholder report
    
    Args:
        report_type: Type of report to generate (basic, full, educational, therapy)
        cleanup: Whether to clean up temporary files
        
    Returns:
        Path to the generated zip file
    """
    logger.info(f"Generating {report_type} report...")
    
    # Create HTML report
    html_file = generate_html_report(report_type)
    
    # Try to create PDF
    pdf_file = convert_to_pdf(html_file)
    
    # Create zip file
    zip_file = create_report_zip(html_file, pdf_file)
    
    # Clean up temporary files
    if cleanup:
        try:
            shutil.rmtree(os.path.join(REPORT_DIR, "temp"))
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")
    
    return zip_file

# Interactive report generation
def interactive_report():
    """Interactive custom report generation"""
    print("\n===== Container Farm Stakeholder Report Generator =====\n")
    
    # Load project info
    config = load_project_config()
    print(f"Project: {config['project_name']}")
    print(f"Location: {config['location']}")
    print(f"Type: {config['system_type'].replace('_', ' ').title()}")
    print()
    
    # Get report type
    print("Select report type:")
    print("1. Basic Report - Project info and photos only")
    print("2. Full Report - Comprehensive system information")
    print("3. Educational Report - Focused on learning outcomes")
    print("4. Therapy Report - Focused on therapeutic outcomes")
    
    while True:
        try:
            choice = int(input("\nEnter choice [1-4]: "))
            if 1 <= choice <= 4:
                break
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")
    
    report_types = ["basic", "full", "educational", "therapy"]
    report_type = report_types[choice - 1]
    
    # Get photo inclusion
    include_photos = input("\nInclude growth photos? (y/n) [y]: ").lower() != 'n'
    
    # Get number of photos if including
    max_photos = 10
    if include_photos:
        try:
            max_photos = int(input("\nMaximum number of photos to include [10]: ") or "10")
        except ValueError:
            print("Using default of 10 photos.")
    
    # Generate report
    print("\nGenerating report...")
    
    # In interactive mode, we need to customize the report generation
    # Here we would add code to customize based on user choices
    # For now, we'll just call the standard function
    zip_file = generate_report(report_type)
    
    print(f"\nReport generated successfully!\nLocation: {zip_file}")
    
    return zip_file

# Parse command line arguments
def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Container Farm Stakeholder Report Generator")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--basic", action="store_true", help="Generate basic report")
    group.add_argument("--full", action="store_true", help="Generate comprehensive report")
    group.add_argument("--educational", action="store_true", help="Generate education-focused report")
    group.add_argument("--therapy", action="store_true", help="Generate therapy-focused report")
    group.add_argument("--custom", action="store_true", help="Generate custom report interactively")
    
    return parser.parse_args()

# Main function
def main():
    """Main function"""
    args = parse_args()
    
    # Determine report type
    if args.basic:
        report_type = "basic"
    elif args.full:
        report_type = "full"
    elif args.educational:
        report_type = "educational"
    elif args.therapy:
        report_type = "therapy"
    elif args.custom:
        interactive_report()
        return
    else:
        # Default to basic report
        report_type = "basic"
    
    # Generate report
    zip_file = generate_report(report_type)
    
    print(f"Report generated successfully!\nLocation: {zip_file}")

if __name__ == "__main__":
    main()

#!/bin/bash
# Container Farm Control System - Offline Curriculum Binder
# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)" >&2
  exit 1
fi
# This script creates a system for managing offline lesson plans and curricula
# Install in SCRIPTS_DIR

INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"
DOCS_DIR="${INSTALL_DIR}/docs"
LESSON_DIR="${DOCS_DIR}/lesson_plans"
INDEX_DIR="${LESSON_DIR}/index"

# Create necessary directories
mkdir -p "${LESSON_DIR}"
mkdir -p "${INDEX_DIR}"
mkdir -p "${LESSON_DIR}/pdf"
mkdir -p "${LESSON_DIR}/markdown"
mkdir -p "${LESSON_DIR}/html"
mkdir -p "${LESSON_DIR}/images"

# Create Python script for importing and indexing lesson plans
cat > "${SCRIPTS_DIR}/lesson_manager.py" << 'EOF'
#!/usr/bin/env python3
"""
Lesson Plan Manager for Container Farm Control System
Manages importing, indexing, and organizing curriculum materials

This tool automatically indexes PDF and Markdown files, extracts metadata,
and creates a searchable catalog of educational materials.
"""

import os
import sys
import json
import re
import shutil
import argparse
import datetime
import hashlib
import subprocess
from pathlib import Path

INSTALL_DIR = "/opt/container-farm-control"
DOCS_DIR = os.path.join(INSTALL_DIR, "docs")
LESSON_DIR = os.path.join(DOCS_DIR, "lesson_plans")
INDEX_DIR = os.path.join(LESSON_DIR, "index")
PDF_DIR = os.path.join(LESSON_DIR, "pdf")
MD_DIR = os.path.join(LESSON_DIR, "markdown")
HTML_DIR = os.path.join(LESSON_DIR, "html")
IMG_DIR = os.path.join(LESSON_DIR, "images")

def ensure_directories():
    """Ensure all required directories exist"""
    for directory in [LESSON_DIR, INDEX_DIR, PDF_DIR, MD_DIR, HTML_DIR, IMG_DIR]:
        os.makedirs(directory, exist_ok=True)

def get_file_hash(file_path):
    """Generate a hash for a file to track duplicates"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def extract_pdf_metadata(pdf_path):
    """Extract metadata from PDF file using pdfinfo if available"""
    metadata = {
        "title": os.path.basename(pdf_path).replace(".pdf", ""),
        "date_added": datetime.datetime.now().strftime("%Y-%m-%d"),
        "file_type": "pdf",
        "size": os.path.getsize(pdf_path),
        "pages": 0,
        "author": "Unknown",
        "keywords": [],
        "description": ""
    }
    
    try:
        # Try to use pdfinfo if available
        if shutil.which("pdfinfo"):
            output = subprocess.check_output(["pdfinfo", pdf_path], 
                                           stderr=subprocess.STDOUT,
                                           universal_newlines=True)
            
            # Extract common metadata fields
            title_match = re.search(r"Title:\s*(.*)", output)
            if title_match and title_match.group(1).strip():
                metadata["title"] = title_match.group(1).strip()
                
            author_match = re.search(r"Author:\s*(.*)", output)
            if author_match and author_match.group(1).strip():
                metadata["author"] = author_match.group(1).strip()
                
            pages_match = re.search(r"Pages:\s*(\d+)", output)
            if pages_match:
                metadata["pages"] = int(pages_match.group(1))
                
            keywords_match = re.search(r"Keywords:\s*(.*)", output)
            if keywords_match and keywords_match.group(1).strip():
                metadata["keywords"] = [k.strip() for k in keywords_match.group(1).split(",")]
                
            # Optional: extract text for content indexing (requires pdftotext)
            if shutil.which("pdftotext"):
                text_output = subprocess.check_output(["pdftotext", "-layout", "-f", "1", "-l", "2", pdf_path, "-"],
                                                  stderr=subprocess.DEVNULL,
                                                  universal_newlines=True)
                # Get first 200 characters as description
                clean_text = re.sub(r'\s+', ' ', text_output).strip()
                metadata["description"] = clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
    except:
        # If pdfinfo fails, we'll use the default metadata
        pass
    
    return metadata

def extract_markdown_metadata(md_path):
    """Extract metadata from markdown file"""
    metadata = {
        "title": os.path.basename(md_path).replace(".md", ""),
        "date_added": datetime.datetime.now().strftime("%Y-%m-%d"),
        "file_type": "markdown",
        "size": os.path.getsize(md_path),
        "author": "Unknown",
        "keywords": [],
        "description": ""
    }
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Look for YAML front matter or HTML comments with metadata
            title_match = re.search(r"title:\s*(.*?)$|<!--\s*Title:\s*(.*?)\s*-->", content, re.MULTILINE)
            if title_match:
                title = title_match.group(1) or title_match.group(2)
                if title and title.strip():
                    metadata["title"] = title.strip()
            
            author_match = re.search(r"author:\s*(.*?)$|<!--\s*Author:\s*(.*?)\s*-->", content, re.MULTILINE)
            if author_match:
                author = author_match.group(1) or author_match.group(2)
                if author and author.strip():
                    metadata["author"] = author.strip()
            
            # Extract tags or keywords
            keywords_match = re.search(r"keywords:\s*(.*?)$|tags:\s*(.*?)$|<!--\s*Keywords:\s*(.*?)\s*-->", content, re.MULTILINE)
            if keywords_match:
                keywords = keywords_match.group(1) or keywords_match.group(2) or keywords_match.group(3)
                if keywords and keywords.strip():
                    metadata["keywords"] = [k.strip() for k in keywords.split(",")]
            
            # Extract description or summary
            desc_match = re.search(r"description:\s*(.*?)$|summary:\s*(.*?)$|<!--\s*Description:\s*(.*?)\s*-->", content, re.MULTILINE)
            if desc_match:
                desc = desc_match.group(1) or desc_match.group(2) or desc_match.group(3)
                if desc and desc.strip():
                    metadata["description"] = desc.strip()
            else:
                # If no explicit description, use first paragraph
                paragraphs = re.findall(r"^(?!#|>|```)(.*?)$", content, re.MULTILINE)
                if paragraphs:
                    first_para = next((p for p in paragraphs if p.strip()), "")
                    if first_para:
                        metadata["description"] = first_para[:200] + "..." if len(first_para) > 200 else first_para
    except Exception as e:
        print(f"Error processing markdown file: {e}")
    
    return metadata

def import_file(file_path, move=True):
    """Import a lesson plan file into the system"""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    file_type = os.path.splitext(file_path)[1].lower()
    
    # Define target directory based on file type
    if file_type == ".pdf":
        target_dir = PDF_DIR
        metadata_func = extract_pdf_metadata
    elif file_type in [".md", ".markdown"]:
        target_dir = MD_DIR
        metadata_func = extract_markdown_metadata
    else:
        print(f"Unsupported file type: {file_type}. Only PDF and Markdown are supported.")
        return False
    
    # Generate file hash to check for duplicates
    file_hash = get_file_hash(file_path)
    
    # Check if file already exists in index
    index_file = os.path.join(INDEX_DIR, "lesson_index.json")
    if os.path.exists(index_file):
        try:
            with open(index_file, 'r') as f:
                index = json.load(f)
            
            # Check if hash exists
            for item in index.get("lessons", []):
                if item.get("hash") == file_hash:
                    print(f"File already exists in library: {item.get('title')}")
                    return False
        except:
            # If index is corrupted, create a new one
            index = {"lessons": []}
    else:
        index = {"lessons": []}
    
    # Extract metadata
    metadata = metadata_func(file_path)
    
    # Add hash and file path to metadata
    base_filename = os.path.basename(file_path)
    target_path = os.path.join(target_dir, base_filename)
    
    # If the file already exists in the target directory, add a timestamp to make it unique
    if os.path.exists(target_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        name, ext = os.path.splitext(base_filename)
        base_filename = f"{name}_{timestamp}{ext}"
        target_path = os.path.join(target_dir, base_filename)
    
    # Copy or move the file
    if move:
        shutil.move(file_path, target_path)
    else:
        shutil.copy2(file_path, target_path)
    
    # Update metadata with file location and hash
    metadata["file_path"] = os.path.relpath(target_path, INSTALL_DIR)
    metadata["hash"] = file_hash
    metadata["id"] = len(index["lessons"]) + 1
    
    # Add grade level and subject tags if available in the filename or path
    grade_patterns = {
        "elementary": ["elementary", "grade[1-5]", "k-5", "primary"],
        "middle": ["middle", "grade[6-8]", "6-8"],
        "high": ["high", "grade[9-12]", "9-12", "secondary"],
        "college": ["college", "university", "higher-ed"]
    }
    
    subject_patterns = {
        "science": ["science", "biology", "chemistry", "physics"],
        "math": ["math", "mathematics", "algebra", "geometry"],
        "language": ["language", "english", "writing", "reading"],
        "social": ["social", "history", "geography", "economics"],
        "agriculture": ["agriculture", "farming", "horticulture", "gardening"],
        "nutrition": ["nutrition", "food", "health", "diet"],
        "environmental": ["environmental", "ecology", "sustainability"],
        "technology": ["technology", "engineering", "coding", "robotics"]
    }
    
    file_string = os.path.basename(file_path).lower() + " " + os.path.dirname(file_path).lower()
    
    # Detect grade levels
    grade_levels = []
    for grade, patterns in grade_patterns.items():
        if any(re.search(pattern, file_string) for pattern in patterns):
            grade_levels.append(grade)
    
    # Detect subjects
    subjects = []
    for subject, patterns in subject_patterns.items():
        if any(re.search(pattern, file_string) for pattern in patterns):
            subjects.append(subject)
    
    metadata["grade_levels"] = grade_levels
    metadata["subjects"] = subjects
    
    # Add to index
    index["lessons"].append(metadata)
    
    # Save updated index
    with open(index_file, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"Imported: {metadata['title']} ({os.path.basename(target_path)})")
    return True

def generate_html_index():
    """Generate an HTML index of all lesson plans"""
    index_file = os.path.join(INDEX_DIR, "lesson_index.json")
    if not os.path.exists(index_file):
        print("No lesson plans found in the index.")
        return
    
    try:
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        lessons = index.get("lessons", [])
        if not lessons:
            print("No lesson plans found in the index.")
            return
        
        # Sort by title
        lessons.sort(key=lambda x: x.get("title", "").lower())
        
        # Generate HTML
        html_output = os.path.join(HTML_DIR, "index.html")
        with open(html_output, 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Container Farm Curriculum Binder</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c7d3d;
            border-bottom: 2px solid #2c7d3d;
            padding-bottom: 10px;
        }
        .filters {
            margin: 20px 0;
            padding: 15px;
            background: #f7f7f7;
            border-radius: 5px;
        }
        .filter-group {
            margin-bottom: 10px;
        }
        .filter-group label {
            font-weight: bold;
            margin-right: 10px;
        }
        .lesson-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .lesson-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .lesson-card h3 {
            margin-top: 0;
            color: #2c7d3d;
        }
        .lesson-card p {
            margin: 5px 0;
        }
        .lesson-card .meta {
            font-size: 0.9em;
            color: #666;
        }
        .tags {
            margin-top: 10px;
        }
        .tag {
            display: inline-block;
            background: #e1f5e1;
            border: 1px solid #c3e6cb;
            border-radius: 3px;
            padding: 2px 6px;
            margin-right: 5px;
            font-size: 0.8em;
            color: #2c7d3d;
        }
        .search-box {
            width: 100%;
            padding: 8px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .no-results {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Container Farm Curriculum Binder</h1>
    
    <div class="filters">
        <input type="text" id="searchBox" class="search-box" placeholder="Search by title, author, keywords...">
        
        <div class="filter-group">
            <label>Grade Level:</label>
            <select id="gradeFilter">
                <option value="">All Grades</option>
                <option value="elementary">Elementary</option>
                <option value="middle">Middle School</option>
                <option value="high">High School</option>
                <option value="college">College/University</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label>Subject:</label>
            <select id="subjectFilter">
                <option value="">All Subjects</option>
                <option value="science">Science</option>
                <option value="math">Math</option>
                <option value="language">Language Arts</option>
                <option value="social">Social Studies</option>
                <option value="agriculture">Agriculture</option>
                <option value="nutrition">Nutrition</option>
                <option value="environmental">Environmental Science</option>
                <option value="technology">Technology</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label>File Type:</label>
            <select id="typeFilter">
                <option value="">All Types</option>
                <option value="pdf">PDF</option>
                <option value="markdown">Markdown</option>
            </select>
        </div>
    </div>
    
    <div class="lesson-grid" id="lessonGrid">
""")
            
            # Add each lesson as a card
            for lesson in lessons:
                title = lesson.get("title", "Untitled Lesson")
                author = lesson.get("author", "Unknown")
                description = lesson.get("description", "No description available.")
                file_type = lesson.get("file_type", "unknown")
                file_path = lesson.get("file_path", "")
                keywords = lesson.get("keywords", [])
                grade_levels = lesson.get("grade_levels", [])
                subjects = lesson.get("subjects", [])
                date_added = lesson.get("date_added", "")
                
                # Create HTML for this lesson
                f.write(f"""        <div class="lesson-card" 
             data-title="{title.lower()}" 
             data-author="{author.lower()}" 
             data-type="{file_type.lower()}" 
             data-grades="{','.join(grade_levels)}" 
             data-subjects="{','.join(subjects)}"
             data-keywords="{','.join(keywords).lower()}">
            <h3>{title}</h3>
            <p class="meta">By {author} | Added: {date_added}</p>
            <p>{description}</p>
            <p><a href="../../{file_path}" target="_blank">Open {file_type.upper()} File</a></p>
            <div class="tags">
""")
                
                # Add grade level tags
                for grade in grade_levels:
                    grade_display = {
                        "elementary": "Elementary",
                        "middle": "Middle School",
                        "high": "High School",
                        "college": "College/University"
                    }.get(grade, grade.title())
                    f.write(f'                <span class="tag">{grade_display}</span>\n')
                
                # Add subject tags
                for subject in subjects:
                    subject_display = {
                        "science": "Science",
                        "math": "Math",
                        "language": "Language Arts",
                        "social": "Social Studies",
                        "agriculture": "Agriculture",
                        "nutrition": "Nutrition",
                        "environmental": "Environmental",
                        "technology": "Technology"
                    }.get(subject, subject.title())
                    f.write(f'                <span class="tag">{subject_display}</span>\n')
                
                # Add keyword tags
                for keyword in keywords[:3]:  # Limit to 3 keywords to avoid clutter
                    f.write(f'                <span class="tag">{keyword}</span>\n')
                
                f.write("""            </div>
        </div>
""")
            
            # Close HTML
            f.write("""    </div>
    <div id="noResults" class="no-results" style="display:none;">
        No matching lessons found. Try different search criteria.
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const searchBox = document.getElementById('searchBox');
            const gradeFilter = document.getElementById('gradeFilter');
            const subjectFilter = document.getElementById('subjectFilter');
            const typeFilter = document.getElementById('typeFilter');
            const lessonGrid = document.getElementById('lessonGrid');
            const noResults = document.getElementById('noResults');
            const lessonCards = document.querySelectorAll('.lesson-card');
            
            function filterLessons() {
                const searchTerm = searchBox.value.toLowerCase();
                const gradeValue = gradeFilter.value.toLowerCase();
                const subjectValue = subjectFilter.value.toLowerCase();
                const typeValue = typeFilter.value.toLowerCase();
                
                let visibleCount = 0;
                
                lessonCards.forEach(card => {
                    const title = card.dataset.title;
                    const author = card.dataset.author;
                    const type = card.dataset.type;
                    const grades = card.dataset.grades.split(',');
                    const subjects = card.dataset.subjects.split(',');
                    const keywords = card.dataset.keywords;
                    
                    // Check all filters
                    const matchesSearch = searchTerm === '' || 
                                         title.includes(searchTerm) || 
                                         author.includes(searchTerm) || 
                                         keywords.includes(searchTerm);
                    
                    const matchesGrade = gradeValue === '' || grades.includes(gradeValue);
                    const matchesSubject = subjectValue === '' || subjects.includes(subjectValue);
                    const matchesType = typeValue === '' || type === typeValue;
                    
                    // Show/hide based on matches
                    if (matchesSearch && matchesGrade && matchesSubject && matchesType) {
                        card.style.display = 'block';
                        visibleCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });
                
                // Show/hide "no results" message
                if (visibleCount === 0) {
                    noResults.style.display = 'block';
                    lessonGrid.style.display = 'none';
                } else {
                    noResults.style.display = 'none';
                    lessonGrid.style.display = 'grid';
                }
            }
            
            // Add event listeners to filter controls
            searchBox.addEventListener('input', filterLessons);
            gradeFilter.addEventListener('change', filterLessons);
            subjectFilter.addEventListener('change', filterLessons);
            typeFilter.addEventListener('change', filterLessons);
        });
    </script>
</body>
</html>""")
        
        print(f"HTML index generated: {html_output}")
        
        # Create a symlink to the HTML index file at the top level for easy access
        symlink_path = os.path.join(LESSON_DIR, "index.html")
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        os.symlink(os.path.relpath(html_output, LESSON_DIR), symlink_path)
        
    except Exception as e:
        print(f"Error generating HTML index: {e}")

def list_lessons(args):
    """List all indexed lesson plans"""
    index_file = os.path.join(INDEX_DIR, "lesson_index.json")
    if not os.path.exists(index_file):
        print("No lesson plans indexed yet.")
        return
    
    try:
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        lessons = index.get("lessons", [])
        if not lessons:
            print("No lesson plans indexed yet.")
            return
        
        # Apply filters
        if args.grade:
            lessons = [l for l in lessons if args.grade.lower() in [g.lower() for g in l.get("grade_levels", [])]]
        
        if args.subject:
            lessons = [l for l in lessons if args.subject.lower() in [s.lower() for s in l.get("subjects", [])]]
        
        if args.type:
            lessons = [l for l in lessons if l.get("file_type", "").lower() == args.type.lower()]
        
        if args.search:
            search_term = args.search.lower()
            lessons = [l for l in lessons if 
                      search_term in l.get("title", "").lower() or
                      search_term in l.get("author", "").lower() or
                      search_term in " ".join(l.get("keywords", [])).lower() or
                      search_term in l.get("description", "").lower()]
        
        # Sort by title
        lessons.sort(key=lambda x: x.get("title", "").lower())
        
        # Display results
        print(f"\nFound {len(lessons)} lesson plans:")
        print("=" * 40)
        
        for i, lesson in enumerate(lessons, 1):
            title = lesson.get("title", "Untitled")
            author = lesson.get("author", "Unknown")
            file_type = lesson.get("file_type", "").upper()
            grade_levels = ", ".join(lesson.get("grade_levels", []))
            subjects = ", ".join(lesson.get("subjects", []))
            
            print(f"{i}. {title} ({file_type})")
            print(f"   Author: {author}")
            if grade_levels:
                print(f"   Grade Levels: {grade_levels}")
            if subjects:
                print(f"   Subjects: {subjects}")
            print(f"   Path: {lesson.get('file_path', '')}")
            print()
    
    except Exception as e:
        print(f"Error listing lessons: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Container Farm Curriculum Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import a lesson plan file")
    import_parser.add_argument("file", help="Path to the file to import")
    import_parser.add_argument("--copy", action="store_true", help="Copy the file instead of moving it")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List indexed lesson plans")
    list_parser.add_argument("--grade", help="Filter by grade level (elementary, middle, high, college)")
    list_parser.add_argument("--subject", help="Filter by subject")
    list_parser.add_argument("--type", help="Filter by file type (pdf, markdown)")
    list_parser.add_argument("--search", help="Search in title, author, and keywords")
    
    # Index command
    subparsers.add_parser("index", help="Regenerate the HTML index")
    
    # Batch import command
    batch_parser = subparsers.add_parser("batch", help="Import all files in a directory")
    batch_parser.add_argument("directory", help="Directory containing files to import")
    batch_parser.add_argument("--copy", action="store_true", help="Copy files instead of moving them")
    
    args = parser.parse_args()
    
    # Ensure all directories exist
    ensure_directories()
    
    if args.command == "import":
        import_file(args.file, not args.copy)
        generate_html_index()
    
    elif args.command == "list":
        list_lessons(args)
    
    elif args.command == "index":
        generate_html_index()
    
    elif args.command == "batch":
        if not os.path.isdir(args.directory):
            print(f"Error: {args.directory} is not a directory")
            return
        
        imported = 0
        for file in os.listdir(args.directory):
            file_path = os.path.join(args.directory, file)
            if os.path.isfile(file_path) and file.lower().endswith((".pdf", ".md", ".markdown")):
                if import_file(file_path, not args.copy):
                    imported += 1
        
        print(f"Imported {imported} files")
        if imported > 0:
            generate_html_index()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
EOF

chmod +x "${SCRIPTS_DIR}/lesson_manager.py"

# Create sample lesson plan markdown files
mkdir -p "${LESSON_DIR}/markdown"

# Sample Lesson 1
cat > "${LESSON_DIR}/markdown/plant_growth_cycle.md" << 'EOF'
---
title: Understanding Plant Growth Cycles
author: Dr. Sarah Johnson
keywords: botany, plant life, seeds, germination, elementary science
grade_levels: elementary, middle
subjects: science, agriculture
description: A basic introduction to plant growth cycles for elementary and middle school students.
---

# Understanding Plant Growth Cycles

## Overview
This lesson introduces students to the basic stages of plant growth from seed to mature plant. Students will observe seeds sprouting and track plant development over time using the Container Farm system.

## Learning Objectives
By the end of this lesson, students will be able to:
- Identify the main stages of plant growth
- Describe what plants need to grow
- Observe and document changes in plant development
- Collect and analyze growth data

## Materials Needed
- Container Farm growing system
- Various seeds (lettuce, basil, and radishes recommended)
- Magnifying glasses
- Plant growth observation journals
- Rulers for measuring plant height

## Lesson Plan

### Day 1: Introduction (30 minutes)
1. Introduce the concept of plant life cycles
2. Show examples of different seeds
3. Discuss what plants need to grow (light, water, nutrients)
4. Plant seeds in the Container Farm system
5. Set up observation journals

### Days 2-14: Observation Period
1. Daily 10-minute observation sessions
2. Students record changes in their journals
3. Measure and record plant height
4. Document environmental conditions from the Container Farm dashboard

### Day 15: Final Analysis (45 minutes)
1. Create growth charts using collected data
2. Discuss patterns observed
3. Compare growth rates between different plant types
4. Relate environmental conditions to growth patterns

## Assessment
- Journal completion and quality of observations
- Participation in class discussions
- Understanding of growth stages demonstrated in final presentation

## Extensions
- Compare plants grown in different conditions
- Investigate the effect of changing light cycles
- Plant parts identification activity
- Seed to table cooking activity

## Standards Alignment
- NGSS: LS1.C: Organization for Matter and Energy Flow in Organisms
- NGSS: LS2.A: Interdependent Relationships in Ecosystems

## Resources
- Time-lapse videos of plant growth
- Plant anatomy diagrams
- Container Farm dashboard data
EOF

# Sample Lesson 2
cat > "${LESSON_DIR}/markdown/water_cycle_investigation.md" << 'EOF'
---
title: Water Cycle Investigation with Container Farming
author: Marcus Rivera
keywords: water cycle, condensation, evaporation, precipitation, hydroponics
grade_levels: middle, high
subjects: science, environmental
description: Students investigate the water cycle using a controlled container farm environment.
---

# Water Cycle Investigation with Container Farming

## Overview
In this lesson, students use the Container Farm system to observe and measure components of the water cycle in a controlled environment. By monitoring water usage, humidity, and condensation patterns, students gain insight into water movement through plants and the environment.

## Learning Objectives
By the end of this lesson, students will be able to:
- Identify the key components of the water cycle
- Measure transpiration rates in plants
- Calculate water efficiency in a hydroponic system
- Explain how water conservation practices apply to agriculture

## Materials Needed
- Container Farm system with humidity sensors
- Growing plants (preferably at different stages)
- Graduated cylinders for water measurement
- Plastic wrap and collection containers
- Graph paper or graphing software
- Humidity monitoring app or access to dashboard

## Lesson Plan

### Day 1: Introduction to the Water Cycle (45 minutes)
1. Review water cycle components: evaporation, condensation, precipitation, collection
2. Discuss how these components appear in a controlled growing environment
3. Introduce transpiration as "plant sweat" and its role in the water cycle
4. Set up experiment protocols for measuring water movement

### Day 2: Transpiration Investigation (45 minutes)
1. Measure water levels in the system
2. Set up plant isolation chambers using plastic wrap
3. Create data collection sheets
4. Make initial observations and predictions

### Days 3-7: Monitoring and Data Collection
1. Daily measurements of:
   - Water consumption by the system
   - Humidity levels in the growing environment
   - Condensation collection in isolation chambers
   - Temperature variations
2. Record all findings in data tables

### Day 8: Analysis and Conclusions (45 minutes)
1. Compile class data
2. Create graphs showing relationships between:
   - Plant size and transpiration rate
   - Temperature and evaporation rate
   - Humidity and condensation formation
3. Calculate the water efficiency of the system
4. Compare to traditional agriculture methods

## Assessment
- Lab report including data tables and graphs
- Written explanation of water movement through the system
- Group presentation on improving water efficiency

## Extensions
- Design improvements to the Container Farm to increase water efficiency
- Investigate how different plant species affect transpiration rates
- Compare water usage between hydroponic and traditional growing
- Create a physical model of the water cycle based on observations

## Standards Alignment
- NGSS MS-ESS2-4: Water cycle and energy flow
- NGSS HS-LS2-5: Cycling of matter in ecosystems

## Resources
- Container Farm system dashboard
- NASA water cycle diagrams
- UN water conservation resources
- USDA agricultural water usage statistics
EOF

# Sample Lesson 3
cat > "${LESSON_DIR}/markdown/data_science_agriculture.md" << 'EOF'
---
title: Data Science in Agriculture
author: Dr. Lin Chen
keywords: data analysis, statistics, graphs, sensors, technology
grade_levels: high, college
subjects: technology, science, math, agriculture
description: Students use real-time sensor data from the Container Farm to develop data analysis skills.
---

# Data Science in Agriculture

## Overview
This lesson connects agricultural science with data analysis skills. Students will collect, analyze and visualize real-time environmental data from the Container Farm system, developing both computational thinking skills and agricultural understanding.

## Learning Objectives
By the end of this lesson, students will be able to:
- Extract and organize environmental sensor data
- Create meaningful data visualizations
- Identify patterns and correlations in agricultural data
- Make data-driven decisions for optimizing plant growth
- Explain how technology enhances modern agriculture

## Materials Needed
- Container Farm with active sensors
- Computers with spreadsheet software
- Data visualization tools (spreadsheet, Tableau, or coding environment)
- CSV export of previous growing data
- Plant specimens at various growth stages

## Lesson Plan

### Day 1: Introduction to Agricultural Data (45 minutes)
1. Discuss the types of data collected in modern agriculture
2. Tour the Container Farm, identifying all sensors and data sources
3. Review basic statistical concepts relevant to agricultural data
4. Demonstrate how to access and export sensor data

### Day 2: Data Collection and Organization (45 minutes)
1. Export 7-day sensor data from the Container Farm
2. Clean and organize data in spreadsheets
3. Identify variables for analysis (temperature, humidity, light intensity, etc.)
4. Create summary statistics for each variable

### Day 3: Data Visualization (45 minutes)
1. Create time-series graphs of environmental conditions
2. Develop multi-variable visualizations 
3. Identify patterns in daily and weekly cycles
4. Correlate environmental data with plant growth measurements

### Day 4: Data-Driven Decision Making (45 minutes)
1. Using visualization insights, develop hypotheses about optimal growing conditions
2. Design experimental changes to growing parameters
3. Implement changes and develop prediction models
4. Create data collection protocols for testing predictions

### Day 5: Results and Optimization (45 minutes)
1. Evaluate the impact of experimental changes
2. Refine growing parameters based on data
3. Present findings with visualizations and recommendations
4. Discuss real-world applications in precision agriculture

## Assessment
- Data analysis portfolio including visualizations
- Written report interpreting findings
- Presentation of optimization recommendations
- Peer review of data analysis methods

## Extensions
- Use programming (Python/R) for advanced statistical analysis
- Develop automated alert systems based on data thresholds
- Create machine learning models to predict optimal harvest times
- Connect with local farms to analyze their agricultural data

## Standards Alignment
- NGSS HS-LS2-2: Factors affecting biodiversity and populations in ecosystems
- CCSS.MATH.HSS.ID: Interpreting categorical and quantitative data
- ISTE 5: Computational Thinker standards

## Resources
- Container Farm sensor documentation
- Sample datasets from previous growing cycles
- Data visualization tutorials
- Precision agriculture case studies
EOF

# Create welcome page
cat > "${LESSON_DIR}/index.md" << 'EOF'
# Container Farm Curriculum Binder

Welcome to the Container Farm Curriculum Binder. This system allows you to:

- Import and organize lesson plans (.pdf and .md files)
- Search and filter lessons by grade level, subject, and keywords
- Access curriculum materials offline
- Share resources among educators

## Quick Start

To manage lesson plans, use the lesson manager script:

```bash
# Import a new lesson plan
sudo python3 /opt/container-farm-control/scripts/lesson_manager.py import /path/to/lesson.pdf

# List all available lessons
sudo python3 /opt/container-farm-control/scripts/lesson_manager.py list

# Filter lessons by grade level
sudo python3 /opt/container-farm-control/scripts/lesson_manager.py list --grade elementary

# Search for lessons by keyword
sudo python3 /opt/container-farm-control/scripts/lesson_manager.py list --search "water"

# Import all lessons from a directory
sudo python3 /opt/container-farm-control/scripts/lesson_manager.py batch /path/to/lessons
```

## Web Interface

A searchable web interface for your lessons is available at:
[Curriculum Binder Web Interface](index.html)

## Adding Your Own Lessons

You can add lessons in either PDF or Markdown format:

1. **PDF Files**: Most common for pre-made curriculum materials
2. **Markdown Files**: Easier to edit and update

For Markdown files, add metadata at the top of the file like this:

```markdown
---
title: My Lesson Title
author: Your Name
keywords: keyword1, keyword2, keyword3
grade_levels: elementary, middle
subjects: science, math
description: A brief description of the lesson.
---

# Lesson content starts here...
```

## Folder Structure

- `pdf/`: PDF lesson plans
- `markdown/`: Markdown lesson plans
- `html/`: Generated HTML index
- `images/`: Images used in lessons

This system was designed to work offline, ensuring all resources are available even without internet access.
EOF

# Convert the index.md to HTML for easy viewing
if command -v pandoc >/dev/null 2>&1; then
  pandoc "${LESSON_DIR}/index.md" -o "${LESSON_DIR}/readme.html" --standalone --metadata title="Container Farm Curriculum Binder"
  echo "Created HTML readme at ${LESSON_DIR}/readme.html"
fi

# Import the sample lessons
echo "Importing sample lesson plans..."
python3 "${SCRIPTS_DIR}/lesson_manager.py" import "${LESSON_DIR}/markdown/plant_growth_cycle.md" --copy
python3 "${SCRIPTS_DIR}/lesson_manager.py" import "${LESSON_DIR}/markdown/water_cycle_investigation.md" --copy
python3 "${SCRIPTS_DIR}/lesson_manager.py" import "${LESSON_DIR}/markdown/data_science_agriculture.md" --copy

# Generate the HTML index
python3 "${SCRIPTS_DIR}/lesson_manager.py" index

echo "Offline Curriculum Binder installed successfully!"
echo "Access the web interface at: ${LESSON_DIR}/index.html"
echo "Manage lessons with: sudo python3 ${SCRIPTS_DIR}/lesson_manager.py"
echo "Three sample lessons have been installed."

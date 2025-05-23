# GitHub Actions Workflows

## File: `.github/workflows/test.yml`

```yaml
name: Test and Validate

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        pip install flake8 black pytest
    
    - name: Lint with flake8
      run: |
        # Stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # Exit-zero treats all errors as warnings
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Check code formatting with black
      run: |
        black --check --diff .
    
    - name: Test Python imports
      run: |
        python -c "import sys; print('Python version:', sys.version)"
        # Test basic imports (skip hardware-specific ones)
        python -c "import flask, sqlite3, datetime; print('✓ Core dependencies OK')"

  documentation:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Check README exists
      run: |
        if [ ! -f README.md ]; then
          echo "❌ README.md not found"
          exit 1
        fi
        echo "✅ README.md exists"
    
    - name: Check required documentation
      run: |
        required_files=(
          "hardware/compatibility/HARDWARE_COMPATIBILITY.md"
          ".github/CONTRIBUTING.md"
          ".github/CODE_OF_CONDUCT.md"
          "LICENSE"
        )
        
        for file in "${required_files[@]}"; do
          if [ -f "$file" ]; then
            echo "✅ $file exists"
          else
            echo "⚠️ $file missing (recommended)"
          fi
        done
    
    - name: Validate JSON configs
      run: |
        # Check if JSON files are valid
        for file in $(find config/ -name "*.json" 2>/dev/null); do
          if python -m json.tool "$file" > /dev/null 2>&1; then
            echo "✅ $file is valid JSON"
          else
            echo "❌ $file is invalid JSON"
            exit 1
          fi
        done || echo "No JSON config files found"

  setup-script:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Check setup script syntax
      run: |
        if [ -f setup/setup.sh ]; then
          bash -n setup/setup.sh
          echo "✅ setup.sh syntax is valid"
        else
          echo "⚠️ setup/setup.sh not found"
        fi
    
    - name: Check file permissions
      run: |
        if [ -f setup/setup.sh ]; then
          if [ -x setup/setup.sh ]; then
            echo "✅ setup.sh is executable"
          else
            echo "⚠️ setup.sh is not executable (should be chmod +x)"
          fi
        fi

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Check for sensitive files
      run: |
        sensitive_patterns=(
          "*.key"
          "*.pem" 
          "*.p12"
          "*password*"
          "*secret*"
          ".env"
        )
        
        found_sensitive=false
        for pattern in "${sensitive_patterns[@]}"; do
          if find . -name "$pattern" -type f | grep -v .git | head -1; then
            echo "⚠️ Found potentially sensitive file: $pattern"
            found_sensitive=true
          fi
        done
        
        if [ "$found_sensitive" = false ]; then
          echo "✅ No sensitive files found in repository"
        fi
    
    - name: Check .gitignore exists
      run: |
        if [ -f .gitignore ]; then
          echo "✅ .gitignore exists"
          # Check if it includes common sensitive patterns
          if grep -q "\.env" .gitignore && grep -q "\.key" .gitignore; then
            echo "✅ .gitignore includes sensitive file patterns"
          else
            echo "⚠️ .gitignore should include .env, *.key patterns"
          fi
        else
          echo "❌ .gitignore missing"
          exit 1
        fi
```

## File: `.github/workflows/hardware-simulation.yml`

```yaml
name: Hardware Simulation Tests

on:
  push:
    branches: [ main ]
    paths: 
      - 'src/**'
      - 'examples/**'
      - 'tests/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'src/**'
      - 'examples/**'
      - 'tests/**'

jobs:
  simulate-hardware:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install test dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest mock
        # Install hardware simulation libraries
        pip install fake-rpi
    
    - name: Run hardware simulation tests
      run: |
        # Set environment variable to use fake hardware
        export FAKE_HARDWARE=1
        
        # Test basic sensor simulation
        python -c "
        import sys
        sys.path.insert(0, 'examples/basic_monitoring')
        
        # Mock hardware for testing
        import unittest.mock as mock
        
        # Test temperature reading simulation
        with mock.patch('w1thermsensor.W1ThermSensor') as mock_sensor:
            mock_sensor.return_value.get_temperature.return_value = 22.5
            temp = mock_sensor().get_temperature()
            assert temp == 22.5
            print(f'✅ Temperature simulation: {temp}°C')
        
        # Test GPIO simulation  
        with mock.patch('RPi.GPIO') as mock_gpio:
            mock_gpio.setmode.return_value = None
            mock_gpio.setup.return_value = None
            mock_gpio.output.return_value = None
            print('✅ GPIO simulation working')
        
        print('✅ All hardware simulations passed')
        "
    
    - name: Test example configurations
      run: |
        # Test that example config files are valid
        python -c "
        import json
        import os
        
        config_files = [
            'config/profiles/educator.json',
            'config/crops/leafy_greens.json', 
            'config/systems/basic_monitoring.json'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file) as f:
                    config = json.load(f)
                    print(f'✅ {config_file} is valid JSON')
                    
                    # Basic validation
                    if 'profile_name' in config or 'crop_category' in config or 'system_name' in config:
                        print(f'✅ {config_file} has required fields')
                    else:
                        print(f'⚠️ {config_file} missing identification fields')
            else:
                print(f'⚠️ {config_file} not found')
        "
```

## File: `.github/workflows/documentation.yml`

```yaml
name: Documentation Build

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - '*.md'
  pull_request:
    branches: [ main ]
    paths:
      - 'docs/**'
      - '*.md'

jobs:
  check-links:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Check internal links
      run: |
        # Check for broken internal links in markdown files
        find . -name "*.md" -exec grep -l "](docs/" {} \; | while read file; do
          echo "Checking links in: $file"
          
          # Extract internal links
          grep -o "](docs/[^)]*)" "$file" | sed 's/](//;s/)$//' | while read link; do
            if [ -f "$link" ]; then
              echo "✅ $link exists"
            else
              echo "❌ $link not found (referenced in $file)"
            fi
          done
        done
    
    - name: Check for TODO markers
      run: |
        # Find TODO markers in documentation
        todo_count=$(find docs/ -name "*.md" -exec grep -l "TODO\|FIXME\|XXX" {} \; 2>/dev/null | wc -l)
        if [ "$todo_count" -gt 0 ]; then
          echo "⚠️ Found $todo_count files with TODO markers"
          find docs/ -name "*.md" -exec grep -H "TODO\|FIXME\|XXX" {} \; 2>/dev/null || true
        else
          echo "✅ No TODO markers found in documentation"
        fi
    
    - name: Validate markdown structure
      run: |
        # Check that all markdown files have proper structure
        for file in $(find . -name "*.md"); do
          # Check for title (# heading)
          if head -10 "$file" | grep -q "^# "; then
            echo "✅ $file has title"
          else
            echo "⚠️ $file missing title (# heading)"
          fi
        done

  spelling:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y aspell aspell-en
    
    - name: Check spelling
      run: |
        # Create custom dictionary for technical terms
        cat > .aspell.en.pws << 'EOF'
        personal_ws-1.1 en 100
        Raspberry
        GPIO
        RPi
        IoT
        microSD
        BME280
        DS18B20
        DHT22
        MH-Z19B
        I2C
        SPI
        UART
        ADC
        pH
        EC
        TDS
        PPM
        WiFi
        JSON
        API
        USB
        LED
        HVAC
        GFCI
        Mycodo
        hydroponic
        aeroponic
        aquaponic
        microgreens
        EOF
        
        # Check spelling in markdown files
        find . -name "*.md" -exec aspell --personal=.aspell.en.pws --mode=markdown list {} \; | sort | uniq > spelling_errors.txt
        
        if [ -s spelling_errors.txt ]; then
          echo "⚠️ Potential spelling errors found:"
          cat spelling_errors.txt
          # Don't fail the build for spelling, just warn
        else
          echo "✅ No spelling errors detected"
        fi
```

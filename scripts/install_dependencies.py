"""
Automated dependency installation and verification
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

class DependencyInstaller:
    """Handle dependency installation and verification"""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.is_raspberry_pi = self._detect_raspberry_pi()
        self.venv_path = Path("venv")
    
    def _detect_raspberry_pi(self) -> bool:
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def check_python_version(self):
        """Verify Python version meets requirements"""
        if self.python_version < (3, 9):
            print(f"Error: Python 3.9+ required, found {self.python_version.major}.{self.python_version.minor}")
            sys.exit(1)
        print(f"✓ Python {self.python_version.major}.{self.python_version.minor} detected")
    
    def install_system_dependencies(self):
        """Install system-level dependencies"""
        print("\nInstalling system dependencies...")
        
        system_packages = [
            "python3-dev",
            "python3-pip",
            "python3-venv",
            "build-essential",
            "libssl-dev",
            "libffi-dev",
            "git",
            "redis-server",
        ]
        
        if self.is_raspberry_pi:
            system_packages.extend([
                "python3-smbus",
                "i2c-tools",
                "python3-rpi.gpio",
            ])
        
        try:
            # Update package list
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            
            # Install packages
            subprocess.run(
                ["sudo", "apt-get", "install", "-y"] + system_packages,
                check=True
            )
            print("✓ System dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"Error installing system dependencies: {e}")
            sys.exit(1)
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        if not self.venv_path.exists():
            print("\nCreating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✓ Virtual environment created")
        else:
            print("✓ Virtual environment already exists")
    
    def activate_virtual_environment(self):
        """Get activation command for virtual environment"""
        if platform.system() == "Windows":
            return str(self.venv_path / "Scripts" / "activate")
        else:
            return f"source {self.venv_path / 'bin' / 'activate'}"
    
    def install_python_dependencies(self):
        """Install Python package dependencies"""
        print("\nInstalling Python dependencies...")
        
        pip_executable = str(self.venv_path / "bin" / "pip")
        
        # Upgrade pip
        subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)
        
        # Install pip-tools
        subprocess.run([pip_executable, "install", "pip-tools"], check=True)
        
        # Compile requirements with hashes
        if Path("requirements.in").exists():
            print("Compiling requirements with hashes...")
            subprocess.run([
                str(self.venv_path / "bin" / "pip-compile"),
                "requirements.in",
                "--generate-hashes",
                "--resolver=backtracking"
            ], check=True)
        
        # Install from requirements.txt
        if Path("requirements.txt").exists():
            subprocess.run([
                pip_executable,
                "install",
                "-r", "requirements.txt",
                "--require-hashes"
            ], check=True)
            print("✓ Python dependencies installed")
        else:
            print("Warning: requirements.txt not found")
    
    def setup_raspberry_pi(self):
        """Additional setup for Raspberry Pi"""
        if not self.is_raspberry_pi:
            return
        
        print("\nConfiguring Raspberry Pi...")
        
        # Enable I2C
        subprocess.run(["sudo", "raspi-config", "nonint", "do_i2c", "0"], check=True)
        
        # Add user to gpio group
        subprocess.run(["sudo", "usermod", "-a", "-G", "gpio", os.environ.get("USER", "pi")], check=True)
        
        print("✓ Raspberry Pi configured")
        print("Note: You may need to reboot for I2C changes to take effect")
    
    def create_directory_structure(self):
        """Create required directory structure"""
        print("\nCreating directory structure...")
        
        directories = [
            "src/farm",
            "src/farm/api",
            "src/farm/sensors",
            "src/farm/actuators",
            "src/farm/controllers",
            "src/farm/database",
            "src/farm/utils",
            "tests",
            "logs",
            "data",
            "config",
            "docs",
            "scripts",
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print("✓ Directory structure created")
    
    def create_env_file(self):
        """Create .env file from template"""
        if not Path(".env").exists() and Path(".env.example").exists():
            print("\nCreating .env file...")
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ .env file created")
            print("Important: Update .env with your configuration values")
    
    def run_initial_tests(self):
        """Run basic tests to verify installation"""
        print("\nRunning installation tests...")
        
        pip_executable = str(self.venv_path / "bin" / "python")
        
        # Test imports
        test_script = """
import sys
import flask
import jwt
import RPi.GPIO as GPIO if 'RPi' in sys.modules else None
print("✓ All imports successful")
"""
        
        result = subprocess.run(
            [pip_executable, "-c", test_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Warning: Some imports failed (this is normal on non-Pi systems)")
    
    def print_next_steps(self):
        """Print next steps for user"""
        print("\n" + "="*50)
        print("Installation Complete!")
        print("="*50)
        print("\nNext steps:")
        print(f"1. Activate virtual environment: {self.activate_virtual_environment()}")
        print("2. Update configuration in .env file")
        print("3. Run database migrations: alembic upgrade head")
        print("4. Start the application: python -m farm.api")
        print("\nFor development:")
        print("- Run tests: pytest")
        print("- Format code: black src/ tests/")
        print("- Type checking: mypy src/")

def main():
    """Main installation process"""
    installer = DependencyInstaller()
    
    print("OpenSource Controlled Environments - Dependency Installation")
    print("="*60)
    
    # Run installation steps
    installer.check_python_version()
    installer.install_system_dependencies()
    installer.create_virtual_environment()
    installer.install_python_dependencies()
    installer.setup_raspberry_pi()
    installer.create_directory_structure()
    installer.create_env_file()
    installer.run_initial_tests()
    installer.print_next_steps()

if __name__ == "__main__":
    main()

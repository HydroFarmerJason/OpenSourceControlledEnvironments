# security/config.py
"""
Production-ready security configuration for OpenSourceControlledEnvironments
Implements authentication, environment variables, and security hardening
"""

import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any

from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SecurityConfig:
    """Central security configuration"""
    
    # Security settings from environment
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # Session configuration
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
    RATE_LIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '5 per minute')
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_SPECIAL_CHAR = True
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBER = True
    
    # API Key settings
    API_KEY_LENGTH = 32
    API_KEY_PREFIX = 'osce_'  # OpenSourceControlledEnvironments
    
    @classmethod
    def validate_password(cls, password: str) -> tuple[bool, str]:
        """Validate password meets security requirements"""
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters"
        
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if cls.REQUIRE_NUMBER and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if cls.REQUIRE_SPECIAL_CHAR and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"


class AuthenticationManager:
    """Handle user authentication and authorization"""
    
    def __init__(self, app: Flask = None):
        self.bcrypt = Bcrypt()
        self.users_db = {}  # In production, use proper database
        self.api_keys = {}  # In production, use proper database
        self.revoked_tokens = set()  # In production, use Redis
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize authentication with Flask app"""
        self.bcrypt.init_app(app)
        app.config['SECRET_KEY'] = SecurityConfig.SECRET_KEY
        
        # Initialize rate limiter
        self.limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[SecurityConfig.RATE_LIMIT_DEFAULT]
        )
    
    def create_user(self, username: str, password: str, role: str = 'user') -> Dict[str, Any]:
        """Create a new user with hashed password"""
        # Validate password
        is_valid, message = SecurityConfig.validate_password(password)
        if not is_valid:
            raise ValueError(message)
        
        # Check if user exists
        if username in self.users_db:
            raise ValueError("User already exists")
        
        # Hash password
        password_hash = self.bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create user
        user = {
            'id': secrets.token_hex(16),
            'username': username,
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None,
            'failed_attempts': 0,
            'locked_until': None
        }
        
        self.users_db[username] = user
        return {'id': user['id'], 'username': username, 'role': role}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data if successful"""
        user = self.users_db.get(username)
        if not user:
            return None
        
        # Check if account is locked
        if user.get('locked_until'):
            locked_until = datetime.fromisoformat(user['locked_until'])
            if datetime.utcnow() < locked_until:
                return None
            else:
                # Unlock account
                user['locked_until'] = None
                user['failed_attempts'] = 0
        
        # Verify password
        if self.bcrypt.check_password_hash(user['password_hash'], password):
            # Reset failed attempts
            user['failed_attempts'] = 0
            user['last_login'] = datetime.utcnow().isoformat()
            
            return {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        else:
            # Increment failed attempts
            user['failed_attempts'] = user.get('failed_attempts', 0) + 1
            
            # Lock account after 5 failed attempts
            if user['failed_attempts'] >= 5:
                user['locked_until'] = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
            
            return None
    
    def generate_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'role': user_data['role'],
            'exp': datetime.utcnow() + timedelta(hours=SecurityConfig.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow(),
            'jti': secrets.token_hex(16)  # JWT ID for revocation
        }
        
        return jwt.encode(payload, SecurityConfig.JWT_SECRET_KEY, algorithm=SecurityConfig.JWT_ALGORITHM)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SecurityConfig.JWT_SECRET_KEY, algorithms=[SecurityConfig.JWT_ALGORITHM])
            
            # Check if token is revoked
            if payload.get('jti') in self.revoked_tokens:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, token: str):
        """Revoke a JWT token"""
        try:
            payload = jwt.decode(token, SecurityConfig.JWT_SECRET_KEY, algorithms=[SecurityConfig.JWT_ALGORITHM])
            if 'jti' in payload:
                self.revoked_tokens.add(payload['jti'])
        except:
            pass
    
    def generate_api_key(self, user_id: str, name: str = "Default") -> str:
        """Generate API key for user"""
        api_key = f"{SecurityConfig.API_KEY_PREFIX}{secrets.token_urlsafe(SecurityConfig.API_KEY_LENGTH)}"
        
        self.api_keys[api_key] = {
            'user_id': user_id,
            'name': name,
            'created_at': datetime.utcnow().isoformat(),
            'last_used': None,
            'active': True
        }
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return associated user data"""
        key_data = self.api_keys.get(api_key)
        if not key_data or not key_data.get('active'):
            return None
        
        # Update last used
        key_data['last_used'] = datetime.utcnow().isoformat()
        
        # Get user data
        for user in self.users_db.values():
            if user['id'] == key_data['user_id']:
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
        
        return None


# Decorators for route protection
def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check JWT token first
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            auth_manager = request.app.auth_manager
            user_data = auth_manager.verify_jwt_token(token)
            if user_data:
                request.current_user = user_data
                return f(*args, **kwargs)
        
        # Check API key
        api_key = request.headers.get('X-API-Key')
        if api_key:
            auth_manager = request.app.auth_manager
            user_data = auth_manager.verify_api_key(api_key)
            if user_data:
                request.current_user = user_data
                return f(*args, **kwargs)
        
        # Check session
        if 'user_id' in session:
            # In production, verify session validity
            request.current_user = {
                'id': session['user_id'],
                'username': session.get('username'),
                'role': session.get('role', 'user')
            }
            return f(*args, **kwargs)
        
        return jsonify({'error': 'Authentication required'}), 401
    
    return decorated_function


def require_role(role: str):
    """Decorator to require specific role for routes"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if request.current_user.get('role') != role and request.current_user.get('role') != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Security headers middleware
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


# Example usage in Flask app
def create_secure_app():
    """Create Flask app with security configured"""
    app = Flask(__name__)
    
    # Configure app
    app.config.update(
        SECRET_KEY=SecurityConfig.SECRET_KEY,
        SESSION_COOKIE_SECURE=SecurityConfig.SESSION_COOKIE_SECURE,
        SESSION_COOKIE_HTTPONLY=SecurityConfig.SESSION_COOKIE_HTTPONLY,
        SESSION_COOKIE_SAMESITE=SecurityConfig.SESSION_COOKIE_SAMESITE
    )
    
    # Initialize authentication
    app.auth_manager = AuthenticationManager(app)
    
    # Add security headers
    app.after_request(add_security_headers)
    
    # Auth routes
    @app.route('/api/auth/register', methods=['POST'])
    @app.auth_manager.limiter.limit("3 per hour")
    def register():
        data = request.get_json()
        try:
            user = app.auth_manager.create_user(
                username=data['username'],
                password=data['password'],
                role=data.get('role', 'user')
            )
            return jsonify({'message': 'User created successfully', 'user': user}), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/auth/login', methods=['POST'])
    @app.auth_manager.limiter.limit(SecurityConfig.RATE_LIMIT_LOGIN)
    def login():
        data = request.get_json()
        user = app.auth_manager.authenticate_user(
            username=data.get('username'),
            password=data.get('password')
        )
        
        if user:
            token = app.auth_manager.generate_jwt_token(user)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': user
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    @app.route('/api/auth/logout', methods=['POST'])
    @require_auth
    def logout():
        # Revoke token if provided
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            app.auth_manager.revoke_token(token)
        
        # Clear session
        session.clear()
        
        return jsonify({'message': 'Logout successful'}), 200
    
    @app.route('/api/auth/api-key', methods=['POST'])
    @require_auth
    def generate_api_key():
        data = request.get_json()
        api_key = app.auth_manager.generate_api_key(
            user_id=request.current_user['id'],
            name=data.get('name', 'Default')
        )
        
        return jsonify({'api_key': api_key}), 201
    
    return app


if __name__ == '__main__':
    # Example: Create admin user for initial setup
    app = create_secure_app()
    
    # Create admin user (do this only once during setup)
    try:
        admin = app.auth_manager.create_user('admin', 'AdminPassword123!', 'admin')
        print(f"Admin user created: {admin}")
    except ValueError as e:
        print(f"Admin user creation failed: {e}")
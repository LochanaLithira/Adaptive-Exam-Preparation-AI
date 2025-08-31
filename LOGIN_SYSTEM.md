# 🔐 Login System Documentation

## Overview
This project now includes a complete authentication system with both frontend and backend components. The system provides secure user registration, login, session management, and user authentication.

## Architecture

### Backend Components (`security/auth.py`)
- **AuthManager**: Main authentication class handling user operations
- **Database**: SQLite database with users and sessions tables
- **Password Security**: SHA-256 hashing with salt for password security
- **Session Management**: Token-based sessions with expiration

### Frontend Components (`ui/LoginUI.py`)
- **Login Form**: Username/email and password authentication
- **Registration Form**: New user account creation
- **User Profile**: Post-login user interface
- **Validation**: Email format and password strength validation

### Main Application (`app.py`, `ui/Home.py`)
- **Authentication Flow**: Integrated login/logout functionality
- **Protected Routes**: Dashboard and other features require login
- **Session Persistence**: Remember me functionality

## Features

### 🔒 Security Features
- **Password Hashing**: SHA-256 with unique salt per user
- **Session Tokens**: Secure random tokens for session management
- **Session Expiration**: Configurable session timeout (24h default, 7 days with "remember me")
- **Input Validation**: Email format and password strength validation
- **SQL Injection Protection**: Parameterized queries

### 👤 User Management
- **Registration**: Create new accounts with validation
- **Login**: Authenticate with username or email
- **Profile Management**: User profile display and management
- **Session Persistence**: Stay logged in across browser sessions

### 🎨 UI Features
- **Responsive Design**: Works on desktop and mobile
- **Tab-based Navigation**: Easy switching between login and registration
- **Real-time Validation**: Immediate feedback on form inputs
- **Loading Indicators**: Spinner animations for better UX
- **Success/Error Messages**: Clear feedback for user actions

## How to Use

### 1. Running the Application
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the main application
python -m streamlit run app.py
```

### 2. Creating an Account
1. Navigate to the Registration tab
2. Fill in all required fields:
   - Full Name
   - Username (unique)
   - Email (unique, valid format)
   - Password (8+ chars, uppercase, lowercase, number)
   - Confirm Password
3. Accept Terms and Conditions
4. Click "Create Account"

### 3. Logging In
1. Navigate to the Login tab
2. Enter username or email
3. Enter password
4. Optionally check "Remember me" for extended session
5. Click "Login"

### 4. Using the Dashboard
Once logged in, you'll have access to:
- **Quiz Module**: Take adaptive quizzes
- **Performance Analytics**: View your progress
- **Study Planner**: Plan your study schedule
- **Settings**: Manage your account

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    full_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    profile_data TEXT DEFAULT '{}'
);
```

### Sessions Table
```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## API Reference

### AuthManager Class

#### Methods
- `create_user(username, email, password, full_name)` - Create new user
- `authenticate_user(username, password)` - Authenticate user
- `create_session(user_id, expiry_hours)` - Create session token
- `validate_session(session_token)` - Validate session
- `logout_user(session_token)` - Invalidate session

#### Usage Example
```python
from security.auth import AuthManager

auth = AuthManager()

# Create user
success = auth.create_user("john_doe", "john@example.com", "Password123", "John Doe")

# Authenticate
user_data = auth.authenticate_user("john_doe", "Password123")

# Create session
if user_data:
    session_token = auth.create_session(user_data['id'])
```

### Streamlit Integration

#### Session State Variables
- `authenticated` - Boolean indicating if user is logged in
- `user_data` - Dictionary containing user information
- `session_token` - Current session token

#### Helper Functions
- `init_session_state()` - Initialize session variables
- `check_authentication()` - Validate current session
- `login_required()` - Decorator for protected functions

## Configuration

### Database Location
The user database is stored in `data/users.db` (SQLite format)

### Session Settings
- Default session duration: 24 hours
- "Remember me" duration: 7 days (168 hours)
- Session cleanup: Automatic on logout

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

## Testing

### Demo Script
Run the demo script to test the authentication system:
```bash
python demo_auth.py
```

This will:
1. Create a demo user
2. Test authentication
3. Create and validate a session
4. Confirm the system is working

### Manual Testing
1. Run the application: `python -m streamlit run app.py`
2. Register a new account
3. Log out and log back in
4. Test "remember me" functionality
5. Verify session persistence

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure virtual environment is activated
2. **Database Errors**: Check that `data/` directory exists
3. **Session Issues**: Clear browser cache and restart application
4. **Form Errors**: Don't use regular buttons inside Streamlit forms

### Error Messages
- "Username or email already exists" - Choose different credentials
- "Invalid username/email or password" - Check credentials
- "Passwords do not match" - Ensure password confirmation matches
- "Please fill in all fields" - Complete all required fields

## Next Steps

### Planned Enhancements
1. **Password Reset**: Email-based password reset functionality
2. **Profile Management**: Edit profile information
3. **Admin Panel**: User management for administrators
4. **OAuth Integration**: Login with Google/GitHub
5. **Two-Factor Authentication**: Enhanced security with 2FA

### Integration Points
- **Quiz Module**: User-specific quiz history and progress
- **Performance Tracking**: Per-user analytics and reports
- **Study Planner**: Personalized study schedules
- **AI Recommendations**: User behavior-based learning suggestions

## Security Notes

### Best Practices Implemented
- ✅ Password hashing with salt
- ✅ Session token-based authentication
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ Session expiration management

### Recommendations
- Change default session secret key in production
- Implement HTTPS in production deployment
- Regular database backups
- Monitor for suspicious login attempts
- Implement rate limiting for login attempts

---

*This authentication system provides a solid foundation for the Adaptive Exam Preparation AI application with room for future enhancements.*

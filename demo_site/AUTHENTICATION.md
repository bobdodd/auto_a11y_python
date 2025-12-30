# Demo Site Authentication

The demo site now has working password authentication for testing login scenarios.

## Demo Credentials

**Email**: `marie.tremblay@example.com`  
**Password**: `assurance2025`

These credentials are displayed on the login page for convenience.

## How It Works

### Flask Routes (auto_a11y/web/routes/demo.py)

1. **POST /demo/login** - Handles login form submission
   - Validates email and password
   - Creates Flask session on success
   - Redirects to dashboard
   - Redirects back to login with ?error=1 on failure

2. **GET /demo/logout** - Clears session and redirects to homepage

3. **GET /demo/check-auth** - JSON endpoint to check authentication status
   - Returns: `{"authenticated": true, "user": "Marie Tremblay", "email": "..."}`
   - Useful for testing/debugging

### Login Pages

- **login.html** (French)
- **login-en.html** (English)

Both pages:
- Display demo credentials in yellow box
- POST to `/demo/login`
- Show error message if `?error=1` in URL
- Use Flask session management

### Dashboard Pages

- **dashboard.html** (French) 
- **dashboard-en.html** (English)

Currently no session check on dashboard (public access for testing).
To restrict dashboard, add session check to the serve_demo route.

## Testing Authentication

### Manual Testing

1. Go to http://127.0.0.1:5001/demo/login.html
2. Enter credentials:
   - Email: marie.tremblay@example.com
   - Password: assurance2025
3. Click "Se connecter"
4. Should redirect to dashboard

### Wrong Password

1. Enter wrong password
2. Click submit
3. Redirected back to login with error message

### Check Session

Visit: http://127.0.0.1:5001/demo/check-auth

Returns JSON:
```json
{
  "authenticated": true,
  "user": "Marie Tremblay",
  "email": "marie.tremblay@example.com"
}
```

### Logout

Visit: http://127.0.0.1:5001/demo/logout

Clears session and redirects to homepage.

## For AutoA11y Testing

### Testing Behind Login

1. **Manual Cookie Copy**:
   - Login manually in browser
   - Copy session cookie
   - Configure autoA11y to use that cookie

2. **Automated Login**:
   - Configure autoA11y to POST to /demo/login first
   - Save session cookie
   - Use cookie for subsequent requests to dashboard

3. **Test Pages**:
   - Login page: http://127.0.0.1:5001/demo/login.html
   - Dashboard (after login): http://127.0.0.1:5001/demo/dashboard.html

## Session Management

- Uses Flask's built-in session management
- Session stored server-side
- Cookie name: `session` (Flask default)
- Session persists until:
  - User logs out
  - Server restarts
  - Session expires (Flask default: permanent sessions)

## Security Notes

**This is a DEMO only** - Not production-ready:
- Password stored in plain text
- No CSRF protection
- No rate limiting
- No password hashing
- Hardcoded credentials
- Sessions not encrypted

For demo/testing purposes only!

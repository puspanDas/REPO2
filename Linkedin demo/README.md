# Portfolio App

A professional portfolio application with secure user authentication, built with Flask and styled like LinkedIn.

## Features

- **Secure Authentication**: User registration and login with password hashing
- **Professional Design**: LinkedIn-inspired UI with modern styling
- **Profile Management**: Create and edit professional profiles
- **Skills Showcase**: Display skills with professional tags
- **Contact Integration**: Email, GitHub, and LinkedIn links
- **Responsive Design**: Mobile-friendly interface

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd portfolio-web
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python linkedin_style_app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

### Production Deployment

#### Heroku

1. **Install Heroku CLI**
2. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secure-secret-key
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

#### Railway

1. **Connect your GitHub repository**
2. **Set environment variables**:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secure-secret-key`
3. **Deploy automatically**

#### Render

1. **Connect your GitHub repository**
2. **Set build command**: `pip install -r requirements.txt`
3. **Set start command**: `gunicorn linkedin_style_app:app`
4. **Set environment variables**:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secure-secret-key`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `SECRET_KEY` | Flask secret key for sessions | dev-key-change-in-production |
| `DATABASE_URL` | Database file path | portfolio.db |
| `PORT` | Server port | 5000 |

## Security Features

- **Password Hashing**: PBKDF2 with salt
- **Session Security**: Secure cookies in production
- **Input Validation**: Server-side validation
- **SQL Injection Protection**: Parameterized queries
- **CSRF Protection**: Session-based authentication

## API Endpoints

- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/check-auth` - Check authentication status
- `GET /api/profile` - Get user profile
- `POST /api/profile` - Update user profile

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS (LinkedIn-inspired)
- **Deployment**: Gunicorn WSGI server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details
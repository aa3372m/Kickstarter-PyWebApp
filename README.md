# Flask Web Application Starter Kit

A modern, feature-rich Flask web application starter kit with authentication, user management, and a responsive UI.

## Features

- Modern UI/UX with responsive design
- Authentication system with JWT support
- User management and roles
- Theme switching (Light/Dark/Custom)
- Database ORM with SQLAlchemy
- RESTful API endpoints
- File upload handling
- Email integration
- Logging and error handling
- Admin interface
- People management module

## Tech Stack

- Python 3.12
- Flask Framework
- SQLAlchemy ORM
- Flask-Login for authentication
- SQLite (Development) / PostgreSQL (Production)
- Bootstrap 5
- Font Awesome 6
- jQuery
- Chart.js

## Project Structure

```
/app
  /static
    /css
      /themes
        light.css
        dark.css
        custom.css
    /js
    /images
  /templates
  /models
  /views
  /utils
/config
  config.json
  config.py
/scripts
/tests
```

## Getting Started

1. Create and activate the conda environment:
   ```bash
   conda create -n kickstarter101 python=3.12
   conda activate kickstarter101
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Create an admin user:
   ```bash
   python scripts/admin_create.py
   ```

6. Run the development server:
   ```bash
   flask run
   ```

## Development Guidelines

### Adding New Pages

1. Create a new route in `app/views/`
2. Add template in `app/templates/`
3. Register blueprint in `app/__init__.py`

### Creating New Features

1. Define models in `app/models/`
2. Create views in `app/views/`
3. Add templates in `app/templates/`
4. Update navigation in `app/templates/base.html`

### Theme Customization

1. Add new theme file in `app/static/css/themes/`
2. Register theme in `config/config.json`
3. Update theme selector in user preferences

## API Documentation

API endpoints are documented using OpenAPI/Swagger. Access the documentation at `/api/docs` when running the application.

## Testing

Run tests with:
```bash
pytest
```

Generate coverage report:
```bash
pytest --cov=app tests/
```

## Deployment

### Local Server
```bash
flask run
```

### Production
1. Set environment variables
2. Configure PostgreSQL database
3. Run with gunicorn:
   ```bash
   gunicorn -w 4 "run:create_app()"
   ```

### Using ngrok
```bash
ngrok http 5000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
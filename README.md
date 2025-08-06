# python-naitei25_docwn
Website đọc tiểu thuyết online

## Deployment on Heroku

### Prerequisites
- Python 3.12.x
- Git
- Heroku CLI installed

### Environment Variables Required on Heroku
Set the following environment variables in your Heroku app settings:

```bash
# Basic Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.herokuapp.com

# Database (Heroku provides DATABASE_URL automatically with Postgres addon)
# DATABASE_URL=postgres://... (auto-configured by Heroku)

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google OAuth
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# reCAPTCHA
RECAPTCHA_PUBLIC_KEY=your-recaptcha-public-key
RECAPTCHA_PRIVATE_KEY=your-recaptcha-private-key

# ImgBB API
IMGBB_API_KEY=your-imgbb-api-key
```

### Deployment Steps

1. **Create a Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Add PostgreSQL addon:**
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
   # Add other environment variables as needed
   ```

4. **Deploy to Heroku:**
   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   ```

5. **Run migrations:**
   ```bash
   heroku run python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   heroku run python manage.py createsuperuser
   ```

### Files configured for Heroku deployment:
- `Procfile` - Specifies how to run the app on Heroku
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Updated with necessary packages
- `settings.py` - Configured for production with WhiteNoise and database URL parsing
- `release.sh` - Script for deployment preparation

### Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```

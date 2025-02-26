
# CORS settings
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

# Allow NextJS frontend to connect
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Allow credentials (for authentication if needed)
CORS_ALLOW_CREDENTIALS = True

# If you want to allow all headers
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

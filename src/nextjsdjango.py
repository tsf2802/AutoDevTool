import argparse
import subprocess
import os
import json
from dotenv import load_dotenv

def setup_nextjs_frontend(args):
    """Setup NextJS frontend for the Django project"""
    load_dotenv(dotenv_path="./devtool.config")
    project_name = os.getenv("PROJECT_NAME") or "djangoproject"
    
    print(f"Setting up NextJS frontend for {project_name}...")
    
    # Create frontend directory
    frontend_dir = f"{project_name}/frontend"
    os.makedirs(frontend_dir, exist_ok=True)
    
    # Initialize NextJS project
    subprocess.run(["npx", "create-next-app@latest", frontend_dir, 
                    "--use-npm", "--typescript", "--eslint", 
                    "--tailwind", "--app", "--src-dir"], check=True)
    
    # Create .env.local file for frontend API connection
    with open(f"{frontend_dir}/.env.local", 'w') as f:
        f.write("NEXT_PUBLIC_API_URL=http://localhost:8000/api\n")
    
    # Create API utility for connecting to Django
    os.makedirs(f"{frontend_dir}/src/utils", exist_ok=True)
    with open(f"{frontend_dir}/src/utils/api.ts", 'w') as f:
        f.write("""/**
 * API utility for connecting to Django backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Fetch wrapper with common options
 */
async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    ...options,
  };

  const response = await fetch(`${API_URL}${endpoint}`, defaultOptions);
  
  if (!response.ok) {
    const error = new Error('API request failed');
    // Add response data to error
    try {
      const data = await response.json();
      (error as any).data = data;
    } catch (e) {
      // Response wasn't JSON
    }
    (error as any).status = response.status;
    throw error;
  }
  
  return response.json();
}

/**
 * API client with common HTTP methods
 */
export const api = {
  get: (endpoint: string) => fetchAPI(endpoint),
  
  post: (endpoint: string, data: any) => 
    fetchAPI(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  put: (endpoint: string, data: any) => 
    fetchAPI(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  delete: (endpoint: string) => 
    fetchAPI(endpoint, {
      method: 'DELETE',
    }),
};
""")
    
    # Create example component that uses the API
    os.makedirs(f"{frontend_dir}/src/components", exist_ok=True)
    with open(f"{frontend_dir}/src/components/DjangoTest.tsx", 'w') as f:
        f.write("""'use client';

import { useState, useEffect } from 'react';
import { api } from '@/utils/api';

export default function DjangoTest() {
  const [apiStatus, setApiStatus] = useState<{ status?: string; message?: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkApiConnection = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await api.get('/v1/ping/');
      setApiStatus(data);
    } catch (err) {
      console.error('API connection error:', err);
      setError('Failed to connect to Django API. Make sure your backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Django Backend Connection</h2>
      
      <button
        onClick={checkApiConnection}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Checking...' : 'Check Connection'}
      </button>
      
      {error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {apiStatus && (
        <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          <p><strong>Status:</strong> {apiStatus.status}</p>
          <p><strong>Message:</strong> {apiStatus.message}</p>
        </div>
      )}
    </div>
  );
}
""")

    # Update docker-compose.yml to include NextJS frontend
    update_docker_compose_for_nextjs(project_name)
    
    # Create Dockerfile for NextJS
    create_nextjs_dockerfile(project_name)
    
    # Update Django for CORS to allow NextJS connections
    configure_django_cors(project_name)
    
    # Update Nginx configuration to serve frontend and API
    update_nginx_for_nextjs(project_name)
    
    print("\n✅ NextJS frontend setup complete!")
    print("\n📋 Next steps:")
    print(f"1. Install django-cors-headers: pip install django-cors-headers")
    print(f"2. Add CORS settings to your Django project")
    print(f"3. Build and run with Docker: cd {project_name} && docker-compose up --build")

def update_docker_compose_for_nextjs(project_name):
    """Update docker-compose.yml to include NextJS frontend service"""
    docker_compose_path = f"{project_name}/docker-compose.yml"
    
    try:
        with open(docker_compose_path, 'r') as f:
            docker_compose_content = f.read()
        
        # Check if frontend service already exists
        if "frontend:" in docker_compose_content:
            print("Frontend service already exists in docker-compose.yml")
            return
        
        # Find the position to insert frontend service
        end_of_services = docker_compose_content.find("volumes:")
        if end_of_services == -1:
            end_of_services = len(docker_compose_content)
        
        # Frontend service definition for NextJS
        frontend_service = """
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api
    depends_on:
      - web
"""
        
        # Insert frontend service before volumes
        updated_content = docker_compose_content[:end_of_services] + frontend_service + docker_compose_content[end_of_services:]
        
        with open(docker_compose_path, 'w') as f:
            f.write(updated_content)
        
        print("Added NextJS frontend service to docker-compose.yml")
    
    except Exception as e:
        print(f"Error updating docker-compose.yml: {e}")

def create_nextjs_dockerfile(project_name):
    """Create Dockerfile for NextJS frontend"""
    os.makedirs(f"{project_name}/frontend", exist_ok=True)
    
    dockerfile_content = """FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all files
COPY . .

# Build the Next.js app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the app
CMD ["npm", "run", "dev"]
"""
    
    with open(f"{project_name}/frontend/Dockerfile", 'w') as f:
        f.write(dockerfile_content)
    
    print("Created Dockerfile for NextJS frontend")

def configure_django_cors(project_name):
    """Configure Django for CORS to allow NextJS connections"""
    requirements_path = f"{project_name}/requirements.txt"
    
    # Add django-cors-headers to requirements.txt if not already present
    try:
        with open(requirements_path, 'r') as f:
            requirements = f.read()
        
        if "django-cors-headers" not in requirements:
            with open(requirements_path, 'a') as f:
                f.write("\ndjango-cors-headers==4.3.0\n")
            
            print("Added django-cors-headers to requirements.txt")
    except Exception as e:
        print(f"Error updating requirements.txt: {e}")
    
    # Create settings snippet to be added to Django settings
    settings_snippet = f"""
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
"""
    
    # Write the settings snippet to a file that can be included in Django settings
    with open(f"{project_name}/cors_settings.py", 'w') as f:
        f.write(settings_snippet)
    
    print(f"Created CORS settings snippet in {project_name}/cors_settings.py")
    print(f"Please add the following line to your {project_name}/{project_name}/settings.py:")
    print(f"from pathlib import Path; exec(Path('../cors_settings.py').read_text())")

def update_nginx_for_nextjs(project_name):
    """Update Nginx configuration to serve NextJS frontend and Django API"""
    nginx_conf_path = f"{project_name}/nginx/nginx.conf"
    
    try:
        # Create a new Nginx configuration optimized for NextJS and Django
        nginx_conf = f"""upstream {project_name}_backend {{
    server web:8000;
}}

upstream {project_name}_frontend {{
    server frontend:3000;
}}

server {{
    listen 80;
    server_name localhost;
    
    # Increase body size for file uploads
    client_max_body_size 20M;

    # API requests go to Django backend
    location /api/ {{
        proxy_pass http://{project_name}_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }}

    # Django admin
    location /admin/ {{
        proxy_pass http://{project_name}_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }}

    # Django static files
    location /static/ {{
        alias /home/app/web/staticfiles/;
    }}

    # Django media files (if applicable)
    location /media/ {{
        alias /home/app/web/mediafiles/;
    }}

    # NextJS app
    location / {{
        proxy_pass http://{project_name}_frontend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for NextJS HMR (Hot Module Replacement)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # NextJS specific settings
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }}
}}"""
        
        with open(nginx_conf_path, 'w') as f:
            f.write(nginx_conf)
        
        print("Updated Nginx configuration for NextJS and Django")
    
    except Exception as e:
        print(f"Error updating Nginx configuration: {e}")

def create_django_api_app(project_name):
    """Create a Django API app with REST framework for NextJS integration"""
    # Update requirements.txt to include DRF
    requirements_path = f"{project_name}/requirements.txt"
    try:
        with open(requirements_path, 'r') as f:
            requirements = f.read()
        
        if "djangorestframework" not in requirements:
            with open(requirements_path, 'a') as f:
                f.write("\ndjangorestframework==3.14.0\n")
            
            print("Added djangorestframework to requirements.txt")
    except Exception as e:
        print(f"Error updating requirements.txt: {e}")
    
    # Change to project directory
    os.chdir(project_name)
    
    # Create the API app
    try:
        subprocess.run(["django-admin", "startapp", "api"])
        print("Created Django API app")
    except Exception as e:
        print(f"Error creating API app: {e}. Make sure Django is installed.")
        os.makedirs("api", exist_ok=True)
    
    # Create API app structure
    os.makedirs("api/urls", exist_ok=True)
    
    # Create __init__.py files
    with open("api/__init__.py", 'w') as f:
        f.write("")
    
    with open("api/urls/__init__.py", 'w') as f:
        f.write("")
    
    # Create v1.py for API versioning
    with open("api/urls/v1.py", 'w') as f:
        f.write("""from django.urls import path
from api.views import ping

urlpatterns = [
    path('ping/', ping, name='ping'),
]
""")
    
    # Create main urls.py for API
    with open("api/urls.py", 'w') as f:
        f.write("""from django.urls import path, include

urlpatterns = [
    path('v1/', include('api.urls.v1')),
]
""")
    
    # Create views.py with a simple ping endpoint
    with open("api/views.py", 'w') as f:
        f.write("""from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['GET'])
def ping(request):
    '''Simple endpoint to test API connectivity'''
    return JsonResponse({
        'status': 'ok',
        'message': 'Django API is connected to NextJS!'
    })
""")
    
    # Return to original directory
    os.chdir("..")
    
    print("Created Django API app with basic endpoints")
    print(f"Add to {project_name}/{project_name}/urls.py:")
    print('from django.urls import path, include')
    print('urlpatterns = [')
    print('    # ... other urls')
    print('    path("api/", include("api.urls")),')
    print(']')

def main():
    """Main function to add to your existing CLI tool"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    # Add the frontend command
    frontend_parser = subparsers.add_parser("frontend")
    frontend_parser.add_argument("--type", default="nextjs", help="Frontend framework type (nextjs)")
    
    args = parser.parse_args()
    
    if args.command == "frontend" and args.type == "nextjs":
        setup_nextjs_frontend(args)
        create_django_api_app(os.getenv("PROJECT_NAME") or "djangoproject")

if __name__ == "__main__":
    main()
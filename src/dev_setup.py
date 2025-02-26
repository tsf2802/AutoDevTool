import argparse
import subprocess
import os
import json
import shutil
from dotenv import load_dotenv

def setup_local_dev(args):
    """Set up local development environment for NextJS frontend"""
    load_dotenv(dotenv_path="./devtool.config")
    project_name = os.getenv("PROJECT_NAME") or "djangoproject"
    
    print(f"Setting up local development environment for {project_name}...")
    
    # Create a dev script in the project root
    create_dev_script(project_name)
    
    # Create an improved docker-compose.dev.yml
    create_dev_docker_compose(project_name)
    
    # Create .env.development file for NextJS
    create_nextjs_dev_env(project_name)
    
    # Create a VSCode configuration for easy debugging
    create_vscode_config(project_name)
    
    # Add development tooling to package.json
    update_package_json(project_name)
    
    # Create file watcher to auto-restart Django on changes
    create_django_file_watcher(project_name)
    
    print("\n✅ Local development environment set up successfully!")
    print("\n📋 To start development:")
    print(f"1. cd {project_name}")
    print("2. ./dev.sh start")
    print("\n💻 Your development URLs:")
    print("- NextJS Frontend: http://localhost:3000")
    print("- Django API: http://localhost:8000/api")
    print("- Django Admin: http://localhost:8000/admin")

def create_dev_script(project_name):
    """Create a convenient development script"""
    script_content = """#!/bin/bash

# Development script for managing the local environment

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project name from config
PROJECT_NAME=$(grep PROJECT_NAME ./devtool.config | cut -d= -f2)

function show_help {
    echo -e "${BLUE}Development Environment Helper${NC}"
    echo ""
    echo "Usage:"
    echo "  ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services (Django and NextJS)"
    echo "  stop        - Stop all running services"
    echo "  restart     - Restart all services"
    echo "  frontend    - Start only the NextJS frontend"
    echo "  backend     - Start only the Django backend"
    echo "  logs        - Show logs from all services"
    echo "  install     - Install dependencies for both frontend and backend"
    echo "  migrate     - Run Django migrations"
    echo "  shell       - Start Django shell"
    echo "  test        - Run tests for both frontend and backend"
    echo "  help        - Show this help message"
}

function start_services {
    echo -e "${GREEN}Starting development services...${NC}"
    docker-compose -f docker-compose.dev.yml up -d
    echo -e "${GREEN}Services started!${NC}"
    echo -e "Frontend: ${YELLOW}http://localhost:3000${NC}"
    echo -e "Backend API: ${YELLOW}http://localhost:8000/api${NC}"
    echo -e "Django Admin: ${YELLOW}http://localhost:8000/admin${NC}"
}

function stop_services {
    echo -e "${YELLOW}Stopping all services...${NC}"
    docker-compose -f docker-compose.dev.yml down
}

function start_frontend {
    echo -e "${GREEN}Starting NextJS frontend...${NC}"
    cd frontend && npm run dev
}

function start_backend {
    echo -e "${GREEN}Starting Django backend...${NC}"
    cd $PROJECT_NAME && python manage.py runserver 0.0.0.0:8000
}

function show_logs {
    echo -e "${BLUE}Showing logs... (Ctrl+C to exit)${NC}"
    docker-compose -f docker-compose.dev.yml logs -f
}

function install_deps {
    echo -e "${GREEN}Installing backend dependencies...${NC}"
    pip install -r $PROJECT_NAME/requirements.txt
    
    echo -e "${GREEN}Installing frontend dependencies...${NC}"
    cd frontend && npm install
    cd ..
}

function run_migrations {
    echo -e "${GREEN}Running Django migrations...${NC}"
    cd $PROJECT_NAME && python manage.py migrate
}

function django_shell {
    echo -e "${GREEN}Starting Django shell...${NC}"
    cd $PROJECT_NAME && python manage.py shell
}

function run_tests {
    echo -e "${GREEN}Running backend tests...${NC}"
    cd $PROJECT_NAME && python manage.py test
    
    echo -e "${GREEN}Running frontend tests...${NC}"
    cd frontend && npm test
}

# Main command router
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        ;;
    frontend)
        start_frontend
        ;;
    backend)
        start_backend
        ;;
    logs)
        show_logs
        ;;
    install)
        install_deps
        ;;
    migrate)
        run_migrations
        ;;
    shell)
        django_shell
        ;;
    test)
        run_tests
        ;;
    help|*)
        show_help
        ;;
esac
"""
    
    script_path = f"{project_name}/dev.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    print(f"Created development script: {script_path}")

def create_dev_docker_compose(project_name):
    """Create a development docker-compose file optimized for local development"""
    
    docker_compose_content = f"""version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - ./{project_name}:/app/{project_name}
      - ./static:/app/static
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DJANGO_SETTINGS_MODULE={project_name}.settings
    command: python manage.py runserver 0.0.0.0:8000
    restart: unless-stopped
    
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api
      - NODE_ENV=development
    command: npm run dev
    restart: unless-stopped
"""
    
    docker_compose_path = f"{project_name}/docker-compose.dev.yml"
    with open(docker_compose_path, 'w') as f:
        f.write(docker_compose_content)
    
    # Create Django dev Dockerfile
    django_dev_dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install development tools
RUN pip install --no-cache-dir \\
    django-debug-toolbar \\
    ipython \\
    watchdog

# Copy project
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=True

EXPOSE 8000

# Command is specified in docker-compose.dev.yml
"""
    django_dockerfile_path = f"{project_name}/Dockerfile.dev"
    with open(django_dockerfile_path, 'w') as f:
        f.write(django_dev_dockerfile)
    
    # Create NextJS dev Dockerfile
    nextjs_dev_dockerfile = """FROM node:18-alpine

WORKDIR /app

# Install dependencies only when needed
COPY package.json package-lock.json* ./
RUN npm install

# Copy next.config.js and other config files
COPY next.config.ts .
COPY tsconfig.json .
COPY tailwind.config.js .
COPY postcss.config.mjs .

# Copy source code
COPY src ./src
COPY public ./public

# Expose NextJS development port
EXPOSE 3000

# Command is specified in docker-compose.dev.yml
"""
    
    os.makedirs(f"{project_name}/frontend", exist_ok=True)
    nextjs_dockerfile_path = f"{project_name}/frontend/Dockerfile.dev"
    with open(nextjs_dockerfile_path, 'w') as f:
        f.write(nextjs_dev_dockerfile)
    
    print(f"Created development Docker configurations")

def create_nextjs_dev_env(project_name):
    """Create development environment variables for NextJS"""
    
    env_content = """# Development environment variables
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_ENV=development

# Enable React strict mode for better development
NEXT_PRIVATE_STRICT_MODE=true

# Set debug mode
NEXT_PUBLIC_DEBUG=true
"""
    
    os.makedirs(f"{project_name}/frontend", exist_ok=True)
    env_path = f"{project_name}/frontend/.env.development"
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"Created NextJS development environment file")

def create_vscode_config(project_name):
    """Create VSCode configuration for easy debugging"""
    
    vscode_dir = f"{project_name}/.vscode"
    os.makedirs(vscode_dir, exist_ok=True)
    
    # Create launch.json for debugging
    launch_json = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Django: Run Server",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/manage.py",
                "args": [
                    "runserver"
                ],
                "django": True,
                "justMyCode": True
            },
            {
                "name": "Django: Shell",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/manage.py",
                "args": [
                    "shell"
                ],
                "django": True,
                "justMyCode": True
            },
            {
                "name": "Next.js: debug server-side",
                "type": "node-terminal",
                "request": "launch",
                "cwd": "${workspaceFolder}/frontend",
                "command": "npm run dev"
            },
            {
                "name": "Next.js: debug client-side",
                "type": "chrome",
                "request": "launch",
                "url": "http://localhost:3000"
            },
            {
                "name": "Next.js: debug full stack",
                "type": "node-terminal",
                "request": "launch",
                "cwd": "${workspaceFolder}/frontend",
                "command": "npm run dev",
                "serverReadyAction": {
                    "pattern": "started server on .+, url: (https?://.+)",
                    "uriFormat": "%s",
                    "action": "debugWithChrome"
                }
            }
        ],
        "compounds": [
            {
                "name": "Full Stack: Django + Next.js",
                "configurations": ["Django: Run Server", "Next.js: debug client-side"]
            }
        ]
    }
    
    with open(f"{vscode_dir}/launch.json", 'w') as f:
        json.dump(launch_json, f, indent=2)
    
    # Create settings.json
    settings_json = {
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        "python.linting.flake8Enabled": False,
        "python.formatting.provider": "black",
        "python.formatting.blackArgs": [
            "--line-length",
            "100"
        ],
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.organizeImports": True
        },
        "[javascript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[typescript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "[typescriptreact]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode"
        },
        "eslint.workingDirectories": [
            "./frontend"
        ],
        "files.associations": {
            "**/*.html": "html",
            "**/templates/**/*.html": "django-html"
        },
        "emmet.includeLanguages": {
            "django-html": "html"
        }
    }
    
    with open(f"{vscode_dir}/settings.json", 'w') as f:
        json.dump(settings_json, f, indent=2)
    
    # Create extensions.json
    extensions_json = {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "batisteo.vscode-django",
            "esbenp.prettier-vscode",
            "dbaeumer.vscode-eslint",
            "dsznajder.es7-react-js-snippets",
            "bradlc.vscode-tailwindcss"
        ]
    }
    
    with open(f"{vscode_dir}/extensions.json", 'w') as f:
        json.dump(extensions_json, f, indent=2)
    
    print(f"Created VSCode configuration for easy debugging")

def update_package_json(project_name):
    """Update package.json with development scripts"""
    
    frontend_dir = f"{project_name}/frontend"
    os.makedirs(frontend_dir, exist_ok=True)
    
    package_json_path = f"{frontend_dir}/package.json"
    
    package_data = {
        "name": f"{project_name}-frontend",
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint",
            "test": "jest",
            "format": "prettier --write \"src/**/*.{ts,tsx}\"",
            "api:check": "curl -s http://localhost:8000/api/v1/ping/ | jq"
        },
        "dependencies": {
            "next": "^14.0.0",
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        },
        "devDependencies": {
            "@types/node": "^20.0.0",
            "@types/react": "^18.0.0",
            "@types/react-dom": "^18.0.0",
            "autoprefixer": "^10.0.0",
            "eslint": "^8.0.0",
            "eslint-config-next": "^14.0.0",
            "jest": "^29.0.0",
            "postcss": "^8.0.0",
            "prettier": "^3.0.0",
            "tailwindcss": "^3.0.0",
            "typescript": "^5.0.0"
        }
    }
    
    # Check if package.json already exists
    try:
        if os.path.exists(package_json_path):
            with open(package_json_path, 'r') as f:
                existing_data = json.load(f)
            
            # Merge scripts
            if "scripts" in existing_data:
                existing_data["scripts"].update(package_data["scripts"])
            else:
                existing_data["scripts"] = package_data["scripts"]
            
            # Write back the updated data
            with open(package_json_path, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            print(f"Updated package.json with development scripts")
        else:
            # Create new package.json
            with open(package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)
            
            print(f"Created package.json with development scripts")
    except Exception as e:
        print(f"Error updating package.json: {e}")
        
        # Create new package.json as fallback
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)

def create_django_file_watcher(project_name):
    """Create a file watcher script to auto-restart Django on changes"""
    
    watchdog_script = """#!/usr/bin/env python
import sys
import time
import subprocess
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DjangoRestartHandler(FileSystemEventHandler):
    def __init__(self, process):
        self.process = process
        self.last_restart = time.time()
    
    def on_any_event(self, event):
        # Skip directories and non-Python files
        if event.is_directory or not event.src_path.endswith('.py'):
            return
            
        # Debounce to avoid multiple restarts
        current_time = time.time()
        if current_time - self.last_restart < 1:
            return
            
        print(f"\\nDetected change in {event.src_path}")
        print("Restarting Django server...")
        
        # Restart the process
        self.process.terminate()
        self.process.wait()
        self.process = subprocess.Popen(
            ["python", "manage.py", "runserver", "0.0.0.0:8000"],
            preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
        )
        self.last_restart = current_time

def main():
    # Start Django server
    process = subprocess.Popen(
        ["python", "manage.py", "runserver", "0.0.0.0:8000"],
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
    )
    
    # Set up file watcher
    event_handler = DjangoRestartHandler(process)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    
    print("Django auto-reload file watcher started.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        process.terminate()
    
    observer.join()
    process.wait()

if __name__ == "__main__":
    main()
"""
    
    script_path = f"{project_name}/autoreload.py"
    with open(script_path, 'w') as f:
        f.write(watchdog_script)
    
    print(f"Created Django auto-reload file watcher")

def main():
    """Main function to add to your existing CLI tool"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    # Add the local-dev command
    local_dev_parser = subparsers.add_parser("local-dev")
    local_dev_parser.add_argument("--with-vscode", action="store_true", help="Set up VSCode configuration")
    
    args = parser.parse_args()
    
    if args.command == "local-dev":
        load_dotenv(dotenv_path="./devtool.config")
        project_name = os.getenv("PROJECT_NAME") or "djangoproject"
        setup_local_dev(args)

if __name__ == "__main__":
    main()
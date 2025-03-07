import argparse
import subprocess
from google import genai
import os
from dotenv import load_dotenv
from docgenerator import DocGenerator

def create_project(args):
    #possibly add features for project_name and directory_name
    if args.framework == "django":
        try:
            subprocess.run(['pip', 'show', 'django'], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            print("Django is not installed. We are installing it now.")
            subprocess.run(["pip", "install", "django"])

        project_name = args.project_name if not None else "myproject"
        subprocess.run(["django-admin", "startproject", f"{project_name}"])

        with open("./devtool.config", 'w') as f:
            f.write('FRAMEWORK=django\n')
            web_server = args.web_server if not None else "nginx"
            f.write(f"WEB_SERVER={web_server}\n")
            f.write(f"PROJECT_NAME={project_name}\n")
            f.write(f"CONTEXT={args.context}\n")
    elif args.framework == "nextjs":
        print("Creating a Next.js project... Not really tho, still need to code that part")

def create_docker_compose_file(reverse_proxy):
    load_dotenv(dotenv_path="./devtool.config")
    project_name = os.getenv("PROJECT_NAME")

    if not check_nginx_folder_exists():
        create_nginx_stuff()

    docker_compose_content = f"""version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    command: gunicorn {project_name}.wsgi:application --bind 0.0.0.0:8000"""

    if reverse_proxy == "nginx":
        docker_compose_content += """
    volumes:
      - static_volume:/home/app/web/staticfiles"""
    
    docker_compose_content += """
    expose:
      - 8000:8000"""
    
    if check_env_file_exists():
        docker_compose_content += """
    env_file:
      - ./.env"""
    
    if reverse_proxy == "nginx":
        docker_compose_content += """
  nginx:
    build: ./nginx
    volumes:
      - static_volume:/home/app/web/staticfiles
    ports:
      - 1337:80
    depends_on:
      - web

volumes:
  static_volume:"""

    with open(f"{project_name}/docker-compose.yml", 'w') as f:
        f.write(docker_compose_content)

def create_nginx_stuff():
    load_dotenv(dotenv_path="./devtool.config")
    project_name = os.getenv("PROJECT_NAME")

    dockerfile_content = """FROM nginx:1.25

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d"""

    directory = os.path.dirname(f"{project_name}/nginx/Dockerfile")
    os.makedirs(directory, exist_ok=True)
    with open(f"{project_name}/nginx/Dockerfile", 'w') as f:
        f.write(dockerfile_content)

    nginx_conf = f"""upstream {project_name} {{
    server web:8000;
}}

server {{

    listen 80;

    location / {{
        proxy_pass http://{project_name};
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }}

}}"""
    
    with open(f"{project_name}/nginx/nginx.conf", 'w') as f:
        f.write(nginx_conf)

def check_nginx_folder_exists():
    load_dotenv(dotenv_path="./devtool.config")
    project_name = os.getenv("PROJECT_NAME")
    full_path = os.path.join(f"./{project_name}", "nginx")
    return os.path.exists(full_path)

def check_env_file_exists():
    load_dotenv(dotenv_path="./devtool.config")
    project_name = os.getenv("PROJECT_NAME")
    full_path = os.path.join(f"./{project_name}", ".env")
    return os.path.exists(full_path)

def check_requirements_file_exists():
    load_dotenv(dotenv_path="./devtool.config")
    project_name = os.getenv("PROJECT_NAME")
    full_path = os.path.join(f"./{project_name}", "requirements.txt")
    return os.path.exists(full_path)

def create_docker_file(framework):
    load_dotenv(dotenv_path="./devtool.config")
    project_name = os.getenv("PROJECT_NAME")
    if not check_requirements_file_exists():
        print("requirements.txt not found. We are creating it now.")

        requirements_content = """Django==4.2.3
gunicorn==21.2.0"""

        with open(f"{project_name}/requirements.txt", 'w') as f:
            f.write(requirements_content)

    if framework == "django":
        docker_file_content = """###########
# BUILDER #
###########

# pull official base image
FROM python:3.11.4-slim-buster as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && \\
    apt-get install -y --no-install-recommends gcc

# lint
RUN pip install --upgrade pip
RUN pip install flake8==6.0.0
COPY . /usr/src/app/
RUN flake8 --ignore=E501,F401 .

# install python dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.11.4-slim-buster

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --group app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app"""

    with open(f"{project_name}/Dockerfile", 'w') as f:
        f.write(docker_file_content)

def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")
    
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--framework", required=True, help="The framework of the project to be initialized. Recommeded to be Django, cause we be like that.")
    init_parser.add_argument("--web-server", help="The web server or reverse proxy of choice. Recommeded to be nginx, cause we be like that.")
    init_parser.add_argument("--project-name", help="The name of the project to be initialized.")
    init_parser.add_argument("--context", help="The context of the project to be initialized.")

    args = parser.parse_args()

    if args.command == "init":
        create_project(args)
        create_docker_file(args.framework)
        create_docker_compose_file(args.web_server)
        
        # Generate documentation after project creation
        print("\nGenerating project documentation...")
        docgen = DocGenerator()
        docgen.generate_documentation("djangoproject")

if __name__ == "__main__":
    # run this code by doing 'python src/cli.py init --framework=django --web-server=nginx --project-name=djangoproject' in command line
    # NOTE: when adding --context, make sure to add qoutes ("") if you have spaces in your sentences isnetad of just one word. Ex: --context="hello this project is called devtool" 
    load_dotenv("src/.env")
    main()
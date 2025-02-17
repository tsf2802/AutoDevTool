import argparse
import subprocess
import os

def create_project(args):
    #possibly add features for project_name and directory_name
    root_directory = "./myproject"
    if args.framework == "django":
        try:
            subprocess.run(["pip", "show", "django"], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            print("Django is not installed. We are installing it now.")
            subprocess.run(["pip", "install", "django"])
        
        subprocess.run(["django-admin", "startproject", "myproject"])
        with open(f"{root_directory}/devtool.config", 'w') as f:
            f.write('FRAMEWORK=django\n')
            f.write(f"WEB_SERVER={args.web_server}\n")
    elif args.framework == "nextjs":
        print("Creating a Next.js project... Not really tho, still need to code that part")

def create_docker_compose_file(reverse_proxy):
    root_directory = "./myproject"
    project_name = "myproject"
    docker_compose_content = f"""version: '3.8'

services:
  web:
    build:
      context: {root_directory}
      dockerfile: Dockerfile
    command: gunicorn {project_name}.wsgi:application --bind 0.0.0.0:8000"""

    if reverse_proxy == "nginx":
        docker_compose_content += """
    volumes:
      - static_volume:/home/app/web/staticfiles"""
    
    docker_compose_content += """
    expose:
      - 8000"""
    
    if check_env_file_exists():
        docker_compose_content += """
    env_file:
      - ./.env"""
    
    if reverse_proxy == "nginx":
        docker_compose_content += """
  nginx:
    build: ./nignx
    volumes:
      - static_volume:/home/app/web/staticfiles
    ports:
      - 1337:80
    depends_on:
      - web

volumes:
  static_volume:"""

    with open(f"{root_directory}/docker-compose.yml", 'w') as f:
        f.write(docker_compose_content)

def check_env_file_exists():
    root_directory = "./myproject"
    full_path = os.path.join(f"./{root_directory}", ".env")
    return os.path.exists(full_path)

def check_requirements_file_exists():
    root_directory = "./myproject"
    full_path = os.path.join(f"./{root_directory}", "requirements.txt")
    return os.path.exists(full_path)

def create_docker_file(framework):
    root_directory = "./myproject"
    if not check_requirements_file_exists():
        print("requirements.txt not found. We are creating it now.")

        requirements_content = """Django==4.2.3
gunicorn==21.2.0"""

        with open(f"{root_directory}/requirements.txt", 'w') as f:
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
RUN apt-get update && \
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

    with open(f"{root_directory}/Dockerfile", 'w') as f:
        f.write(docker_file_content)

def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")
    
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--framework", help="The framework of the project to be initialized. Recommeded to be Django, cause we be like that.")
    init_parser.add_argument("--web-server", help="The web server or reverse proxy of choice. Recommeded to be nginx, cause we be like that.")

    args = parser.parse_args()

    if args.command == "init":
        create_project(args)
        create_docker_file(args.framework)
        create_docker_compose_file(args.web_server)

if __name__ == "__main__":
    # run this code by doing 'python src/cli.py init --framework=django --web-server=nginx' in command line
    main()
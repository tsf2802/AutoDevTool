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
    print(f"version: '3.8'\n\nservices:\n  web:\n    build:\n      context: {root_directory}\n      dockerfile: Dockerfile\n    command: gunicorn {project_name}.wsgi:application --bind 0.0.0.0:8000\n    volumes:\n      - static_volume:/home/app/web/staticfiles\n    expose:\n      - 8000")
    if check_env_file_exists():
        print(f"    env_file:\n      - ./.env")
    if reverse_proxy == "nginx":
        # if nginx_folder_exists():
            print(f"  nginx:\n    build: ./nignx\n    volumes:\n      - static_volume:/home/app/web/staticfiles\n    ports:\n      - 1337:80\n    depends_on:\n      - web\n\nvolumes:\n  static_volume:")

def check_env_file_exists():
    root_directory = "./myproject"
    full_path = os.path.join(f"./{root_directory}", ".env")
    return os.path.exists(full_path)

def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")
    
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--framework", help="The framework of the project to be initialized. Recommeded to be Django, cause we be like that.")
    init_parser.add_argument("--web-server", help="The web server or reverse proxy of choice. Recommeded to be nginx, cause we be like that.")

    args = parser.parse_args()

    if args.command == "init":
        create_project(args)
        # create_docker_compose_file("nginx")

if __name__ == "__main__":
    # run this code by doing 'python src/cli.py init --framework=django' in command line
    main()
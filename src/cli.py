import argparse
import subprocess

def create_project(args):
    if args.framework == "django":
        try:
            subprocess.run(["pip", "show", "django"], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            print("Django is not installed. We are installing it now.")
            subprocess.run(["pip", "install", "django"])
        
        subprocess.run(["django-admin", "startproject", "myproject"])
    elif args.framework == "nextjs":
        print("Creating a Next.js project... Not really tho, still need to code that part")

def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")
    
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--framework", help="The name of the project to be initialized")

    args = parser.parse_args()

    if args.command == "init":
        create_project(args)

if __name__ == "__main__":
    main()
import argparse
import subprocess
from google import genai

def create_project(args):
    if args.framework == 'django':
        try:
            subprocess.run(['pip', 'show', 'django'], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            print('Django is not installed. We are installing it now.')
            subprocess.run(['pip', 'install', 'django'])
        
        subprocess.run(['django-admin', 'startproject', 'myproject'])
    elif args.framework == 'nextjs':
        print('Creating a Next.js project... Not really tho, still need to code that part')

def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")
    
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--framework", help="The name of the project to be initialized")

    args = parser.parse_args()

    if args.command == "init":
        create_project(args)

if __name__ == "__main__":
    # run this code by doing 'python src/cli.py init --framework=django' in command line

    client = genai.Client(api_key="AIzaSyCYYYkGXec0Y3sZUpWFH36hw77573VlS0M")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="""
        Write a docstring for the following code, without adding extra empty lines for formatting (just line after line) and don't add an example of the usage of the function, but make sure to add explanation of args and any errors that might occur and don't add anything like ```python, but instead simply return the function with the docstring: 
        def create_project(args):
    if args.framework == 'django':
        try:
            subprocess.run(['pip', 'show', 'django'], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            print('Django is not installed. We are installing it now.')
            subprocess.run(['pip', 'install', 'django'])
        
        subprocess.run(['django-admin', 'startproject', 'myproject'])
    elif args.framework == 'nextjs':
        print('Creating a Next.js project... Not really tho, still need to code that part')
        """,
    )

    print(response.text)

    main()
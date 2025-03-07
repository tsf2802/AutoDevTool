from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

def read_files_in_dir(dir):
    file_contents = {}
    try:
        for filename in os.listdir(dir):
            filepath = os.path.join(dir, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r') as file:
                    file_contents[filepath] = file.read()
    except FileNotFoundError:
        print(f"Error: Directory not found: {dir}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return file_contents

# New helper function to get context from devtool.config
def get_context(config_path="devtool.config"):
    try:
        with open(config_path, "r") as config_file:
            for line in config_file:
                if line.startswith("CONTEXT="):
                    # Extract the value after 'CONTEXT=' and strip any whitespace/newlines.
                    context_value = line.split("=", 1)[1].strip()
                    return context_value
    except FileNotFoundError:
        print(f"Config file {config_path} not found.")
        return None
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None
    return None

class DocGenerator():
    def __init__(self):
        self.client = genai.Client(api_key=api_key)

    def generate_documentation(self, dir):

        print("Generating documentation...")

        # Prepare the base prompt for generating documentation.
        prompt = (
            "Based on the given code in my project, please generate a documentation for the codebase. "
            "Please note it needs to be able to be placed in an MD file. Ignore sensitive information. "
            "Please note that it shouldn't have code. Include information that will help user expand on given template. "
            "It's getting written into an MD file. Please don't have the ```."
            "\n\nCode:\n"
            f"{read_files_in_dir(dir)}"
        )

        # Check the CONTEXT in devtool.config and add it to the prompt if applicable.
        context = get_context()
        if context and context != "None":
            prompt += f"\n\nTailor the documentaion to account the follo project:\n{context}"

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        readme_path = os.path.join("djangoproject", "README.md")
        os.makedirs("djangoproject", exist_ok=True)
        
        with open(readme_path, "w") as mdFile:
            mdFile.write(response.text)

        print(f"Documentation generated successfully in {readme_path}!")

    
if __name__ == "__main__":
    docgen = DocGenerator()
    docgen.generate_documentation("djangoproject")

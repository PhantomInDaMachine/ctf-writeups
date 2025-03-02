import os
import re

def update_image_links(file_path, base_url):
    """Update image links in a Markdown file to prepend the base URL."""
    
    # Read the file content
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Regex pattern to find images in the format ![Image](/images/filename.png)
    pattern = r'(!\[[^\]]*\]\()/images/([^)\s]+)(\))'

    # Replace matches with new URL format
    new_content = re.sub(pattern, rf'\1{base_url}/images/\2\3', content)

    # Check if changes were made
    if content != new_content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes made to {file_path}")

if __name__ == "__main__":
    # User input
    file_path = input("Enter the path to the Markdown file: ").strip()
    base_url = input("Enter the base URL: ").strip()

    # Validate input
    if not os.path.isfile(file_path):
        print("Error: The specified file does not exist.")
    else:
        update_image_links(file_path, base_url)

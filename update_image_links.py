import os
import re

def find_image_path(image_name, images_root):
    """Search for an image file within the images directory structure."""
    # print(f"Searching for {image_name} inside {images_root}")  # Debugging

    for root, _, files in os.walk(images_root):
        # print(f"Checking {root}, found files: {files}")  # Debugging
        if image_name in files:
            relative_path = os.path.relpath(root, images_root).replace("\\", "/")
            print(f"✅ Found {image_name} in {relative_path}")  # Debugging
            return relative_path if relative_path != "." else ""  # Return empty if in root

    print(f"❌ Image not found: {image_name}")  # Debugging
    return None  # Return None if the image is not found

def update_image_links(file_path, base_url, images_root):
    """Update image links in a Markdown file with full URLs, detecting subdirectories automatically."""
    
    # Read the file content
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Regex pattern to find images in Markdown (![desc](current_path))
    pattern = r'(!\[[^\]]*\]\()(https?://[^)]+)(\))'

    changes_made = False  # Track if replacements were done

    def replace_match(match):
        """Replace Markdown image links with correctly structured URLs"""
        nonlocal changes_made
        image_url = match.group(2)  # Extract the current image URL (e.g., https://yoursite.com/images/Hammer.png)

        # Extract only the filename (e.g., "Hammer.png")
        image_name = os.path.basename(image_url)  

        detected_sub_path = find_image_path(image_name, images_root)
        if detected_sub_path is not None:
            # Construct the new URL with the correct path
            new_url = f"{base_url}/images/{detected_sub_path}/{image_name}".replace("//", "/")
            print(f"Updating: {image_name} → {new_url}")  # Debugging output
            changes_made = True
            return f'{match.group(1)}{new_url}{match.group(3)}'
        
        return match.group(0)  # Return the original if not modified

    # Process the markdown content
    new_content = re.sub(pattern, replace_match, content)

    # Write changes if any were made
    if changes_made:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes made to {file_path} (check image paths and names)")

if __name__ == "__main__":
    # User input
    file_path = input("Enter the path to the Markdown file (e.g., 'content/example_dir1/example_dir2/file_name.md'): ").strip()
    base_url = input("Enter the base URL: ").strip().rstrip("/")  # Remove trailing slash if present
    images_root = input("Enter the root directory for images (e.g., 'static/images/'): ").strip()

    # Validate input
    if not os.path.isfile(file_path):
        print("Error: The specified file does not exist.")
    elif not os.path.isdir(images_root):
        print("Error: The specified images directory does not exist.")
    else:
        update_image_links(file_path, base_url, images_root)

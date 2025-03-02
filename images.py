import os
import re
import shutil

# Paths (using raw strings to handle Windows backslashes correctly)
posts_dir = r"C:\Users\DaMayor\Codium\Git_Projects\WriteUps\THM\Medium\Hammer\content\posts\Hammer"
attachments_dir = r"C:\Users\DaMayor\Codium\Git_Projects\Windows\secondBrain\Posts\Hammer\images"
static_images_dir = r"C:\Users\DaMayor\Codium\Git_Projects\WriteUps\THM\Medium\Hammer\static\images"

# Step 1: Process each markdown file in the posts directory
for filename in os.listdir(posts_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(posts_dir, filename)
        
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Step 2: Find all image links in Markdown
        images = re.findall(r'!\[\[([^]]*\.png)\]\]|\!\[.*?\]\(([^)]+\.png)\)', content)

        # Step 3: Replace image links and copy files
        for match in images:
            image = match[0] if match[0] else match[1]  # Get image name from regex match
            new_path = f"/images/{image.replace(' ', '%20')}"  # Format for Markdown
            
            # Replace links in markdown
            content = content.replace(f"![[{image}]]", f"![Image]({new_path})")
            content = content.replace(f"![Alt Text]({image})", f"![Image]({new_path})")

            # Step 4: Copy the image to the static/images directory if it exists
            image_source = os.path.join(attachments_dir, image)
            if os.path.exists(image_source):
                shutil.copy(image_source, static_images_dir)
                print(f"Copied {image} to {static_images_dir}")

        # Step 5: Write the updated content back to the markdown file
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
            print(f"Updated {filename} with new image paths.")

print("Markdown files processed and images copied successfully.")

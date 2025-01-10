import os
import re
import json
from datetime import datetime

ARTICLES_DIR = 'articles'

# Function to normalize file names
def normalize_filename(filename):
    name, ext = os.path.splitext(filename)
    normalized_name = re.sub(r'\s+', '_', name.strip())  # Replace spaces with underscores and trim spaces
    normalized_name = re.sub(r'[^a-zA-Z0-9_-]', '', normalized_name)  # Remove special characters
    return f"{normalized_name}{ext}"

# Function to sanitize existing article files
def sanitize_article_files():
    for filename in os.listdir(ARTICLES_DIR):
        old_path = os.path.join(ARTICLES_DIR, filename)
        if not filename.endswith('.json'):
            continue

        normalized_name = normalize_filename(filename)
        new_path = os.path.join(ARTICLES_DIR, normalized_name)

        if old_path != new_path:
            print(f"Renaming '{filename}' to '{normalized_name}'")
            os.rename(old_path, new_path)

# Function to add metadata to articles
def add_metadata_to_articles():
    for filename in os.listdir(ARTICLES_DIR):
        file_path = os.path.join(ARTICLES_DIR, filename)
        
        if filename.endswith('.json'):
            with open(file_path, 'r') as f:
                try:
                    article = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON file: {filename}")
                    continue

            # Add or update metadata fields
            article['last_modified'] = datetime.now().isoformat()
            if 'created_at' not in article:
                article['created_at'] = datetime.now().isoformat()

            # Save the updated article
            with open(file_path, 'w') as f:
                json.dump(article, f, indent=4)
                print(f"Updated metadata for '{filename}'")

# Function to detect conflicts during article updates
def check_for_conflicts(new_title, existing_files, original_title=None):
    normalized_new_title = normalize_filename(f"{new_title}.json")
    for filename in existing_files:
        normalized_filename = normalize_filename(filename)
        if normalized_filename == normalized_new_title and original_title != new_title:
            return True
    return False

# Function to handle adding a new article
def add_article(new_title, new_content):
    existing_files = os.listdir(ARTICLES_DIR)
    if check_for_conflicts(new_title, existing_files):
        print(f"Conflict detected: An article with the title '{new_title}' already exists.")
        return False

    new_filename = normalize_filename(f"{new_title}.json")
    file_path = os.path.join(ARTICLES_DIR, new_filename)
    article = {
        "title": new_title,
        "content": new_content,
        "created_at": datetime.now().isoformat(),
        "last_modified": datetime.now().isoformat()
    }
    with open(file_path, 'w') as f:
        json.dump(article, f, indent=4)
    print(f"Article '{new_title}' added successfully.")
    return True

# Function to handle editing an existing article
def edit_article(original_title, new_title, new_content):
    existing_files = os.listdir(ARTICLES_DIR)
    if check_for_conflicts(new_title, existing_files, original_title):
        print(f"Conflict detected: An article with the title '{new_title}' already exists.")
        return False

    original_filename = normalize_filename(f"{original_title}.json")
    new_filename = normalize_filename(f"{new_title}.json")

    original_path = os.path.join(ARTICLES_DIR, original_filename)
    new_path = os.path.join(ARTICLES_DIR, new_filename)

    if not os.path.exists(original_path):
        print(f"Original article '{original_title}' not found.")
        return False

    with open(original_path, 'r') as f:
        article = json.load(f)

    article['title'] = new_title
    article['content'] = new_content
    article['last_modified'] = datetime.now().isoformat()

    with open(new_path, 'w') as f:
        json.dump(article, f, indent=4)

    if original_path != new_path:
        os.remove(original_path)
        print(f"Renamed and updated article '{original_title}' to '{new_title}'.")
    else:
        print(f"Updated article '{original_title}'.")

    return True

# Example usage of file handling functions
if __name__ == "__main__":
    # Step 1: Sanitize existing file names
    print("Sanitizing article files...")
    sanitize_article_files()

    # Step 2: Add metadata to articles
    print("Adding metadata to articles...")
    add_metadata_to_articles()

    # Example of adding an article
    print("Adding a new article...")
    add_article("New Article", "This is the content of the new article.")

    # Example of editing an article
    print("Editing an article...")
    edit_article("New Article", "Updated Article", "This is the updated content.")

    print("File handling and metadata updates complete.")

# Import necessary modules
import os
import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from blogapp.models import BlogPost

# Define the path to the directory containing markdown files
markdown_files_path = 'blogapp/blogs/'

# Function to extract front matter (metadata) and content from a markdown file
def extract_front_matter(file_content):
    front_matter = {}
    match = re.match(r'^---\n(.*?)\n---\n(.*)', file_content, re.DOTALL)
    if match:
        front_matter_text, content = match.groups()
        front_matter_lines = front_matter_text.strip().split('\n')
        for line in front_matter_lines:
            key, value = line.split(':', 1)
            front_matter[key.strip()] = value.strip()

    return front_matter, content

# Custom Django management command to create or update blog posts based on changes in Markdown files
class Command(BaseCommand):
    help = 'Create or update blog posts based on changes in Markdown files'

    # Main handle function for the command
    def handle(self, *args, **kwargs):
        try:
            # Retrieve existing blog posts from the database
            existing_posts = BlogPost.objects.all()
            existing_slugs = {post.slug for post in existing_posts}

            # Process markdown files and update or create blog posts
            self.process_markdown_files(existing_posts, existing_slugs)
            
            # Remove missing blog posts not found in the markdown files
            self.remove_missing_blog_posts(existing_slugs)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

    # Function to process markdown files and update or create blog posts
    def process_markdown_files(self, existing_posts, existing_slugs):
        for filename in os.listdir(markdown_files_path):
            if filename.endswith('.md'):
                with open(os.path.join(markdown_files_path, filename), 'r') as file:
                    file_content = file.read()
                    front_matter, content = extract_front_matter(file_content)
                    title = front_matter.get('Title', 'Untitled')
                    slug = slugify(title)
                    existing_slugs.discard(slug)

                    # Update or create a blog post based on the file content
                    self.update_or_create_post(
                        existing_posts,
                        slug,
                        title,
                        content,
                    )
            else:
                self.stdout.write(self.style.WARNING(f'Skipping file: {filename}'))

    # Function to update or create a blog post based on the provided information
    def update_or_create_post(self, existing_posts, slug, title, content):
        matching_posts = existing_posts.filter(slug=slug)

        if matching_posts.exists():
            # If the post exists, update it
            self.update_post(matching_posts.first(), title, content)
        else:
            # If the post does not exist, create a new one
            self.create_post(title, content, slug)

    # Function to update an existing blog post
    def update_post(self, post, title, content):
        if (
            post.title != title
            or post.content != content
        ):
            # Update the title and content if changes are detected
            post.title = title
            post.content = content

            post.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated post: {title}'))

        else:
            # No changes detected
            self.stdout.write(self.style.SUCCESS(f'No changes detected for post: {title}'))

    # Function to create a new blog post
    def create_post(self, title, content, slug):
        new_post = BlogPost(
            title=title,
            content=content,
            slug=slug,
        )
        new_post.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully created post: {title}'))

    # Function to remove missing blog posts that are not found in the markdown files
    def remove_missing_blog_posts(self, existing_slugs):
        if existing_slugs:
            # Delete missing blog posts based on their slugs
            BlogPost.objects.filter(slug__in=existing_slugs).delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted missing blog posts: {existing_slugs}'))


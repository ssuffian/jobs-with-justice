#!/usr/bin/env python3
"""
Convert WordPress SQL dump to Markdown files.
Extracts posts from wp_posts table and converts them to markdown format.
Connects to MySQL/MariaDB database (e.g., running in Docker).
"""

import re
import sys
from datetime import datetime
from pathlib import Path

import html2text
import pandas as pd
import pymysql


def get_posts_from_mysql(host='localhost', port=3306, user='root', password='root', database='pantheon'):
    """Extract published posts from MySQL/MariaDB database using pandas."""
    print(f"Connecting to MySQL database at {host}:{port}...")
    
    try:
        # Create connection (don't use DictCursor - pandas handles this better)
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        # Query for published posts
        query = """
            SELECT * FROM wp_posts 
            WHERE post_type = 'post' AND post_status = 'publish'
            ORDER BY post_date
        """
        
        # Use pandas to read SQL - it will handle column names automatically
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"Found {len(df)} published posts")
        
        # Debug: show column names and first row
        print(f"Column names: {list(df.columns)}")
        first_row = df.iloc[0]
        print(f"First row keys: {list(first_row.keys())[:5]}...")
        print(f"First row values (sample): {dict(list(first_row.items())[:3])}")
        
        # Convert to list of dictionaries where keys are column names
        records = df.to_dict('records')
        return records
        
    except pymysql.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        print("\nMake sure:")
        print("1. Docker container is running: docker ps")
        print("2. Database is created and SQL dump is imported")
        print("3. Connection credentials are correct")
        sys.exit(1)

def sanitize_filename(title):
    """Convert post title to a safe filename."""
    # Remove or replace invalid filename characters
    filename = re.sub(r'[^\w\s-]', '', title)
    filename = re.sub(r'[-\s]+', '-', filename)
    filename = filename.lower().strip('-')
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    return filename or 'untitled'

def html_to_markdown(html_content):
    """Convert HTML content to Markdown."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0  # Don't wrap lines
    h.unicode_snob = True
    markdown = h.handle(html_content)
    return markdown.strip()

def format_date(date_str):
    """Format WordPress date to markdown date format."""
    try:
        # WordPress format: 2018-05-15 00:37:40
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        # Format: Jul 08 2022
        return dt.strftime('%b %d %Y')
    except:
        return date_str

def create_markdown_file(post, output_dir):
    """Create a markdown file from a WordPress post."""
    # Debug: print post keys to see what we're working with
    if not hasattr(create_markdown_file, '_debug_printed'):
        print(f"Sample post keys: {list(post.keys())[:5]}...")
        create_markdown_file._debug_printed = True
    
    # Handle different possible column name formats
    # Try original case first (WordPress uses lowercase with underscores)
    title = post.get('post_title', '') or post.get('POST_TITLE', '') or post.get('Post_Title', 'Untitled')
    content = post.get('post_content', '') or post.get('POST_CONTENT', '') or post.get('Post_Content', '')
    excerpt = post.get('post_excerpt', '') or post.get('POST_EXCERPT', '') or post.get('Post_Excerpt', '')
    pub_date = post.get('post_date', '') or post.get('POST_DATE', '') or post.get('Post_Date', '')
    modified_date = post.get('post_modified', '') or post.get('POST_MODIFIED', '') or post.get('Post_Modified', '')
    post_id = post.get('ID', '') or post.get('id', '') or post.get('Id', 'unknown')
    
    # Check if we got column names as values (common issue)
    if title in ['post_title', 'POST_TITLE', 'Post_Title'] or title in post.keys():
        raise ValueError(f"Got column name '{title}' as value. Check database query. Post keys: {list(post.keys())}")
    
    # Use excerpt as description, or generate from content
    description = excerpt if excerpt else content[:200].replace('\n', ' ').strip()
    if len(description) > 200:
        description = description[:197] + '...'
    
    # Convert HTML to markdown
    markdown_content = html_to_markdown(content)
    
    # Generate filename
    filename = sanitize_filename(title)
    if not filename:
        filename = f"post-{post_id}"
    filepath = output_dir / f"{filename}.md"
    
    # Ensure unique filename
    counter = 1
    original_filepath = filepath
    while filepath.exists():
        filepath = output_dir / f"{filename}-{counter}.md"
        counter += 1
    
    # Create frontmatter
    frontmatter = f"""---
title: '{title.replace("'", "''")}'
description: '{description.replace("'", "''")}'
pubDate: '{format_date(pub_date)}'
"""
    
    if modified_date and modified_date != pub_date:
        frontmatter += f"updatedDate: '{format_date(modified_date)}'\n"
    
    frontmatter += "---\n\n"
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        f.write(markdown_content)
    
    return filepath

def main():
    # Output directory relative to project root (one level up from wordpress_export)
    output_dir = Path('../src/content/blog').resolve()
    
    # MySQL connection settings (defaults for Docker setup)
    mysql_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'pantheon'  # Default database name from SQL dump
    }
    
    # Allow override via command line args or environment
    import argparse
    parser = argparse.ArgumentParser(description='Convert WordPress posts to Markdown')
    parser.add_argument('--host', default=mysql_config['host'], help='MySQL host')
    parser.add_argument('--port', type=int, default=mysql_config['port'], help='MySQL port')
    parser.add_argument('--user', default=mysql_config['user'], help='MySQL user')
    parser.add_argument('--password', default=mysql_config['password'], help='MySQL password')
    parser.add_argument('--database', default=mysql_config['database'], help='MySQL database name')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract posts from MySQL using pandas
    posts = get_posts_from_mysql(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    if not posts:
        print("No posts found in database")
        sys.exit(1)
    
    # Convert each post to markdown
    print(f"\nConverting {len(posts)} posts to markdown...")
    for i, post in enumerate(posts, 1):
        try:
            filepath = create_markdown_file(post, output_dir)
            print(f"[{i}/{len(posts)}] Created: {filepath.name}")
        except Exception as e:
            print(f"Error converting post {post.get('ID', 'unknown')}: {e}")
    
    print(f"\nDone! Created {len(posts)} markdown files in {output_dir}")

if __name__ == '__main__':
    main()


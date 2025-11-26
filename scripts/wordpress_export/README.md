# WordPress to Markdown Converter

This script converts WordPress posts from a MySQL/MariaDB database to Markdown files.

All scripts are located in the `wordpress_export/` folder.

## Setup

1. **Navigate to the wordpress_export folder:**
   ```bash
   cd wordpress_export
   ```

2. **Install Python dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up MariaDB in Docker:**
   
   Option A: Use the setup script (recommended):
   ```bash
   ./setup_mysql.sh
   ```
   
   Option B: Manual setup:
   ```bash
   # Start MariaDB container
   docker run --name wpdb -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 -d mariadb:10.6
   
   # Wait a few seconds for MySQL to start, then create database
   docker exec -i wpdb mysql -uroot -proot -e "CREATE DATABASE pantheon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   
   # Import SQL dump (from wordpress_export directory)
   docker exec -i wpdb mysql -uroot -proot pantheon < philidelphia-jobs-with-justice_dev_2025-11-25T01-04-53_UTC_database.sql
   ```

## Usage

Once the database is set up and running (from the `wordpress_export/` directory):

```bash
source venv/bin/activate
python3 convert_wordpress_to_markdown.py
```

The script will:
1. Connect to the MySQL database
2. Extract all published posts
3. Convert HTML content to Markdown
4. Create markdown files in `../src/content/blog/` (relative to wordpress_export folder) with proper frontmatter

### Custom Connection Settings

If you need to use different connection settings:

```bash
python3 convert_wordpress_to_markdown.py \
  --host localhost \
  --port 3306 \
  --user root \
  --password root \
  --database pantheon
```

## Output

Markdown files will be created in `../src/content/blog/` (relative to wordpress_export folder) with:
- Frontmatter including title, description, and publication date
- HTML content converted to Markdown
- Safe filenames based on post titles

## Troubleshooting

- **Connection errors**: Make sure the Docker container is running (`docker ps`)
- **No posts found**: Check that the SQL dump was imported correctly
- **Database name**: The default is `pantheon` (from the SQL dump). Change with `--database` if needed


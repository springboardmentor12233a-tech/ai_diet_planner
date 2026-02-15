#!/usr/bin/env python3
"""
Database migration script for AI NutriCare System.

Usage:
    python migrations/migrate.py [--db-path PATH]
"""

import argparse
import os
import sqlite3
from datetime import datetime
from pathlib import Path


def get_current_version(conn: sqlite3.Connection) -> int:
    """Get current schema version."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(version) FROM schema_version")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return 0


def get_migration_files(migrations_dir: Path) -> list:
    """Get list of migration SQL files."""
    files = []
    for file in sorted(migrations_dir.glob("*.sql")):
        # Extract version number from filename (e.g., 001_initial_schema.sql -> 1)
        version_str = file.stem.split('_')[0]
        try:
            version = int(version_str)
            files.append((version, file))
        except ValueError:
            print(f"Warning: Skipping invalid migration file: {file.name}")
    return sorted(files, key=lambda x: x[0])


def apply_migration(conn: sqlite3.Connection, version: int, sql_file: Path) -> None:
    """Apply a migration file."""
    print(f"Applying migration {version}: {sql_file.name}")
    
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    cursor = conn.cursor()
    
    # Execute migration
    try:
        cursor.executescript(sql)
        conn.commit()
        print(f"✓ Migration {version} applied successfully")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"✗ Error applying migration {version}: {e}")
        raise


def run_migrations(db_path: str) -> None:
    """Run all pending migrations."""
    print(f"Database: {db_path}")
    print("=" * 50)
    
    # Get migrations directory
    migrations_dir = Path(__file__).parent
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    try:
        # Get current version
        current_version = get_current_version(conn)
        print(f"Current schema version: {current_version}")
        
        # Get migration files
        migrations = get_migration_files(migrations_dir)
        
        if not migrations:
            print("No migration files found")
            return
        
        # Apply pending migrations
        pending = [m for m in migrations if m[0] > current_version]
        
        if not pending:
            print("Database is up to date")
            return
        
        print(f"Found {len(pending)} pending migration(s)")
        print()
        
        for version, sql_file in pending:
            apply_migration(conn, version, sql_file)
        
        print()
        print("=" * 50)
        print("All migrations completed successfully")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


def create_backup(db_path: str) -> str:
    """Create a backup of the database."""
    if not os.path.exists(db_path):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    print(f"Creating backup: {backup_path}")
    
    # Copy database file
    import shutil
    shutil.copy2(db_path, backup_path)
    
    print(f"✓ Backup created")
    return backup_path


def main():
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument(
        "--db-path",
        default="data/nutricare.db",
        help="Path to SQLite database (default: data/nutricare.db)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup before migration"
    )
    
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
    
    # Create backup unless disabled
    if not args.no_backup and os.path.exists(args.db_path):
        create_backup(args.db_path)
        print()
    
    # Run migrations
    run_migrations(args.db_path)


if __name__ == "__main__":
    main()

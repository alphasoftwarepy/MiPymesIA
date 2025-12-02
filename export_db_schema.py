"""
Export Database Schema and Structure
Generates a SQL file with the complete database schema for documentation and migration
"""

import sqlite3
import os
from datetime import datetime

DB_NAME = "users.db"
OUTPUT_FILE = "database_schema.sql"

def export_schema():
    """Export complete database schema to SQL file."""
    
    if not os.path.exists(DB_NAME):
        print(f"❌ Database file '{DB_NAME}' not found!")
        return
    
    conn = sqlite3.connect(DB_NAME)
    
    # Get schema
    schema = "\n".join(conn.iterdump())
    
    # Create header
    header = f"""-- ============================================
-- MiPymesIA Database Schema Export
-- Generated: {datetime.now().isoformat()}
-- ============================================

"""
    
    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(schema)
    
    conn.close()
    
    print(f"✅ Schema exported to {OUTPUT_FILE}")
    
    # Print statistics
    print_db_stats()


def print_db_stats():
    """Print database statistics."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("\n📊 Database Statistics:")
    print("=" * 50)
    
    # Get all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = c.fetchall()
    
    for (table_name,) in tables:
        c.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = c.fetchone()[0]
        print(f"  📋 {table_name}: {count} records")
    
    # Get database size
    db_size = os.path.getsize(DB_NAME) / 1024  # KB
    print(f"\n  💾 Database size: {db_size:.2f} KB")
    
    conn.close()
    print("=" * 50)


def export_table_structure():
    """Export detailed table structure information."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    output = []
    output.append("# Database Table Structure\n")
    output.append(f"Generated: {datetime.now().isoformat()}\n\n")
    
    # Get all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = c.fetchall()
    
    for (table_name,) in tables:
        output.append(f"## Table: {table_name}\n")
        
        # Get table info
        c.execute(f"PRAGMA table_info({table_name})")
        columns = c.fetchall()
        
        output.append("| Column | Type | Not Null | Default | Primary Key |")
        output.append("|--------|------|----------|---------|-------------|")
        
        for col in columns:
            cid, name, col_type, not_null, default_val, pk = col
            output.append(f"| {name} | {col_type} | {not_null} | {default_val or 'NULL'} | {pk} |")
        
        # Get record count
        c.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = c.fetchone()[0]
        output.append(f"\n**Records:** {count}\n")
        
        # Get indexes
        c.execute(f"PRAGMA index_list({table_name})")
        indexes = c.fetchall()
        if indexes:
            output.append("\n**Indexes:**")
            for idx in indexes:
                output.append(f"- {idx[1]} (unique: {idx[2]})")
        
        output.append("\n---\n")
    
    # Write to markdown file
    with open("database_structure.md", 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    
    conn.close()
    print(f"✅ Table structure exported to database_structure.md")


if __name__ == "__main__":
    print("🔄 Exporting database schema...\n")
    export_schema()
    export_table_structure()
    print("\n✅ Export complete!")

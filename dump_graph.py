import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv()
sys_root = os.getenv("SYSTEM_ROOT_DIRECTORY")
db_path = os.path.join(sys_root, "databases", "cognee_db")

def dump_graph(output_file):
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try to find tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    dump = {}
    for table in tables:
        # Include tables that are likely graph nodes/edges or entities
        if any(kw in table.lower() for kw in ['edge', 'node', 'entity', 'relationship']):
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            col_names = [description[0] for description in cursor.description]
            
            dump[table] = [dict(zip(col_names, row)) for row in rows]
            
    conn.close()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dump, f, indent=4)
        
    print(f"Dumped graph data to {output_file}")

if __name__ == "__main__":
    import sys
    out = "graph_output.json"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    dump_graph(out)

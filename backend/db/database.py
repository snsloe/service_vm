import sqlite3

def init_db():
    conn = sqlite3.connect("hosting.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_type TEXT,
            os_type TEXT,
            cpu_cores INTEGER,
            ram_gb INTEGER,
            disk_gb INTEGER,
            ssh_key TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_resource(resource: dict):
    conn = sqlite3.connect("hosting.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resources (resource_type, os_type, cpu_cores, ram_gb, disk_gb, ssh_key)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        resource["resource_type"],
        resource["os_type"],
        resource["cpu_cores"],
        resource["ram_gb"],
        resource["disk_gb"],
        resource["ssh_key"]
    ))
    conn.commit()
    conn.close()
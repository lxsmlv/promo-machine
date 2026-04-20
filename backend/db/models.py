SCHEMA = """
CREATE TABLE IF NOT EXISTS trends (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    url TEXT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    duration REAL DEFAULT 0,
    hashtags TEXT DEFAULT '[]',
    audio_id TEXT,
    audio_name TEXT,
    description TEXT,
    file_path TEXT,
    analyzed INTEGER DEFAULT 0,
    analysis TEXT,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    features TEXT DEFAULT '[]',
    target_audience TEXT DEFAULT '',
    app_url TEXT DEFAULT '',
    screenshots_dir TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS renders (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    template TEXT NOT NULL,
    hook_text TEXT,
    script TEXT DEFAULT '{}',
    audio_path TEXT,
    output_path TEXT,
    duration REAL DEFAULT 30,
    status TEXT DEFAULT 'pending',
    platform_copy TEXT DEFAULT '{}',
    hashtags TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
"""

async def init_db(db):
    await db.executescript(SCHEMA)
    await db.commit()

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_PARAMS = {
    "host":     "localhost",
    "dbname":   os.getenv("DATABASE_NAME"),
    "user":     os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
}

def connect():
    """Establish a connection to the PostgreSQL database using psycopg2."""
    return psycopg2.connect(**DATABASE_PARAMS)

def create_vector_extension(cur):
    """Create the vector extension if it does not already exist."""
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

def drop_tables(cur):
    """Drop all tables in the database."""
    cur.execute("DROP TABLE IF EXISTS chunk_relationships;")
    cur.execute("DROP TABLE IF EXISTS questions;")
    cur.execute("DROP TABLE IF EXISTS knowledge_chunks;")

def create_tables(cur):
    """Create the necessary tables for the knowledge base."""
    cur.execute("""
        CREATE TABLE knowledge_chunks (
            id SERIAL PRIMARY KEY,
            document_id          TEXT,
            section              TEXT,
            original_sentence    TEXT,
            declarative_sentence TEXT,
            answer               TEXT,
            citations            JSONB,
            emb_declarative      VECTOR(384),
            emb_answer           VECTOR(384)
        );
    """)
    cur.execute("""
        CREATE TABLE questions (
            id SERIAL PRIMARY KEY,
            chunk_id      INTEGER REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
            question      TEXT,
            emb_question  VECTOR(384)
        );
    """)
    cur.execute("""
        CREATE TABLE chunk_relationships (
            id SERIAL PRIMARY KEY,
            source_chunk_id INTEGER REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
            target_chunk_id INTEGER REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
            relation_type   TEXT
        );
    """)

def create_vector_indexes(cur):
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_question_embedding
        ON questions USING ivfflat (emb_question vector_cosine_ops)
        WITH (lists = 100);
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_declarative_embedding
        ON knowledge_chunks USING ivfflat (emb_declarative vector_cosine_ops)
        WITH (lists = 100);
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_answer_embedding
        ON knowledge_chunks USING ivfflat (emb_answer vector_cosine_ops)
        WITH (lists = 100);
    """)
    cur.execute("ANALYZE questions;")
    cur.execute("ANALYZE knowledge_chunks;")

def init_db():
    with connect() as conn:
        with conn.cursor() as cur:
            print("🔧 Initializing database...")
            create_vector_extension(cur)
            drop_tables(cur)
            create_tables(cur)
            create_vector_indexes(cur)
        conn.commit()
    print("✅ Database initialized with tables and indexes.")

def drop_db():
    with connect() as conn:
        with conn.cursor() as cur:
            print("🗑️ Dropping all tables...")
            drop_tables(cur)
        conn.commit()
    print("🧹 All tables dropped.")

def delete_by_document_id(cur, document_id: str):
    """
    Deletes all questions and knowledge_chunks associated with the given document_id.
    """
    # Delete questions first due to foreign key constraints
    cur.execute("""
        DELETE FROM questions
        WHERE document_id = %s;
    """, (document_id,))

    # Then delete chunks
    cur.execute("""
        DELETE FROM knowledge_chunks
        WHERE document_id = %s;
    """, (document_id,))

def delete_document_data(document_id):
    with connect() as conn:
        with conn.cursor() as cur:
            print(f"Deleting data for document_id = '{document_id}'...")
            delete_by_document_id(cur, document_id)
        conn.commit()
    print(f"✅ Deleted all data for document_id = '{document_id}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python database.py <init|drop>")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "init":
        init_db()
    elif command == "drop":
        drop_db()
    elif command == "document:delete":
        if len(sys.argv) != 3:
            print("Usage: python database.py delete <document_id>")
            sys.exit(1)
        document_id = sys.argv[2]
        delete_document_data(document_id)
    else:
        print("Unknown command. Use 'init' to initialize or 'drop' to drop all tables.")
        sys.exit(1)

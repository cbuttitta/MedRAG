import os
import csv
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Force load .env from medrag root regardless of where script is run from
dotenv_path = Path(__file__).parent.parent / '.env'
print(f"Loading .env from: {dotenv_path}")
print(f".env exists: {dotenv_path.exists()}")
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv('DATABASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

print(f"DATABASE_URL: {DATABASE_URL}")
print(f"OPENAI_API_KEY set: {bool(OPENAI_API_KEY)}")

# Test database connection before doing anything else
print("\nTesting database connection...")
try:
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
    print("Database connection successful.")
    cur = conn.cursor()
except Exception as e:
    print(f"DATABASE CONNECTION FAILED: {e}")
    raise SystemExit(1)

# Test OpenAI connection
print("\nTesting OpenAI connection...")
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    test = client.embeddings.create(
        model='text-embedding-3-small',
        input='test connection'
    )
    print(f"OpenAI connection successful. Embedding dimensions: {len(test.data[0].embedding)}")
except Exception as e:
    print(f"OPENAI CONNECTION FAILED: {e}")
    raise SystemExit(1)

CORPUS_DIR = Path(__file__).parent / 'corpus'
METADATA_FILE = CORPUS_DIR / 'metadata.csv'

print(f"\nCorpus directory: {CORPUS_DIR}")
print(f"Corpus directory exists: {CORPUS_DIR.exists()}")
print(f"Metadata file exists: {METADATA_FILE.exists()}")


def embed(text: str) -> list[float]:
    print(f"    Embedding text ({len(text)} chars)...")
    try:
        response = client.embeddings.create(
            model='text-embedding-3-small',
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"    EMBEDDING FAILED: {e}")
        raise


def ingest_file(filename: str, source_name: str, section: str):
    filepath = CORPUS_DIR / filename
    print(f"\nProcessing: {filename}")
    print(f"  Source: {source_name}")
    print(f"  Section: {section}")
    print(f"  File exists: {filepath.exists()}")

    if not filepath.exists():
        print(f"  SKIPPING — file not found at {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        chunks = [line.strip() for line in f if line.strip()]

    print(f"  Chunks found: {len(chunks)}")

    for i, chunk in enumerate(chunks):
        print(f"  [{i+1}/{len(chunks)}] Processing chunk ({len(chunk)} chars)...")
        try:
            embedding = embed(chunk)
            cur.execute(
                '''
                INSERT INTO documents (source, section, content, embedding)
                VALUES (%s, %s, %s, %s::vector)
                ''',
                (source_name, section, chunk, str(embedding))
            )
            print(f"  [{i+1}/{len(chunks)}] Inserted successfully.")
        except Exception as e:
            print(f"  [{i+1}/{len(chunks)}] FAILED: {e}")
            conn.rollback()
            raise

    conn.commit()
    print(f"  Committed. Done with {filename}.")


def main():
    print("\nReading metadata.csv...")
    try:
        with open(METADATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        print(f"Found {len(rows)} files to ingest.")
    except Exception as e:
        print(f"FAILED to read metadata.csv: {e}")
        raise SystemExit(1)

    for row in rows:
        try:
            ingest_file(
                filename=row['filename'],
                source_name=row['source_name'],
                section=row['section']
            )
        except Exception as e:
            print(f"\nINGESTION ABORTED on {row['filename']}: {e}")
            raise SystemExit(1)

    cur.close()
    conn.close()
    print('\nAll documents ingested successfully.')


if __name__ == '__main__':
    main()

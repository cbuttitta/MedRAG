import os
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def get_connection():
    """Returns a new database connection. Called fresh each request."""
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def embed(text: str) -> list[float]:
    """Embeds a query string using the same model used during ingestion."""
    response = client.embeddings.create(
        model='text-embedding-3-small',
        input=text
    )
    return response.data[0].embedding


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Embeds the query and finds the top_k most similar document chunks.

    The <=> operator is pgvector's cosine distance operator.
    Cosine distance ranges from 0 (identical) to 2 (opposite).
    We subtract from 1 to get cosine SIMILARITY (1 = identical, -1 = opposite).

    ORDER BY embedding <=> query_vector sorts by distance ascending,
    so the most similar chunks come first.
    """
    query_embedding = embed(query)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        '''
        SELECT
            source,
            section,
            content,
            1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        ''',
        (str(query_embedding), str(query_embedding), top_k)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            'source': row[0],
            'section': row[1],
            'content': row[2],
            'similarity': float(row[3]),
        }
        for row in rows
    ]


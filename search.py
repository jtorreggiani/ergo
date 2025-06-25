from database import connect
from embedding import create_embedding


def to_pgvector_literal(vec: list[float]) -> str:
    """
    Convert a Python list of floats into a PostgreSQL pgvector literal string,
    e.g. [0.1, 0.2] -> '[0.1,0.2]'
    """
    # limit float precision for readability; adjust as needed
    return '[' + ','.join(f'{v:.6f}' for v in vec) + ']'


def search(query: str, k: int = 5):
    """
    Search all fields (questions, answers, declarative sentences) for semantic similarity
    and return top-k results ordered by closest distance.

    Returns a list of tuples:
    (question, answer, declarative_sentence, original_sentence, distance, source)
    """

    raw_emb = create_embedding(query)
    pg_emb = to_pgvector_literal(raw_emb)

    sql = """
    WITH question_matches AS (
        SELECT
            q.question,
            kc.answer,
            kc.declarative_sentence,
            kc.original_sentence,
            q.emb_question <-> %s::vector AS distance,
            'question' AS source
        FROM questions q
        JOIN knowledge_chunks kc ON q.chunk_id = kc.id
    ),
    answer_matches AS (
        SELECT
            NULL::TEXT AS question,
            kc.answer,
            kc.declarative_sentence,
            kc.original_sentence,
            kc.emb_answer <-> %s::vector AS distance,
            'answer' AS source
        FROM knowledge_chunks kc
    ),
    declarative_matches AS (
        SELECT
            NULL::TEXT AS question,
            kc.answer,
            kc.declarative_sentence,
            kc.original_sentence,
            kc.emb_declarative <-> %s::vector AS distance,
            'declarative' AS source
        FROM knowledge_chunks kc
    )
    SELECT * FROM (
        SELECT * FROM question_matches
        UNION ALL
        SELECT * FROM answer_matches
        UNION ALL
        SELECT * FROM declarative_matches
    ) combined
    ORDER BY distance
    LIMIT %s;
    """

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (pg_emb, pg_emb, pg_emb, k))
            results = cur.fetchall()

    return results


if __name__ == "__main__":
    import sys
    from rich.console import Console
    from rich.table import Table

    console = Console()

    if len(sys.argv) < 2:
        console.print("Usage: python -m src.search <query> [k]")
        sys.exit(1)

    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    rows = search(query, k)

    table = Table(title="Search Results")
    table.add_column("#", justify="right")
    table.add_column("Question", style="cyan")
    table.add_column("Answer", style="green")
    table.add_column("Statement", style="magenta")
    table.add_column("Distance", justify="right")
    table.add_column("Source", style="yellow")

    for i, (question, answer, declarative, original, dist, source) in enumerate(rows, 1):
        display_question = question if question else "-"
        table.add_row(str(i), display_question, answer, declarative, f"{dist:.4f}", source)

    console.print(table)

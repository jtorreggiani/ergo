import os
import sys
import json
from database import connect
from embedding import create_embedding
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import dspy
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

MODEL = 'anthropic/claude-3-opus-20240229'
API_KEY = os.getenv("ANTHROPIC_API_KEY")

lm = dspy.LM(MODEL, api_key=API_KEY)
dspy.configure(lm=lm)

# ---------- Data Models ----------

class ChunkObject(BaseModel):
    question: str
    answer: str
    statement: str

class ChunkKnowledge(dspy.Signature):
    """Chunk the sentence into Q/A/declarative triples"""
    sentence: str = dspy.InputField()
    chunks: list[ChunkObject] = dspy.OutputField()
    confidence: float = dspy.OutputField()

def chunk_knowledge(sentence: str) -> ChunkKnowledge:
    classify = dspy.Predict(ChunkKnowledge)
    return classify(sentence=sentence)

# ---------- Helpers ----------

def save_chunk_to_preview(item: dict, chunk: ChunkObject):
    preview_path = "data/preview.json"
    if os.path.exists(preview_path):
        with open(preview_path, "r", encoding="utf-8") as pf:
            preview_data = json.load(pf)
    else:
        preview_data = {"chunks": []}

    preview_data["chunks"].append({**chunk.model_dump(), **item})
    with open(preview_path, "w", encoding="utf-8") as pf:
        json.dump(preview_data, pf, indent=2, ensure_ascii=False)

# ---------- Insert Logic ----------

def insert_knowledge_chunk(cur, document_id, section, original, declarative, answer, citations, emb_decl, emb_ans):
    cur.execute("""
        INSERT INTO knowledge_chunks (
            document_id,
            section,
            original_sentence,
            declarative_sentence,
            answer,
            citations,
            emb_declarative,
            emb_answer
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (document_id, section, original, declarative, answer, json.dumps(citations), emb_decl, emb_ans))
    return cur.fetchone()[0]

def insert_question(cur, chunk_id, question, emb_question):
    cur.execute("""
        INSERT INTO questions (
            chunk_id,
            question,
            emb_question
        ) VALUES (%s, %s, %s);
    """, (chunk_id, question, emb_question))

# ---------- Load Function ----------

def load_sentences(json_path: str):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    sentences = data.get("sentences", [])
    total_chunks = 0

    # Get file base name for document_id
    document_id = os.path.splitext(os.path.basename(json_path))[0]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} sentences"),
        transient=True
    ) as progress:
        task = progress.add_task("Processing sentences", total=len(sentences))

        with connect() as conn:
            with conn.cursor() as cur:
                for item in sentences:
                    original = item["sentence"]
                    section = item.get("section")
                    citations = item.get("citations", [])

                    result = chunk_knowledge(original)

                    for chunk in result.chunks:
                        save_chunk_to_preview(item, chunk)

                        emb_decl = create_embedding(chunk.statement)
                        emb_ans  = create_embedding(chunk.answer)
                        emb_q    = create_embedding(chunk.question)

                        chunk_id = insert_knowledge_chunk(
                            cur, document_id, section, original, chunk.statement,
                            chunk.answer, citations, emb_decl, emb_ans
                        )

                        insert_question(cur, chunk_id, chunk.question, emb_q)
                        total_chunks += 1

                    conn.commit()
                    progress.update(task, advance=1)

    print(f"✅ Loaded {total_chunks} chunks from {len(sentences)} sentences.")

# ---------- Entrypoint ----------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load.py <path_to_json>")
        sys.exit(1)

    load_sentences(sys.argv[1])

import os
import sys
import json
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
    """
    Break up the sentence into discrete chunks of knowledge that are 7-10 words long.
    If a sentence is an introduction sentence, always include a chunk
    with a definitional statement and appropriate question/answer pair where
    the question is in the form of "What is <term>?" and the answer is a definition
    of the core term.
    """
    sentence: str = dspy.InputField(desc="The sentence to break into chunks.")
    chunks: list[ChunkObject] = dspy.OutputField()
    confidence: float = dspy.OutputField()

def chunk_knowledge(sentence: str, paragraph: str) -> ChunkKnowledge:
    classify = dspy.Predict(ChunkKnowledge)
    return classify(
        sentence=sentence,
        paragraphs=paragraph,
    )

# ---------- Helpers ----------



def save_chunk_to_preview(document_id: str, item: dict, chunk: ChunkObject):
    data_path = f"chunks/{document_id}.json"
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as pf:
            chunks_data = json.load(pf)
    else:
        chunks_data = {"chunks": []}

    chunks_data["chunks"].append({**chunk, **item})
    with open(data_path, "w", encoding="utf-8") as pf:
        json.dump(chunks_data, pf, indent=2, ensure_ascii=False)


def load_sentences(json_path: str):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    sentences = data.get("sentences", [])
    total_chunks = 0

    # Get file base name for document_id
    document_id = os.path.splitext(os.path.basename(json_path))[0]

    chunks_path = f"chunks/{document_id}.json"
    with open(chunks_path, "w", encoding="utf-8") as pf:
        json.dump({"chunks": []}, pf, indent=2, ensure_ascii=False)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} sentences"),
        transient=True
    ) as progress:
        task = progress.add_task("Processing sentences", total=len(sentences))
        for item in sentences:
            sentence = item.get("sentence", "")
            paragraph = item.get("paragraph", "")
            result = chunk_knowledge(sentence, paragraph)
            for chunk in result.chunks:
                chunk_data = chunk.model_dump()
                save_chunk_to_preview(document_id, item, chunk_data)
                total_chunks += 1

            progress.update(task, advance=1)

    print(f"✅ Loaded {total_chunks} chunks from {len(sentences)} sentences.")

# ---------- Entrypoint ----------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load.py <path_to_json>")
        sys.exit(1)

    load_sentences(sys.argv[1])

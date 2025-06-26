# ERGO

Ergo is a tool for knowledge extraction and generating structured datasets that are optimized for human understanding and learning, and development of AI applications.

## BACKGROUND

Ergo was developed to test the application insights from cognitive science and psychology to the optimize automated processes for knowledge extraction and information-retrieval. The tool draws inspiration from the work of [Dr. Piotr Wozniak](https://en.wikipedia.org/wiki/Piotr_Wo%C5%BAniak_(researcher)) and the principles of spaced repetition, chunking, cognitive load theory, and incremental reading.

## CORE PRINCIPLES

**Knowledge Representation**

At its core, Ergo is built around breaking up knowledge into chunks according Wozniak's [Twenty rules of formulating knowledge](https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge), and our current understanding of human cognition and neuroscience. These rules are designed to optimize the way knowledge is structured and presented, making it easier for humans to understand and remember.

**Incremental Reading**

Incremental reading is a learning method where you read small portions from multiple documents per session rather than completing texts linearly. Key concepts are extracted into flashcards and reviewed using spaced repetition algorithms. This approach prioritizes understanding and retaining the underlying knowledge over memorizing exact wording, focusing on conceptual grasp rather than sequential text completion.[1]

**Chunking**

[Chunking](https://en.wikipedia.org/wiki/Chunking_(psychology)) a process by which individual pieces of information are bound together to create a meaningful whole in or memory. This technique is used to improve the efficiency of information processing and retention, and bypass capacity limits of working memory. Chunking has already been applied in Retrieval-Augmented Generation (RAG) systems. Please see the article [Breaking up is hard to do: Chunking in RAG applications](https://stackoverflow.blog/2024/12/27/breaking-up-is-hard-to-do-chunking-in-rag-applications/) for more about the current thinking around chunking data for RAG.

Some of the current approaches to chunking in RAG applications include:

- Fixed-size chunking splits text into predetermined chunk sizes with optional overlap - the most common approach.
- Recursive chunking uses hierarchical separators (paragraphs → sentences → words) to maintain content coherence while reaching target chunk sizes.
- Semantic chunking groups sentences by embedding similarity, creating context-aware chunks based on meaning rather than length.
- Document-based chunking splits text according to structural elements like headings, tables, code blocks, and markdown formatting.
- Agentic chunking uses AI to intelligently determine splits based on both semantic meaning and document structure, simulating human reasoning for optimal segmentation. [2]

Ergo's chunking strategy can be considered a hybrid approach that leverages techniques from these methods and integrates them with a cognitive science based framework.

**Spaced Repetition**

Spaced Repetition (SR) is a learning technique that leverages the spacing effect, which demonstrates that learning is more effective when study sessions are spaced out. This effect shows that more information is encoded into long-term memory by spaced study sessions. This technique is widely used in educational software and applications, such as SuperMemo and Anki, to help users retain information over time.

SR attempts to address the "forgetting curve", which hypothesizes the decline of human memory retention over time. This curve shows how information is lost after a period of time when there is no attempt to retain it. This is related to the concept is the "strength of memory" that refers to the durability of memory traces in the brain. This decline in memory can partially be explain by natural process of Synaptic pruning in the brain where connections between neurons are eliminated, strengthening the most important connections.

Applying this principle to Ergo, we seek to avoid the issues with overtraining models by incorporating a process analogous to spaced repetition to continuously evaluate the performance of queries on knowledge graphs as new information is added. This process can also identify when a source material has changed and needs to be re-evaluated, ensuring that the knowledge representation remains up-to-date and relevant.

## CORE DEPENDENCIES

- Python 3.10 or higher
- uv
- Postgresql
- [DSPY](https://dspy.ai/)
- [NLTK](https://www.nltk.org/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Psycopg](https://www.psycopg.org/)
- [sentence-transformers](https://sbert.net/)

## GETTING STARTED

Ergo currently only supports extracting knowledge from Wikipedia articles and only implements a basic single pass chunking strategy. The demo does leverage vector search via PGVector, but its not configured with a specific LLM/RAG application. In order to use data generated by Ergo, with a tool like LLamaIndex or LangChain, you will likely need to change the embeddding model used in `embedding.py`. The default embedding model being used is `all-MiniLM-L6-v2`.

To extract knowledge from a wikipedia article, for example [https://en.wikipedia.org/wiki/Systems_thinking](https://en.wikipedia.org/wiki/Systems_thinking) you enter the URL slug `Systems_thinking` into the `read_wikipedia.py` script and run it:

```bash
python -m src.read_wikipedia Systems_thinking
```

This will generate a JSON file in the `raw_data` directory with the form `TITLE-YYYY-MM-DD.json`. The file will contain a structured representation of the knowledge extracted from the article. Wikipedia articles are not always well-structured, so the output may vary in quality. If you are getting bad results you may need to tweak the `read_wikipedia.py` script to improve the extraction process.

## GENERATING CHUNKS

To generate chunks from the extracted knowledge, you can use the `generate_chunks.py` script. This script will take the JSON file generated by `read_wikipedia.py` and create smaller, more  These will be stored in the `chunks` directory.

```bash
python -m src.generate_chunks raw_data/TITLE-YYYY-MM-DD.json
```

You should review these before writing them to the database, as they may need some manual adjustments to ensure they are well-structured and useful for training AI models or for human understanding.

## INITIALIZING THE DATABASE

Ergo uses a PostgreSQL database to store the extracted knowledge and chunks. You will need to have a PostgreSQL server running and create a database for Ergo. You can do this using the following commands:

```bash
createdb ergo_db
```

Set your database configs in the `.env` file in the root directory of the project. The `.env` file should contain the following variables:

```bash
ANTHROPIC_API_KEY="OPTIONAL_API_KEY"
DATABASE_NAME="ergo_db"
DATABASE_USER="usernamed"
DATABASE_PASSWORD=""
```

To initialize the database schema, you can use the `database.py` script. This script will create the necessary tables and indexes in the database to store the extracted knowledge and chunks.

```bash
python -m src.database init
```

## INSERTING CHUNKS INTO THE DATABASE

Once you have generated the chunks and reviewed them, you can write them to the database using the `insert_chunks.py` script. This script will take the chunks from the `chunks` directory and write them to the database.

```bash
python -m src.insert_chunks chunks/TITLE-YYYY-MM-DD.json
```

## QUERY THE DATABASE

You can test natural language search queries on your database using the `chat.py` script. This script starts a simple chat that allows you to ask questions about the knowledge stored in the database and return the top three most relevant chunks.

```bash
python -m src.chat
```

<img width="1277" alt="Screenshot 2025-06-26 at 3 45 38 PM" src="https://github.com/user-attachments/assets/7bfae842-47c0-4a5f-988f-064b54173063" />

## REFERENCES

- 1. [Wikipedia: Incremental Reading](https://en.wikipedia.org/wiki/Incremental_reading)
- 2. [Implement RAG chunking strategies with LangChain and watsonx.ai](https://www.ibm.com/think/tutorials/chunking-strategies-for-rag-with-langchain-watsonx-ai)

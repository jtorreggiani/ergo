# ERGO

Ergo is a tool for extracting knowledge from text and generating structured data structures that are optimized for human understanding and learning, and training and information-retrieval in AI applications.

## Getting Started

Ergo currently supports extracting knowledge from Wikipedia articles.

To extract knowledge from a wikipedia article, for example [https://en.wikipedia.org/wiki/Systems_thinking](https://en.wikipedia.org/wiki/Systems_thinking) you enter the URL slug `Systems_thinking` into the `read_wikipedia.py` script and run it:

```bash
python read_wikipedia.py Systems_thinking
```

This will generate a JSON file in the `raw_data` directory with the form `TITLE-YYYY-MM-DD.json`. The file will contain a structured representation of the knowledge extracted from the article. Wikipedia articles are not always well-structured, so the output may vary in quality. If you are getting bad results you may need to tweak the `read_wikipedia.py` script to improve the extraction process.

## Chunking
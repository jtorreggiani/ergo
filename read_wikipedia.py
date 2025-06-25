import os
import sys
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re
import json
import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from datetime import datetime

punkt_param = PunktParameters()
punkt_param.abbrev_types = set(['dr', 'vs', 'mr', 'mrs', 'prof', 'inc', 'al', 'u.s.', 'bce', 'ca'])
sentence_splitter = PunktSentenceTokenizer(punkt_param)


def collapse_adjacent_duplicate_citations(text):
    return re.sub(r'(\[\d+\])(?:\1)+', r'\1', text)

def fetch_wikipedia_html(title):
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_sections(soup):
    content_div = soup.find("div", {"id": "mw-content-text"})
    target_div = content_div.find('div', class_='mw-content-ltr mw-parser-output')
    sections = []

    if not target_div:
        print("No content found in the specified div.")
        return sections

    elements = target_div.find_all()
    current_section_name = "Introduction"
    current_section = {
        "name": current_section_name,
        "paragraphs": []
    }

    for element in elements:
        if element.name == "h2":
            if current_section["paragraphs"]:
                sections.append(current_section)
            current_section_name = element.get_text(separator=' ').strip()
            current_section = {
                "name": current_section_name,
                "paragraphs": []
            }
        elif element.name in {"p", "ul", "ol"}:
            if element.name == "p":
                # Skip if element parent is sidebar-list-content
                if element.parent and element.parent.get("class") == ['sidebar-list-content', 'mw-collapsible-content']:
                    continue

                text = element.get_text(separator=' ')
                formatted_text = re.sub(r'\s+', ' ', text).strip()
                if formatted_text:
                    current_section["paragraphs"].append(formatted_text)
            else:
                list_items = element.find_all("li")
                list_content = []
                for item in list_items:
                    text = item.get_text(separator=' ')
                    formatted_text = re.sub(r'\s+', ' ', text).strip()
                    if formatted_text:
                        list_content.append(formatted_text)
                if list_content:
                    list_text = " ".join(list_content)
                    current_section["paragraphs"].append(list_text)

    if current_section["paragraphs"]:
        sections.append(current_section)
    return sections

def extract_embedded_citations(text):
    text = collapse_adjacent_duplicate_citations(text)
    pattern = re.compile(r'\[\s*(\d+)\s*\]')
    citations = pattern.findall(text)
    return [int(c) for c in citations] if citations else []

def extract_ending_citations(sentence):
    match = re.search(r'(\s*(?:\[\s*\d+\s*\]\s*)+)$', sentence)
    if match:
        citation_block = match.group(1)
        numbers = [int(n) for n in re.findall(r'\d+', citation_block)]
        return numbers
    return []

def get_sentence_and_proceeding_citations(text):
    if not text or text == "":
        return (text, [])
    match = re.match(r'^((?:\s*\[\s*\d+\s*\])+)\s*(.*)', text)
    if match:
        citations_boxes = match.group(1).strip()
        sentence = match.group(2).strip()
        # Split the citations into a list of integers
        citations = [int(num) for num in re.findall(r'\d+', citations_boxes)]
        return (sentence, citations)
    else:
        return (text, [])

def format_sentence(sentence):
    return re.sub(r'^\s*(?:\[\s*\d+\s*\]\s*)+', '', sentence).strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: python read_wikipedia.py <Wikipedia Title>")
        sys.exit(1)

    title = sys.argv[1]
    html = fetch_wikipedia_html(title)
    soup = BeautifulSoup(html, 'html.parser')
    sections = extract_sections(soup)

    sections_to_skip = {"References", "External links", "Further reading", "See also"}
    data_records = []
    seen_paragraphs = set()

    for section in sections:
        if section["name"] in sections_to_skip:
            continue

        for paragraph in section["paragraphs"]:
            # Skip exacty duplicate paragraphs
            if paragraph in seen_paragraphs:
                continue
            seen_paragraphs.add(paragraph)

            sentences = sentence_splitter.tokenize(paragraph)
            # iterate over each with an index to be able to look up the next sentence
            for i, sentence_text in enumerate(sentences):
                # This removes any leading citations from the sentence text.
                sentence, _ = get_sentence_and_proceeding_citations(sentence_text)
                next_sentence = None

                next_index = i + 1
                proceeding_citations = []
                if next_index < len(sentences):
                    next_sentence = sentences[next_index]
                    _, proceeding_citations = get_sentence_and_proceeding_citations(next_sentence)

                embedded_citations = extract_embedded_citations(sentence)
                citations = embedded_citations + proceeding_citations
                record = {
                    "section": section["name"],
                    "paragraph": paragraph,
                    "sentence": sentence,
                    "citations": citations,
                }
                data_records.append(record)

    data = {
        "title": title,
        "sentences": data_records,
    }

    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    out_filename = f"data/{title.replace(' ', '_')}-{timestamp}.json"

    with open(out_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(data_records)} sentences to {out_filename}")

if __name__ == "__main__":
    main()

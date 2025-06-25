import pytest
from bs4 import BeautifulSoup

from read_wikipedia import (
    collapse_adjacent_duplicate_citations,
    extract_embedded_citations,
    extract_ending_citations,
    get_sentence_and_proceeding_citations,
    format_sentence,
    extract_sections,
)

def test_collapse_adjacent_duplicate_citations():
    text = "This is a test [1][1][1] and another [2][2]."
    expected = "This is a test [1] and another [2]."
    assert collapse_adjacent_duplicate_citations(text) == expected

def test_extract_embedded_citations():
    text = "Some text [12] with [34] citations [12][12]."
    assert extract_embedded_citations(text) == [12, 34, 12]

def test_extract_ending_citations():
    sentence = "Some statement. [1][2][3]"
    assert extract_ending_citations(sentence) == [1, 2, 3]

    sentence = "Some statement with no citations"
    assert extract_ending_citations(sentence) == []

def test_get_sentence_and_proceeding_citations():
    sentence = "[1][2] The quick brown fox."
    expected = ("The quick brown fox.", [1, 2])
    assert get_sentence_and_proceeding_citations(sentence) == expected

    sentence = "No citations here."
    expected = ("No citations here.", [])
    assert get_sentence_and_proceeding_citations(sentence) == expected

def test_format_sentence():
    assert format_sentence("[1][2] Hello world.") == "Hello world."
    assert format_sentence("No citations.") == "No citations."

def test_extract_sections_minimal_html():
    html = """
    <div id="mw-content-text">
      <div class="mw-content-ltr mw-parser-output">
        <h2>History</h2>
        <p>This is the first paragraph.</p>
        <ul><li>Bullet one</li><li>Bullet two</li></ul>
        <h2>References</h2>
        <p>This should not appear in History.</p>
      </div>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    sections = extract_sections(soup)
    assert sections[0]["name"] == "History"
    assert "This is the first paragraph." in sections[0]["paragraphs"]
    assert "Bullet one Bullet two" in sections[0]["paragraphs"]


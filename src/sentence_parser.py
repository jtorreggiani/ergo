from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

punkt_param = PunktParameters()
punkt_param.abbrev_types = set([
    'dr',
    'vs',
    'mr',
    'mrs',
    'prof',
    'inc',
    'al',
    'us',
    'u.s',
    'u. s',
    'bce',
    'ca',
    'ie',
    'eg',
    'i.e',
    'aka',
    'etc',
    'a.k.a',
    '(i.e'
    '(a.k.a',
    'etc.)'
])

sentence_splitter = PunktSentenceTokenizer(punkt_param)

def split_sentences(text: str):
    """
    Split a given text into sentences using NLTK's PunktSentenceTokenizer.
    """
    sentences = sentence_splitter.tokenize(text)

    formatted_sentences = []
    for sentence in sentences:
        # Remove leading and trailing whitespace
        sentence = sentence.strip()
        # Remove any trailing punctuation that might be left over
        sentence = sentence.replace(" ,", ",")
        formatted_sentences.append(sentence)
    return formatted_sentences
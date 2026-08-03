"""
NLP preprocessing pipeline, as described in Chapter Five, Section 5.4:
lowercase -> remove punctuation/special characters -> tokenize (NLTK) ->
remove stop words -> lemmatize (WordNetLemmatizer).
"""
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

_stop_words = set(stopwords.words("english"))
_lemmatizer = WordNetLemmatizer()


def preprocess(text: str) -> str:
    """Clean and normalise a raw query string into a lemmatised token string."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = word_tokenize(text)
    tokens = [_lemmatizer.lemmatize(t) for t in tokens if t not in _stop_words and t.strip()]
    return " ".join(tokens)

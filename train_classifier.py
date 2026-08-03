"""
Trains the TF-IDF + Multinomial Naive Bayes intent classifier described
in Chapter Five, Section 5.5.1, using the knowledge base as training data,
and serialises the fitted pipeline components with joblib.

Run from the project root:
    python ml/train_classifier.py
"""
import os
import sys
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import f1_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import KnowledgeBase
from app.nlp_utils import preprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    app = create_app()
    with app.app_context():
        entries = KnowledgeBase.query.all()
        if len(entries) < 5:
            print("Not enough knowledge base entries to train on. "
                  "Run 'python data/seed_knowledge_base.py' first.")
            return

        texts = [preprocess(e.question) for e in entries]
        labels = [e.intent_label for e in entries]

        # CountVectorizer + unigrams/bigrams performs more reliably than TF-IDF
        # for MultinomialNB on this dataset size; alpha=0.1 gives a realistic
        # (not artificially inflated) confidence calibration.
        vectorizer = CountVectorizer(ngram_range=(1, 2))
        X = vectorizer.fit_transform(texts)

        classifier = MultinomialNB(alpha=0.1)
        classifier.fit(X, labels)

        # --- Honest, held-out performance estimate (5-fold cross-validation) ---
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(classifier, X, labels, cv=skf)
        cv_preds = cross_val_predict(classifier, X, labels, cv=skf)
        cv_f1 = f1_score(labels, cv_preds, average="macro")

        joblib.dump(vectorizer, os.path.join(HERE, "vectorizer.pkl"))
        joblib.dump(classifier, os.path.join(HERE, "classifier.pkl"))

        print(f"Trained on {len(entries)} knowledge base entries "
              f"across {len(set(labels))} intent classes.")
        print("Saved vectorizer.pkl and classifier.pkl to", HERE)
        print()
        print("--- Honest held-out performance (5-fold cross-validation) ---")
        print(f"Per-fold accuracy: {[round(s, 3) for s in cv_scores]}")
        print(f"Mean accuracy:     {cv_scores.mean():.3f}")
        print(f"Macro F1 score:    {cv_f1:.3f}")
        print("Use THESE numbers in Chapter Six, not assumed/copied benchmark figures.")


if __name__ == "__main__":
    main()

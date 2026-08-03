"""
Chat blueprint: serves the chat interface and handles the /api/chat
endpoint described in Chapter Five, Section 5.4 (Backend Processing Logic).
"""
import os
import uuid
import joblib
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, session

from app import db
from app.models import KnowledgeBase, Response
from app.nlp_utils import preprocess
from app.llm_fallback import generate_fallback_response

chat_bp = Blueprint("chat", __name__)

CONFIDENCE_THRESHOLD = 0.70
MAX_QUERY_LENGTH = 500

_ml_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml")
_vectorizer_path = os.path.join(_ml_dir, "vectorizer.pkl")
_classifier_path = os.path.join(_ml_dir, "classifier.pkl")

_vectorizer = None
_classifier = None


def _load_model():
    global _vectorizer, _classifier
    if _vectorizer is None or _classifier is None:
        if not (os.path.exists(_vectorizer_path) and os.path.exists(_classifier_path)):
            raise FileNotFoundError(
                "Model files not found. Run 'python ml/train_classifier.py' first."
            )
        _vectorizer = joblib.load(_vectorizer_path)
        _classifier = joblib.load(_classifier_path)
    return _vectorizer, _classifier


@chat_bp.route("/")
def chat_page():
    return render_template("chat.html")


@chat_bp.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    raw_query = (data.get("message") or "").strip()

    # --- Input validation (Chapter 5, Section 5.4) ---
    if not raw_query:
        return jsonify({
            "response": "Please enter a question.",
            "intent": None, "confidence": None, "escalated": False
        }), 200

    if len(raw_query) > MAX_QUERY_LENGTH:
        raw_query = raw_query[:MAX_QUERY_LENGTH]

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    session_id = session["session_id"]

    cleaned = preprocess(raw_query)

    escalated = False
    intent_label = None
    confidence = 0.0
    response_text = ""

    try:
        vectorizer, classifier = _load_model()
        vec = vectorizer.transform([cleaned])
        probs = classifier.predict_proba(vec)[0]
        best_idx = probs.argmax()
        intent_label = classifier.classes_[best_idx]
        confidence = float(probs[best_idx])
    except FileNotFoundError:
        intent_label = None
        confidence = 0.0

    if intent_label and confidence >= CONFIDENCE_THRESHOLD:
        # Retrieval path: query KNOWLEDGE_BASE filtered by intent, score by keyword overlap
        candidates = KnowledgeBase.query.filter_by(intent_label=intent_label).all()
        if candidates:
            query_tokens = set(cleaned.split())
            best_entry = max(
                candidates,
                key=lambda kb: len(query_tokens & set(preprocess(kb.question).split())),
            )
            response_text = best_entry.answer
        else:
            response_text = generate_fallback_response(raw_query)
            escalated = True
    else:
        # Generative fallback path
        response_text = generate_fallback_response(raw_query)
        if confidence < CONFIDENCE_THRESHOLD:
            escalated = confidence < 0.4  # very low confidence -> flag for escalation

    interaction = Response(
        session_id=session_id,
        query_text=raw_query,
        intent_label=intent_label,
        confidence_score=confidence,
        response_text=response_text,
        escalated=escalated,
        timestamp=datetime.utcnow(),
    )
    db.session.add(interaction)
    db.session.commit()

    return jsonify({
        "response": response_text,
        "intent": intent_label,
        "confidence": round(confidence, 2),
        "escalated": escalated,
        "interaction_id": interaction.id,
    }), 200


@chat_bp.route("/api/rate", methods=["POST"])
def api_rate():
    data = request.get_json(silent=True) or {}
    interaction_id = data.get("interaction_id")
    rating = data.get("rating")

    if not interaction_id or rating is None:
        return jsonify({"error": "interaction_id and rating are required"}), 400

    interaction = Response.query.get(interaction_id)
    if not interaction:
        return jsonify({"error": "interaction not found"}), 404

    interaction.user_rating = int(rating)
    db.session.commit()
    return jsonify({"status": "ok"}), 200

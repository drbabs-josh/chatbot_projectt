"""
Admin blueprint: authentication, dashboard, and knowledge base management,
as described in Chapter Four (Manage Knowledge Base, Manage User Accounts
use cases) and Chapter Five (ADMIN_LOG audit trail).
"""
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app import db
from app.models import AdminLog, KnowledgeBase, Response, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "admin_user" not in session:
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return wrapper


def _log_action(action: str):
    db.session.add(AdminLog(admin_username=session.get("admin_user", "unknown"), action=action))
    db.session.commit()


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["admin_user"] = user.username
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password.")
    return render_template("admin_login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_user", None)
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    total_interactions = Response.query.count()
    escalated = Response.query.filter_by(escalated=True).count()
    kb_count = KnowledgeBase.query.count()
    avg_rating = db.session.query(db.func.avg(Response.user_rating)).scalar()
    recent = Response.query.order_by(Response.timestamp.desc()).limit(15).all()
    return render_template(
        "admin_dashboard.html",
        total_interactions=total_interactions,
        escalated=escalated,
        kb_count=kb_count,
        avg_rating=round(avg_rating, 2) if avg_rating else None,
        recent=recent,
    )


@admin_bp.route("/knowledge-base")
@login_required
def kb_list():
    entries = KnowledgeBase.query.order_by(KnowledgeBase.category, KnowledgeBase.intent_label).all()
    return render_template("admin_kb.html", entries=entries)


@admin_bp.route("/knowledge-base/add", methods=["POST"])
@login_required
def kb_add():
    entry = KnowledgeBase(
        intent_label=request.form["intent_label"].strip(),
        question=request.form["question"].strip(),
        answer=request.form["answer"].strip(),
        category=request.form["category"].strip(),
    )
    db.session.add(entry)
    db.session.commit()
    _log_action(f"Added knowledge base entry #{entry.id} ({entry.intent_label})")
    return redirect(url_for("admin.kb_list"))


@admin_bp.route("/knowledge-base/<int:entry_id>/delete", methods=["POST"])
@login_required
def kb_delete(entry_id):
    entry = KnowledgeBase.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    _log_action(f"Deleted knowledge base entry #{entry_id}")
    return redirect(url_for("admin.kb_list"))

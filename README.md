# AI-Powered Chatbot for Customer Support — Group 8

A working Flask + SQLAlchemy chatbot with a TF-IDF/Naive Bayes intent
classifier, GPT-3.5-turbo fallback, an admin dashboard, and a knowledge
base — built to match the architecture described in Chapters 4 and 5 of
the project report.

## 1. Honest status — read this first

This code is real and runs end-to-end. Two things you should know before
you present it:

1. **Held-out classifier accuracy is ~59% (macro F1 ≈ 0.585)**, measured
   by genuine 5-fold cross-validation — not the 84%+ F1 or "≥80% intent
   recognition" figures that appear elsewhere in the report. Those figures
   were the lecturer's *suggested* benchmark targets, not measured results.
   Update Chapter 6 with the real numbers `ml/train_classifier.py` prints
   when you run it — presenting invented figures as measured results is
   an integrity risk if you're asked to explain them.
2. The knowledge base currently has **140 entries** (not the 150 stated
   in Chapter 5). Either add 10 more entries via the admin panel, or
   update that sentence to say 140.

Both are easy to fix — see Sections 4 and 5 below.

## 2. Local setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Seed the database (creates knowledge base + admin user)
python data/seed_knowledge_base.py
python data/expand_knowledge_base.py

# (Optional — pre-trained vectorizer.pkl/classifier.pkl are already
#  included in ml/, so this step is only needed if you change the KB)
python ml/train_classifier.py

python run.py
```

Visit **http://127.0.0.1:5000** for the chat interface, and
**http://127.0.0.1:5000/admin** to log in (default: `admin` /
`ChangeMe123!` — change this immediately, see `.env.example`).

## 3. Take your real screenshot for Figure 5.1

Once it's running locally, open the chat page, have a short conversation,
and take a real screenshot (Windows: Win+Shift+S; Mac: Cmd+Shift+4).
Send it to me and I'll drop it into the document in place of the current
one — or paste it in yourself using Word's Insert > Picture.

## 4. Improving classifier accuracy before submission

The ~59% accuracy is a direct, honest consequence of a small dataset
(140 short questions across 20 intents). To genuinely improve it before
your defense:
- Add more paraphrased example questions per intent via `/admin/knowledge-base`
  (aim for 10-15 per intent instead of 7)
- Re-run `python ml/train_classifier.py` after any KB changes — it will
  print the new honest cross-validation numbers
- Use those printed numbers in Chapter 6, not the earlier placeholder figures

## 5. Deploying to get a real URL

I can't deploy this for you directly (no network access to hosting
platforms from where I run), but here's the fastest legitimate path:

### Render.com (free tier, easiest for Flask)
1. Push this project to a GitHub repository
2. Go to https://render.com → New → Web Service → connect your repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn run:app`
5. Add environment variables from `.env.example` (at minimum `SECRET_KEY`)
6. Deploy — Render gives you a URL like `https://your-app.onrender.com`

**Important caveat:** Render's free tier has an *ephemeral filesystem* —
the default SQLite database resets on every redeploy/restart. For a demo
or a short evaluation window this is usually fine. For anything longer:
- Use Render's free PostgreSQL add-on and change `DATABASE_URL`
  accordingly (SQLAlchemy needs `psycopg2-binary` added to
  requirements.txt), or
- Use a free-tier hosted MySQL service (e.g. Railway, Aiven) and set
  `DATABASE_URL=mysql+pymysql://user:pass@host:3306/dbname` (add
  `pymysql` to requirements.txt) to match the "MySQL" claim in Chapter 5
  literally.

Once you have a working URL, send it to me and I'll insert it into
Section 5.8 of the document, replacing the placeholder.

## 6. Project structure

```
app/                Flask application (routes, models, NLP, LLM fallback)
templates/           Chat UI, admin login/dashboard/KB pages
static/              CSS and JS for the chat widget
ml/                  Classifier training script + trained model files
data/                Knowledge base seed scripts
run.py               Entry point
requirements.txt     Pinned dependencies (matches Chapter 5, Table 5.1)
Procfile             For gunicorn-based deployment (Render/Railway)
.env.example         Copy to .env and fill in real values
```

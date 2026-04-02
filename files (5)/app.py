"""
Dharma Lens – Backend v3
Enhanced with legal content validation + online mode support
Run: python3 app.py   →   http://localhost:5050
"""
import os, sys, re, json, time, uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

try:
    import pdfplumber
    PDF_BACKEND = "pdfplumber"
except ImportError:
    try:
        from pypdf import PdfReader
        PDF_BACKEND = "pypdf"
    except ImportError:
        PDF_BACKEND = None

sys.path.insert(0, os.path.dirname(__file__))
from legal_engine import classifier, LEGAL_CATEGORIES

BASE_DIR   = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=str(STATIC_DIR))
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024
ALLOWED_EXT = {".pdf", ".txt"}
case_store  = {}

@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"]  = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,DELETE,OPTIONS"
    return resp

@app.route("/", defaults={"p":""}, methods=["OPTIONS"])
@app.route("/<path:p>", methods=["OPTIONS"])
def preflight(p): return jsonify({}), 200

@app.route("/")
def serve_index(): return send_from_directory(str(STATIC_DIR), "index.html")

def allowed(f): return Path(f).suffix.lower() in ALLOWED_EXT

def extract_pdf(path):
    text = ""
    if PDF_BACKEND == "pdfplumber":
        with pdfplumber.open(path) as pdf:
            for pg in pdf.pages:
                t = pg.extract_text()
                if t: text += t + "\n"
    elif PDF_BACKEND == "pypdf":
        from pypdf import PdfReader
        for pg in PdfReader(path).pages:
            text += (pg.extract_text() or "") + "\n"
    return text.strip()

def extract_txt(path):
    return open(path, encoding="utf-8", errors="ignore").read().strip()

@app.route("/api/health")
def health():
    return jsonify({"status":"ok","pdf_backend":PDF_BACKEND or "unavailable",
                    "legal_categories":len(LEGAL_CATEGORIES),
                    "cases_in_memory":len(case_store),"version":"3.0.0"})

@app.route("/api/categories")
def categories():
    return jsonify({"categories":{
        cat:{"color":d["color"],"acts":d["acts"],
             "constitutional_articles":d["constitutional_articles"],
             "keyword_count":len(d["keywords"])}
        for cat,d in LEGAL_CATEGORIES.items()
    },"total":len(LEGAL_CATEGORIES)})

@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error":"No file field in request"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error":"Empty filename"}), 400
    if not allowed(f.filename):
        return jsonify({"error":"Only PDF and TXT files are accepted. Images, videos and other file types are not valid legal documents for this platform."}), 400

    fname = secure_filename(f.filename)
    fid   = str(uuid.uuid4())[:8]
    fpath = UPLOAD_DIR / f"{fid}_{fname}"
    f.save(str(fpath))

    try:
        ext  = Path(fname).suffix.lower()
        text = extract_pdf(str(fpath)) if ext==".pdf" else extract_txt(str(fpath))
    except Exception as e:
        return jsonify({"error":f"Text extraction failed: {e}"}), 500
    finally:
        try: fpath.unlink()
        except: pass

    if not text.strip():
        return jsonify({"error":"No text could be extracted. The file may be image-based, password-protected, or empty."}), 422

    # ── Legal content validation ───────────────────────────────
    is_legal, val_conf, val_reason = classifier.validator.validate(text)
    if not is_legal:
        return jsonify({
            "error": val_reason,
            "validation_failed": True,
            "hint": "Please upload a legal document such as a court order, FIR, petition, contract, legal notice, judgment, agreement, or any case-related text file."
        }), 422

    try:
        a = classifier.full_analysis(text)
    except Exception as e:
        return jsonify({"error":f"Classification error: {e}"}), 500

    result = {
        "case_id":    fid,
        "filename":   fname,
        "char_count": len(text),
        "word_count": len(text.split()),
        "extracted_text_preview": text[:800]+("…" if len(text)>800 else ""),
        "category":   a["category"],
        "confidence": a["confidence"],
        "severity":   a["severity"],
        "summary":    a["summary"],
        "tfidf_keywords": [{"word":w,"score":s} for w,s in a["tfidf_keywords"]],
        "all_category_scores": a["all_scores"],
        "applicable_acts": a["applicable_acts"],
        "constitutional_articles": a["constitutional_articles"],
        "recommended_action": a["recommended_action"],
        "color":      a["color"],
        "analysed_at":time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source":     "upload"
    }
    case_store[fid] = result
    return jsonify(result), 200

@app.route("/api/scenario", methods=["POST"])
def scenario():
    body = request.get_json(silent=True) or {}
    sc   = body.get("scenario","").strip()

    if not sc:         return jsonify({"error":"No scenario provided"}), 400
    if len(sc) < 20:   return jsonify({"error":"Scenario too short – please provide more detail (minimum 20 characters)"}), 400
    if len(sc) > 10000:return jsonify({"error":"Scenario too long (maximum 10,000 characters)"}), 400

    # Validate scenario is legal in nature
    is_legal, _, reason = classifier.validator.validate(sc)
    if not is_legal:
        return jsonify({
            "error": "This does not appear to be a legal scenario. " + reason,
            "validation_failed": True,
            "hint": "Please describe a legal situation involving court cases, contracts, rights violations, crimes, employment disputes, family matters, or other law-related issues."
        }), 422

    try:
        a = classifier.full_analysis(sc)
    except Exception as e:
        return jsonify({"error":f"Analysis error: {e}"}), 500

    cid = str(uuid.uuid4())[:8]
    result = {
        "case_id":    cid,
        "input_scenario": sc,
        "category":   a["category"],
        "confidence": a["confidence"],
        "severity":   a["severity"],
        "explanation":_expl(sc, a),
        "tfidf_keywords": [{"word":w,"score":s} for w,s in a["tfidf_keywords"]],
        "all_category_scores": a["all_scores"],
        "applicable_acts": a["applicable_acts"],
        "constitutional_articles": a["constitutional_articles"],
        "recommended_action": a["recommended_action"],
        "color":      a["color"],
        "analysed_at":time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source":     "scenario"
    }
    case_store[cid] = result
    return jsonify(result), 200

@app.route("/api/cases")
def list_cases():
    return jsonify({"cases":[
        {"case_id":cid,
         "label":c.get("filename",c.get("input_scenario","")[:60]),
         "category":c["category"],"confidence":c["confidence"],
         "severity":c["severity"],"source":c.get("source","upload"),
         "analysed_at":c["analysed_at"]}
        for cid,c in reversed(list(case_store.items()))
    ],"total":len(case_store)})

@app.route("/api/case/<cid>")
def get_case(cid):
    c = case_store.get(cid)
    return jsonify(c) if c else (jsonify({"error":"Not found"}), 404)

@app.route("/api/case/<cid>", methods=["DELETE"])
def del_case(cid):
    if cid in case_store:
        del case_store[cid]
        return jsonify({"deleted":cid})
    return jsonify({"error":"Not found"}), 404

@app.route("/api/stats")
def stats():
    from collections import Counter
    cats = Counter(c["category"] for c in case_store.values())
    sevs = Counter(c["severity"] for c in case_store.values())
    avg  = round(sum(c["confidence"] for c in case_store.values())/len(case_store),1) if case_store else 0
    return jsonify({"total_cases":len(case_store),"avg_confidence":avg,
                    "by_category":dict(cats.most_common()),"by_severity":dict(sevs)})

def _expl(text, a):
    cat   = a["category"]
    words = [w for w in text.split() if len(w)>4 and w.lower() not in
             {"about","their","which","should","would","could","these","those","where","there","after","before"}]
    kp = " ".join(words[:6]).lower() if words else "the described events"
    return {
        "Criminal Law":           f"This scenario describes criminal conduct involving {kp}. The matter is governed by the IPC 1860 and CrPC 1973. Cognizable offences require immediate police intervention and filing of an FIR.",
        "Civil Law":              f"This is a civil dispute concerning {kp}. The aggrieved party may approach the appropriate civil court for remedies including damages, injunction or specific performance under the CPC 1908 and Indian Contract Act.",
        "Cyber Law":              f"The scenario involves digital/online misconduct — {kp}. This is governed by the Information Technology Act 2000, its 2008 amendments, and relevant IPC provisions on cheating, fraud and impersonation.",
        "Corporate/Business Law": f"This involves corporate or commercial conduct: {kp}. The Companies Act 2013, SEBI regulations, Competition Act 2002 and IBC 2016 form the applicable legal framework.",
        "Family Law":             f"This is a personal/family law matter involving {kp}. The applicable personal law statute (Hindu, Muslim, Christian, or Parsi) governs the dispute; Family Courts provide the designated forum for resolution.",
        "Constitutional Law":     f"The scenario raises constitutional questions regarding {kp}. Fundamental rights under Part III of the Constitution are engaged and the aggrieved party may seek writ remedies under Articles 32 (Supreme Court) or 226 (High Court).",
        "Labour/Employment Law":  f"This is a labour and employment dispute involving {kp}. The Industrial Disputes Act 1947, Payment of Gratuity Act 1972, EPF Act 1952 and related statutes provide remedies through Labour Courts and Industrial Tribunals.",
        "Intellectual Property Law": f"The scenario concerns intellectual property rights — {kp}. The Copyright Act 1957, Trade Marks Act 1999 or Patents Act 1970 provide both civil remedies (injunctions, damages) and criminal prosecution for infringement.",
    }.get(cat, f"Classified under {cat} based on legal terminology analysis of the scenario.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"\n⚖  DHARMA LENS v3  |  http://localhost:{port}  |  PDF: {PDF_BACKEND}\n")
    app.run(host="0.0.0.0", port=port, debug=False)

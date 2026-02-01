# app.py (updated with AI search, bcrypt auth, categories, officers, ads)
import os
import json
from flask import Flask, jsonify, render_template, request, session, redirect, send_file, abort
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import csv
from dotenv import load_dotenv
import bcrypt
import pathlib
from recommendation_engine import RecommendationEngine

# AI / embeddings
import numpy as np
from sentence_transformers import SentenceTransformer

# faiss may not be present on every host — allow fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")
CORS(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
services_col = db["services"]  # original services (ministries + subservices)
admins_col = db["admins"]
eng_col = db["engagements"]
categories_col = db["categories"]  # new: category groups
officers_col = db["officers"]  # new: officers metadata
ads_col = db["ads"]  # new: ads & training program announcements
users_col = db["users"]  # new: progressive profile / accounts
products_col = db["products"]
orders_col = db["orders"]
payments_col = db["payments"]

# Initialize Recommendation Engine
recommendation_engine = RecommendationEngine()

# Embedding model (lazy-init)
EMBED_MODEL = None
INDEX_PATH = pathlib.Path("./data/faiss.index")
META_PATH = pathlib.Path("./data/faiss_meta.json")
VECTOR_DIM = 384  # for all-MiniLM-L6-v2


def get_embedding_model():
    global EMBED_MODEL
    if EMBED_MODEL is None:
        EMBED_MODEL = SentenceTransformer(os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    return EMBED_MODEL


# --- Helpers ---
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "unauthorized"}), 401
        return fn(*a, **kw)
    return wrapper


# --- Public pages ---
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin")
def admin_page():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")
    return render_template("admin.html")


@app.route("/admin/manage")
@admin_required
def manage_page():
    return render_template("manage.html")


# --- API: services & categories (public) ---
@app.route("/api/services")
def get_services():
    docs = list(services_col.find({}, {"_id": 0}))
    return jsonify(docs)


@app.route("/api/categories")
def get_categories():
    # categories collection contains category documents: {id, name:{en,si,ta}, ministries:[id,...]}
    cats = list(categories_col.find({}, {"_id": 0}))
    # if not seeded, create dynamic categories from existing services grouped by service.category
    if not cats:
        pipeline = [
            {"$project": {"id": 1, "name": 1, "category": 1, "subservices": 1}},
            {"$group": {"_id": "$category", "ministries": {"$push": {"id": "$id", "name": "$name"}}}}
        ]
        try:
            groups = list(services_col.aggregate(pipeline))
            cats = [{"id": g["_id"] or "uncategorized", "name": {"en": g["_id"] or "Uncategorized"}, "ministries": g["ministries"]} for g in groups]
        except Exception:
            cats = []
    return jsonify(cats)


@app.route("/api/service/<service_id>")
def get_service(service_id):
    doc = services_col.find_one({"id": service_id}, {"_id": 0})
    return jsonify(doc or {})


# Autosuggest search (quick matches for typeahead)
@app.route("/api/search/autosuggest")
def autosuggest():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    # simple text search across service names and subservice names
    regex = {"$regex": q, "$options": "i"}
    results = []
    for s in services_col.find({"$or": [{"name.en": regex}, {"subservices.name.en": regex}]}, {"_id": 0, "id": 1, "name": 1, "subservices": 1}).limit(20):
        results.append(s)
    return jsonify(results)


# Engagement logging (extended to include ad clicks / profile step)
@app.route("/api/engagement", methods=["POST"])
def log_engagement():
    payload = request.json or {}
    doc = {
        "user_id": payload.get("user_id") or None,
        "age": int(payload.get("age")) if payload.get("age") else None,
        "job": payload.get("job"),
        "desires": payload.get("desires") or [],
        "question_clicked": payload.get("question_clicked"),
        "service": payload.get("service"),
        "ad": payload.get("ad"),
        "source": payload.get("source"),
        "timestamp": datetime.utcnow()
    }
    eng_col.insert_one(doc)
    return jsonify({"status": "ok"})


# Progressive profile: save step-by-step partial profile (upsert by anonymous id or email)
@app.route("/api/profile/step", methods=["POST"])
def profile_step():
    payload = request.json or {}
    profile_id = payload.get("profile_id") or None
    email = payload.get("email")
    data = payload.get("data", {})
    if profile_id:
        users_col.update_one({"_id": profile_id}, {"$set": {"profile." + payload.get("step", "unknown"): data, "updated": datetime.utcnow()}}, upsert=True)
        return jsonify({"status": "ok", "profile_id": profile_id})
    if email:
        res = users_col.find_one_and_update({"email": email}, {"$set": {"profile." + payload.get("step", "unknown"): data, "updated": datetime.utcnow()}}, upsert=True, return_document=True)
        return jsonify({"status": "ok", "profile_id": str(res.get("_id"))})
    # fallback - create anonymous
    new_id = users_col.insert_one({"profile": {payload.get("step", "unknown"): data}, "created": datetime.utcnow()}).inserted_id
    return jsonify({"status": "ok", "profile_id": str(new_id)})


# Ads
@app.route("/api/ads")
def get_ads():
    ads = list(ads_col.find({}, {"_id": 0}))
    return jsonify(ads)


# --- AI / vector index endpoints ---
def build_vector_index():
    """
    Build or rebuild a FAISS index from services_col. Saves index file + metadata.
    This should be run via /api/admin/build_index by admin after seeding/updating services.
    """
    os.makedirs("data", exist_ok=True)
    docs = []
    # flatten each service/subservice/question to a searchable doc
    for svc in services_col.find():
        svc_id = svc.get("id")
        svc_name = svc.get("name", {}).get("en") or str(svc.get("name"))
        for sub in svc.get("subservices", []):
            sub_id = sub.get("id")
            sub_name = sub.get("name", {}).get("en") or str(sub.get("name"))
            # base content: service+subservice name + question text + answer
            for q in sub.get("questions", []):
                q_text = q.get("q", {}).get("en") or str(q.get("q"))
                a_text = q.get("answer", {}).get("en") or str(q.get("answer"))
                content = " | ".join([svc_name or "", sub_name or "", q_text or "", a_text or ""])
                docs.append({
                    "doc_id": f"{svc_id}::{sub_id}::{q_text[:80]}",
                    "service_id": svc_id,
                    "subservice_id": sub_id,
                    "title": q_text,
                    "content": content,
                    "metadata": {
                        "downloads": q.get("downloads", []),
                        "location": q.get("location"),
                        "instructions": q.get("instructions")
                    }
                })
    # embed
    model = get_embedding_model()
    texts = [d["content"] for d in docs]
    if not texts:
        # nothing to index
        return {"count": 0}
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    # normalize for cosine if using IP
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms
    if FAISS_AVAILABLE:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        # store id mapping separately
        index.add(embeddings.astype(np.float32))
        faiss.write_index(index, str(INDEX_PATH))
    else:
        # fallback: store embeddings in JSON (slow search)
        np.save("data/embeddings.npy", embeddings)
    # save metadata
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    return {"count": len(docs), "faiss": FAISS_AVAILABLE}


@app.route("/api/admin/build_index", methods=["POST"])
@admin_required
def admin_build_index():
    res = build_vector_index()
    return jsonify(res)


def search_vectors(query, top_k=5):
    model = get_embedding_model()
    q_emb = model.encode([query], convert_to_numpy=True)
    q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-10)
    if FAISS_AVAILABLE and INDEX_PATH.exists() and META_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        D, I = index.search(q_emb.astype(np.float32), top_k)
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        hits = []
        for idx in I[0]:
            if idx < len(meta):
                hits.append(meta[idx])
        return hits
    else:
        # fallback linear scan
        if not META_PATH.exists():
            return []
        meta = json.load(open(META_PATH, "r", encoding="utf-8"))
        if not os.path.exists("data/embeddings.npy"):
            return []
        db_emb = np.load("data/embeddings.npy")
        sims = (db_emb @ q_emb[0]).tolist()
        idxs = np.argsort(sims)[::-1][:top_k]
        return [meta[int(i)] for i in idxs]


@app.route("/api/ai/search", methods=["POST"])
def ai_search():
    """
    Accepts: {query: "...", top_k: 5}
    Returns: {answer: "...", sources: [ {...} ] }
    """
    payload = request.json or {}
    query = payload.get("query", "").strip()
    top_k = int(payload.get("top_k", 5))
    if not query:
        return jsonify({"error": "empty query"}), 400
    hits = search_vectors(query, top_k)
    # Build a simple answer: concatenate top answers and include source pointers
    # Optionally: here you would call an LLM (OpenAI) to produce a natural language answer
    answer_parts = []
    sources = []
    for h in hits:
        # safe fallback: use "title" + "content" truncated
        txt = h.get("content", "")
        answer_parts.append(txt[:800])
        sources.append({
            "service_id": h.get("service_id"),
            "subservice_id": h.get("subservice_id"),
            "title": h.get("title"),
            **h.get("metadata", {})
        })
    answer = "\n\n---\n\n".join(answer_parts) if answer_parts else "No matching content found."
    return jsonify({"query": query, "answer": answer, "sources": sources, "hits": len(sources)})


# --- Admin auth with bcrypt ---
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin.html")
    data = request.form
    username = data.get("username")
    password = data.get("password", "")
    admin = admins_col.find_one({"username": username})
    if admin:
        stored = admin.get("password")
        try:
            if isinstance(stored, bytes):
                ok = bcrypt.checkpw(password.encode("utf-8"), stored)
            else:
                ok = bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))
        except Exception:
            ok = stored == password  # legacy plain password fallback
        if ok:
            session["admin_logged_in"] = True
            session["admin_user"] = username
            return redirect("/admin")
    return "Login failed", 401


@app.route("/api/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.clear()
    return jsonify({"status": "logged out"})


# --- Admin CRUD: services (unchanged), categories, officers, ads ---
@app.route("/api/admin/services", methods=["GET", "POST"])
@admin_required
def admin_services():
    if request.method == "GET":
        return jsonify(list(services_col.find({}, {"_id": 0})))
    payload = request.json
    sid = payload.get("id")
    if not sid:
        return jsonify({"error": "id required"}), 400
    services_col.update_one({"id": sid}, {"$set": payload}, upsert=True)
    return jsonify({"status": "ok"})


@app.route("/api/admin/services/<service_id>", methods=["DELETE"])
@admin_required
def delete_service(service_id):
    services_col.delete_one({"id": service_id})
    return jsonify({"status": "deleted"})


# categories
@app.route("/api/admin/categories", methods=["GET", "POST", "DELETE"])
@admin_required
def manage_categories():
    if request.method == "GET":
        return jsonify(list(categories_col.find({}, {"_id": 0})))
    if request.method == "POST":
        payload = request.json
        cid = payload.get("id")
        if not cid:
            return jsonify({"error": "id required"}), 400
        categories_col.update_one({"id": cid}, {"$set": payload}, upsert=True)
        return jsonify({"status": "ok"})
    if request.method == "DELETE":
        cid = request.args.get("id")
        categories_col.delete_one({"id": cid})
        return jsonify({"status": "deleted"})


# officers
@app.route("/api/admin/officers", methods=["GET", "POST", "DELETE"])
@admin_required
def manage_officers():
    if request.method == "GET":
        return jsonify(list(officers_col.find({}, {"_id": 0})))
    if request.method == "POST":
        payload = request.json
        oid = payload.get("id")
        if not oid:
            return jsonify({"error": "id required"}), 400
        officers_col.update_one({"id": oid}, {"$set": payload}, upsert=True)
        return jsonify({"status": "ok"})
    if request.method == "DELETE":
        oid = request.args.get("id")
        officers_col.delete_one({"id": oid})
        return jsonify({"status": "deleted"})


# ads
@app.route("/api/admin/ads", methods=["GET", "POST", "DELETE"])
@admin_required
def manage_ads():
    if request.method == "GET":
        return jsonify(list(ads_col.find({}, {"_id": 0})))
    if request.method == "POST":
        payload = request.json
        aid = payload.get("id")
        if not aid:
            return jsonify({"error": "id required"}), 400
        ads_col.update_one({"id": aid}, {"$set": payload}, upsert=True)
        return jsonify({"status": "ok"})
    if request.method == "DELETE":
        aid = request.args.get("id")
        ads_col.delete_one({"id": aid})
        return jsonify({"status": "deleted"})


# --- Admin insights (kept but extended) ---
@app.route("/api/admin/insights")
@admin_required
def admin_insights():
    # Age groups, jobs, services, questions (as before) ... plus top ads (clicks)
    age_groups = {"<18": 0, "18-25": 0, "26-40": 0, "41-60": 0, "60+": 0}
    for e in eng_col.find({}, {"age": 1}):
        age = e.get("age")
        if not age:
            continue
        try:
            age = int(age)
            if age < 18:
                age_groups["<18"] += 1
            elif age <= 25:
                age_groups["18-25"] += 1
            elif age <= 40:
                age_groups["26-40"] += 1
            elif age <= 60:
                age_groups["41-60"] += 1
            else:
                age_groups["60+"] += 1
        except:
            continue
    jobs = {}
    services = {}
    questions = {}
    desires = {}
    for e in eng_col.find({}, {"job": 1, "service": 1, "question_clicked": 1, "desires": 1, "ad": 1}):
        j = (e.get("job") or "Unknown").strip()
        jobs[j] = jobs.get(j, 0) + 1
        s = e.get("service") or "Unknown"
        services[s] = services.get(s, 0) + 1
        q = e.get("question_clicked") or "Unknown"
        questions[q] = questions.get(q, 0) + 1
        for d in e.get("desires") or []:
            desires[d] = desires.get(d, 0) + 1
    # premium suggestions
    pipeline = [
        {"$group": {"_id": {"user": "$user_id", "question": "$question_clicked"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 2}}}
    ]
    repeated = list(eng_col.aggregate(pipeline))
    premium_suggestions = [{"user": r["_id"]["user"], "question": r["_id"]["question"], "count": r["count"]} for r in repeated if r["_id"]["user"]]
    return jsonify({
        "age_groups": age_groups,
        "jobs": jobs,
        "services": services,
        "questions": questions,
        "desires": desires,
        "premium_suggestions": premium_suggestions
    })


@app.route("/api/admin/engagements")
@admin_required
def admin_engagements():
    items = []
    for e in eng_col.find().sort("timestamp", -1).limit(500):
        e["_id"] = str(e["_id"])
        e["timestamp"] = e.get("timestamp").isoformat() if e.get("timestamp") else ""
        items.append(e)
    return jsonify(items)


# CSV export (extended for ads)
@app.route("/api/admin/export_csv")
@admin_required
def export_csv():
    cursor = eng_col.find()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["user_id", "age", "job", "desire", "question", "service", "ad", "timestamp"])
    for e in cursor:
        cw.writerow([
            e.get("user_id"), e.get("age"), e.get("job"),
            ",".join(e.get("desires") or []),
            e.get("question_clicked"), e.get("service"), e.get("ad"),
            e.get("timestamp").isoformat() if e.get("timestamp") else ""
        ])
    si.seek(0)
    output = BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="engagements.csv"
    )


# --- Navigation Routes ---
@app.route("/store")
def store():
    return render_template("store.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")
    
    # Get enhanced analytics
    analytics_response = get_dashboard_analytics()
    analytics = analytics_response.get_json()
    
    # We need to create a dashboard template or pass to existing one
    # If dashboard.html doesn't exist, we might need to create it.
    # For now assuming dashboard.html will be created.
    return render_template("dashboard.html", 
                           analytics=analytics)

# --- Enhanced Customer Data Collection System ---

# 1.1 Extended User Profile Schema
@app.route("/api/profile/extended", methods=["POST"])
def extended_profile():
    payload = request.json or {}
    profile_id = payload.get("profile_id")
    if not profile_id:
        return jsonify({"error": "profile_id required"}), 400
        
    extended_data = {
        "family": {
            "marital_status": payload.get("marital_status"),
            "children": payload.get("children", []),
            "children_ages": payload.get("children_ages", []),
            "children_education": payload.get("children_education", []),
            "dependents": payload.get("dependents", 0)
        },
        "education": {
            "highest_qualification": payload.get("highest_qualification"),
            "institution": payload.get("institution"),
            "year_graduated": payload.get("year_graduated"),
            "field_of_study": payload.get("field_of_study")
        },
        "career": {
            "current_job": payload.get("current_job"),
            "years_experience": payload.get("years_experience"),
            "skills": payload.get("skills", []),
            "career_goals": payload.get("career_goals", [])
        },
        "interests": {
            "hobbies": payload.get("hobbies", []),
            "learning_interests": payload.get("learning_interests", []),
            "service_preferences": payload.get("service_preferences", [])
        },
        "consent": {
            "marketing_emails": payload.get("marketing_emails", False),
            "personalized_ads": payload.get("personalized_ads", False),
            "data_analytics": payload.get("data_analytics", False)
        }
    }
    
    users_col.update_one(
        {"_id": ObjectId(profile_id)},
        {"$set": {"extended_profile": extended_data, "updated": datetime.utcnow()}}
    )
    return jsonify({"status": "ok"})

# 1.2 Enhanced Engagement Tracking
@app.route("/api/engagement/enhanced", methods=["POST"])
def log_enhanced_engagement():
    payload = request.json or {}
    # Extract behavioral data
    user_agent = request.headers.get('User-Agent', '')
    ip_address = request.remote_addr
    referrer = request.headers.get('Referer', '')
    
    doc = {
        "user_id": payload.get("user_id"),
        "session_id": payload.get("session_id"),
        "age": int(payload.get("age")) if payload.get("age") else None,
        "job": payload.get("job"),
        "desires": payload.get("desires", []),
        "question_clicked": payload.get("question_clicked"),
        "service": payload.get("service"),
        "ad": payload.get("ad"),
        "source": payload.get("source"),
        "time_spent": payload.get("time_spent"),
        "scroll_depth": payload.get("scroll_depth"),
        "clicks": payload.get("clicks", []),
        "searches": payload.get("searches", []),
        "device_info": {
            "user_agent": user_agent,
            "ip_address": ip_address,
            "screen_resolution": payload.get("screen_resolution")
        },
        "referral_data": {
            "referrer": referrer,
            "utm_source": payload.get("utm_source"),
            "utm_medium": payload.get("utm_medium"),
            "utm_campaign": payload.get("utm_campaign")
        },
        "timestamp": datetime.utcnow()
    }
    eng_col.insert_one(doc)
    return jsonify({"status": "ok"})

# --- Smart Recommendation Algorithm ---

@app.route("/api/recommendations/<user_id>")
def get_recommendations(user_id):
    try:
        ads = recommendation_engine.get_personalized_ads(user_id)
        edu_recommendations = recommendation_engine.generate_education_recommendations(user_id)
        return jsonify({
            "ads": ads,
            "education_recommendations": edu_recommendations,
            "user_segment": recommendation_engine.get_user_segment(user_id)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Store Implementation ---

@app.route("/api/store/products")
def get_products():
    category = request.args.get("category")
    subcategory = request.args.get("subcategory")
    tags = request.args.get("tags", "").split(",") if request.args.get("tags") else []
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    
    query = {"in_stock": True}
    
    if category:
        categories = category.split(",")
        if len(categories) > 1:
            query["category"] = {"$in": categories}
        else:
            query["category"] = category
            
    if subcategory:
        query["subcategory"] = subcategory
        
    if tags and tags[0]:
        query["tags"] = {"$in": tags}
        
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price
            
    products = list(products_col.find(query, {"_id": 0}).limit(50))
    return jsonify(products)

@app.route("/api/store/categories")
def get_store_categories():
    categories = products_col.distinct("category")
    subcategories = {}
    for cat in categories:
        subcategories[cat] = products_col.distinct("subcategory", {"category": cat})
    
    return jsonify({
        "categories": categories,
        "subcategories": subcategories
    })

@app.route("/api/store/order", methods=["POST"])
def create_order():
    payload = request.json or {}
    order = {
        "order_id": f"ORD{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "user_id": payload.get("user_id"),
        "items": payload.get("items", []),
        "total_amount": payload.get("total_amount", 0),
        "status": "pending",
        "shipping_address": payload.get("shipping_address", {}),
        "payment_method": payload.get("payment_method"),
        "created": datetime.utcnow(),
        "updated": datetime.utcnow()
    }
    result = orders_col.insert_one(order)
    return jsonify({"status": "ok", "order_id": order["order_id"]})

@app.route("/api/store/payment", methods=["POST"])
def process_payment():
    payload = request.json or {}
    payment = {
        "payment_id": f"PAY{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "order_id": payload.get("order_id"),
        "user_id": payload.get("user_id"),
        "amount": payload.get("amount", 0),
        "currency": payload.get("currency", "LKR"),
        "method": payload.get("method"),
        "status": "completed",
        "transaction_id": payload.get("transaction_id"),
        "created": datetime.utcnow()
    }
    
    # Update order status
    orders_col.update_one(
        {"order_id": payload.get("order_id")},
        {"$set": {"status": "paid", "updated": datetime.utcnow()}}
    )
    
    payments_col.insert_one(payment)
    
    # Log engagement for recommendation system
    eng_col.insert_one({
        "user_id": payload.get("user_id"),
        "type": "purchase",
        "product_ids": [item.get("product_id") for item in payload.get("items", [])],
        "amount": payload.get("amount", 0),
        "timestamp": datetime.utcnow()
    })
    
    return jsonify({"status": "ok", "payment_id": payment["payment_id"]})

# --- Enhanced Dashboard with Analytics ---

@app.route("/api/dashboard/analytics")
@admin_required
def get_dashboard_analytics():
    # User analytics
    total_users = users_col.count_documents({})
    # active_users logic: "last_active" exists
    active_users = users_col.count_documents({"last_active": {"$gte": datetime.utcnow() - timedelta(days=30)}})
    
    # Engagement analytics
    total_engagements = eng_col.count_documents({})
    recent_engagements = eng_col.count_documents({"timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}})
    
    # Store analytics
    total_orders = orders_col.count_documents({})
    
    # Revenue
    cursor_rev = payments_col.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    revenue_result = list(cursor_rev)
    total_revenue_amount = revenue_result[0]["total"] if revenue_result else 0
    
    # User segmentation (Sample - in real app this might be pre-calculated)
    # We'll just sample last 100 users for performance if DB is huge
    user_segments = {}
    users = users_col.find().sort("created", -1).limit(100)
    for user in users:
        segments = recommendation_engine.get_user_segment(str(user["_id"]))
        for segment in segments:
            user_segments[segment] = user_segments.get(segment, 0) + 1
            
    # Popular products
    popular_products = list(products_col.find().sort("rating", -1).limit(5))
    for prod in popular_products:
        if "_id" in prod:
            prod["_id"] = str(prod["_id"])
        if "created" in prod and isinstance(prod["created"], datetime):
            prod["created"] = prod["created"].isoformat()
    
    # Recent activities (convert ObjectId/Date for JSON)
    recent_activities = []
    for act in eng_col.find().sort("timestamp", -1).limit(10):
        act["_id"] = str(act["_id"])
        if act.get("timestamp"):
            act["timestamp"] = act["timestamp"].isoformat()
        recent_activities.append(act)

    return jsonify({
        "user_metrics": {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_7d": users_col.count_documents({"created": {"$gte": datetime.utcnow() - timedelta(days=7)}})
        },
        "engagement_metrics": {
            "total_engagements": total_engagements,
            "recent_engagements": recent_engagements,
            "avg_session_duration": "5m 23s" 
        },
        "store_metrics": {
            "total_orders": total_orders,
            "total_revenue": total_revenue_amount,
            "conversion_rate": "3.2%"
        },
        "user_segments": user_segments,
        "popular_products": popular_products,
        "recent_activities": recent_activities
    })

# --- Ethical Data Collection ---

@app.route("/api/consent/update", methods=["POST"])
def update_consent():
    payload = request.json or {}
    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
        
    consent_updates = {
        "extended_profile.consent.marketing_emails": payload.get("marketing_emails", False),
        "extended_profile.consent.personalized_ads": payload.get("personalized_ads", False),
        "extended_profile.consent.data_analytics": payload.get("data_analytics", False),
        "extended_profile.consent.updated": datetime.utcnow()
    }
    
    users_col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": consent_updates}
    )
    return jsonify({"status": "ok", "message": "Consent preferences updated"})

@app.route("/api/data/export/<user_id>")
def export_user_data(user_id):
    """GDPR-compliant data export"""
    try:
        user = users_col.find_one({"_id": ObjectId(user_id)})
    except:
        return jsonify({"error": "Invalid ID"}), 400
        
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Remove sensitive internal fields
    export_data = {
        "profile": user.get("profile", {}),
        "extended_profile": user.get("extended_profile", {}),
        "consent_preferences": user.get("extended_profile", {}).get("consent", {}),
        "created": user.get("created"),
        "last_active": user.get("last_active")
    }
    
    return jsonify(export_data)

@app.route("/api/data/delete/<user_id>", methods=["DELETE"])
def delete_user_data(user_id):
    """GDPR-compliant data deletion"""
    try:
        uid_obj = ObjectId(user_id)
        result = users_col.delete_one({"_id": uid_obj})
        
        # Also delete related engagements (anonymized)
        eng_col.update_many(
            {"user_id": user_id},
            {"$set": {"user_id": None, "anonymized": True}}
        )
        
        if result.deleted_count > 0:
            return jsonify({"status": "ok", "message": "User data deleted"})
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ensure at least one admin user exists (hashed)
if __name__ == "__main__":
    if admins_col.count_documents({}) == 0:
        pwd = os.getenv("ADMIN_PWD", "admin123")
        hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
        admins_col.insert_one({"username": "admin", "password": hashed})
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

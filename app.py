"""
LangChain Multi-tool Agent powered by Grok
"""
import os
import uuid

from flask import Flask, request, jsonify
from flask_cors import CORS

from config.settings import (
    FLASK_SECRET_KEY, HOST, PORT,
    MAX_FILE_SIZE_MB, MAX_CONTENT_CHARS, MAX_MESSAGE_LENGTH,
    ALLOWED_EXTENSIONS, GROK_MODEL,
)
from utils.rate_limiter import is_rate_limited
from utils.file_handler import extract_text_from_file, detect_content_type
from agent_builder import build_agent_executor
from prompts.agent_prompts import get_code_analysis_prompt, get_cv_analysis_prompt

#  App setup 
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
CORS(app)

#  In-memory session store 
agent_executors  = {}   # session_id -> AgentExecutor
project_contexts = {}   # session_id -> raw text (للـ reference)


def get_client_ip() -> str:
    return request.headers.get("X-Forwarded-For", request.remote_addr)



#  ROUTES

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "mode":   "LangChain Multi-tool Agent",
        "model":  GROK_MODEL,
        "tools":  ["code_structure_analyzer", "bug_detector",
                   "best_practices_checker", "code_improver",
                   "cv_analyzer", "web_search"],
    }), 200


@app.route("/AI", methods=["POST"])
def analyze_content():
    """يستقبل الملف، يشغّل الـ Agent، يرجع التحليل + session_id."""
    ip = get_client_ip()
    if is_rate_limited(ip):
        return jsonify({"error": "تجاوزت الحد المسموح به. حاول لاحقاً."}), 429

    if "file" not in request.files:
        return jsonify({"error": "لم يتم رفع أي ملف"}), 400

    file     = request.files["file"]
    filename = file.filename or ""
    if not filename:
        return jsonify({"error": "اسم الملف غير صالح"}), 400

    #  File size check 
    file.seek(0, 2)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if size_mb > MAX_FILE_SIZE_MB:
        return jsonify({"error": f"حجم الملف يتجاوز {MAX_FILE_SIZE_MB} MB"}), 413

    #  Extension check 
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"نوع الملف غير مدعوم: {ext}"}), 415

    #  Extract text 
    try:
        content = extract_text_from_file(file, filename)
        if not content.strip():
            return jsonify({"error": "الملف فارغ أو لا يمكن قراءته"}), 400
    except Exception as e:
        return jsonify({"error": f"فشل في قراءة الملف: {str(e)}"}), 400

    #  Build session 
    content_type = detect_content_type(content)
    session_id   = str(uuid.uuid4())
    executor     = build_agent_executor()

    agent_executors[session_id]  = executor
    project_contexts[session_id] = content[:MAX_CONTENT_CHARS]

    #  Choose prompt 
    prompt = (
        get_cv_analysis_prompt(content[:MAX_CONTENT_CHARS])
        if content_type == "cv"
        else get_code_analysis_prompt(content[:MAX_CONTENT_CHARS])
    )

    #  Run agent 
    try:
        result   = executor.invoke({"input": prompt})
        analysis = result.get("output", "لم يتمكن الـ Agent من إنهاء التحليل.")
    except Exception as e:
        agent_executors.pop(session_id, None)
        project_contexts.pop(session_id, None)
        return jsonify({"error": f"خطأ في الـ Agent: {str(e)}"}), 500

    return jsonify({
        "session_id":   session_id,
        "analysis":     analysis,
        "content_type": content_type,
        "filename":     filename,
    }), 200


@app.route("/chat", methods=["POST"])
def chat():
    """محادثة متابعة — الـ Agent يتذكر السياق تلقائياً عبر الـ Memory."""
    ip = get_client_ip()
    if is_rate_limited(ip):
        return jsonify({"error": "تجاوزت الحد المسموح به. حاول لاحقاً."}), 429

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "البيانات المرسلة غير صالحة"}), 400

    session_id   = data.get("session_id", "").strip()
    user_message = data.get("message", "").strip()

    if not session_id:
        return jsonify({"error": "session_id مطلوب"}), 400
    if not user_message:
        return jsonify({"error": "الرسالة لا يمكن أن تكون فارغة"}), 400
    if len(user_message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": f"الرسالة طويلة جداً (الحد {MAX_MESSAGE_LENGTH} حرف)"}), 400
    if session_id not in agent_executors:
        return jsonify({"error": "الجلسة غير موجودة أو انتهت. ارفع الملف مجدداً."}), 404

    executor = agent_executors[session_id]

    try:
        result = executor.invoke({"input": user_message})
        reply  = result.get("output", "لم يتمكن الـ Agent من الإجابة.")
    except Exception as e:
        return jsonify({"error": f"خطأ في الـ Agent: {str(e)}"}), 500

    messages = executor.memory.chat_memory.messages
    u_count  = sum(1 for m in messages if m.type == "human")

    return jsonify({
        "reply":         reply,
        "session_id":    session_id,
        "message_count": u_count,
    }), 200


@app.route("/session/<session_id>", methods=["DELETE"])
def clear_session(session_id: str):
    agent_executors.pop(session_id, None)
    project_contexts.pop(session_id, None)
    return jsonify({"message": "تم حذف الجلسة بنجاح"}), 200


@app.route("/session/<session_id>/history", methods=["GET"])
def get_history(session_id: str):
    if session_id not in agent_executors:
        return jsonify({"error": "الجلسة غير موجودة"}), 404

    messages = agent_executors[session_id].memory.chat_memory.messages
    visible  = [
        {"role": "user" if m.type == "human" else "assistant", "content": m.content}
        for m in messages
    ]
    return jsonify({"history": visible, "count": len(visible)}), 200



if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)

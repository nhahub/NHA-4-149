"""
Code Analysis Tools
أدوات تحليل الكود البرمجي — كل tool تحلّل جانباً مختلفاً
"""
from langchain.tools import tool


@tool
def code_structure_analyzer(code: str) -> str:
    """
    يحلل البنية الهيكلية للكود:
    عدد الأسطر، اللغة، الـ imports، هل فيه classes / async / tests / type hints.
    استخدمه أول حاجة عند تحليل أي مشروع برمجي.
    """
    lines     = code.split("\n")
    non_blank = [l for l in lines if l.strip()]
    imports   = [l.strip() for l in lines if l.startswith("import") or l.startswith("from")]

    has_class = any("class "    in l for l in lines)
    has_async = any("async "    in l for l in lines)
    has_tests = any("def test_" in l or "test_" in l for l in lines)
    has_types = any("->" in l or ": str" in l or ": int" in l or ": list" in l for l in lines)
    has_docs  = any('"""' in l or "'''" in l for l in lines)

    # Guess language
    if any("flask" in i.lower() or "django" in i.lower() for i in imports):
        lang = "Python — Web Framework"
    elif any("fastapi" in i.lower() for i in imports):
        lang = "Python — FastAPI"
    elif any("import React" in l or "useState" in l for l in lines):
        lang = "JavaScript / React"
    elif "public static void main" in code:
        lang = "Java"
    elif "#include" in code:
        lang = "C / C++"
    elif imports:
        lang = "Python"
    else:
        lang = "Unknown"

    return f"""
=== تحليل البنية الهيكلية ===
اللغة المكتشفة   : {lang}
إجمالي الأسطر    : {len(lines)}
أسطر فعّالة      : {len(non_blank)}
Classes          : {'✅ يوجد' if has_class else '❌ لا يوجد'}
Async / Await    : {'✅ يوجد' if has_async else '❌ لا يوجد'}
Type Hints       : {'✅ يوجد' if has_types else '❌ لا يوجد'}
Docstrings       : {'✅ يوجد' if has_docs else '❌ لا يوجد'}
Unit Tests       : {'✅ يوجد' if has_tests else '❌ لا يوجد'}
الـ Imports ({len(imports)}) : {imports[:10]}
"""


@tool
def bug_detector(code: str) -> str:
    """
    يكشف الـ bugs والثغرات الأمنية الشائعة:
    hardcoded secrets، debug mode، SQL injection، exception swallowing، إلخ.
    استخدمه دائماً بعد code_structure_analyzer.
    """
    issues   = []
    warnings = []

    # ── Critical security ──
    if "debug=True" in code or "DEBUG=True" in code:
        issues.append("🔴 [CRITICAL] debug=True مفعَّل — خطر أمني في production")

    if "os.urandom" in code and ("secret" in code.lower() or "key" in code.lower()):
        issues.append("🔴 [CRITICAL] Secret key عشوائي عند كل restart — استخدم متغير بيئة ثابت")

    if "password" in code.lower() and "=" in code and ('"' in code or "'" in code):
        issues.append("🟠 [HIGH] كلمة مرور محتملة hardcoded — انقلها لـ .env")

    sql_patterns = ["f\"SELECT", "f'SELECT", "+ \"SELECT", "+ 'SELECT"]
    if any(p in code for p in sql_patterns):
        issues.append("🔴 [CRITICAL] SQL Injection محتمل — استخدم Parameterized Queries")

    # ── Code quality ──
    if "except Exception:" in code or "except Exception as" in code:
        idx     = code.find("except Exception")
        snippet = code[idx: idx + 120]
        if "pass" in snippet or (
            "logging" not in snippet and "print" not in snippet and "logger" not in snippet
        ):
            warnings.append("⚠️ [MEDIUM] Exception يُبتلع بدون logging — صعب debugging")

    if "time.sleep" in code:
        warnings.append("⚠️ [MEDIUM] time.sleep يُعطّل الـ thread — فكّر في async أو background task")

    if "global " in code:
        warnings.append("⚠️ [LOW] استخدام global variables — يُصعّب الـ testing والـ concurrency")

    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        if ".read()" in line and "file" in line.lower():
            warnings.append(
                f"⚠️ [LOW] السطر {i}: قراءة الملف كاملاً في الذاكرة — فكّر في chunked reading للملفات الكبيرة"
            )
            break

    if not issues and not warnings:
        return "✅ لم يُكتشف bugs أو ثغرات واضحة في هذا التحليل."

    result = "=== تقرير الـ Bugs والثغرات ===\n"
    if issues:
        result += "\n🚨 مشاكل حرجة:\n" + "\n".join(f"  {x}" for x in issues)
    if warnings:
        result += "\n\n⚠️ تحذيرات:\n" + "\n".join(f"  {x}" for x in warnings)
    return result


@tool
def best_practices_checker(code: str) -> str:
    """
    يقارن الكود بأفضل الممارسات:
    PEP8، Flask best practices، separation of concerns،
    rate limiting، input validation، إلخ.
    """
    good  = []
    needs = []

    # ── Good ──
    if "defaultdict" in code:
        good.append("✅ defaultdict للـ rate limiting — كفء")
    if "uuid.uuid4()" in code:
        good.append("✅ UUID للـ sessions — آمن")
    if "CORS" in code:
        good.append("✅ CORS مُفعَّل")
    if "os.getenv" in code:
        good.append("✅ Secrets تُقرأ من env variables")
    if "try:" in code and "except" in code:
        good.append("✅ Error handling موجود")
    if "strip()" in code:
        good.append("✅ Input sanitization باستخدام strip()")
    if ".seek(0" in code:
        good.append("✅ إعادة ضبط file pointer — دقيق")

    # ── Needs improvement ──
    if "= {}" in code and "redis" not in code.lower():
        needs.append("💡 الـ in-memory dicts لا تصمد عند restart — استخدم Redis أو SQLite")
    if "logging" not in code and "logger" not in code:
        needs.append("💡 لا يوجد logging framework — استخدم Python logging بدل print()")
    if "pytest" not in code and "unittest" not in code and "def test_" not in code:
        needs.append("💡 لا توجد unit tests — أضف pytest")
    if "timeout" not in code.lower():
        needs.append("💡 أضف timeout للـ API calls لتجنب hanging requests")
    if "max_tokens" not in code and "MAX_TOKENS" not in code:
        needs.append("💡 لا يوجد حد للـ tokens — ضع max_tokens لتجنب تكاليف مرتفعة")

    result = "=== تقييم Best Practices ===\n"
    if good:
        result += "\n✅ ممارسات صحيحة:\n" + "\n".join(f"  {g}" for g in good)
    if needs:
        result += "\n\n💡 تحسينات مقترحة:\n" + "\n".join(f"  {n}" for n in needs)
    return result


@tool
def code_improver(issue_description: str) -> str:
    """
    يولّد كود Python محسَّن لمشكلة معينة.
    المدخل: وصف المشكلة أو الجزء المراد تحسينه.
    يُرجع: كود جاهز للاستخدام مع شرح مختصر.
    أمثلة على المدخل: 'redis session store'، 'logging setup'، 'api timeout'.
    """
    desc = issue_description.lower()

    if "redis" in desc or "session" in desc or "memory" in desc:
        return '''
=== استبدال الـ in-memory dict بـ Redis ===

```python
import redis, json, os

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True,
)
SESSION_TTL = 60 * 60 * 24  # 24 hours

def save_session(session_id: str, data: dict):
    r.setex(f"session:{session_id}", SESSION_TTL, json.dumps(data))

def get_session(session_id: str) -> dict | None:
    raw = r.get(f"session:{session_id}")
    return json.loads(raw) if raw else None

def delete_session(session_id: str):
    r.delete(f"session:{session_id}")
```
'''

    if "log" in desc:
        return '''
=== إعداد Python Logging الصحيح ===

```python
import logging, sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger(__name__)

# الاستخدام
logger.info("Session created: %s", session_id)
logger.warning("Rate limit hit for IP: %s", ip)
logger.error("API error: %s", str(e), exc_info=True)
```
'''

    if "timeout" in desc or "api" in desc:
        return '''
=== إضافة Timeout للـ LLM API Calls ===

```python
import asyncio
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.x.ai/v1",
    model="grok-3-mini",
    temperature=0.3,
    request_timeout=30,
    max_retries=2,
)

async def call_with_timeout(agent_exec, inputs, timeout=30):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(agent_exec.invoke, inputs),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return {"output": "⏱️ انتهى الوقت. حاول بسؤال أبسط."}
```
'''

    return f"""
=== اقتراح تحسين: {issue_description} ===

لتحسين هذا الجانب:
1. حدّد الـ function أو الـ class المراد تحسينه
2. اكتب unit test يفشل أولاً (TDD)
3. طبّق التحسين حتى ينجح الـ test

أخبرني بالجزء المحدد وسأكتب لك الكود مباشرة.
"""
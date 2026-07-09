from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

_search = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """
    يبحث في الإنترنت عن:
    - documentation لـ libraries مستخدمة في المشروع
    - أحدث best practices لتقنية معينة
    - حلول لـ errors أو مشاكل معينة
    - مقارنات بين libraries
    استخدمه عندما تحتاج معلومة خارج نطاق الكود المرفوع.
    """
    try:
        result = _search.run(query)
        return f"=== نتائج البحث: '{query}' ===\n{result}"
    except Exception as e:
        return f" تعذّر البحث: {str(e)}"

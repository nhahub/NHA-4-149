from langchain.tools import tool


@tool
def cv_analyzer(cv_text: str) -> str:
    """
    يحلل الـ CV التقني ويعطي تقرير شامل:
    ATS compatibility، مهارات مكتشفة، نقاط قوة، توصيات.
    استخدمه فقط عندما يكون المحتوى سيرة ذاتية وليس كوداً.
    """
    word_count   = len(cv_text.split())
    has_github   = "github"   in cv_text.lower()
    has_linkedin = "linkedin" in cv_text.lower()
    has_numbers  = any(ch.isdigit() for ch in cv_text)
    has_summary  = any(kw in cv_text.lower() for kw in ["summary", "objective", "profile", "ملخص", "هدف"])

    tech_skills = [
        skill for skill in [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "Vue",
            "SQL", "PostgreSQL", "MongoDB", "Redis",
            "Docker", "Kubernetes", "AWS", "GCP", "Azure",
            "ML", "AI", "TensorFlow", "PyTorch", "LangChain",
            "FastAPI", "Flask", "Django", "REST", "GraphQL",
            "Git", "CI/CD", "Linux",
        ]
        if skill.lower() in cv_text.lower()
    ]

    # ATS Score calculation
    ats_score = 4
    if has_github:            ats_score += 1
    if has_linkedin:          ats_score += 1
    if has_numbers:           ats_score += 1
    if has_summary:           ats_score += 1
    if len(tech_skills) >= 5: ats_score += 1
    if word_count > 300:      ats_score += 1
    ats_score = min(ats_score, 10)

    ats_label = (
        " ممتاز" if ats_score >= 8 else
        " متوسط" if ats_score >= 6 else
        " يحتاج تحسيناً"
    )

    recommendations = []
    if not has_github:
        recommendations.append(" أضف رابط GitHub — ضروري لأي مطوّر")
    if not has_linkedin:
        recommendations.append(" أضف رابط LinkedIn")
    if not has_numbers:
        recommendations.append(" أضف أرقاماً وإنجازات قابلة للقياس: 'رفعت الأداء 30%' بدل 'حسّنت الأداء'")
    if not has_summary:
        recommendations.append(" أضف ملخصاً مهنياً في الأعلى (3-4 جمل)")
    if len(tech_skills) < 5:
        recommendations.append(" أضف مزيداً من المهارات التقنية المحددة")
    if word_count < 300:
        recommendations.append(" الـ CV قصير جداً — أضف تفاصيل لمشاريعك وإنجازاتك")

    return f"""
=== تحليل الـ CV التقني ===

 إحصائيات عامة:
  عدد الكلمات    : {word_count}
  ATS Score      : {ats_score}/10 — {ats_label}
  GitHub         : {' موجود' if has_github   else ' مفقود'}
  LinkedIn       : {' موجود' if has_linkedin  else ' مفقود'}
  أرقام وإنجازات : {' موجودة' if has_numbers else ' مفقودة'}
  ملخص مهني      : {' موجود' if has_summary  else ' مفقود'}

 مهارات تقنية مكتشفة ({len(tech_skills)}):
  {', '.join(tech_skills) if tech_skills else 'لم تُكتشف مهارات تقنية واضحة — أضفها بشكل صريح'}

 توصيات ({len(recommendations)}):
{chr(10).join(f'  {r}' for r in recommendations) if recommendations else '   الـ CV في حالة جيدة!'}
"""

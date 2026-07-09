import os

#  LLM 
GROK_API_KEY  = os.getenv("GROQ_API_KEY")
GROK_BASE_URL = "https://api.groq.com/openai/v1"
GROK_MODEL    = "llama-3.3-70b-versatile"
LLM_TEMPERATURE   = 0.3
LLM_TIMEOUT       = 30      # seconds
LLM_MAX_RETRIES   = 2

#  Agent 
AGENT_MAX_ITERATIONS   = 6
AGENT_VERBOSE          = True   # set False in production to hide reasoning logs

#  Flask 
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())
HOST = "0.0.0.0"
PORT = 7860

#  Rate limiting 
RATE_LIMIT_MAX    = 20        # requests
RATE_LIMIT_WINDOW = 60 * 60  # 1 hour in seconds

#  File upload 
MAX_FILE_SIZE_MB = 15
MAX_CONTENT_CHARS = 7_000   # chars sent to LLM
MAX_MESSAGE_LENGTH = 2_000

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".cs",
    ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".html", ".css",
    ".json", ".yaml", ".yml", ".md", ".txt", ".pdf", ".zip",
    ".env", ".toml", ".cfg", ".ini", ".sh", ".dockerfile", ".xml",
}

SKIP_DIRS = {"__pycache__", "node_modules", ".git", ".DS_Store"}

#  CV detection keywords 
CV_KEYWORDS = [
    "experience", "education", "skills", "resume", "cv",
    "خبرة", "تعليم", "مهارات", "السيرة", "العمل",
]
CV_KEYWORD_THRESHOLD = 3

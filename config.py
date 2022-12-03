from os.path import dirname, abspath

CURR_DIR = dirname(abspath(__file__))

URL = "https://www.sqlink.com/career/db/פיתוח-אוטומציה/?page="

# ================ DATA SETUP ==================
CV_FILE = f"{CURR_DIR}/TEST_CV.docx"
SUBMIT_LOG_FILE = f"{CURR_DIR}/submit_log.log"
SEEN_JOBS_FILE = f"{CURR_DIR}/seen_jobs.log"

# =============== KEY WORDS SETUP ==============
KEY_WORDS = ["אוטומציה", "automation", " engineer", "selenium", "aws", "linux", "backend", "api", "docker",
             "html", "css", "web", "rest", "gui", "ui", "playwright", "pytest"]
LANGUAGES = ["python", "#c", "java", "javascript", "node.js", ".net"]
DESIRED_LANGUAGES = "python"
AVOID_KEY_WORDS = ["leader", "senior", "בצפון", "הצפון"]

# ============== BOT SETUP =====================
HEADLESS = True


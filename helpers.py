# ---------- Helpers ----------
from io import BytesIO
import re
# Optional libs for parsing (install if needed)
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    import docx
except Exception:
    docx = None

TECH_KEYWORDS = [
    # Add / extend as needed
    "python","django","flask","fastapi","javascript","typescript","react","angular",
    "vue","node","express","java","spring","kotlin","golang","go","c#","c++",
    "aws","azure","gcp","docker","kubernetes","postgres","mysql","mongodb",
    "redis","graphql","rest","sql","tensorflow","pytorch","keras","spark"
]
CONVERSATION_END_KEYWORDS = ["exit","quit","bye","goodbye","thanks","thank you","stop"]
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+\d{1,3}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?[\d\s-]{6,15}")


def extract_text_from_pdf(bytes_data):
    if PyPDF2 is None:
        return ""
    text = []
    reader = PyPDF2.PdfReader(BytesIO(bytes_data))
    for page in reader.pages:
        try:
            text.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(text)

def extract_text_from_docx(bytes_data):
    if docx is None:
        return ""
    tmp_path = "/tmp/_tmp_docx.docx"
    with open(tmp_path, "wb") as f:
        f.write(bytes_data)
    doc = docx.Document(tmp_path)
    paras = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paras)

def extract_text_from_txt(bytes_data):
    try:
        return bytes_data.decode("utf-8", errors="ignore")
    except:
        return str(bytes_data)

def autofill_fields_from_text(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = lines[0] if lines else ""
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    email = email_match.group(0) if email_match else ""
    phone = phone_match.group(0) if phone_match else ""
    # Try to detect tech stack using keywords
    lowered = text.lower()
    detected_tech = sorted({k for k in TECH_KEYWORDS if k in lowered}, key=lambda x: lowered.find(x))
    # Try to estimate years of experience: look for patterns like 'X years'
    years = None
    ymatch = re.search(r"(\d{1,2})\+?\s+years", lowered)
    if ymatch:
        years = int(ymatch.group(1))
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": "",
        "years_experience": years if years is not None else 0,
        "tech_stack": detected_tech
    }

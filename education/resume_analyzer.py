import re

# ---------------- CLEAN TEXT ----------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\r', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text

# ---------------- EXTRACT SKILLS SECTION ----------------
def extract_skills_section(text):

    text = text.lower()

    # Fix OCR mistakes
    text = text.replace("sk1lls", "skills").replace("ski11s", "skills")

    # Common section boundaries
    pattern = r"(skills|technical skills|key skills)([\s\S]*?)(experience|education|projects|summary|strengths|languages|$)"

    match = re.search(pattern, text)

    if match:
        return match.group(2)

    return ""
# ---------------- PARSE SKILLS ----------------
def extract_skills(text):

    skills_block = extract_skills_section(text)

    if not skills_block:
        return []

    # Split based on separators
    raw_skills = re.split(r'[\n,•|/·]', skills_block)

    skills = []

    for skill in raw_skills:
        skill = skill.strip()

        # Remove long sentences (THIS is your main problem)
        if len(skill.split()) > 4:
            continue

        # Remove numbers, junk
        skill = re.sub(r'[^a-zA-Z0-9+ ]', '', skill)

        if len(skill) > 2:
            skills.append(skill.lower())

    return list(set(skills))[:15]
# ---------------- ATS SCORE ----------------
def calculate_ats(text, skills):

    score = 0

    # Skills importance
    score += min(len(skills) * 5, 40)

    # Sections presence
    if "skills" in text:
        score += 10
    if "experience" in text:
        score += 10
    if "projects" in text:
        score += 10

    # Length
    words = len(text.split())
    if words > 300:
        score += 20
    elif words > 150:
        score += 10

    return min(score, 100)

# ---------------- ROLE PROBABILITY ----------------
def calculate_role_probabilities(skills, domain):

    DOMAIN_KEYWORDS = {
        "it": {
            "Frontend Developer": ["html","css","javascript","react"],
            "Backend Developer": ["python","java","node","sql"],
            "Data Analyst": ["sql","excel","data"],
            "ML Engineer": ["machine learning","ai","model"],
            "DevOps Engineer": ["docker","cloud","linux"]
        },
        "management": {
            "Project Manager": ["management","planning"],
            "HR Manager": ["communication"],
            "Business Analyst": ["analysis","business"]
        },
        "non_it": {
            "Content Writer": ["writing","content"],
            "Sales Executive": ["sales","marketing"],
            "Customer Support": ["support","client"]
        }
    }

    roles = DOMAIN_KEYWORDS.get(domain, {})
    role_scores = {}

    for role, keywords in roles.items():
        score = 0

        for skill in skills:
            for key in keywords:
                if key in skill or skill in key:
                    score += 3

        score += 1
        role_scores[role] = score

    total = sum(role_scores.values())

    for role in role_scores:
        role_scores[role] = round((role_scores[role] / total) * 100, 2)

    return role_scores

# ---------------- EVALUATION ----------------
def evaluate(score):
    if score >= 75:
        return "good", "Strong resume. Ready for applications."
    elif score >= 50:
        return "average", "Moderate resume. Needs improvements."
    else:
        return "poor", "Weak resume. Improve significantly."

# ---------------- MAIN ----------------
def analyze_resume(text, domain):

    text = clean_text(text)

    skills = extract_skills(text)

    score = calculate_ats(text, skills)
    if not skills:
        return {
            "score": 10,
            "skills": [],
            "role_probabilities": {"No Skills Detected": 100},
            "status": "poor",
            "message": "Skills section not detected clearly."
        }

    role_probabilities = calculate_role_probabilities(skills, domain)

    status, message = evaluate(score)

    return {
        "score": score,
        "skills": skills,
        "role_probabilities": role_probabilities,
        "status": status,
        "message": message
    }
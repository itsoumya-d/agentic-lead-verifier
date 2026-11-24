"""B2B lead data cleaner, normalizer, and ICP fit scoring engine."""
from dataclasses import dataclass
import re
from typing import Dict, List, Optional
import urllib.parse


DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "guerrillamail.com", "10minutemail.com",
    "throwawaymail.com", "trashmail.com", "getairmail.com"
}

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com"
}


@dataclass
class LeadRecord:
    first_name: str
    last_name: str
    company_name: str
    raw_title: str
    cleaned_title: str
    seniority: str  # C-Level, VP, Director, Manager, Senior, IC
    email: Optional[str]
    email_status: str  # 'valid_business', 'free_provider', 'disposable', 'invalid_syntax', 'missing'
    linkedin_url: Optional[str]
    headcount: int
    icp_score: int  # 0 to 100


class LeadCleaner:
    EMAIL_REGEX = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
    COMPANY_SUFFIXES = re.compile(r"\b(inc\.?|llc\.?|ltd\.?|corp\.?|corporation|gmbh|co\.?)\b", re.IGNORECASE)
    EMOJI_PATTERN = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)

    def clean_name(self, raw: str) -> str:
        if not raw:
            return ""
        no_emoji = self.EMOJI_PATTERN.sub("", raw)
        clean = re.sub(r"[^a-zA-Z\s\-']", "", no_emoji)
        return re.sub(r"\s+", " ", clean).strip().title()

    def clean_company(self, raw: str) -> str:
        if not raw:
            return ""
        no_emoji = self.EMOJI_PATTERN.sub("", raw)
        stripped = self.COMPANY_SUFFIXES.sub("", no_emoji)
        cleaned = re.sub(r"[\s,\.\-]+$", "", stripped)
        return re.sub(r"\s+", " ", cleaned).strip().title()

    def clean_title_and_seniority(self, raw: str) -> tuple[str, str]:
        if not raw:
            return ("", "IC")
        # Remove emojis and bracketed suffixes (e.g., "| Hiring!", "[Open to Work]")
        no_emoji = self.EMOJI_PATTERN.sub("", raw)
        base = re.split(r"[\|\-–—•\[\(]", no_emoji)[0].strip()
        cleaned_title = re.sub(r"\s+", " ", base)

        low = cleaned_title.lower()
        if any(w in low for w in ["chief", "cto", "ceo", "cfo", "coo", "cro", "cmo", "cpo", "founder", "owner", "president"]):
            seniority = "C-Level"
        elif any(w in low for w in ["vp", "vice president"]):
            seniority = "VP"
        elif "director" in low or "head" in low:
            seniority = "Director"
        elif "lead" in low or "manager" in low:
            seniority = "Manager"
        elif "senior" in low or "sr" in low:
            seniority = "Senior"
        else:
            seniority = "IC"

        return (cleaned_title, seniority)

    def validate_email(self, email: Optional[str]) -> str:
        if not email or not email.strip():
            return "missing"
        email = email.strip().lower()
        if not self.EMAIL_REGEX.match(email):
            return "invalid_syntax"
        domain = email.split("@")[-1]
        if domain in DISPOSABLE_DOMAINS:
            return "disposable"
        if domain in FREE_EMAIL_DOMAINS:
            return "free_provider"
        return "valid_business"

    def clean_linkedin_url(self, raw_url: Optional[str]) -> Optional[str]:
        if not raw_url or not raw_url.strip():
            return None
        parsed = urllib.parse.urlparse(raw_url.strip())
        path = parsed.path.rstrip("/")
        if not path:
            return None
        return f"https://www.linkedin.com{path}"

    def calculate_icp_score(self, seniority: str, email_status: str, headcount: int) -> int:
        score = 0
        # Seniority weights
        seniority_weights = {
            "C-Level": 40,
            "VP": 35,
            "Director": 30,
            "Manager": 20,
            "Senior": 15,
            "IC": 10,
        }
        score += seniority_weights.get(seniority, 10)

        # Email verifiability weights
        if email_status == "valid_business":
            score += 35
        elif email_status == "free_provider":
            score += 15
        elif email_status in ("missing", "disposable", "invalid_syntax"):
            score += 0

        # Company headcount fit (ideal 11-200 for high-converting outbound)
        if 11 <= headcount <= 250:
            score += 25
        elif 251 <= headcount <= 1000:
            score += 20
        elif headcount > 1000:
            score += 15
        else:
            score += 10

        return min(100, score)

    def process_lead(self, raw: Dict) -> LeadRecord:
        first_name = self.clean_name(raw.get("first_name", ""))
        last_name = self.clean_name(raw.get("last_name", ""))
        company_name = self.clean_company(raw.get("company_name", ""))
        raw_title = raw.get("title", "")
        cleaned_title, seniority = self.clean_title_and_seniority(raw_title)

        email = raw.get("email")
        email_status = self.validate_email(email)
        clean_url = self.clean_linkedin_url(raw.get("linkedin_url"))
        headcount = int(raw.get("headcount", 0))

        score = self.calculate_icp_score(seniority, email_status, headcount)

        return LeadRecord(
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            raw_title=raw_title,
            cleaned_title=cleaned_title,
            seniority=seniority,
            email=email,
            email_status=email_status,
            linkedin_url=clean_url,
            headcount=headcount,
            icp_score=score,
        )

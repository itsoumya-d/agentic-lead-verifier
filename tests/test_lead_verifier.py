from src.verifier.cleaner import LeadCleaner
from src.verifier.tool_schema import CLEAN_AND_VERIFY_LEADS_TOOL


def test_name_and_company_normalization():
    cleaner = LeadCleaner()
    assert cleaner.clean_name("  John 🚀 Doe  ") == "John Doe"
    assert cleaner.clean_company("Acme Enterprise, Inc.") == "Acme Enterprise"
    assert cleaner.clean_company("Global Logistics LLC.") == "Global Logistics"
    assert cleaner.clean_company("Stripe 🔥") == "Stripe"


def test_title_and_seniority_extraction():
    cleaner = LeadCleaner()
    title, seniority = cleaner.clean_title_and_seniority("VP of Sales | Hiring A-Players! 🚀")
    assert title == "VP of Sales"
    assert seniority == "VP"

    title2, seniority2 = cleaner.clean_title_and_seniority("Chief Technology Officer [Open to Collabs]")
    assert title2 == "Chief Technology Officer"
    assert seniority2 == "C-Level"

    title3, seniority3 = cleaner.clean_title_and_seniority("Senior Software Engineer - Platform Team")
    assert title3 == "Senior Software Engineer"
    assert seniority3 == "Senior"


def test_email_validation():
    cleaner = LeadCleaner()
    assert cleaner.validate_email("alex@company.com") == "valid_business"
    assert cleaner.validate_email("alex@gmail.com") == "free_provider"
    assert cleaner.validate_email("test@mailinator.com") == "disposable"
    assert cleaner.validate_email("invalid-email-string") == "invalid_syntax"
    assert cleaner.validate_email(None) == "missing"


def test_linkedin_url_cleaning():
    cleaner = LeadCleaner()
    raw = "https://www.linkedin.com/in/alex-smith-12345/?utm_source=nav&trackingId=xyz"
    assert cleaner.clean_linkedin_url(raw) == "https://www.linkedin.com/in/alex-smith-12345"


def test_icp_score_calculation():
    cleaner = LeadCleaner()
    # C-Level at high-fit 50-person company with valid business email
    high_fit = cleaner.process_lead({
        "first_name": "Sarah",
        "last_name": "Connor",
        "company_name": "Cyberdyne Systems Corp",
        "title": "CTO & Co-Founder | Hiring",
        "email": "sarah@cyberdyne.io",
        "linkedin_url": "https://www.linkedin.com/in/sarah-connor/",
        "headcount": 85,
    })
    assert high_fit.seniority == "C-Level"
    assert high_fit.email_status == "valid_business"
    assert high_fit.company_name == "Cyberdyne Systems"
    assert high_fit.icp_score == 100  # 40 (C-level) + 35 (valid) + 25 (headcount 85) = 100

    # Low fit: IC with disposable email
    low_fit = cleaner.process_lead({
        "first_name": "Bob",
        "last_name": "User",
        "company_name": "Generic Co",
        "title": "Junior Intern",
        "email": "bob@mailinator.com",
        "headcount": 5,
    })
    assert low_fit.seniority == "IC"
    assert low_fit.email_status == "disposable"
    assert low_fit.icp_score == 20  # 10 (IC) + 0 (disposable) + 10 (headcount 5) = 20


def test_tool_schema_structure():
    assert CLEAN_AND_VERIFY_LEADS_TOOL["name"] == "clean_and_verify_leads"
    assert "leads" in CLEAN_AND_VERIFY_LEADS_TOOL["input_schema"]["properties"]

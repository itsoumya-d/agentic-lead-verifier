"""Anthropic Claude tool definition for autonomous agentic lead enrichment."""

CLEAN_AND_VERIFY_LEADS_TOOL = {
    "name": "clean_and_verify_leads",
    "description": (
        "Normalizes raw B2B prospect records from Sales Navigator or CSV exports. "
        "Strips emojis, standardizes job titles, maps seniority tiers, validates email deliverability, "
        "and scores ICP fit."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "leads": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "company_name": {"type": "string"},
                        "title": {"type": "string"},
                        "email": {"type": "string"},
                        "linkedin_url": {"type": "string"},
                        "headcount": {"type": "integer"},
                    },
                    "required": ["first_name", "last_name", "company_name", "title"],
                },
                "description": "List of raw prospect objects to clean and score.",
            }
        },
        "required": ["leads"],
    },
}

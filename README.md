# agentic-lead-verifier

Agentic B2B prospecting lead verification, data normalization, MX validation, and ICP scoring pipeline in Python.

## Features

- **Lead Sanitization & Data Normalization**: Cleans noisy titles, removes emojis, capitalizes company names, strips tracking parameters from LinkedIn URLs.
- **Email Syntax & Domain MX Heuristics**: Validates RFC 5322 syntax, flags disposable and free email providers, detects corporate domain MX availability.
- **ICP Fit Scoring**: Deterministic rule-based scoring matching seniority, department, company headcount, and industry relevance.
- **Agentic SDR Tool Schema**: Ready-to-use tool definitions for autonomous outbound SDR agents.

## Quickstart

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest
```

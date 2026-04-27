import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_greenwashing_risk(company_name, official_claim, news_snippets, model_name="llama-3.3-70b-versatile"):
    system_prompt = (
        "You are a Senior ESG Quant Analyst at a top-tier Investment Bank. "
        "Provide a highly structured, data-dense JSON forensic report. "
        "CRITICAL: DO NOT copy the placeholder values from the prompt. You MUST calculate real scores based on the provided Alternative Data."
    )
    
    news_context = "\n".join([f"- {n['title']}: {n['body']}" for n in news_snippets])
    
    user_prompt = f"""
    TARGET: {company_name}
    MANAGEMENT CLAIM: "{official_claim}"
    ALTERNATIVE DATA: {news_context}
    
    Perform a rigorous ESG gap analysis. Calculate risk scores (0-100, where 100 is maximum greenwashing/risk).
    
    OUTPUT EXACTLY IN THIS JSON SCHEMA (Replace brackets with your calculated data):
    {{
      "overall_risk_score": [Calculate integer 0-100 based on severity of news],
      "risk_level": "[Classify as LOW, MODERATE, HIGH, or SEVERE]",
      "verdict": "[e.g., SELL - HIGH REPUTATIONAL RISK, or HOLD - MINOR ISSUES]",
      "forensic_summary": "[1 sentence executive summary of the discrepancy]",
      "pillar_scores": {{
        "Environment": [Calculate integer 0-100],
        "Social": [Calculate integer 0-100],
        "Governance": [Calculate integer 0-100]
      }},
      "contradiction_table": [
        {{
          "issue": "[Name of the ESG issue]",
          "evidence": "[Specific evidence from the Alternative Data]",
          "severity": "[LOW, MEDIUM, HIGH, or CRITICAL]"
        }}
      ]
    }}
    Ensure contradiction_table has 3-4 distinct rows.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=model_name,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        return {"overall_risk_score": 0, "risk_level": "ERROR", "forensic_summary": str(e), "pillar_scores": {}, "contradiction_table": []}
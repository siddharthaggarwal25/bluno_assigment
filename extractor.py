import re
import json
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="GOOGLE_API_KEY",
    temperature=0
)

def rule_extract(text):

    data = {
        "issuer": None,
        "date": None,
        "totals": {},
        "reference_ids": []
    }

    confidence = 0.0


    # ------------------
    # Reference IDs
    # ------------------

    refs = re.findall(
        r"(?:Invoice|INV|Reference|PO)\s*(?:No|Number|#)?[:\s-]*([A-Za-z0-9\-\/]+)",
        text,
        re.IGNORECASE
    )


    if refs:

        # remove duplicates
        data["reference_ids"] = list(
            set(refs)
        )

        confidence += 0.25




    # ------------------
    # Date
    # ------------------

    dates = re.findall(
        r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b",
        text
    )


    if dates:

        # take first unique date
        data["date"] = list(
            dict.fromkeys(dates)
        )[0]

        confidence += 0.25





    # ------------------
    # Amounts
    # ------------------

    amounts = re.findall(
        r"(?:Grand Total|Total Amount|Amount Due|Total)"
        r"[:\s₹$]*"
        r"([0-9,]+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE
    )


    if amounts:

        unique_amounts = list(
            dict.fromkeys(amounts)
        )


        amount = (
            unique_amounts[0]
            .replace(",", "")
        )


        data["totals"] = {
            "total": float(amount)
        }

        confidence += 0.25





    # ------------------
    # Issuer
    # ------------------

    issuers = re.findall(
        r"(?:From|Vendor|Seller|Supplier)"
        r"[:\s]+(.+)",
        text,
        re.IGNORECASE
    )


    if issuers:

        unique_issuers = list(
            dict.fromkeys(
                [
                    i.strip()
                    for i in issuers
                ]
            )
        )


        data["issuer"] = unique_issuers[0]

        confidence += 0.25



    print( "RULE BASED" , data)

    return {
        "data": data,
        "confidence": round(
            confidence,
            2
        )
    }


def llm_extract(text):

    try:

        prompt = ChatPromptTemplate.from_template(
            """
            Extract invoice information from the text.

            Return ONLY valid JSON, no extra text, no markdown formatting.

            Required schema:

            {{
                "issuer": "vendor/company name",
                "date": "YYYY-MM-DD",
                "totals": {{
                    "total": amount
                }},
                "reference_ids": [
                    "invoice numbers or PO numbers"
                ]
            }}


            Invoice text:

            {text}
            """
        )


        chain = prompt | llm


        response = chain.invoke(
            {
                "text": text
            }
        )

        print(f"LLM Response raw: {response.content}")

        # Extract JSON from markdown code blocks if present
        content = response.content.strip()
        
        # Remove markdown code block formatting (```json ... ```)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        print(f"LLM Response cleaned: {content}")

        extracted = json.loads(content)

        print(f"LLM Extracted Data: {extracted}")

        return extracted
    


    except Exception as e:

        print(f"❌ LLM extraction error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "issuer": None,
            "date": None,
            "totals": {},
            "reference_ids": [],
            "error": str(e)
        }
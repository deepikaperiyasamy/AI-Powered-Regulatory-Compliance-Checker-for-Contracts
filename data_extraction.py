from google import genai
from google.genai import types
from pydantic import BaseModel
from enum import Enum
import PyPDF2
import json
import os
from dotenv import load_dotenv

load_dotenv()

# # 1️⃣ Detect document type
# def document_type(file):
#     class DocumentType(str, Enum):
#         DPA = "Data Processing Agreement"
#         JCA = "Joint Controller Agreement"
#         C2C = "Controller-to-Controller Agreement"
#         SUB = "Processor-to-Subprocessor Agreement"
#         SCC = "Standard Contractual Clauses"
#         NoOne="NoOne"

#     class FindDocumentType(BaseModel):
#         document_type: DocumentType

#     text = ""
#     with open(file, "rb") as f:
#         reader = PyPDF2.PdfReader(f)
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text

#     client = genai.Client(api_key=os.getenv("gemini_API_KEY"))

#     prompt = f"""
#    Tell me what type of document is this

#      document should be type of between

#      1. Data Processing Agreement
#      2. Joint Controller Agreement
#      3. Controller-to-Controller Agreement
#      4. Processor-to-Subprocessor Agreement
#      5. Standard Contractual Clauses
#      6. NoOne

#       ### Rules:
#     - If the document is **not a legal or data protection agreement**, return `"NoOne"`.
#     - Examples of documents that should return `"NoOne"`:
#     - Resumes, CVs, invoices, letters, research papers, images, empty text, etc.
#     - If the text contains **no legal keywords** (e.g. controller, processor, data, processing, transfer, subprocessor, SCC, GDPR, agreement, clause, party, etc.), classify as `"NoOne"`.
#     - If the document contains mostly personal info (like education, name, contact, skills, experience), classify as `"NoOne"`.
#     - Never guess the closest type — only classify if it clearly fits one of the 5 agreement types.

    
#     Read the text carefully and pick the **closest legal category**, even if the title is generic like “Services Agreement”.
#     Input: {text}

#     Respond ONLY in JSON:
#     [
#       {{
#         "document_type": "<type_of_document>"
#       }}
#     ]
#     """

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             thinking_config=types.ThinkingConfig(thinking_budget=0),
#             response_mime_type="application/json",
#             response_schema=list[FindDocumentType]
#         ),
#     )

#     json_object = json.loads(response.text)
#     return json_object[0]["document_type"]

# 2️⃣ Extract and summarise clauses
def Clause_extraction_with_summarization(file):
    print("Inside clause extraction")
    class ClauseExtraction(BaseModel):
        clause_id: str
        heading: str
        summarised_text: str

    text = ""
    with open(file, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    

    client = genai.Client(api_key=os.getenv("gemini_API_KEY"))

    prompt = f"""
        you are an expert in legal contract analysis.
    Your task is to extract all **clauses** from the following contract text and summarise its clause data.
  
    
    ### Guidelines:
    - A clause may begin with:
    - A number/letter (e.g. "1.", "A."),
    - The word "Clause" followed by a number (e.g. "Clause 1", "Clause 5"), OR
    - An ALL CAPS heading (e.g. "DEFINATION", "TRANSFER OF DATA".)
    
    -Each extracted clause must include:
    -**clause_id** (the exact numbering/label from the contract e.g. "1.", "A.", "Clause 1", "EXHIBIT A" etc)
    -**heading/title** (use the explicit heading if present; if absent, use the first few words of the clause as a makeshift title)
    -**summarised text** (short and summarise text of the clause, including any sub-clauses, preserving legal wording exactly as in the contract, contains only important information from the clause and its sub-clauses)
    
    -Maintain clause boundaries percisly. do not merge multiple clauses into one.
    -Include clauses from exhibits, appendices, and annexes if present.
    -Do not omit any content unless it is clearly not-contractual (e.g. page numbers, headers, footers, blank sihnature lines).
    -response in **valid json** only (no explanation, no notes, no extra text).

    

    

    Input: {text}

    Respond ONLY in valid JSON array:
    [
        {{
            "clause_id": "<clause_id>",
            "heading": "<heading/title>",
            "summarised_text": "<short summary>"
        }}
    ]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
            response_schema=list[ClauseExtraction]
        ),
    )

    return response.text


import notification

if __name__ == "__main__":
    
    # for normal flow 
    try:
        # tamplets mapping 
        TEMPLATE_MAP={
            "dpa.json":"templates/GDPR-Sample-Agreement.pdf",
            "jca.json":"templates/(JCA) model-joint-controllership-agreement.pdf",
            "c2c.json":"templates/(C2C) 2-Controller-to-controller-data-privacy-addendum.pdf",
            "scc.json":"templates/Standard-Contractual-Clauses-SCCs.pdf",
            "subprocessing.json":"templates/(Subprocessing Contract) Personal-Data-Sub-Processor-Agreement-2024-01-24.pdf"
        }
        
        for key, value in TEMPLATE_MAP.items():
            
            response = Clause_extraction_with_summarization(value)
            
            # for summarised flow 
            # response = Clause_extraction_with_summarization("GDPR-Sample-Agreement.pdf")
            
            with open("json_files/"+key, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error Occured",e)
        error_type = type(e).__name__ 
        notification.send_notification("Error Occured in Template Data Extraction", f"Error is {e}")
        # notification.send_notification(f"⚠️ Compliance Checker Error: {error_type}", f"Error is {e}")
        
        

from google import genai
from google.genai import types
from pydantic import BaseModel
from enum import Enum
import PyPDF2
import json
import os
from dotenv import load_dotenv

load_dotenv()


# ----------- 1️⃣ Identify document type ----------------
def document_type(file):
    class DocumentType(str, Enum):
        DPA = "Data Processing Agreement"
        JCA = "Joint Controller Agreement"
        C2C = "Controller-to-Controller Agreement"
        subprocessor = "Processor-to-Subprocessor Agreement"
        SCC = "Standard Contractual Clauses"
        NoOne="NoOne"

    class FindDocumentType(BaseModel):
        document_type: DocumentType

    # Read PDF text
    text = ""
    with open(file, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""

    document should be type of between

       1. Data Processing Agreement
       2. Joint Controller Agreement
       3. Controller-to-Controller Agreement
       4. Processor-to-Subprocessor Agreement
       5. Standard Contractual Clauses
       6. NoOne

    

Read the text carefully and pick the **closest legal category**, even if the title is generic like “Services Agreement”.

    Input: {text}

    Respond ONLY in JSON:
    [
      {{
        "document_type": "<type_of_document>"
      }}
    ]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
            response_schema=list[FindDocumentType]
        ),
    )

    json_object = json.loads(response.text)
    return json_object[0]["document_type"]


# ----------- 2️⃣ Compare agreements ----------------
def compare_agreements(unseen_data, template_data):
    # class CompareResult(BaseModel):
    #     missing_clauses: list[str]
    #     compliance_risks: list[str]
    #     risk_score: int
    #     reasoning: str
    #     recommendations: list[str]

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    You are an AI legal assistant specialized in GDPR and contract compliance.

    Compare these two documents:

    Trusted template (reference for regulatory compliance):
    {template_data}

    New contract to review:
    {unseen_data}

    Tasks:
    1. Identify any missing or altered clauses in the new contract compared to the template.
    2. Flag potential compliance risks based on GDPR regulations.
    3. Assign a risk score between 0 and 100 for the new contract (0 = no risk, 100 = maximum risk).
    4. Provide reasoning for the assigned risk score.
    5. Suggest specific amendments or recommendations to bring the contract in line with current regulatory standards and best practices.
    6. Provide the response in a **concise, structured format**, like this:

    - 📌 Missing Clauses: [...]
    -⚠️ Potential Compliance Risks: [...]
    -🔢 Risk Score (0-100): ...
    -📝 Reasoning: [...]
    -✅ Recommendations: [...]

    
    Keep each section brief and focused on key points. Avoid long paragraphs or unnecessary details.  

    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            # response_mime_type="application/json",
            # response_schema=CompareResult,
            temperature=0.3
        ),
    )
    print(response.text)
    return response.text

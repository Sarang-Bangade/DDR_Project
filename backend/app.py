import os, json, re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pdfplumber
import pypdf

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GEMINI_API_KEY")

def extract_text(file_bytes):
    import io
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def call_ai(inspection, thermal, context):
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("models/gemini-2.5-flash")
         # 🔥 LIMIT TEXT (IMPORTANT)
        inspection = inspection[:4000]
        thermal = thermal[:4000]
        prompt = f"""
Generate DDR report in JSON.

Inspection:
{inspection}
Thermal:
{thermal}
Context:
{context}
Rules:
- No fake data
- Missing = Not Available
"""

        response = model.generate_content(prompt)
        text = response.text
        clean = re.sub(r'```json|```', '', text).strip()
        return json.loads(clean)

    except Exception as e:
        return {"error": str(e)}

@app.route("/generate", methods=["POST"])
def generate():
    insp = ""
    therm = ""

    if "inspection" in request.files:
        insp = extract_text(request.files["inspection"].read())

    if "thermal" in request.files:
        therm = extract_text(request.files["thermal"].read())

    context = request.form.get("context", "")

    if not insp and not therm:
        return jsonify({"error": "No file"}), 400

    try:
        report = call_ai(insp, therm, context)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
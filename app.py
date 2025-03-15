from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
import google.generativeai as genai
import os
import json
import pandas as pd
from datetime import datetime

os.environ["GOOGLE_API_KEY"] = "AIzaSyACCG9fWDn7aMQxxgT6HLzgGkePogEAzZo"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

app = Flask(__name__)
model = genai.GenerativeModel("models/gemini-1.5-pro")

def safe_extract(data, path, default=None):
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current if current is not None else default

def process_skills(data):
    skills = {
        'technical': [],
        'non_technical': []
    }
    
    tech_skills = safe_extract(data, 'skills.technical_skills', [])
    if isinstance(tech_skills, str):
        tech_skills = [s.strip() for s in tech_skills.split(',')]
    skills['technical'] = list(filter(None, tech_skills))
    
    non_tech_skills = safe_extract(data, 'skills.non_technical_skills', [])
    if isinstance(non_tech_skills, str):
        non_tech_skills = [s.strip() for s in non_tech_skills.split(',')]
    skills['non_technical'] = list(filter(None, non_tech_skills))
    
    return skills

def save_to_excel(template_data):
    try:
        excel_data = {
            "Full Name": template_data["full_name"],
            "Contact Number": template_data["contact_number"],
            "Email Address": template_data["email_address"],
            "Location": template_data["location"],
            "Technical Skills": ", ".join(template_data["technical_skills"]),
            "Non-Technical Skills": ", ".join(template_data["non_technical_skills"]),
            "Education": "\n".join(template_data["education"]),
            "Work Experience": "\n".join(template_data["work_experience"]),
            "Certifications": ", ".join(template_data["certifications"]),
            "Languages": ", ".join(template_data["languages"]),
            "Suggested Category": template_data["suggested_resume_category"],
            "Recommended Roles": ", ".join(template_data["recommended_job_roles"])
        }

        df = pd.DataFrame([excel_data])
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = template_data["full_name"].replace(" ", "_").lower() if template_data["full_name"] else "resume"
        filename = f"{safe_name}_{timestamp}.xlsx"
        save_path = os.path.join(app.static_folder, 'exports', filename)
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_excel(save_path, index=False)
        
        return f"/static/exports/{filename}"
    except Exception as e:
        print(f"Error saving Excel file: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files['resume']
        if not file or file.filename == '':
            return jsonify({"error": "No selected file"})

        if file.filename.endswith('.pdf'):
            text = "\n".join([page.extract_text() or '' for page in PdfReader(file).pages])
            
            raw_response = model.generate_content(
                f"""Extract resume details in JSON format with this exact structure:
{{
    "full_name": "string",
    "contact_number": "string",
    "email_address": "string",
    "location": "string",
    "skills": {{
        "technical_skills": ["array"],
        "non_technical_skills": ["array"]
    }},
    "education": ["array of strings"],
    "work_experience": ["array of strings"],
    "certifications": ["array"],
    "languages": ["array"],
    "suggested_resume_category": "string",
    "recommended_job_roles": ["array"]
}}
Resume text: {text}"""
            ).text

            response_clean = raw_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(response_clean)

            skills = process_skills(data)
            
            template_data = {
                "full_name": safe_extract(data, 'full_name', ''),
                "contact_number": safe_extract(data, 'contact_number', ''),
                "email_address": safe_extract(data, 'email_address', ''),
                "location": safe_extract(data, 'location', ''),
                "technical_skills": skills['technical'],
                "non_technical_skills": skills['non_technical'],
                "education": safe_extract(data, 'education', []),
                "work_experience": safe_extract(data, 'work_experience', []),
                "certifications": safe_extract(data, 'certifications', []),
                "languages": safe_extract(data, 'languages', []),
                "suggested_resume_category": safe_extract(data, 'suggested_resume_category', ''),
                "recommended_job_roles": safe_extract(data, 'recommended_job_roles', [])
            }

            # Save to Excel and add download link
            excel_path = save_to_excel(template_data)
            if excel_path:
                template_data["excel_download"] = excel_path

            return render_template('index.html', **template_data)

        return jsonify({"error": "Invalid file format"})
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse resume data"})
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
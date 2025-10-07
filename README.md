
---

## 🧩 Methodology

### 1️⃣ PDF Text Extraction
- The uploaded resume is processed using **PyPDF2** to extract text from all pages.

### 2️⃣ Resume Data Parsing (LLM)
- Extracted text is sent to the **Gemini 2.0 Flash** model.  
- The AI returns structured JSON data with specific resume attributes.

### 3️⃣ Data Cleaning
- The JSON response is validated using a custom `safe_extract()` function to avoid missing data issues.

### 4️⃣ Excel Generation
- Parsed data is stored into a **Pandas DataFrame**.  
- An Excel file is created with timestamped filenames.  
- The file is saved inside `static/exports/` and a **download link** is displayed.

---

## ⚡ Example Output (Excel Columns)

| Full Name | Contact Number | Email Address | Location | Technical Skills | Non-Technical Skills | Education | Work Experience | Certifications | Languages | Suggested Category | Recommended Roles |
|------------|----------------|----------------|-----------|------------------|----------------------|------------|-----------------|----------------|------------|---------------------|

---

## 🧱 Installation & Setup

### 1️⃣ Clone the Repository
git clone https://github.com/yourusername/AI-Resume-Parser.git
cd AI-Resume-Parser


### 2️⃣ Create and Activate Virtual Environment
python -m venv venv
venv\Scripts\activate     # For Windows
source venv/bin/activate  # For Mac/Linux

### 3️⃣ Install Dependencies
pip install -r requirements.txt

### 4️⃣ Add Google API Key
GOOGLE_API_KEY="your_api_key_here"


### 🚀 How to Run

Start the Flask application:

python app.py

Then open your browser and visit:

http://127.0.0.1:5000/

Upload any PDF resume to see the parsed output and Excel download link.


### 👤 Author

Saurabh Khodke
📧 saurabhkhodke999@gmail.com

### 📜 License

This project is licensed under the MIT License.
Feel free to use and modify for personal or professional purposes.

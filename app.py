import spacy
from flask import Flask, request, jsonify
import re

nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)
app.debug = True

def extract_experience(text):
    doc = nlp(text)
    experiences = []
    confidence = 0
    debug_info = []

    for sent in doc.sents:
        debug_info.append(f"Processing sentence: {sent}")
        sent_text = sent.text.lower()
        
        if "experience" in sent_text or "years" in sent_text:
            debug_info.append(f"Found 'experience' or 'years' in: {sent}")
            
            # Look for patterns like "X+ years" or "X years"
            year_matches = re.findall(r'(\d+\+?\s*(?:year|yr)s?)', sent_text)
            if year_matches:
                for match in year_matches:
                    experiences.append(match)
                    confidence = max(confidence, 0.9)
                    debug_info.append(f"Found year experience: {match}")
            
            # Look for specific experience levels
            levels = ["entry", "junior", "mid", "senior", "expert"]
            for level in levels:
                if level in sent_text:
                    experiences.append(f"{level.capitalize()}-level")
                    confidence = max(confidence, 0.8)
                    debug_info.append(f"Found experience level: {level}-level")
            
            # Look for general experience mentions
            if "experience" in sent_text and not experiences:
                experiences.append("Experience mentioned (details not specified)")
                confidence = max(confidence, 0.6)
                debug_info.append("Found general experience mention")

    if not experiences:
        debug_info.append("No experiences found")
        return "Not specified", 0, debug_info
    
    return ", ".join(experiences), confidence, debug_info

@app.route('/extract_experience', methods=['POST'])
def extract_experience_api():
    data = request.json
    text = data['text']
    print(f"Received text: {text[:100]}...")  # Print first 100 characters of the text
    experience, confidence, debug_info = extract_experience(text)
    return jsonify({
        "experience": experience, 
        "confidence": confidence,
        "debug_info": debug_info
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
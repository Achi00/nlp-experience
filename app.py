import spacy
from flask import Flask, request, jsonify
import re

nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)
app.debug = True

def extract_experience_and_knowledge(text):
    doc = nlp(text)
    experiences = []
    knowledge = []
    confidence = 0
    debug_info = []

    for sent in doc.sents:
        debug_info.append(f"Processing sentence: {sent}")
        sent_text = sent.text.lower()
        
        # Patterns for experience
        exp_patterns = [
            (r'((?:\d+\+?\s*(?:year|yr)s?(?:\s+of)?\s+)?experience\s+(?:with|in|of)?\s+[\w\s,]+(?:and|or)?\s[\w\s,]+)', 0.9),
            (r'(prior experience\s+[\w\s,]+)', 0.8),
            (r'((senior|junior|entry[\s-]level|mid[\s-]level).*experience)', 0.8),
            (r'(hands-on experience\s+[\w\s,]+)', 0.8),
            (r'([\w\s,]+ experience (?:required|preferred|essential|mandatory))', 0.7),
        ]
        
        # Patterns for knowledge
        know_patterns = [
            (r'((solid|strong|extensive) knowledge (?:of|in)\s+[\w\s,]+)', 0.8),
            (r'(knowledge (?:of|in)\s+[\w\s,]+)', 0.7),
            (r'(familiarity (?:with|in)\s+[\w\s,]+)', 0.7),
            (r'(understanding (?:of|in)\s+[\w\s,]+)', 0.7),
            (r'(proficiency (?:with|in)\s+[\w\s,]+)', 0.8),
        ]
        
        def process_matches(patterns, category):
            for pattern, conf in patterns:
                matches = re.findall(pattern, sent_text)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]  # Take the full match
                    item = match.strip()
                    if item and len(item) > 10:  # Avoid very short matches
                        if category == 'experience':
                            experiences.append(item)
                        else:
                            knowledge.append(item)
                        nonlocal confidence
                        confidence = max(confidence, conf)
                        debug_info.append(f"Found {category}: {item}")
        
        process_matches(exp_patterns, 'experience')
        process_matches(know_patterns, 'knowledge')
        
        # Catch-all for sentences mentioning experience or knowledge
        if ('experience' in sent_text or 'knowledge' in sent_text) and \
           not any(exp in sent_text for exp in experiences) and \
           not any(know in sent_text for know in knowledge):
            if 'experience' in sent_text:
                experiences.append(sent.text.strip())
            else:
                knowledge.append(sent.text.strip())
            confidence = max(confidence, 0.5)
            debug_info.append(f"Caught general mention: {sent.text.strip()}")

    if not experiences and not knowledge:
        debug_info.append("No experiences or knowledge found")
        return [], [], 0, debug_info
    
    return experiences, knowledge, confidence, debug_info

@app.route('/extract_experience', methods=['POST'])
def extract_experience_api():
    data = request.json
    text = data['text']
    print(f"Received text: {text[:100]}...")  # Print first 100 characters of the text
    experiences, knowledge, confidence, debug_info = extract_experience_and_knowledge(text)
    return jsonify({
        "experiences": experiences,
        "knowledge": knowledge,
        "confidence": confidence,
        "debug_info": debug_info
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template, request, jsonify
import random
import re
from itertools import permutations

app = Flask(__name__)

def clean_text(text):
    """ Remove bullet points, numbers, and special symbols from input text """
    lines = text.split("\n")
    # Improved cleaning: remove bullets, numbers, and normalize whitespace
    cleaned_lines = []
    for line in lines:
        if line.strip():
            # Remove bullet points, numbers at start, and other common list markers
            cleaned = re.sub(r"^[\s•\-\*\d\.\)]+", "", line)
            # Remove common starting phrases to help with deduplication
            cleaned = re.sub(r"^(responsible for|accountable for|manages|oversees|handles)\s+", "", 
                           cleaned, flags=re.IGNORECASE)
            # Normalize whitespace and lowercase for better comparison
            cleaned = " ".join(cleaned.lower().split())
            if cleaned:
                cleaned_lines.append(cleaned)
    return cleaned_lines

def normalize_line(line):
    """Normalize a line for comparison by removing common variations"""
    # Remove punctuation and convert to lowercase
    normalized = re.sub(r'[^\w\s]', '', line.lower())
    # Remove common business words that don't change meaning
    common_words = ['the', 'and', 'or', 'to', 'for', 'in', 'of', 'with']
    normalized = ' '.join(word for word in normalized.split() 
                         if word not in common_words)
    return normalized

def is_similar(line1, line2, similarity_threshold=0.8):
    """Check if two lines are similar based on word overlap"""
    words1 = set(normalize_line(line1).split())
    words2 = set(normalize_line(line2).split())
    
    if not words1 or not words2:
        return False
        
    overlap = len(words1.intersection(words2))
    similarity = overlap / max(len(words1), len(words2))
    return similarity >= similarity_threshold

def paraphrase_line(line):
    """Generate variations of a line using common business terms and structures"""
    starters = [
        "Responsible for", "Accountable for", "Manages", "Oversees",
        "Handles", "Coordinates", "Leads", "Ensures", "Facilitates",
        "Drives", "Develops", "Implements", "Maintains", "Supports"
    ]
    
    connectors = [
        "including", "through", "by", "via", "while",
        "and", "with focus on", "to achieve", "to ensure"
    ]
    
    # Generate variation
    if random.random() < 0.7:  # 70% chance to modify the line
        starter = random.choice(starters)
        if random.random() < 0.3 and "," in line:  # 30% chance to add connector if line has comma
            parts = line.split(",", 1)
            connector = random.choice(connectors)
            return f"{starter} {parts[0]} {connector} {parts[1]}"
        return f"{starter} {line}"
    
    return line.capitalize()

def remove_duplicates(lines):
    """Remove similar or duplicate lines from a list"""
    unique_lines = []
    for line in lines:
        # Check if this line is similar to any existing unique line
        if not any(is_similar(line, existing) for existing in unique_lines):
            unique_lines.append(line)
    return unique_lines

def generate_variations(responsibilities, job_description, num_outputs=3):
    """Generate multiple variations of shuffled and paraphrased outputs"""
    # Clean and combine inputs
    cleaned_responsibilities = clean_text(responsibilities)
    cleaned_job_description = clean_text(job_description)
    combined_list = cleaned_responsibilities + cleaned_job_description
    
    # Remove duplicates from combined list
    unique_list = remove_duplicates(combined_list)
    variations = []
    
    # Generate specified number of variations
    for _ in range(num_outputs):
        # Shuffle the list
        shuffled_list = unique_list.copy()
        random.shuffle(shuffled_list)
        
        # Paraphrase each line
        paraphrased = [paraphrase_line(line) for line in shuffled_list]
        
        # Add bullet points and join
        formatted = "\n".join([f"• {line}" for line in paraphrased])
        variations.append(formatted)
    
    return variations

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shuffle", methods=["POST"])
def shuffle():
    data = request.json
    responsibilities = data.get("responsibilities", "")
    job_description = data.get("job_description", "")
    num_outputs = data.get("num_outputs", 3)  # Default to 3 variations
    
    # Limit the number of outputs to prevent excessive processing
    num_outputs = min(max(1, num_outputs), 5)
    
    variations = generate_variations(responsibilities, job_description, num_outputs)
    
    return jsonify({
        "variations": variations,
        "num_outputs": num_outputs
    })

if __name__ == "__main__":
    app.run(debug=True)
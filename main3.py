import json
import os
import random
from collections import Counter
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Load data from the file if it exists, else initialize an empty data structure
def load_data(data_file):
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error loading JSON data. Initializing empty data.")
            return {"previous_queries": [], "known_terms": []}
    else:
        return {"previous_queries": [], "known_terms": []}

# Load vulgar words dataset
def load_vulgar_words(vulgar_file):
    if os.path.exists(vulgar_file):
        try:
            with open(vulgar_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error loading vulgar words data.")
            return []
    else:
        return []

# Check if the query contains any vulgar words
def contains_vulgar_word(query, vulgar_words):
    query_words = query.split()
    return any(word.lower() in vulgar_words for word in query_words)

# Update the data with new user queries
def update_data(data, user_query):
    try:
        data["previous_queries"].append(user_query)

        # Split user query into words and add them to known terms
        words = user_query.split()
        data["known_terms"].extend(words)

        # Remove duplicates while preserving order
        data["previous_queries"] = list(dict.fromkeys(data["previous_queries"]))
        data["known_terms"] = list(dict.fromkeys(data["known_terms"]))

    except Exception as e:
        print(f"Error updating data: {e}")
    return data

# Suggest queries based on previous inputs and known terms
def suggest_queries(data, current_query):
    try:
        suggestions = []
        all_terms = data["previous_queries"] + data["known_terms"]

        # Count frequency of terms for suggestion prioritization
        term_freq = Counter(all_terms)

        # Generate suggestions by matching the current query
        for term in all_terms:
            if term.lower().startswith(current_query.lower()):
                suggestions.append(term)

        # Sort suggestions based on frequency (most frequent first)
        suggestions.sort(key=lambda x: term_freq.get(x, 0), reverse=True)

        # Return unique suggestions
        return list(dict.fromkeys(suggestions))
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return []

# Save the updated data back to the file
def save_data(data, data_file):
    try:
        with open(data_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving data: {e}")

# Home route serving the HTML
@app.route('/')
def home():
    return render_template('index3.html')

# Autocomplete endpoint
@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    try:
        data_file = "autocomplete_data.json"
        vulgar_file = "vulgar_words.json"

        # Load existing data and vulgar words
        data = load_data(data_file)
        vulgar_words = load_vulgar_words(vulgar_file)

        # Get the current user query from the request
        user_query = request.json.get('query', '')

        if not user_query:
            return jsonify({'suggestions': [], 'message': ''})

        # Check for vulgar words
        if contains_vulgar_word(user_query, vulgar_words):
            return jsonify({'suggestions': [], 'message': 'Hey, what are you doing? Watch your language!'})

        # Get suggestions based on current query
        suggestions = suggest_queries(data, user_query)

        # Update data with the current query
        data = update_data(data, user_query)

        # Save the updated data
        save_data(data, data_file)

        # Return the suggestions and a learned message
        return jsonify({'suggestions': suggestions, 'message': f'Word "{user_query}" has been learned!'})

    except Exception as e:
        print(f"Error in autocomplete endpoint: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

# Run the app
if __name__ == "__main__":
    port = random.randint(1024, 65535)  # Random port between 1024 and 65535
    print(f"Running on port {port}")
    app.run(debug=True, port=port)

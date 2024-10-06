import re
from nltk.corpus import stopwords

# Ensure you download NLTK stopwords data (run this once)
# import nltk
# nltk.download('stopwords')

'''Preprocess Text Files: -

For .txt files, preprocessing may include:
    1) Removing stop words.
    2) Tokenization.
    3) Converting to lowercase.
    4) Removing special characters.'''


def preprocess_text(file_path, agent_id):
    with open(file_path, 'r') as f:
        content = f.read()

    # Convert to lowercase
    content = content.lower()

    # Remove special characters
    content = re.sub(r'\W+', ' ', content)

    # Tokenization and stop words removal
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in content.split() if word not in stop_words]

    # Return processed content as a single string (can also return list of tokens)
    processed_content = ' '.join(tokens)

    # Add agent-specific data alterations (e.g., watermark or ID)
    # Example: Appending agent ID to the processed text
    processed_content += f"\n\n[Processed by Agent: {agent_id}]"

    # Optionally save the processed content
    processed_file_path = file_path.replace('.txt', '_processed.txt')
    with open(processed_file_path, 'w') as f:
        f.write(processed_content)

    return processed_file_path  # Return path to processed file

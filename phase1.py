import string

def remove_punctuation(text):
    """Remove punctuation from the given text."""
    return text.translate(str.maketrans('', '', string.punctuation))

def to_lowercase(text):
    """Convert all characters in the text to lowercase."""
    return text.lower()

def remove_stopwords(text, stopwords):
    """Remove common stopwords from the text."""
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)

def remove_numbers(text):
    """Remove numbers from the text."""
    return ''.join([char for char in text if not char.isdigit()])

def strip_whitespace(text):
    """Remove leading and trailing whitespace from the text."""
    return text.strip()

def clean_text(text, stopwords):
    """Perform a series of text cleaning operations."""
    text = remove_punctuation(text)
    text = to_lowercase(text)
    text = remove_stopwords(text, stopwords)
    text = remove_numbers(text)
    text = strip_whitespace(text)
    return text

# Example usage
if __name__ == "__main__":
    sample_text = "Hello, World! This is a test message with numbers 12345."
    stopwords = {"is", "a", "with"}
    cleaned_text = clean_text(sample_text, stopwords)
    print("Cleaned Text:", cleaned_text)
    # Output: "hello world test message numbers"
    # The cleaned text is now ready for further processing, such as tokenization or vectorization.
import spacy

def calculate_similarity(sentence, keyword):
    # Load the spaCy model
    nlp = spacy.load("en_core_web_md")
    # Calculate the similarity between the sentence and the keyword
    similarity = nlp(sentence).similarity(nlp(keyword))
    return similarity




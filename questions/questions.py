import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.splitext(file_path)[1]==".txt":
            with open(file_path, 'r') as f:
                files[file]=f.read().replace("\n", "") #" ".join(f.readlines()).replace("\n", "")
    
    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = nltk.word_tokenize(document.lower())
    return [
        # Filter out words that are punctuation(s) or stopwords
        word for word in words if not all(char in string.punctuation for char in word) and\
            word not in nltk.corpus.stopwords.words("english")
    ]


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = dict()
    words = set()
    for filename in documents:
        words.update(documents[filename])
    for word in words:
        freq = sum(word in documents[filename] for filename in documents)
        idf = math.log(len(documents)/freq)
        idfs[word]=idf
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    #tfs = {fname:(word, files[fname].count(word)) for fname in files for word in query}
    tfidfs = {}
    for file in files:
        tfidfs[file]=[]
        for word in query:
            tf=files[file].count(word)
            tfidfs[file].append((word, tf*idfs[word]))
    #print(tfidfs)

    file_tfidfs = [(fname,sum(v[1] for v in tfidfs[fname])) for fname in tfidfs]
    #print(file_tfidfs)
    return [elem[0] for elem in sorted(file_tfidfs, key=lambda t:t[1], reverse=True)][:n]



def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    rank = []
    for sentence in sentences:
        sentence_values = [sentence, 0, 0]
        for word in query:
            if word in sentences[sentence]:
                sentence_values[1] += idfs[word]
                sentence_values[2] += (sentences[sentence].count(word)/len(sentences[sentence]))
        
        rank.append(sentence_values)
    
    return [sentence for sentence, mwm, qtd in\
        sorted(rank, key=lambda elem: (elem[1], elem[2]), reverse=True)
        ][:n]



if __name__ == "__main__":
    main()

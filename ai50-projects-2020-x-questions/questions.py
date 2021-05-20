import codecs
import math
import os
import string
import sys
import re

import nltk

from collections import Counter

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
    # get the list of files in the category
    corpList = {}
    for root, dirs, files in os.walk(directory):
        # iterate through the files in the category
        for aFile in files:
            currFile = os.path.join(directory, aFile)
            print("Reading '" + currFile + "' file into the dictionary")
            # regular file read gave me decoding error, so i used utf8 reading
            with codecs.open(currFile, 'r', encoding='utf8') as f:
                textData = f.read()

            corpList[aFile] = textData

    return corpList


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    wl2 = []
    # get the lower words
    wl1 = nltk.word_tokenize(document.lower())
    # Go through all the words
    for word in wl1:
        # check if word contains any alpha character
        if (word not in string.punctuation) and (word not in nltk.corpus.stopwords.words("english")):
            wl2.append(word)
    return wl2


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # IDF = the natural logarithm of the number of documents divided by the number of documents in which the word appears.
    idfDict = {}

    # prepare a unique word list
    wl = []
    for doc in documents:
        for word in documents[doc]:
            if word not in wl:
                wl.append(word)

    # print('Total ',len(wl),' words to process')
    # for each unique word, calc the idf
    for word in wl:
        docCount = 0

        # if word in doc (at least once), increase the counter
        for doc in documents:
            if word in documents[doc]:
                docCount += 1

        # calc the idf (doc count / instance count)
        idfDict[word] = math.log(float(len(documents)) / float(docCount))

    return idfDict


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # initialize values
    tfIDFlist = {}

    # for each file, find the tf-idf value of the query, by summing the tf-idf of each word (tokenized word) of the query
    for file in files:
        # reset query tf-idf
        queryTFidf = 0
        for word in query:
            if word in files[file]:
                # user Counter (imported from collection) to count the occurrence of a word in a file
                fileWordCounter = Counter(files[file])
                # TF(t) = (Number of times term t appears in a document) / (Total number of terms in the document).
                tf = float(fileWordCounter[word]) / float(len(files[file]))
                # tf-idf = tf * idf
                tfIDF = tf * idfs[word]

                # add word tf-idf to query tf-idf of the file
                queryTFidf += tfIDF
        # add query tf-idf of the file to the list of query tf-idfs
        tfIDFlist.update({file: queryTFidf})

    # sort the list of query tf-idfs of files, according to the tf-idf score, in a descending order
    tfIDFlistSorted = {k: v for k, v in sorted(tfIDFlist.items(), key=lambda item: item[1], reverse=True)}

    # create a list of file names only, according to the tf-idf score of the query in that file
    # list will be N size
    topList = []
    for i in range(0, n):
        if i < len(tfIDFlistSorted):
            topList.append(list(tfIDFlistSorted)[i])

    return topList


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentenceIDFList = {}
    # for each sentence, find the idf value of the query, by summing the idf of each word (tokenized word) of the query
    for sentence in sentences:
        # reset query idf
        queryIDF = 0.0
        for word in query:
            if word in sentences[sentence]:
                # add word idf to query idf of the sentence
                queryIDF += idfs[word]
        # add query idf of the sentence to the list of query idfs
        sentenceIDFList.update({sentence: queryIDF})

    # sort the list of query idfs of sentences, according to the idf score, in a descending order
    sentenceIDFListSorted = {k: v for k, v in sorted(sentenceIDFList.items(), key=lambda item: item[1], reverse=True)}

    # create a list of N+1 sentences and IDF scores (so we can compare the idf values)
    topSentenceList = []
    topSentenceIDFList = []
    for i in range(0, n + 1):
        if i < len(sentenceIDFListSorted):
            item = list(sentenceIDFListSorted)[i]
            topSentenceList.append(item)
            topSentenceIDFList.append(sentenceIDFListSorted[item])

    # check the idf values for every 2 sentences in the sorted list
    # if idf values are the same, compare the term density of those 2 sentences
    # and if needed, replace they're order
    for i in range(0, n):
        # check the
        if topSentenceIDFList[i] == topSentenceIDFList[i + 1]:
            compareStatus = compareTermDensity(topSentenceList[i], topSentenceList[i + 1], query)

            # if second sentence has better density we need to act
            # if first sentence densitiy is better or they have equal density, do nothing
            if compareStatus == 1:
                # replace the sentence order (no need to replace the idf values, since they are the same....)
                tempVal = topSentenceList[i + 1]
                topSentenceList[i + 1] = topSentenceList[i]
                topSentenceList[i] = tempVal

    # finally, take only the top N values from the fixed sentences list
    finalTopList = []
    for i in range(0, n):
        finalTopList.append(topSentenceList[i])

    return finalTopList


def compareTermDensity(sentence1, sentence2, query):
    # set initial values
    wl1 = tokenize(sentence1)
    wl2 = tokenize(sentence2)
    wl1Counter = Counter(wl1)
    wl2Counter = Counter(wl2)
    S1WordCount = len(wl1)
    S2WordCount = len(wl2)

    # count the total frequency of query terms in sentence 1 and 2
    S1QueryWordCount = 0
    S2QueryWordCount = 0
    for word in query:
        S1QueryWordCount += wl1Counter[word]
        S2QueryWordCount += wl2Counter[word]

    # Query term density is defined as the proportion of words in the sentence that are also words in the query. For
    firstTD = float(S1QueryWordCount) / S1WordCount
    SecondTD = float(S2QueryWordCount) / S2WordCount

    # return compare result (-1 = first sentence denser, 1=second senctence desnser, 0 = density equal)
    if firstTD > SecondTD:
        return -1
    elif firstTD < SecondTD:
        return 1
    else:
        return 0


if __name__ == "__main__":
    main()

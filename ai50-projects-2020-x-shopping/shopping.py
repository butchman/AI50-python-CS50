import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    with open(filename, newline='') as csvfile:
        rows = list(csv.DictReader(csvfile))
        cnt = 1
        for row in rows:

            # Administrative, Informational, ProductRelated, Month, OperatingSystems, Browser, Region, TrafficType, VisitorType, and Weekend
            # should all be of type int (weekend is boolean, must be here by mistake...)
            row['Administrative'] = int(row['Administrative'])
            row['Informational'] = int(row['Informational'])
            row['ProductRelated'] = int(row['ProductRelated'])
            row['OperatingSystems'] = int(row['OperatingSystems'])
            row['Browser'] = int(row['Browser'])
            row['Region'] = int(row['Region'])
            row['TrafficType'] = int(row['TrafficType'])

            # Administrative_Duration, Informational_Duration, ProductRelated_Duration, BounceRates, ExitRates, PageValues, and SpecialDay
            # should all be of type float.
            row['Administrative_Duration'] = float(row['Administrative_Duration'])
            row['Informational_Duration'] = float(row['Informational_Duration'])
            row['ProductRelated_Duration'] = float(row['ProductRelated_Duration'])
            row['BounceRates'] = float(row['BounceRates'])
            row['ExitRates'] = float(row['ExitRates'])
            row['PageValues'] = float(row['PageValues'])
            row['SpecialDay'] = float(row['SpecialDay'])

            # handle month name -> num
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            try:
                row['Month'] = months.index(row['Month'])
            except:
                row['Month'] = -1

            # convert VisitorType to a number
            if row['VisitorType'] == 'Returning_Visitor':
                row['VisitorType'] = 1
            else:
                row['VisitorType'] = 0

            # convert Weekend to a number
            if row['Weekend'] == 'TRUE':
                row['Weekend'] = 1
            else:
                row['Weekend'] = 0

            # get the Label
            rowLabel = 0
            if row['Revenue'] == 'TRUE':
                rowLabel = 1

            # create a list from row values
            currValues = list(row.values())
            # and remove the last list item (which is the label)
            del(currValues[-1])

            evidence.append(currValues)
            labels.append(rowLabel)

    """
    the value of the first evidence list should be
    [0, 0.0, 0, 0.0, 1, 0.0, 0.2, 0.2, 0.0, 0.0, 1, 1, 1, 1, 1, 1, 0] 
    
    the value of the first label should be 0.
    
    print(evidence[0])
    print(labels[0])    
    [0, 0.0, 0, 0.0, 1, 0.0, 0.2, 0.2, 0.0, 0.0, 1, 1, 1, 1, 1, 1, 0]
    0
    
    """
    return evidence, labels

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    """
    return a scikit-learn nearest-neighbor classifier - a k-nearest-neighbor classifier where k = 1
    You’ll want to use a KNeighborsClassifier in this function.
    """

    modelClassifier = KNeighborsClassifier(n_neighbors = 1)
    modelClassifier.fit(evidence, labels)

    return modelClassifier


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    TPLbl = 0
    TPPred = 0
    TNLbl = 0
    TNPred = 0

    # go through the labels
    for i in range(len(labels)):
        if labels[i] == 1: # positive label
            TPLbl += 1
            TPPred += predictions[i]
        else: # negative label
            TNLbl += 1
            TNPred += 1 - predictions[i]

    #calc sensitivity & specificity
    sensitivity = TPPred / TPLbl
    specificity = TNPred / TNLbl

    #print(sensitivity, specificity)

    return sensitivity, specificity

if __name__ == "__main__":
    main()

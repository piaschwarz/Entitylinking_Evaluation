import csv

# https://iamirmasoud.com/2022/06/19/understanding-micro-macro-and-weighted-averages-for-scikit-learn-metrics-in-multi-class-classification-with-example/
# https://hipe-eval.github.io/HIPE-2022/tasks
# https://github.com/hipe-eval/HIPE-scorer
# file:///C:/Users/Schwarz/Downloads/HIPE2022-ParticipationGuidelines-v1.0-1.pdf


# HIPE 2022 Shared Task Participation Guidelines (https://zenodo.org/records/6045662)
# Micro average P, R, F1 at entity level (not at token level), i.e. consideration of all true positives, false positives, true negatives and false negatives over all documents.
# - strict (exact boundary matching) and fuzzy (at least 1 token overlap) => evaluation here follows the fuzzy regime!

# HIPE-scorer (https://github.com/hipe-eval/HIPE-scorer/blob/master/hipe_evaluation/ner_eval.py#L395)
#  Scenario I  : exact match of both type and boundaries (TP).
#  Scenario II : spurious entity (insertion, FP).
#  Scenario III: missed entity (deletion, FN).
#  Scenario IV : type substitution (counted as both FP and FN in fuzzy regime).
#  Scenario V  : span substitution (overlap) offsets do not match exactly and entity type is the same (counted as TP in fuzzy regime).


if __name__ == '__main__':

    #file_to_evaluate = "data/HIPE-data-v1.4-test_de_OPENTAPIOCA_final.tsv"
    #file_to_evaluate = "data/HIPE-data-v1.4-test_de_SPACYFISHING_final.tsv"
    file_to_evaluate = "data/HIPE-data-v1.4-test_de_DBPEDIASPOTLIGHT_final.tsv"

    TP = 0
    FP = 0
    FN = 0

    with open(file_to_evaluate, encoding='utf-8') as f:
        tsv_reader = csv.reader(f, delimiter='\t')
        header = next(tsv_reader, None)  # skip the headers

        prev_tokens = []  # parse IOB tagged tokens that form words in lists
        prev_token_ids_actual = []
        prev_token_ids_predicted = []

        for line in tsv_reader:
            if len(line) > 0 and '#' not in line[0]:
                token = line[0]
                iob = line[1].split('-')[0]
                id_actual = line[7]  # column NEL-LIT
                id_pred = line[10]
                if iob == 'B' or iob == 'I':
                    prev_tokens.append(token)
                    prev_token_ids_actual.append(id_actual)
                    prev_token_ids_predicted.append(id_pred)
                else:
                    # print('Previous: ', prev_tokens, prev_token_ids_actual, prev_token_ids_predicted)

                    # EVALUATE SINGLE TOKEN WORDS (O)
                    #  Scenario II : spurious entity (insertion, FP)
                    if id_pred != '_':
                        FP += 1

                    # EVALUATE MULTI-TOKEN WORDS (B, I)
                    any_qid_exists_in_predicted = False
                    any_qid_exists_in_actual = False
                    if any(item.startswith('Q') for item in prev_token_ids_predicted):
                        any_qid_exists_in_predicted = True
                    if any(item.startswith('Q') for item in prev_token_ids_actual):
                        any_qid_exists_in_actual = True

                    # Scenario I  : exact match of both type and boundaries (TP),
                    # e.g:  prev_tokens = ['Schweizerische', 'Eidgenossenschaft']
                    #   prev_ids_actual = ['Q39', 'Q39']
                    #   prev_ids_predicted = ['Q39', 'Q39']
                    if any_qid_exists_in_actual and prev_token_ids_predicted == prev_token_ids_actual:
                        TP += 1

                    # Scenario V  : span substitution (overlap) offsets do not match exactly and entity type is the same (counted as TP in fuzzy regime)
                    if bool(set(prev_token_ids_predicted) & set(prev_token_ids_actual)):  # list has overlap
                        TP += 1
                    else:  # no list overlap
                        # Scenario IV: Substitution type, offsets match, but entity type is wrong (both words have a Q-id but it differs), counted as both FP and FN in fuzzy regime
                        if any_qid_exists_in_predicted and any_qid_exists_in_actual:
                            FP += 1
                            FN += 1

                        #  Scenario II : spurious entity (insertion, FP)
                        if any_qid_exists_in_predicted and not any_qid_exists_in_actual:
                            FP += 1

                        #  Scenario III: missed entity (deletion, FN)
                        if any_qid_exists_in_actual and not any_qid_exists_in_predicted:
                            FN += 1

                    # reset lists as tokens indicate that new
                    prev_tokens = []
                    prev_token_ids_actual = []
                    prev_token_ids_predicted = []

    print('TP: ', TP)
    print('FP: ', FP)
    print('FN: ', FN)
    # Precision: Of all the positive predictions, how many of them are truly positive?
    precision = TP / (TP + FP)
    # Recall: Of all the actual positive examples out there, how many of them were correctly predicted to be positive?
    recall = TP / (TP + FN)
    F1 = ( 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0 )

    print('Precision: ', precision)
    print('Recall: ', recall)
    print('F1: ', F1)
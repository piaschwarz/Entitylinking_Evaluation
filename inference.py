# Docs on how to use Spacyfishing: https://github.com/Lucaterre/spacyfishing
# Overlap of DBpedia and Wikidata: https://meta.wikimedia.org/wiki/Wikidata/Notes/DBpedia_and_Wikidata
# HIPE-data-v1.4-test-de.tsv => changed " to “ (due to erroneous parsing)

import os.path
import csv
import spacy
from SPARQLWrapper import SPARQLWrapper, JSON


def sparql_query(entity_dbp):
    """
    Queries Sparql endpoint http://de.dbpedia.org/sparql with entity URI and returns corresponding (relation sameAs)
    Wikidata Q-item if available, else returns None
    :param entity_dbp: the entity uri to query for, e.g: "http://de.dbpedia.org/resource/Christian_Drosten"
    :return: Q-item of Wikidata as string
    """
    sparql = SPARQLWrapper("http://de.dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery("""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>

            SELECT *
            WHERE {
                <%s> owl:sameAs ?wikidata_uri .
                FILTER(regex(str(?wikidata_uri), "www.wikidata.org/entity"))
            }
            """ % entity_dbp  # e.g. entity_dbp = "http://de.dbpedia.org/resource/Majestät"
    )

    q_item_final = ""

    try:
        ret = sparql.queryAndConvert()
        if len(ret["results"]["bindings"]) > 0:
            for r in ret["results"]["bindings"]:
                q_item = r['wikidata_uri']['value']
                q_item_final = q_item.split('/')[-1]
                print('SPARQL Q-ID: ', q_item_final, 'Wikidata URI: ', q_item)
        else:
            q_item_final = None
    except Exception as e:
        print(e)

    return q_item_final


def print_processed_lines_to_file(filename, header_extension, segment_lines):
    """
    Takes a list of lists and prints them to tsv file in the same format as the input data (but now with one additional
    column containing the model's prediction
    :param filename: name for the tsv file to be written
    :param header_extension: name for the new column
    :param segment_lines: list of lists with the individual lines to be appended to file,
                          except for first line containig nine items and no nexted lists
    """
    # test if tsv file already exists, if not create one
    if os.path.isfile(filename):
        with open(filename, 'a', encoding='utf-8') as f:
            tsv_writer = csv.writer(f, delimiter='\t', lineterminator='\n')
            for seg_line in segment_lines:
                tsv_writer.writerow(seg_line)

    else:  # create file and add header line including the new column with name header_extension
        segment_lines.append(header_extension)
        with open(filename, 'w', encoding='utf-8') as f:
            tsv_writer = csv.writer(f, delimiter='\t', lineterminator='\n')
            tsv_writer.writerow(segment_lines)


if __name__ == '__main__':
    nlp_spacy = spacy.load('de_core_news_lg')

    nlp_spacy.add_pipe('opentapioca', config={"url": "https://opentapioca.wordlift.io/api/annotate?lc=de"})
    # nlp_spacy.add_pipe("entityfishing", config={"language": "de", "extra_info": True, "filter_statements": ['P214', 'P227']})
    # nlp_spacy.add_pipe("dbpedia_spotlight", config={"language_code": "de"})

    with open("data/HIPE-data-v1.4-test-de.tsv", "rb") as f:
        num_lines = sum(1 for _ in f)

    with open("data/HIPE-data-v1.4-test-de.tsv", encoding='utf-8') as f:
        tsv_reader = csv.reader(f, delimiter='\t')

        segment = ''
        document = ''
        documents_all = []
        segment_lines = []
        header = next(tsv_reader, None)  # skip the headers
        print_processed_lines_to_file('data/HIPE-data-v1.4-test_de_OPENTAPIOCA_final.tsv', 'EL_OPENTAPIOCA', header)
        counter = 1  # read already one line

        for line in tsv_reader:
            counter += 1
            segment_lines.append(line)
            if len(line) > 0 and '#' not in line[0]:
                if "PySBDSegment" not in line[9]:
                    if "NoSpaceAfter" in line[9]:
                        segment += line[0]
                    else:
                        segment += (line[0] + ' ')
                else:
                    segment.strip()
                    segment = segment + line[0]
                    segment = segment.replace('¬ ', '')
                    document += (' ' + segment)
                    print("SEGMENT: ", segment)

                    doc = nlp_spacy(segment)

                    # print('\nDBpedia Spotlight on model: de_core_news_lg')
                    # for ent_span in doc.ents:
                    #    # print((ent_span.start_char, ent_span.end_char, ent_span.text, ent_span.kb_id_, ent_span.label_, ent_span._.dbpedia_raw_result))
                    #    token_text = ent_span.text
                    #    wikidata_qid = sparql_query(ent_span.kb_id_)
                    #    print('ent_span.kb_id_: ', ent_span.kb_id_)
                    #    if wikidata_qid is None and len(ent_span.kb_id_) > 0:
                    #        wikidata_qid = "WIKIDATA-Q-ITEM-NOT-FOUND-FOR:"+ent_span.kb_id_

                    # print('Spacyfishing on model: de_core_news_lg')
                    # for ent in doc.ents:
                    #    if ent._.kb_qid:
                    #        # print((ent.text, ent.label_, ent._.kb_qid, ent._.url_wikidata, ent._.nerd_score, ent._.normal_term))
                    #        token_text = ent.text
                    #        wikidata_qid = ent._.kb_qid
                    #        print(token_text, wikidata_qid)

                    print('OpenTapioca on model: de_core_news_lg')
                    for span in doc.ents:  # Input spans which are too long cause http error 403
                        if span.kb_id_:
                            # print((span.text, span.kb_id_, span.label_, span._.description, span._.score))
                            token_text = span.text
                            wikidata_qid = span.kb_id_
                            print(token_text, wikidata_qid)

                            # add Q id as last item to segment line (segment line item l is a list: ['Gesandten', 'O', 'O', 'O', 'O', 'O', 'O', '_', '_', '_'] )
                            for l in segment_lines:
                                # split token_text into single words to append Q item to each line containing part of the token_text (e.g. Schweizerische Eidgenossenschaft)
                                for token_split in token_text.split(' '):
                                    if 0 < len(l) <= 10:
                                        if l[0] == token_split or l[0] in token_split:
                                            l.append(wikidata_qid)

                    for l in segment_lines:
                        if 0 < len(l) <= 10 and '#' not in l[0]:
                            l.append('_')
                    print("SEGMENT LINES FINAL: ", segment_lines)
                    print_processed_lines_to_file('data/HIPE-data-v1.4-test_de_OPENTAPIOCA_final.tsv', 'EL_OPENTAPIOCA', segment_lines)
                    segment = ''
                    segment_lines = []
                    print('--------------------')

            else:
                document = document.strip()
                if document != '':
                    documents_all.append(document)
                document = ''

            if counter == num_lines:
                document = document.strip()
                if document != '':
                    documents_all.append(document)


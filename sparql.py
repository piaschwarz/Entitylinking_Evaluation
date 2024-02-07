from SPARQLWrapper import SPARQLWrapper, JSON


def sparql_query(entity_dbp):
    """
    Queries Sparql endpoint http://de.dbpedia.org/sparql with entity URI and returns corresponding (relation sameAs)
    Wikidata Q-item if available, else returns None
    :param entity_dbp: the entity uri to query for, e.g: "http://de.dbpedia.org/resource/Christian_Drosten"
    :return: Q-item of Wikidata as string
    """
    sparql = SPARQLWrapper(
        "http://de.dbpedia.org/sparql"
    )
    sparql.setReturnFormat(JSON)
    # e.g. entity_dbp = "http://de.dbpedia.org/resource/Majestät"

    sparql.setQuery("""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>

            SELECT *
            WHERE {
                <%s> owl:sameAs ?wikidata_uri .
                FILTER(regex(str(?wikidata_uri), "www.wikidata.org/entity"))
            }
            """ % entity_dbp
    )

    try:
        ret = sparql.queryAndConvert()
        if len(ret["results"]["bindings"]) > 0:
            for r in ret["results"]["bindings"]:
                q_item = r['wikidata_uri']['value']
                return q_item.split('/')[-1]
        else:
            return None

    except Exception as e:
        print(e)


if __name__ == '__main__':
    q_id = sparql_query("http://de.dbpedia.org/resource/Majestät")
    print(q_id)


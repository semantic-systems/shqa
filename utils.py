import json
from SPARQLWrapper import SPARQLWrapper, JSON

def load_json_data(file_name):
    try:
        with open(file_name, 'r') as json_file:
            data = json.load(json_file)
        return data['data']
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return []


def write_to_json(result, out_file_path):
    with open(out_file_path, "w", encoding="utf-8") as f:
        json.dump({"data": result}, f, indent=4)

    print("Successfully written to file!")


def query_sparql_endpoint(endpoint_url, sparql_query, search_key, flag=False):
    sparql = SPARQLWrapper(endpoint_url)
    # cleaned_search_key = search_key.strip("<>").strip()
    if flag:
        sparql.setQuery(sparql_query % (search_key, search_key, search_key.strip("<>").strip()))
    else:
        sparql.setQuery(sparql_query % search_key)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return_result = []
    for result in results["results"]["bindings"]:
        converted_result = {}
        for key, value_info in result.items():
            value = value_info.get('value')
            if value:
                converted_result[key] = value
        return_result.append(converted_result)
    return return_result


def get_author_semoa_institute_info(institute_uri):
    sparql_endpoint = "https://semoa.skynet.coypu.org/sparql"
    institute_sparql = """PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX ns5: <https://dbpedia.org/property/>
            PREFIX soa: <https://semopenalex.org/ontology/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT *
            WHERE {
                  %s foaf:name ?institute_name ;
                    soa:worksCount ?publicationsCount ;
                    soa:citedByCount ?publicationsCitedByCount ;
                    soa:rorType ?institute_type ;
                    ns5:countryCode ?institute_country_code ;
                    rdfs:seeAlso ?wikipedia_url .
                  FILTER (CONTAINS(STR(?wikipedia_url), "en.wikipedia.org"))
             }
        """
    # sparql_query = institute_sparql % uri
    results = query_sparql_endpoint(sparql_endpoint, institute_sparql, institute_uri)
    institute_info = []
    if results:
        for result in results:
            institute_info.append({'name': result['institute_name'],
                                   'publicationsCount': result['publicationsCount'],
                                   'publicationsCitedByCount': result['publicationsCitedByCount'],
                                   'institute_type': result['institute_type'],
                                   'institute_country_code': result['institute_country_code'],
                                   'wikipedia_url': result['wikipedia_url']})
    return institute_info


def search_semoa(author_dblp_orcid):
    sparql_endpoint = "http://localhost:3030/sopena/sparql"
    orcid_query = """PREFIX ns2: <https://semopenalex.org/ontology/>
               PREFIX ns3: <http://purl.org/spar/bido/>
               PREFIX ns4: <https://dbpedia.org/ontology/>
               PREFIX ns5: <https://dbpedia.org/property/>

               SELECT * WHERE
               {
                 GRAPH <https://semopenalex.org/authors/context> {
                 {
                   OPTIONAL {?author_uri ns2:orcidId ?orcid . }
                   OPTIONAL {?author_uri ns3:orcidId ?orcid . }
                   OPTIONAL { ?author_uri ns4:orcidId ?orcid . }
                   OPTIONAL { ?author_uri ns5:orcidId ?orcid . }
                   FILTER (?orcid = "%s")
                 }
               }
               } 
           """
    author_semoa_detail_query = """PREFIX foaf: <http://xmlns.com/foaf/0.1/>
       PREFIX ns3: <http://purl.org/spar/bido/>
       PREFIX org: <http://www.w3.org/ns/org#>
       PREFIX soa: <https://semopenalex.org/ontology/>

       SELECT *
       WHERE {
         GRAPH <https://semopenalex.org/authors/context> {
           {
            %s foaf:name ?author_name ;
               soa:worksCount ?worksCount ;
               soa:citedByCount ?citedByCount ;                        
               ns3:h-index ?hIndex ;
               soa:i10Index ?i10Index ;
               soa:2YrMeanCitedness ?twoYearMeanCitedness .
           }
         }
       }
       """

    search_author_institute_sparql = """PREFIX foaf: <http://xmlns.com/foaf/0.1/>
       PREFIX org: <http://www.w3.org/ns/org#>
       SELECT ?institute_uri
       WHERE {
        GRAPH <https://semopenalex.org/authors/context> {
         {
           %s org:memberOf ?institute_uri .
           }
           }
        }
       """
    orcid_query_result = query_sparql_endpoint(sparql_endpoint, orcid_query, author_dblp_orcid)
    if orcid_query_result:
        author_semoa_uri = f"<{orcid_query_result[0]['author_uri']}>"
        author_semoa_detail_query_result = query_sparql_endpoint(sparql_endpoint, author_semoa_detail_query, author_semoa_uri)

        institute_uris = query_sparql_endpoint(sparql_endpoint, search_author_institute_sparql, author_semoa_uri)

        semoa_institute_info = []
        for institute in institute_uris:
            institute_uri = f"<{institute['institute_uri']}>"
            institute_results = get_author_semoa_institute_info(institute_uri)
            if institute_results:
                semoa_institute_info.append(institute_results[0])

        return {'author_semoa_uri': orcid_query_result[0]['author_uri'],
                'author_name': author_semoa_detail_query_result[0]['author_name'],
                "worksCount": author_semoa_detail_query_result[0]['worksCount'],
                "citedByCount": author_semoa_detail_query_result[0]['citedByCount'],
                "hIndex": author_semoa_detail_query_result[0]['hIndex'],
                "i10Index": author_semoa_detail_query_result[0]['i10Index'],
                "twoYearMeanCitedness": author_semoa_detail_query_result[0]['twoYearMeanCitedness'],
                "institute": semoa_institute_info,
                'semoa_orcid': orcid_query_result[0]['orcid']}
    # return orcid_query, author_semoa_detail_query, search_author_institute_sparql
    return None


def deduplicate_list(input_list):
    seen = set()
    output_list = []
    for item in input_list:
        if item not in seen:
            seen.add(item)
            output_list.append(item)
    return output_list


def run_sparql_query(sparql_endpoint, sparql_query, param='', flag=False):
    if flag:
        sparql_query = sparql_query % param
    try:
        sparql = SPARQLWrapper(sparql_endpoint)
        sparql.setQuery(sparql_query)
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        return result
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    return


def entity_linking(entity='', flag=True):
    sparql_end_point = "https://dblp-april24.skynet.coypu.org/sparql"
    if flag:
        entity = entity.rstrip("'")
        entity = entity.lstrip("'")
        entity = entity.rstrip('"')
        entity = entity.lstrip('"')
        if not entity.endswith('.'):
            entity += '.'
        query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
                    SELECT *
                      WHERE {
                      ?paper dblp:title "%s" .
                      ?author ^dblp:authoredBy ?paper ;
                              dblp:primaryCreatorName ?primarycreatorname ;
                              dblp:orcid ?orcid ;
                              dblp:wikipedia ?wikipedia .
                      FILTER (CONTAINS(STR(?wikipedia), "en.wikipedia.org"))
                    }"""
    else:
        query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
                    SELECT *
                      WHERE {
                      %s dblp:primaryCreatorName ?primarycreatorname ;
                         dblp:orcid ?orcid ;
                         dblp:wikipedia ?wikipedia .
                      FILTER (CONTAINS(STR(?wikipedia), "en.wikipedia.org"))
                    }"""

    sparql_result = run_sparql_query(sparql_end_point, query, entity, True)
    search_result = []
    if sparql_result:
        for result in sparql_result["results"]["bindings"]:
            temp = {}
            for key, value_info in result.items():
                temp[key] = value_info.get('value')
            search_result.append(temp)
    # print(search_result)
    return search_result
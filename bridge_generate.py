import llms
import utils
from urllib.parse import urlparse

def generate_assertion_statement(entity_encapsulating_phrase, entity, flag=False):
    prompt = f"""[INST]Task: Form a sentence by joining the given PHRASE and ANSWER. Be sure the sentence is grammatically and semantically correct.
            Only return the sentence.
            [/INST]
            PHRASE: {entity_encapsulating_phrase}
            ANSWER:{entity}

            sentence:
    """
    if flag:
        prompt = f"""[INST]Task: Replace part of the QUESTION using the given ANSWER and form a sentence. Be sure the sentence is grammatically and semantically correct.
            Only return the sentence.
            QUESTION: What is the primary language of instruction at the institution where Yves Moreau is affiliated?
            ANSWER: University of Leuven
            sentence: The institution where Yves Moreau affiliated is University of Leuven.
            QUESTION: When was the establishment year of the academic institution of Fang Liu?
            ANSWER: Notre Dame University
            sentence: The academic institution of Fang Liu is Notre Dame University.
            [/INST]
            QUESTION: {entity_encapsulating_phrase}
            ANSWER:{entity}

            sentence:
    """
    assertion_sentence = llms.chatgpt(prompt, 8)
    utils.write_to_json([assertion_sentence], "./assertion_sentence.json")
    assertion_sentence_formatted = utils.load_json_data("./assertion_sentence.json")
    if 'text' in assertion_sentence_formatted[0]:
        return assertion_sentence_formatted[0]['text']
    else:
        return ''


def generate_context(question, assertions, entity):
    prompt = f"""Task: Your task is generating a text about an entity. The text should include facts about the entity, that allow to answer questions like {question}'.

                TEXT:
        """
    new_prompt = f"""Task: Your task is generating a text about an entity. The text should include facts about the entity, that allow to answer questions like {question}'.
                      ASSERTIONS: {assertions}
                      ENTITY: {entity}

                      TEXT:
                """
    context = llms.chatgpt(new_prompt, 8)
    utils.write_to_json([context], "./generated_context.json")
    context_formatted = utils.load_json_data("./generated_context.json")
    if 'text' in context_formatted[0]:
        return context_formatted[0]['text']
    else:
        return ''


def answer_generation(question, assertion, context):
    prompt = f"""[INST]Task: Answer the given QUESTION using the CONTEXT. The ASSERTIONS will help you to resolve unknown information.
                 Only return the answer. No need of description.
                 Please provide your result in JSON format only.
                 [\INST]

                 QUESTION: {question}
                 ASSERTIONS: {assertion}
                 CONTEXT: {context}

                 ANSWER: 
                """
    answer = llms.chatgpt(prompt, 4)  # test_chatAI.test_chat_ai(prompt) # llms.chatgpt(prompt, 4)  #   #
    return answer


def identify_entity_encapsulating_phrase(question, q_type =''):
    example = ''
    prompt = f"""[INST]Task: Your task is extracting the entity encapsulating phrases and publication titles in a given QUESTION.
                Example:
                 {example}                    
                Do not add anything else.
                [/INST]          
                [{{entity_encapsulating_phrase: entity encapsulating phrase}},
                {{title: title}}
                ]
                [INST]
                Please provide your result in JSON format only. Please do not include the Example in your response.
                [/INST] 

                question: {question}

            """
    entity_encapsulating_phrase = llms.chatgpt(prompt, 5)
    utils.write_to_json(entity_encapsulating_phrase, "./entity_encapsulating_phrase.json")
    formatted_entity_encapsulating_phrase = utils.load_json_data("./entity_encapsulating_phrase.json")
    return formatted_entity_encapsulating_phrase


def identify_title(phrase):
    example = ''
    prompt = f"""Task: Your task is extracting a publication title from the given phrase. 
                    Example
                        {example}                    
                    Do not add anything else.
                    Please provide your result in JSON format only. Please do not include the Example in your response.

                    phrase: {phrase}
                """
    title = llms.chatgpt(prompt, 6)
    return title


def get_title(entity_phrase):
    title = ''
    if 'title' in entity_phrase:
        if isinstance(entity_phrase['title'], list):
            if len(entity_phrase['title']) > 0:
                title = entity_phrase['title'][0]
    else:
        title_dict = identify_title(entity_phrase['entity_encapsulating_phrase'][0])
        utils.write_to_json(title_dict, "title_updated.json")
        title_new = utils.load_json_data("title_updated.json")
        if 'title' in title_new:
            if len(title_new['title']) > 0:
                title = title_new['title'][0]
    return title


def entity_semoa_facts(semoa_record):
    records = []
    if 'institute' in semoa_record:
        for institute_info in semoa_record['institute']:
            records.append({'institute_name': institute_info['name'],
                            'wikipedia_uri': institute_info['wikipedia_url']})
    return records


def identify_next_hop(updated_question):
    example = ""
    prompt = f"""[INST]Task: Your task is extracting the entity encapsulating phrase in the QUESTION. 
                    Example:
                    {example}                    
                    Do not add anything else.
                    [/INST]          
                    [{{entity_encapsulating_phrase: entity encapsulating phrase}}]
                    [INST]
                    Please provide your result in JSON format only. Please do not include the Example in your response.
                    [/INST] 

                    question: {updated_question}

                """
    next_hop_phrase = llms.chatgpt(prompt, 7)
    utils.write_to_json([next_hop_phrase], "./next_hop_phrase.json")
    next_hop_phrase_formatted = utils.load_json_data("./next_hop_phrase.json")
    if 'entity_encapsulating_phrase' in next_hop_phrase_formatted[0]:
        return next_hop_phrase_formatted[0]['entity_encapsulating_phrase']
    else:
        return ''


def answer_kg_text_questions(question, q_type, author_dblp_uri, flag=False):
    entity_encapsulating_phrase = identify_entity_encapsulating_phrase(question, q_type)
    question_updating_process = [question]
    assertions = []
    context = ''
    kg_context = []
    updated_question = question
    if 'entity_encapsulating_phrase' in entity_encapsulating_phrase:
        entity_phrase = entity_encapsulating_phrase['entity_encapsulating_phrase'][0]
        title = get_title(entity_phrase)
        entity = utils.entity_linking(title)
        author_uri = author_dblp_uri.strip('<>')

        if entity:
            for entity_item in entity:
                if urlparse(entity_item['author']) == urlparse(author_uri):
                    updated_question = updated_question.replace(entity_phrase, entity_item['primarycreatorname'])
                    assertions.append(
                        generate_assertion_statement(entity_phrase, entity_item['primarycreatorname']))
                    question_updating_process.append(updated_question)
                if flag:
                    semoa_record = utils.search_semoa(entity_item['orcid'])
                    if semoa_record:
                        entity_semoa_info = entity_semoa_facts(semoa_record)
                        kg_context.append({'author_name': entity_item['primarycreatorname'],
                                           'institute_name': entity_semoa_info[0]['institute_name']})
                        next_hop_sq = identify_next_hop(updated_question)
                        updated_question = updated_question.replace(next_hop_sq, entity_semoa_info[0]['institute_name'])
                        question_updating_process.append(updated_question)
                        assertions.append(
                            generate_assertion_statement(next_hop_sq, entity_semoa_info[0]['institute_name']))
    deduplicated_assertions = utils.deduplicate_list(assertions)
    question_update_history = utils.deduplicate_list(question_updating_process)
    context = generate_context(updated_question, deduplicated_assertions)
    if context != '':
        answer = answer_generation(question, deduplicated_assertions, context)
        return answer, deduplicated_assertions, question_update_history, context, entity_phrase
    else:
        return None, deduplicated_assertions, question_update_history, context, entity_phrase


def answer_extractor(question, context):
    prompt = f"""Task: Your task is answering the question based on the given context.
                     Do not add anything else.
                     Please provide your result in JSON format only. Please do not include the Example in your response.

                     context: {context}
                     question:{question}
                     answer: 
                """
    answer = llms.chatgpt(prompt, 4)
    return answer


def answer_kg_kg_questions(question, q_type, author_dblp_uri):
    entity_encapsulating_phrase = (identify_entity_encapsulating_phrase(question, q_type))
    context = []
    question_updating_process = [question]
    updated_question = question
    entity_phrase = ''
    assertions = []
    if 'entity_encapsulating_phrase' in entity_encapsulating_phrase:
        visited_nodes = []
        if q_type == 'bridge':
            entity_phrase = entity_encapsulating_phrase['entity_encapsulating_phrase'][0]
            title = get_title(entity_phrase)
            entity = utils.entity_linking(title)
            author_uri = author_dblp_uri.strip('<>')
            if entity:
                for entity_item in entity:
                    if 'orcid' in entity_item:
                        if urlparse(entity_item['author']) == urlparse(author_uri):
                            updated_question = question.replace(entity_phrase, entity_item['primarycreatorname'])
                            assertions.append(
                                generate_assertion_statement(entity_phrase, entity_item['primarycreatorname']))
                            question_updating_process.append(updated_question)
                        semoa_record = utils.search_semoa(entity_item['orcid'])
                        # print(semoa_record)
                        if entity_item['author'] not in visited_nodes:
                            visited_nodes.append(entity_item['author'])
                            context.append(semoa_record)
                if question_updating_process[-1] != question:
                    if context:
                        next_hop = identify_next_hop(question_updating_process[-1])
                        # next_hop_phrases = next_hop.split(';')
                        assertions.append(generate_assertion_statement(next_hop, answer_extractor(next_hop + '?', context)))
        if q_type == 'comparison':
            author_uris = [author_dblp_uri[0]['author1_dblp_uri'].strip('<>'),
                           author_dblp_uri[0]['author2_dblp_uri'].strip('<>')]
            if len(entity_encapsulating_phrase['entity_encapsulating_phrase']) > 1:
                title_1 = identify_title(entity_encapsulating_phrase['entity_encapsulating_phrase'][0])
                title_2 = identify_title(entity_encapsulating_phrase['entity_encapsulating_phrase'][1])
                entity_1 = utils.entity_linking(title_1['title'][0])
                entity_2 = utils.entity_linking(title_2['title'][0])
                if entity_1 and entity_2:
                    for entity_1_item in entity_1:
                        if 'orcid' in entity_1_item:
                            if entity_1_item['author'] in author_uris:
                                updated_question = question.replace(entity_encapsulating_phrase['entity_encapsulating_phrase'][0], entity_1_item['primarycreatorname'])
                                assertions.append(generate_assertion_statement(entity_encapsulating_phrase['entity_encapsulating_phrase'][0], entity_1_item['primarycreatorname']))
                            semoa_record_1 = utils.search_semoa(entity_1_item['orcid'])

                            if entity_1_item['author'] not in visited_nodes:
                                visited_nodes.append(entity_1_item['author'])
                                context.append(semoa_record_1)

                    for entity_2_item in entity_2:
                        if 'orcid' in entity_2_item:
                            if entity_2_item['author'] in author_uris:
                                updated_question = updated_question.replace(entity_encapsulating_phrase['entity_encapsulating_phrase'][1], entity_2_item['primarycreatorname'])
                                assertions.append(generate_assertion_statement(entity_encapsulating_phrase['entity_encapsulating_phrase'][1], entity_2_item['primarycreatorname']))
                                question_updating_process.append(updated_question)
                            semoa_record_2 = utils.search_semoa(entity_2_item['orcid'])
                            if entity_2_item['author'] not in visited_nodes:
                                visited_nodes.append(entity_2_item['author'])
                                context.append(semoa_record_2)
                    if question_updating_process[-1] != question:
                        if context:
                            prev_entity_encapsulating_phrase = question_updating_process[-1]
                            next_hop = identify_next_hop(prev_entity_encapsulating_phrase)
                            next_hop_phrases = next_hop.split(';')
                            print(next_hop_phrases)
                            if len(next_hop_phrases) > 1:
                                ans_1 = answer_extractor(next_hop_phrases[0] + '?', context)
                                assertions.append(generate_assertion_statement(next_hop_phrases[0], ans_1))
                                ans_2 = answer_extractor(next_hop_phrases[1] + '?', context)
                                assertions.append(generate_assertion_statement(next_hop_phrases[1], ans_2))
                                next_entity_encapsulating_phrase = prev_entity_encapsulating_phrase.replace(next_hop_phrases[0], ans_1)
                                next_entity_encapsulating_phrase = next_entity_encapsulating_phrase.replace(next_hop_phrases[1], ans_2)
                                question_updating_process.append(next_entity_encapsulating_phrase)
    question_update_history = utils.deduplicate_list(question_updating_process)
    deduplicated_assertions = utils.deduplicate_list(assertions)
    if context:
        answer = answer_generation(question, deduplicated_assertions, context)
        return answer, deduplicated_assertions, question_update_history, context, entity_phrase
    else:
        return None, deduplicated_assertions, question_update_history, context, entity_phrase


def main(test_data_file):
    test_data = utils.load_json_data(test_data_file)
    answer_predictions = utils.load_json_data("./answer_predictions.json")
    for item in test_data:
        question = item['question']
        author_dblp_uri = item['author_dblp_uri']
        q_type = item['type']
        source_type = " ".join(item['source_types'])
        if source_type == 'KG KG':
            answer, assertions, question_update_history, context, entity_encapsulating_phrase = answer_kg_kg_questions(question, q_type, author_dblp_uri)
        else:
            reasoning_path = " ".join(item['reasoning_path'])
            if reasoning_path.__contains__('institute wikipedia text'):
                answer, assertions, question_update_history, context, entity_encapsulating_phrase = answer_kg_text_questions(question, q_type, author_dblp_uri, True)
            else:
                answer, assertions, question_update_history, context, entity_encapsulating_phrase = answer_kg_text_questions(question, q_type, author_dblp_uri)
        answer_predictions.append({"author_dblp_uri": author_dblp_uri,
                                   "id": item["id"],
                                   "answer": answer,
                                   "assertions": assertions,
                                   "entity_encapsulating_phrase": entity_encapsulating_phrase,
                                   "question_update_history": question_update_history,
                                   "context": context,
                                   "type": q_type,
                                   "source_type": source_type
                                   })
        utils.write_to_json(answer_predictions, "./answer_predictions.json")


if __name__ == "__main__":
    test_data_path = "./test_data.json"
    main(test_data_path)

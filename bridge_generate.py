import llms
import utils
from urllib.parse import urlparse

def generate_assertion_statement(sub_question_phrase, entity, flag=False):
    prompt = f"""[INST]Task: Form a sentence by joining the given PHRASE and ANSWER. Be sure the sentence is grammatically and semantically correct.
            Only return the sentence.
            [/INST]
            PHRASE: {sub_question_phrase}
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
            QUESTION: {sub_question_phrase}
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
    prompt = f"""[INST]Task: Your task is extracting the sub-question phrases and publication titles in a given QUESTION.
                Example:
                 {example}                    
                Do not add anything else.
                [/INST]          
                [{{sub_question_phrase: sub question phrase}},
                {{title: title}}
                ]
                [INST]
                Please provide your result in JSON format only. Please do not include the Example in your response.
                [/INST] 

                question: {question}

            """
    sub_questions = llms.chatgpt(prompt, 5)
    utils.write_to_json(sub_questions, "./entity_encapsulating_phrase.json")
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
    prompt = f"""[INST]Task: Your task is extracting the sub-question phrase in the QUESTION. 
                    Example:
                    {example}                    
                    Do not add anything else.
                    [/INST]          
                    [{{sub_question_phrase: sub question phrase}}]
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


def answer_kg_kg_questions(question, q_type, author_dblp_uri):
    pass


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

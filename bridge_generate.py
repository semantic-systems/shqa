import llms
import utils

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
    utils.write_to_json([assertion_sentence], "chain_of_assertion/assertion_sentence.json")
    assertion_sentence_formatted = utils.load_json_data("chain_of_assertion/assertion_sentence.json")
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
    utils.write_to_json([context], "temp.json")
    context_formatted = utils.load_json_data("temp.json")
    if 'text' in context_formatted[0]:
        return context_formatted[0]['text']
    else:
        return ''



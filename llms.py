import requests
import json
from openai import OpenAI


def chatgpt(prompt, model="gpt-3.5-turbo", function_call_flag=1):

    answer_generation_function = [
        {
            "name": "answer_generation_function",
            "description": "Answer the given question based on the given context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "Answer of the given question",
                    }
                }
            }

        }
    ]

    entity_encapsulating_phrase_identification_function = [
        {
            "name": "entity_encapsulating_phrase_identification_function",
            "description": "Extract the entity encapsulating phrases and title from the given question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_encapsulating_phrase": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Entity encapsulating phrase in a given question. Be sure to follow the examples given in the prompt",
                    },
                    "title": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Publication title in a question. Be sure to follow the examples given in the prompt",
                    }
                }
            }

        }
    ]
    title_extraction_function = [
        {
            "name": "title_extraction_function",
            "description": "Extract the title from the given phrase.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Publication title in a question. Be sure to follow the examples given in the prompt",
                    }
                }
            }

        }
    ]
    next_hop_phrase_extraction = [
        {
            "name": "next_hop_phrase_extraction",
            "description": "Extract the entity encapsulating phrase from the given question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_encapsulating_phrase": {
                        "type": "string",
                        "description": "Next hop phrase. Be sure to follow the examples given in the prompt",
                    }
                }
            }

        }
    ]
    text_generation_function = [
        {
            "name": "text_generation_function",
            "description": "Generate a text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Generated Text.",
                    }
                }
            }

        }
    ]

    if function_call_flag == 4:
        function_call = answer_generation_function
    elif function_call_flag == 5:
        function_call = entity_encapsulating_phrase_identification_function
    elif function_call_flag == 6:
        function_call = title_extraction_function
    elif function_call_flag == 7:
        function_call = next_hop_phrase_extraction
    elif function_call_flag == 8:
        function_call = text_generation_function

    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        functions=function_call,
        function_call='auto'
    )
    try:
        json_response = json.loads(completion.choices[0].message.function_call.arguments)
        return json_response
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def llama(user_prompt, sys_prompt_string="You are an experienced annotator."):
    server_url = "http://localhost:11434/api/generate"
    model = "llama3:instruct"  # "instruct" # "llama3:8B"
    messages = [
        {"role": "system", "content": sys_prompt_string},
        {"role": "user", "content": user_prompt}]

    data = dict(model=model, prompt=user_prompt, stream=False)

    headers = {"content-type": "application/json"}

    response = requests.post(server_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        # print(f"Model: {response_data["model"]}")
        # print(f"Response: {response_data["response"]}")
        return response_data["response"]
    else:
        print(f"Error: {response.status_code}")
        return None
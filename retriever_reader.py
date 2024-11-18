import torch
from sentence_transformers import SentenceTransformer
import numpy as np
from transformers import (AutoModelForQuestionAnswering, AutoTokenizer, pipeline)
# from transformers import AutoTokenizer, AutoModelForQuestionAnswering
# from sklearn.metrics.pairwise import cosine_similarity
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

retriever_model = SentenceTransformer('all-MiniLM-L6-v2')
# reader_model_name = "deepset/roberta-base-squad2"
# reader_model_name = "t5-small"
# tokenizer = AutoTokenizer.from_pretrained(reader_model_name)
# reader_model = AutoModelForSeq2SeqLM.from_pretrained(reader_model_name)
model_name = "sjrhuschlee/flan-t5-base-squad2"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#reader_model.to(device)
# Chunking function to split text into chunks of a given size
def chunk_text(text, chunk_size=300):
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks


# Retrieve relevant chunks using embedding similarity
def retrieve_chunks(question, chunks, top_n=3):
    question_embedding = retriever_model.encode([question])
    chunk_embeddings = retriever_model.encode(chunks)
    # similarities = cosine_similarity(question_embedding, chunk_embeddings).flatten()
    similarities = np.dot(question_embedding, chunk_embeddings.T).flatten()
    top_chunk_indices = np.argsort(similarities)[-top_n:][::-1]
    top_chunks = [chunks[i] for i in top_chunk_indices]

    return top_chunks


# Reader to find the answer from the selected chunks
def answer_from_chunks(question, chunks):
    answers = []
    nlp = pipeline(
        'question-answering',
        model=model_name,
        tokenizer=model_name,
        # trust_remote_code=True, # Do not use if version transformers>=4.31.0
    )
    for chunk in chunks:
        qa_input = {
            'question': f"{nlp.tokenizer.cls_token}{question}",  # '<cls>Where do I live?'
            'context': chunk
        }
        res = nlp(qa_input)
        res.update({"context_chunk": chunk})
        answers.append(res)
    best_answer = max(answers, key=lambda x: x['score'])
    return best_answer, answers
    # {'score': 0.980, 'start': 30, 'end': 37, 'answer': ' London'}


def run_retriever_reader(text, question, chunk_size=300, top_n=3):
    chunks = chunk_text(text, chunk_size)
    relevant_chunks = retrieve_chunks(question, chunks, top_n)
    answer = answer_from_chunks(question, relevant_chunks)
    return answer


if __name__ == "__main__":
    # Example usage
    text = """Eric "Rick" C. R. Hehner (born 16 September 1947) is a Canadian computer scientist. He was born in Ottawa. He studied mathematics and physics at Carleton University, graduating with a Bachelor of Science (B.Sc.) in 1969. He studied computer science at the University of Toronto, graduating with a Master of Science (M.Sc.) in 1970, and a Doctor of Philosophy (Ph.D.) in 1974. He then joined the faculty there, becoming a full professor in 1983. He became the Bell University Chair in software engineering in 2001, and retired in 2012.
    Hehner's main research area is formal methods of software design. His method, initially called predicative programming, later called Practical Theory of Programming, is to consider each specification to be a binary (boolean) expression, and each programming construct to be a binary expression specifying the effect of executing the programming construct. Refinement is just implication. This is the simplest formal method, and the most general, applying to sequential, parallel, stand-alone, communicating, terminating, nonterminating, natural-time, real-time, deterministic, and probabilistic programs, and includes time and space bounds. This idea has influenced other computer science researchers, including Tony Hoare.
    Hehner's other research areas include probabilistic programming, unified algebra, and high-level circuit design. In 1979, Hehner invented a generalization of radix complement called quote notation, which is a representation of the rational numbers that allows easier arithmetic and precludes roundoff error.
    He was involved with developing international standards in programming and informatics, as a member of the International Federation for Information Processing (IFIP) IFIP Working Group 2.1 on Algorithmic Languages and Calculi, which specified, maintains, and supports the programming languages ALGOL 60 and ALGOL 68. and of IFIP Working Group 2.3 on Programming Methodology.
    
    This biography of a Canadian academic is a stub. You can help Wikipedia by expanding it.This biographical article relating to a computer scientist is a stub. You can help Wikipedia by expanding it.This biographical article relating to a Canadian computer specialist is a stub. You can help Wikipedia by expanding it.      
    """

    question = "What is the birth date of  Eric Hehner ?"
    text = text.strip()
    answer, top_n_answers = run_retriever_reader(text, question, chunk_size=200, top_n=3)
    best_answer = answer["answer"].strip()
    best_answer = best_answer.strip(")")
    best_answer = best_answer.strip("(")

    print("Answer:", best_answer)
    print("All Answer:", top_n_answers)
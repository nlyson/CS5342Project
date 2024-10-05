import gradio as gr
import chromadb
import os
import PyPDF2
import re
import pandas as pd
from spacy.lang.en import English # see https://spacy.io/usage for install instructions
from tqdm.auto import tqdm # for progress bars, requires !pip install tqdm 


class QuizBot:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="../chroma")
        self.lecture_notes = self.client.get_or_create_collection(name="lecture_notes", metadata={"hnsw:space" : "cosine"})

    # Function to embed and add a single document to our vector db
    def add_document(self, file_name: str):
        if not file_name.endswith('pdf'):
            print('ERROR: File must be a .pdf')
            return False

        pages_and_texts = pdf_to_text(file_name)

        nlp = English()

        # Add a sentencizer pipeline, see https://spacy.io/api/sentencizer/ 
        nlp.add_pipe("sentencizer")

        for item in tqdm(pages_and_texts):
            item["sentences"] = list(nlp(item["text"]).sents)
            
            # Make sure all sentences are strings
            item["sentences"] = [str(sentence) for sentence in item["sentences"]]
            
            # Count the sentences 
            item["page_sentence_count_spacy"] = len(item["sentences"])

        # Define split size to turn groups of sentences into chunks
        num_sentence_chunk_size = 10 

        # Loop through pages and texts and split sentences into chunks
        for item in tqdm(pages_and_texts):
            item["sentence_chunks"] = split_list(input_list=item["sentences"], slice_size=num_sentence_chunk_size)
            item["num_chunks"] = len(item["sentence_chunks"])

        # Split each chunk into its own item
        pages_and_chunks = []
        for item in tqdm(pages_and_texts):
            for sentence_chunk in item["sentence_chunks"]:
                chunk_dict = {}
                chunk_dict["page_number"] = item["page_number"]
                
                # Join the sentences together into a paragraph-like structure, aka a chunk (so they are a single string)
                joined_sentence_chunk = "".join(sentence_chunk).replace("  ", " ").strip()
                joined_sentence_chunk = re.sub(r'\.([A-Z])', r'. \1', joined_sentence_chunk) # ".A" -> ". A" for any full-stop/capital letter combo 
                chunk_dict["sentence_chunk"] = joined_sentence_chunk

                # Get stats about the chunk
                chunk_dict["chunk_char_count"] = len(joined_sentence_chunk)
                chunk_dict["chunk_word_count"] = len([word for word in joined_sentence_chunk.split(" ")])
                chunk_dict["chunk_token_count"] = len(joined_sentence_chunk) / 4 # 1 token = ~4 characters
                
                pages_and_chunks.append(chunk_dict)

        # Get stats about our chunks
        df = pd.DataFrame(pages_and_chunks)

        # Get rid of random chunks with under 30 tokens in length
        min_token_length = 30
        pages_and_chunks_over_min_token_len = df[df["chunk_token_count"] > min_token_length].to_dict(orient="records")

        # Embed chunks
        documents_list = []
        ids_list = []

        for i, item in enumerate(pages_and_chunks_over_min_token_len):
            documents_list.append(item['sentence_chunk'])
            ids_list.append(f'{file_name}_{i}')

        self.lecture_notes.upsert(
            documents = documents_list,
            ids = ids_list
        )

        return True

    # Function to add all .pdfs in a directory to our vector db
    def add_documents(self, path_to_doc_folder):
        self.client.delete_collection(name='lecture_notes')
        self.lecture_notes = self.client.create_collection(name='lecture_notes', metadata={'hnsw:space' : 'cosine'})

        for root, dirs, files in os.walk(path_to_doc_folder):
            for file_name in files:
                if not self.add_document(os.path.join(root, file_name)):
                    print(f'Unable to add [{file_name}]. Moving on to next file.')
                    continue
                print(f'Successfully added [{file_name}]')

    # Function to display the embeddings
    def display_embeddings(self):
        ids = self.lecture_notes.get()['ids']
        count = 0
        for id in ids:
            count += 1
            embed_data = self.lecture_notes.get(ids=id, include=['embeddings'])
            print(embed_data)

        print(f'There are [{count}] embeddings.')

    # Function to submit a query and get related docs
    def submit_query(self):
        query = input('Enter a query (type exit to exit): ')
        max_results = int(input('Max results: '))

        while query != 'exit':
            results = self.lecture_notes.query(query_texts=[query], include=['documents'])
            ids = results['ids'][0][:max_results]
            docs = results['documents'][0][:max_results]
            
            for i in range(len(ids)):
                print(f'---ID [{ids[i]}]')
                print('------------------------Result-------------------------')
                print(docs[i])
                print('\n\n\n\n')

            query = input('Enter a query (type exit to exit): ')
            max_results = input('Max results: ')

# Helper function to convert .pdf files to strings    
def pdf_to_text(file_path: str):
    pages_and_texts = []
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            text = pdf_reader.pages[page_num].extract_text()
            text = text_formatter(text)
            pages_and_texts.append({"page_number": page_num,  # adjust page numbers since our PDF starts on page 42
                                    "page_char_count": len(text),
                                    "page_word_count": len(text.split(" ")),
                                    "page_sentence_count_raw": len(text.split(". ")),
                                    "page_token_count": len(text) / 4,  # 1 token = ~4 chars, see: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
                                    "text": text})

    return pages_and_texts

def text_formatter(text: str):
    """Performs minor formatting on text."""
    cleaned_text = text.replace("\n", " ").strip() # note: this might be different for each doc (best to experiment)

    # Other potential text formatting functions can go here
    return cleaned_text

# Create a function that recursively splits a list into desired sizes
def split_list(input_list: list, slice_size: int) -> list[list[str]]:
    """
    Splits the input_list into sublists of size slice_size (or as close as possible).

    For example, a list of 17 sentences would be split into two lists of [[10], [7]]
    """
    return [input_list[i:i + slice_size] for i in range(0, len(input_list), slice_size)]


quizbot = QuizBot()

PROMPT_MAX_TOKENS = 100
QUERY_N_RESULTS = 4
QUERY_MAX_DISTANCE = 10
PROMPT_CONTEXT = """
CS-5342 Quizbot.



"""

def answer(message: str, history: list[str]) -> str:
    """Answer questions about my network security."""
    # counters
    n_tokens = 0
    # messages
    messages = []
    # - context
    n_tokens += len(quizbot.text_splitter.split_text(PROMPT_CONTEXT))
    messages += [{"role": "system", "content": PROMPT_CONTEXT}]
    # - history
    for user_content, assistant_content in history:
        n_tokens += len(quizbot.text_splitter.split_text(user_content))
        n_tokens += len(quizbot.text_splitter.split_text(assistant_content))
        messages += [{"role": "user", "content": user_content}]
        messages += [{"role": "assistant", "content": assistant_content}]
    # - message
    n_tokens += len(quizbot.text_splitter.split_text(message))
    messages += [{"role": "user", "content": message}]
    # database
    results = quizbot.lecture_notes.query(query_texts=message, n_results=QUERY_N_RESULTS)
    distances, documents = results["distances"][0], results["documents"][0]

    content = ""
    choices = ['A', 'B', 'C', 'D']
    choice_count = 0
    for distance, document in zip(distances, documents): 
        content += f'---------------------Choice {choices[choice_count]} ------------------------\n'
        content += document
        content += '\n\n\n'
        choice_count += 1
        """
        # - distance
        if distance > QUERY_MAX_DISTANCE:
            break
        # - document
        n_document_tokens = len(quizbot.text_splitter.split_text(document))
        if (n_tokens + n_document_tokens) >= PROMPT_MAX_TOKENS:
            break
        n_tokens += n_document_tokens
        messages[0]["content"] += document
        """

    # response
    #api_response = MODEL(messages=messages)
    #content = api_response["choices"][0]["message"]["content"]
    # return
    return content    

gr.ChatInterface(answer).launch()

#quizbot.submit_query()

#quizbot.add_documents('../docs')      #<-------------Uncomment this line if you need to add documents

#quizbot.display_embeddings()         <---------------Uncomment this to see the embeddings


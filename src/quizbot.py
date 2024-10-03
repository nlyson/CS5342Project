import gradio as gr
import chromadb
import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoModelForCausalLM
import torch

class QuizBot:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="../chroma")
        self.lecture_notes = self.client.get_or_create_collection(name="lecture_notes", metadata={"hnsw:space" : "cosine"})
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        #self.model = AutoModelForCausalLM.from_pretrained("togethercomputer/RedPajama-INCITE-Chat-3B-v1")
        #self.model = self.model.to('cuda' if torch.cuda.is_available() else 'cpu')

    # Function to embed and add a single document to our vector db
    def add_document(self, file_name: str):
        if not file_name.endswith('pdf'):
            print('ERROR: File must be a .pdf')
            return False

        text = pdf_to_text(file_name)

        chunks = self.text_splitter.split_text(text)

        if not chunks:
            print(f'Error: Emptyh chunks in [{file_name}]')
            return False
        
        documents_list = []
        ids_list = []

        for i, chunk in enumerate(chunks):
            documents_list.append(chunk)
            ids_list.append(f'{file_name}_{i}')

        self.lecture_notes.upsert(
            documents = documents_list,
            ids = ids_list
        )

        return True

    # Function to add all .pdfs in a directory to our vector db
    def add_documents(self, path_to_doc_folder):
        self.client.delete_collection(name='lecture_notes')
        self.lecture_notes = self.client.create_collection(name='lecture_notes')

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
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()

    return text



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


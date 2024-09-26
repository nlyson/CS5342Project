import chromadb
import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

class QuizBot:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="../chroma")
        self.lecture_notes = self.client.get_or_create_collection(name="lecture_notes", metadata={"hnsw:space" : "cosine"})
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

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

quizbot.submit_query()

#quizbot.add_documents('../docs')      <-------------Uncomment this line if you need to add documents

#quizbot.display_embeddings()         <---------------Uncomment this to see the embeddings


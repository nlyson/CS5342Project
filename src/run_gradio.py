from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import gradio as gr

def answer(message: str, history: list[str]):
    print(f'-----------------------History: {history}')
    #Use llm to determine if question is relevant to network security
    relevant_response = llm(f"Question: Is this question: {message} relevant to network security? Simple yes or no. Don't overthink it. Obvious answers only.").lower()
    print(relevant_response)
    relevant = 'yes' in relevant_response

    #Find similar docs if relevant
    similar_docs = vectorstore.similarity_search(message, k=10) if relevant else []

    #Document the source
    source = "\n".join([f"Source: {document.metadata['source'][document.metadata['source'].index('/')+1:]} Page Number: {document.metadata['page']}" for document in similar_docs]) if relevant else "Source: Not relevant to network security."

    #Construct prompt using history from past requests - this will allows to take interactive quizzes
    prompt = "\n".join([f"User: {item[0]}\nBot: {item[1][:item[1].index('Source')]}" for item in history]) + f"\nUser: {message}"
    
    #Construct context if relevant
    context = "\n".join([doc.page_content for doc in similar_docs]) if relevant else []

    #Send constructed prompt to llm and add message, result to history
    response = llm(f"Context: {context}\nQuestion: {prompt}") if relevant else llm(f"Question: {prompt}")
    #history.append([message, response])

    #Display the reponse as well as the source
    return (response + "\n\n" + source)

if __name__ == '__main__':
    embeddings = OllamaEmbeddings(model="llama3.2")
    vectorstore = Chroma(persist_directory='../chroma', embedding_function=embeddings)
    # Initialize LLama 3.2
    llm = Ollama(model="llama3.2", base_url="http://localhost:11434")

    chatbot = gr.ChatInterface(
        fn=answer,
        title="Group 5 Quizbot",
        description="Enter the following prompt to be quizzed: Generate a multiple choice, true/false, or short answer network security question and provide feedback to my answer."
    )

    chatbot.launch(server_port=7860)
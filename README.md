# CS5342Project
Project repo for CS 5342 Project

Linux Instructions

Step 1: Clone the repo 
git clone https://github/com/nlyson/CS5342Project

Step 2: Create virtual environment
python3 -m venv venv

Step 3: Install dependencies
pip install -r requirements.txt

Step 4: Pull the model (make sure you have ollama running... Google 'how to run ollama locally' for help)
ollama pull llama3.2

Step 5: Open VS Code
code .

Step 6: Open the src/llama_train.ipynb notebook

Step 7: Run 'Dependencies' cell.

Step 8: Run 'Embed Documents' cell.  (use vectorstore = Chroma.from_documents(persist_directory=<path_to_local_dir>, documents=splits, embedding=embeddings) if you want to save your embeddings locally.

Step 9: Run 'Initialize Llama locally' cell.

Step 10: Run 'Generate prompt with GUI using gradio' cell.

Step 11: Broswe to http://127.0.0.1:7862 in your browser.

Step 12: In the text box, enter one of the following:
1) Generate a multiple choice network security question and provide feedback to my answer.
2) Generate a true/false network security question and provide feedback to my answer.
3) Generate a short answer network security question and provide feedback to my answer.

Step 13: You can also be creative. Try telling the Chatbot to give you questions, grade them, and give you feedback.


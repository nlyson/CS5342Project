<h1>Welcome to Network Security Bot</h1>
<h2> Project Description </h2>
<p>This project develops an interactive quiz bot aimed at enhancing learning in network security. It features a user- friendly interface for seamless interaction, an Embedding Model to convert text into vectors for efficient comparison, and a Vector Database (Chroma DB) to match similar knowledge documents. The bot uses Large Language Models (LLM) to process user inputs and generate accurate, contextual responses. Drawing from various sources such as textbooks, lecture slides, and online materials, the system provides personalized feedback, correct answers, and citations, ensuring an engaging and effective learning experience in network security.. The quiz includes multiple-choice questions, true/false questions, and open-ended questions. Finally, the bot will provide feedback on the user's answers if it is correct or not along with the reference source documentation title.</p>
<h2> System Architecture </h2>
<p align="center">
  <img src="Flow_diagram.png" width="500" title="sys arch">
</p>
<p>
  <h4>User Input:</h4>
  The user enters a prompt in the user interface.
  <h4>Embedding Generation:</h4>
  The system translates the user query into a numerical embedding, encapsulating its semantic meaning.
  <h4>Vector Database:</h4>
  This embedding is then sent to a vector database, where it’s matched against precomputed embeddings of various documents. The database returns a list of 
   documents most relevant to the user's query based on similarity.</br>
  <h4>Contextual Prompt Generation:</h4>
  The system creates a new prompt by combining the user's input with relevant documents as context. This added context enhances the prompt, equipping the Language Model with additional information.
  <h4>Local Language Model Processing (LLM):</h4>
  The contextualized prompt is sent to the local Language Model, which generates a response that considers both the user query and relevant background documents.
  <h4>User Interface Display:</h4>
  The system displays the response, along with citations or references to the original context documents. This transparency allows users to verify the sources and builds credibility.
</p>
<h2> Video </h2> 
<video width="320" height="240" controls>
  <source src="movie.mp4" type="QuizBot_Video.mp4">
  Your browser does not support the video tag.
</video>

https://github.com/user-attachments/assets/e2ec6121-8aa0-4b48-b943-fc297a90501d

<h2> Prerequisite </h2>
Install python3</br>
Create virtual environment</br>
python3 -m venv venv</br>
./venv/bin/activate - for MAC users</br>
./venv/Scripts/activate - for WINDOWS users</br>
<h2> Requirements </h2>
*pip install langchain==0.3.6</br>
*pip install chromadb==0.5.11</br>
*pip install llama_models==0.0.47</br>
*pip install urllib3==2.2.3 </br>
*pip install pypdf==5.1.0 </br>
*pip install python-dotenv==1.0.1 </br>
*pip install requests==2.32.3 </br>
*pip install google-auth==2.35.0</br>
*pip install nltk==3.9.1</br>
*pip install pillow==10.4.0 </br>
*pip install ipython==8.28.0 </br>
*pip install PyPDF2==3.0.1</br>
*pip install zipp==3.20.2</br>
*pip install dataclasses-json==0.6.7 </br>
   
<h2> Step by step instructions for executions </h2>

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

Step 11: Broswe to http://127.0.0.1:7860 in your browser.

Step 12: In the text box, enter one of the following:
1) Generate a multiple choice network security question and provide feedback to my answer.
2) Generate a true/false network security question and provide feedback to my answer.
3) Generate a short answer network security question and provide feedback to my answer.

Step 13: You can also be creative. Try telling the Chatbot to give you questions, grade them, and give you feedback.

<h2>Identifying issues and Implementing Solutions</h2>
<p>
  Issue 1: We initially embedded and stored the preprocessed documents into a vector database. We used similar matching to retrieve the results, but the results didn’t come in question/answer format.
</p>
<p>
  Solution 1: We augment the results with the llama3.2 model. We were able to augment results with generated content.
</p>
<p>
  Issue 2: After giving questions and answers, the quizbot would not give citations.
</p>
<p>
  Solution 2: We used metadata stored with the embeddings in the vector database. After performing a similar match and passing results to the LLM, we saved the metadata (document and page number) and appended the metadata to the results. 
</p>
<p>
  Issue 3: Overfitting in Quiz Logic: Overfitting can lead the quiz bot to perform well on familiar questions from its training data but may hinder its ability to handle new or varied quiz scenarios.
</p>
<p>
  Solution 3: Improving the quiz bot’s generalization can be achieved by using a diverse and representative dataset, including a wide range of real-world question types, and regularly retraining the model with fresh data.
</p>

<h2>Features</h2>
<p>
  Bot will generate random and specific topic quizes from trained datasets based on user requirement.</br>
  Bot generates different types of questions in quiz like multiple choice, true or false and open-ended.</br>
  Bot will provide feedback as score to user once user completes quiz.</br>
  Bot works both as quizbot and chatbot.  
</p>
<h2> Describe training data and data formats </h2>
<p>We trained our bot using lecture slides and network security textbook(Network Security Essentials: Applications and Standards sixth edition - by William Stallings)</p>



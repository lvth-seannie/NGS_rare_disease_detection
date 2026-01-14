"""
1. load the pdf
2. split it into chunks (paragraphs)
3. search for relevant chunks when u ask a question
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))      # .../src/tools
project_root = os.path.dirname(os.path.dirname(current_dir))  # .../disease_detection

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaLLM  # added for making output human-readable

from src.config import KB_PATH, DB_PATH

# initialize Ollama (connect to the app running)
llm = OllamaLLM(model="mistral")

# initialize embedding model
print("⏳ Loading Embedding Model (this happens once)...")
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def setup_knowledge_base():
    # read PDFs from data/knowledge_base & build a Vector Database
    # run this ONLY ONCE or when new PDFs are added
    print("🏗️ Indexing Knowledge Base...")
    
    # 1. load PDFs
    docs = []
    if not os.path.exists(KB_PATH):
        print(f"⧱ ERROR >>> Knowledge Base path NOT FOUND at {KB_PATH}")
        return None
    
    for filename in os.listdir(KB_PATH):
        if filename.endswith(".pdf"):
            file_path = os.path.join(KB_PATH, filename)
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())
            print(f"✅ Loaded >>> {filename} with {len(docs)} pages.")
        if not docs:
            print(f"⧱ ERROR >>> No PDFs found in {KB_PATH}")
            return None
        
    # 2. split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    splits = splitter.split_documents(docs)
    
    # 3. build VectorDB (save to disk)
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embedding_function,
        persist_directory=DB_PATH
    )
    print(f"✅ Database created with {len(splits)} chunks.")
    return vectordb

# added a new function: -- FUNCTION TO MAKE THE RESPONSE HUMAN READABLE --
def generate_human_readable_response(query, context_text, audience="patient"):
    if audience == "Patient":
        prompt = f"""
        You are a kind and helpful Genetic Counselor.
        Your goal is to explain medical findings to a PATIENT who has no medical background.
        
        Task: Answer the question based ONLY on the provided context.
        Style: Simple language, empathetic, short sentences. Avoid complex jargon.
        
        Question: {query}
        Context: {context_text}
        
        Response:
        """
    elif audience == "Doctor" or audience == "Clinician":
        prompt = f"""
        You are a Clinical Geneticist assistant.
        Your goal is to summarize findings for a DOCTOR or CLINICIAN.
        
        Task: Answer the question based ONLY on the provided context.
        Style: Technical, precise, professional, realistic. Focus on mechanisms and clinical significance.
        
        Question: {query}
        Context: {context_text}
        
        Response:
        """
    else:
        # if audience is undefined or doesn't match
        prompt = f"""
        You are a medical AI assistant.
        Summarize the following context to answer the question.
        
        Question: {query}
        Context: {context_text}
        """
    # invoke LLM
    return llm.invoke(prompt)

def query_literature(query_text, audience="patient"): # <-- added audience param
    """search the Knowledge Base for relevant text"""
    # load existing DB
    if not os.path.exists(DB_PATH) or not os.listdir(DB_PATH):
        print(f"⧱ ERROR >>> Knowledge Base DB NOT FOUND at {DB_PATH}")
        vectordb = setup_knowledge_base()
        if not vectordb: return "⧱ ERROR >>> Knowledge Base is empty!"
    else:
        vectordb = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)
    
    # 1. retrieve raw chunks
    results = vectordb.similarity_search(query_text, k=3)
    raw_context = "\n".join([doc.page_content for doc in results])
    
    # 2. generate readable answer using LLM
    print(f"🧬 Generating {audience} explanation via Ollama...")
    human_response = generate_human_readable_response(query_text, raw_context, audience)

    return human_response

if __name__ == "__main__":
    # test run
    print("\n>>> Asking: 'What is Long QT Syndrome?'")
    response = query_literature("What is Long QT Syndrome?")
    print("📝 RETRIEVED CONTEXT >>>\n", response)    
        
    
    

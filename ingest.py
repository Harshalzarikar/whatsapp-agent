import os
import shutil
from dotenv import load_dotenv
from datasets import load_dataset
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL_NAME = "models/gemini-embedding-2"
DATASET_NAME = "Abhaykoul/Ancient-Indian-Wisdom" # Contains Upanishads and other texts

def main():
    print("Loading dataset from HuggingFace...")
    try:
        # Load the dataset
        dataset = load_dataset(DATASET_NAME, split="train")
        
        documents = []
        for item in dataset:
            # Depending on the dataset structure, we extract the text.
            # This dataset typically has a 'text' or 'content' column. 
            # We'll try a few common keys.
            content = item.get('text', '') or item.get('content', '') or item.get('instruction', '') + " " + item.get('output', '')
            
            if content:
                # Add metadata if available (like source or title)
                metadata = {"source": item.get('source', 'Ancient Indian Wisdom')}
                documents.append(Document(page_content=content, metadata=metadata))
        
        print(f"Loaded {len(documents)} documents.")
        
        if not documents:
            print("No documents found. Check dataset structure.")
            return

        print("Splitting text into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks.")

        # Clear existing DB if it exists
        if os.path.exists(CHROMA_PATH):
            print("Clearing existing vector database...")
            shutil.rmtree(CHROMA_PATH)

        print("Initializing Embedding model...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

        print("Creating Vector Database...")
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        
        batch_size = 90
        import time
        # Initial sleep to clear previous rate limits
        print("Sleeping 10s to clear previous rate limits...")
        time.sleep(10)
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            print(f"Adding batch {i//batch_size + 1} of {(len(chunks)//batch_size)+1}...")
            
            success = False
            retries = 3
            while not success and retries > 0:
                try:
                    db.add_documents(batch)
                    success = True
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        print(f"Rate limited. Retrying in 65 seconds... (Retries left: {retries-1})")
                        time.sleep(65)
                        retries -= 1
                    else:
                        raise e
                        
            if i + batch_size < len(chunks):
                print("Sleeping for 60 seconds to respect free tier rate limits...")
                time.sleep(60)

        print("Data successfully ingested and persisted into Chroma vector database.")

    except Exception as e:
        print(f"An error occurred during ingestion: {e}")

if __name__ == "__main__":
    main()

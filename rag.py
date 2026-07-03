import os
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# Setup Vector Store
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL_NAME = "models/gemini-embedding-2"

# Setup LLM
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

class RAGPipeline:
    def __init__(self):
        print("Initializing Embeddings...")
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
        
        print("Loading Vector Store...")
        self.vector_store = Chroma(
            persist_directory=CHROMA_PATH, 
            embedding_function=self.embeddings
        )
        
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        print("Initializing LLM...")
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=GROQ_API_KEY,
            model_name="llama-3.1-8b-instant"
        )
        
        self.qa_chain = self._build_chain()
        print("RAG Pipeline Ready.")

    def _build_chain(self):
        system_prompt = (
            "You are an AI assistant knowledgeable in ancient Indian wisdom, specifically the Upanishads. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, say that you don't know based on the provided context. "
            "Keep the answer concise and relevant to the user's question, suitable for a WhatsApp message.\n\n"
            "Context:\n{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(self.retriever, question_answer_chain)
        return rag_chain

    def get_answer(self, query: str) -> str:
        if not self.vector_store.get()['ids']:
            return "The knowledge base is currently empty. Please run the ingestion script first."
            
        try:
            response = self.qa_chain.invoke({"input": query})
            return response["answer"]
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I apologize, but I encountered an error while trying to process your request."

    def ingest_pdf(self, file_path: str) -> bool:
        """Loads a PDF, extracts text, splits it, and adds it to the ChromaDB."""
        try:
            print(f"Loading PDF from {file_path}...")
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            if not documents:
                print("No text found in PDF.")
                return False
                
            print("Splitting text into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            chunks = text_splitter.split_documents(documents)
            
            print(f"Adding {len(chunks)} chunks to vector store...")
            self.vector_store.add_documents(chunks)
            print("PDF successfully ingested!")
            
            return True
        except Exception as e:
            print(f"Error ingesting PDF: {e}")
            return False

# Initialize a global instance (singleton pattern for fast API access)
try:
    rag_pipeline = RAGPipeline()
except Exception as e:
    print(f"Failed to initialize RAG pipeline: {e}")
    rag_pipeline = None

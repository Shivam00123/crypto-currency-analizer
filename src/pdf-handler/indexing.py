#fle in python
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()


file_path = Path(__file__).parent.parent / "crypto.pdf"
loader = PyPDFLoader(file_path=file_path)

docs = loader.load()

#chunks

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=400)

chunks = text_splitter.split_documents(documents=docs)

#embedding


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

#store in qdrant

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name ="crypto"
)

print("Indexing complete.")


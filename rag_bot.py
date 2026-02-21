
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

if not os.path.exists("data.pdf"):
    print("? Still missing data.pdf! Check the file extension.")
    exit()

print("?? Reading PDF...")
loader = PyPDFLoader("data.pdf")
docs = loader.load()

print("?? Splitting text...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(docs)

print("?? Creating Embeddings... (First time may take a minute)")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma.from_documents(documents=chunks, embedding=embeddings)
retriever = vector_db.as_retriever()

llm = ChatGroq(model="llama-3.3-70b-versatile")

template = "Answer based ONLY on context:\n{context}\n\nQuestion: {question}"
prompt = ChatPromptTemplate.from_template(template)
chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm)

print("\n? READY!")
while True:
    q = input("\nAsk me: ")
    if q.lower() == "exit": break
    try:
        response = chain.invoke(q)
        print(f"\nAI: {response.content}")
    except Exception as e:
        print(f"\n? Error: {e}")


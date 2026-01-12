from google import genai
from google.genai import types

import os
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter 
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))

EMBED_DIM = 1536

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap = 200)

def load_and_chunk_pdf(path: str):
    docs = PDFReader().load_data(file = path)
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks
    
def embed_texts(texts:list[str]):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents= texts,
        config=types.EmbedContentConfig(output_dimensionality=1536))

    return [embedding.values for embedding in result.embeddings]

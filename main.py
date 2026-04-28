import datetime
import logging
import os
import uuid

import inngest
import inngest.fast_api
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from custom_types import RAGChunkAndSrc, RAGSearchResult, RAGUpsertResult
from data_loader import embed_texts, load_and_chunk_pdf
from vector_db import QdrantStorage

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)




adapter = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("LLM_API_KEY", ""),
)

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer(),
)


@inngest_client.create_function(
    fn_id="RAG: PDF Ingestion",
    throttle=inngest.Throttle(
        limit=1,
        period=datetime.timedelta(seconds=5),
        key="event.data.user_id",
        burst=2,
    ),
    rate_limit=inngest.RateLimit(
        limit=10,
        period=datetime.timedelta(hours=1),
        key="event.data.company_id",
    ),
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
)
async def rag_ingest_pdf(ctx: inngest.Context):
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(str(pdf_path))
        return RAGChunkAndSrc(chunks=chunks, source_id=str(source_id))

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vecs = embed_texts(chunks)
        ids = [
            str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}"))
            for i in range(len(chunks))
        ]
        payloads = [
            {"source": source_id, "text": chunks[i]} for i in range(len(chunks))
        ]
        QdrantStorage().upsert(ids, vecs, payloads)
        return RAGUpsertResult(ingested=len(chunks))

    chunks_and_src = await ctx.step.run(
        "load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc
    )
    ingested = await ctx.step.run(
        "embed-and-upsert", lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult
    )
    return ingested.model_dump()


@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    rate_limit=inngest.RateLimit(
        limit=20,
        period=datetime.timedelta(hours=1),
        key="event.data.company_id",
    ),
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"),
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    def _search(question: str, top_k: int = 5) -> RAGSearchResult:
        query_vec = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec, top_k)
        logged_data = {}
        logger.info(logged_data)
        return RAGSearchResult(contexts=found["contexts"], sources=found["sources"])

    def _gen_res(user_content):
        res = adapter.chat.completions.create(
            model="allenai/olmo-3.1-32b-instruct",
            max_tokens=1024,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": """Role: You are a precise Fact-Checking Assistant. Your sole objective is to answer the user's question using only the provided context snippets.
                Constraints:
                    Strict Grounding: Your answer must be derived entirely from the provided context. Do not use outside knowledge or general facts not contained in the snippets.
                    The "I Don't Know" Rule: If the provided context does not contain the answer, or if the information is insufficient to answer the question fully, state clearly: "I’m sorry, but the provided documents do not contain enough information to answer this question." Do not attempt to guess.
                    Citations: Every factual claim must be followed by an inline citation referencing the source document ID or name (e.g., [Source 1] or [Policy_Manual.pdf]).
                    Tone: Maintain a neutral, professional, and concise tone.
                Output Format:
                    Answer the question directly.
                    Use bullet points for lists.
                    Place citations immediately after the relevant sentence or phrase.""",
                },
                {"role": "user", "content": user_content},
            ],
        )
        ans = res.choices[0].message.content.strip()
        return {"msg": ans}

    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 5))

    found = await ctx.step.run(
        "embed-and-search",
        lambda: _search(question, top_k),
        output_type=RAGSearchResult,
    )

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)

    user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
    )

    res = await ctx.step.run("generate_response", lambda: _gen_res(user_content))

    answer = res["msg"]
    return {
        "answer": answer,
        "sources": found.sources,
        "num_contexts": len(found.contexts),
    }


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.2.1"}


inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])

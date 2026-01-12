# sample pdf path  E:\\Aman\\aman2\\Folder1\\Resumes\\test.py
# uv run uvicorn main:app
# npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery



#     adapter = ai.openai.Adapter(
#         auth_key=os.getenv("OPENAI_API_KEY"),
#         model="gpt-4o-mini"
#     )

#     res = await ctx.step.ai.infer(
#         "llm-answer",
#         adapter=adapter,
#         body={
#             "max_tokens": 1024,
#             "temperature": 0.2,
#             "messages": [
#                 {"role": "system", "content": "You answer questions using only the provided context."},
#                 {"role": "user", "content": user_content}
#             ]
#         }
#     )
    
    
#     from qdrant_client import QdrantClient
    
#     client = QdrantClient(url="http://localhost:6333")
    
#     results = client.query_points(
#         collection_name="my_collection",
#         query=[0.12, 0.98, 0.45, 0.33],  # the query vector
#         limit=5
#     )
    
#     for pt in results:
#         print(pt.id, pt.score, pt.payload)

#   # res = await ctx.step.ai.infer(
#     #     "llm-answer",
#     #     adapter=adapter,
#     #     body={
#     #         "max_tokens": 1024,
#     #         "temperature": 0.2,
#     #         "messages": [
#     #             {"role": "system", "content": "You answer questions using only the provided context."},
#     #             {"role": "user", "content": user_content}
#     #         ]
#     #     }
#     # )

from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

context_block = "you are a  computer nerd"
question = "name types of ram"
user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using the context above."
    )
    
adapter = OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=os.getenv("LLM_API_KEY",""),
    )
    
res = adapter.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
      },
    model="allenai/olmo-3.1-32b-instruct",
    max_tokens=1024,
    temperature=0.2,
    messages=[
        {"role": "system", "content": "You answer questions using only the provided context."},
        {"role": "user", "content": user_content}
        ]
    )
print(res.choices[0].message.content)

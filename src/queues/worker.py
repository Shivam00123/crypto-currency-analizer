from pydantic import BaseModel
import aiohttp
from ..utils.endpoints import generate_crypto_price_endpoint
from openai import OpenAI
from dotenv import load_dotenv
import json
from ..utils.prompts import generate_system_prompts
from typing import Optional
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import asyncio
from redis import Redis

load_dotenv()


client = OpenAI()

redis_client = Redis(host="localhost", port="6379", decode_responses=True)

embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    collection_name="crypto",
    url="http://localhost:6333",
    embedding=embeddings
)


class AgentResponse(BaseModel):
    step: str
    content: Optional[str] = None
    tool: Optional[str] = None
    input1: Optional[str] = None
    input2: Optional[str] = None


class Worker(BaseModel):

    async def get_crypto_price(self, session, coin: str, currency: str):
        key = f"cache:crypto:{coin}:{currency}"
        cached = redis_client.get(key)
        if cached:
            print("⚡ Cache hit")
            price = json.loads(cached)
            return f"Current price of {coin} is {price}{currency}"
        print("🌐 API call")
        price = await self.get_current_crypto_price(session, coin, currency)
        redis_client.setex(
            key,
            60,
            json.dumps(price)
        )
        return f"Current price of {coin} is {price}{currency}"

    async def get_current_crypto_price(self, session, crypto: str, currency: str = "usd"):
        async with session.get(generate_crypto_price_endpoint(crypto=crypto, currency=currency)) as response:
            if response.status == 200:
                data = await response.json()
                price = data[crypto][currency]
                return price
            return None

    async def process_user_query(self, user_query: str):
        chunks = vector_db.similarity_search(query=user_query, k=3)

        context = "\n\n\n".join([
            f"Page content: {result.page_content}\n"
            f"Page Number: {result.metadata['page_label']}\n"
            f"Page Location: {result.metadata['source']}"
            for result in chunks
        ])

        message_history = [
            {"role": "system", "content": generate_system_prompts(
                context)}  # context
        ]

        message_history.append({"role": "user", "content": user_query})
        async with aiohttp.ClientSession() as session:
            while True:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=message_history
                )
                raw_data = response.choices[0].message.content
                message_history.append(
                    {"role": "assistant", "content": raw_data})
                parsed_object = AgentResponse.model_validate_json(raw_data)

                step = parsed_object.step

                available_tools = {
                    "get_crypto_price": self.get_crypto_price
                }

                print("obj",parsed_object)

                if step == "START":
                    print("🔥", parsed_object.content)
                    continue
                if step == "PLAN":
                    print("🧠", parsed_object.content)
                    continue
                if step == "OBSERVE":
                    if not parsed_object.input1 or not parsed_object.input2:
                        print("Tool input missing")
                        break
                    if parsed_object.tool not in available_tools:
                        print("Unknown tool requested")
                        break

                    tool_response = await available_tools[parsed_object.tool](session, parsed_object.input1, parsed_object.input2)
                    message_history.append({"role": "developer", "content": json.dumps({
                        "step": "OBSERVE", "tool": parsed_object.tool, "output": tool_response
                    })})

                    continue
                if step == "OUTPUT":
                    print("🤖", parsed_object.content)
                    return parsed_object.content
                    break


def helper_function(query: str):
    worker = Worker()
    return asyncio.run(worker.process_user_query(query))

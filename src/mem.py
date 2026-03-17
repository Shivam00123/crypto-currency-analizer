from mem0 import Memory
import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

config = {
    "version":"v1.1",
    "embedder":{
        "provider":"openai",
        "config":{
            "api_key":OPENAI_API_KEY,
            "model":"text-embedding-3-small"
        }
    },
    "llm":{
        "provider":"openai",
        "config":{
            "api_key":OPENAI_API_KEY,
            "model":"gpt-4.1"
        }
    },
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "host":"localhost",
            "port":6333
        }
    }
}

memory_client = Memory.from_config(config)
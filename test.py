from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from time import sleep
import asyncio

load_dotenv()

class LLM:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            max_tokens=1000,
            timeout=10,
            max_retries=3,
        )

    async def invoke(self, prompt: str):
        # Remove this line as it's using a hardcoded prompt instead of the passed parameter
        # response = self.llm.invoke("Write me a 1 verse song about sparkling water.")
        
        # For storing the complete response
        full_response = ""
        
        # Stream the response chunks
        async for chunk in self.llm.astream(prompt):
            chunk_content = chunk.content
            if chunk_content:
                print(chunk_content, end="|", flush=True)
                full_response += chunk_content
                await asyncio.sleep(2)  # Using asyncio.sleep instead of time.sleep in async context
        
        return full_response
    

async def main():
    llm = LLM()
    response = await llm.invoke("Write a description of a 3D website.")
    print("\n\nFull response:", response)

if __name__ == "__main__":
    asyncio.run(main())
import requests
import sys
import os

API_URL = "http://localhost:10000/process/stream"


def stream_response():
    with requests.post(API_URL, json=payload, stream=True) as resp:
        resp.raise_for_status()
        print("Streaming response:")
        for chunk in resp.iter_content(chunk_size=None):
            if "[LLM Synthesis]" in chunk.decode():
                # Clear the console when the LLM Synthesis is done
                os.system('clear')
                pass
            if chunk:
                sys.stdout.write(chunk.decode())
                sys.stdout.flush()

if __name__ == "__main__":

    payload = {
        "project_description": input("Enter a project description: "),
        "model_type": "gemini",
        "follow_up_question": None,
        "session_id": None
    }


    stream_response()
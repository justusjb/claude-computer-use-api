from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import asyncio
from computer_use_demo.shared import message_queue, responses, response_ready

app = FastAPI()

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: List[Dict[str, Any]]

@app.post("/chat")
async def send_message(chat_message: ChatMessage):
    try:
        # Generate unique ID for this message
        message_id = str(uuid.uuid4())
        
        # Put message and ID in queue
        message_queue.put((message_id, chat_message.message))
        
        # Wait for response with timeout
        timeout = 60  # 60 seconds timeout
        try:
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                if message_id in responses:
                    response = responses.pop(message_id)  # Get and remove response
                    return ChatResponse(response=response)
                await asyncio.sleep(1)  # Check every second
            
            raise HTTPException(
                status_code=408,
                detail="Response timeout - message was sent but no response received within timeout period"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
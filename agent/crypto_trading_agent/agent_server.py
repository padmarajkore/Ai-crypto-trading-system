from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from .agent import root_agent
from google.adk.runners import Runner
from google.genai.types import Content, Part
from google.adk.sessions import InMemorySessionService
from datetime import datetime

app = FastAPI(title="AI Crypto Agent API")

# Setup Session Service (using in-memory to avoid stale session issues)
session_service = InMemorySessionService()

# Setup Runner
runner = Runner(
    agent=root_agent,
    app_name="crypto_trader",
    session_service=session_service
)

class TriggerRequest(BaseModel):
    message: str

@app.post("/trigger")
async def trigger_agent(request: TriggerRequest):
    print(f"🔔 Trigger received: {request.message}")
    
    try:
        # Create or get session
        # Always create a new session to ensure fresh context (bypassing potential persistent corruption)
        import uuid
        user_id = f"user_{uuid.uuid4()}" # Force unique user ID every time
        # sessions = await session_service.list_sessions(app_name="crypto_trader", user_id=user_id)
        # if sessions.sessions:
        #     session_id = sessions.sessions[0].id
        # else:
        session = await session_service.create_session(app_name="crypto_trader", user_id=user_id)
        session_id = session.id
        print(f"🆕 Created new session: {session_id} for user: {user_id}")
            
        # Run agent
        response_text = ""
        # Construct message object
        message_obj = Content(role="user", parts=[Part(text=request.message)])
        
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=message_obj):
            # Check if event has content (it might be a chunk or a full event)
            # We'll try to extract meaningful text
            if hasattr(event, 'content') and event.content:
                 response_text += str(event.content)
            # Also check for 'text' attribute if content is missing
            elif hasattr(event, 'text') and event.text:
                 response_text += str(event.text)
        
        # --- LOGGING ---
        log_entry = f"""
--------------------------------------------------------------------------------
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
TRIGGER: {request.message}
RESPONSE: {response_text}
--------------------------------------------------------------------------------
"""
        with open("conversation_history.log", "a") as f:
            f.write(log_entry)
        # ---------------
        
        return {
            "status": "success", 
            "agent_response": response_text
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error running agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

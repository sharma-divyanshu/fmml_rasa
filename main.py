import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Import chat router
from period_tracker.chat import router as chat_router

# Create FastAPI app
app = FastAPI(title="Period Tracker API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Configure templates
templates = Jinja2Templates(directory=os.path.join(current_dir, "period_tracker/chat/templates"))

# Mount static files
static_dir = os.path.join(current_dir, "period_tracker/chat/static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include chat router with prefix
app.include_router(chat_router, prefix="/chat")

# Simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

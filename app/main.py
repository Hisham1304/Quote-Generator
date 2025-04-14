from fastapi import FastAPI, Request, Form 
from fastapi.responses import RedirectResponse 
from fastapi.templating import Jinja2Templates 
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from fastapi.staticfiles import StaticFiles



load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

session_data = {
    "name": "",
    "tags": []
}


@app.get("/")
def get_name(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/set-name")
def set_name(name: str = Form(...)):
    session_data["name"] = name
    return RedirectResponse(url="/interests", status_code=303)

@app.get("/interests")
def show_interests(request: Request):
    return templates.TemplateResponse("interests.html", {"request": request})

@app.post("/generate")
async def generate_tags(request: Request):
    form = await request.form()
    tags = form.getlist("tags")
    session_data["tags"] = tags
    return RedirectResponse(url="/quotes", status_code=303)

@app.get("/quotes")
async def show_quote(request: Request):
    tags = session_data.get("tags", [])
    name = session_data.get("name", "User")

    # Construct a prompt for OpenAI
    prompt = (
        f"Create an inspiring, personalized and educational quote for {name}. "
        f"Give fun facts: {', '.join(tags)}. "
        f"Based on the following interests: {', '.join(tags)}. "
        f"Respond only in the following JSON format (no explanation, no markdown): {{\"quote\": \"...\"}}"
    )

    # Call OpenAI API

    client = OpenAI()
    response = client.responses.create(
        model="gpt-4o",
        input= prompt 
    )

    # Extract the quote from the JSON response
    message_content = response.output_text
    print("OpenAI Raw Response:", message_content)
    quote_data = json.loads(message_content)
    


    return templates.TemplateResponse("quotes.html", {
        "request": request,
        "quote": quote_data["quote"]
    })


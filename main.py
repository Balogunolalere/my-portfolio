from fastapi import FastAPI, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Create the FastAPI app
# disable the docs
# disable the redoc
app = FastAPI(docs_url=None, redoc_url=None)

# Create the Jinja2Templates instance
templates = Jinja2Templates(directory="templates")

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/works")
async def works(request: Request):
    return templates.TemplateResponse("works.html", {"request": request})


@app.middleware("http")
async def fix_mime_type(request: Request, call_next):
    response = await call_next(request)
    content_types = {
        ".ttf" :"font/ttf",
        ".woff": "font/woff", 
        ".woff2": "font/woff2"
    }
    for e in content_types:
        if request.url.path.endswith(e): response.headers["Content-Type"] = content_types[e]
    return response

@app.post("/email")
async def mail_me(request: Request, email: str = Form(...), subject: str = Form(...), message: str = Form(...)):

    from_email = os.getenv('EMAIL_ADDRESS') 
    password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEMultipart('alternative')
    msg['From'] = from_email
    msg['To'] = os.getenv('TO_EMAIL')
    msg['Subject'] = subject

    text = message
    html = f"""
    <html>
        <head>
            <style>
            body {{
                font-family: 'Arial', sans-serif;
                font-size: 16px;
                color: #333;
                line-height: 1.5;
                padding: 20px;
                background-color: #f5f5f5; 
            }}
            
            h1 {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px; 
                color: #0066CC;
            }}
            
            p {{
                margin-bottom: 10px;
            }}
            
            .email {{
                font-weight: bold;
            }}
            
            .subject {{
                font-style: italic;
                color: #888;
            }}
            
            </style>
        </head>
        
        <body>
            <h1>New Contact Form Submission</h1>
            
            <p class="email">From: {email}</p>
            
            <p class="subject">Subject: {subject}</p>
            
            <p>{message}</p>
        </body>
        </html>
    """

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(from_email, password)
        server.sendmail(from_email, os.getenv('TO_EMAIL'), msg.as_string())
        server.close()
        
        return RedirectResponse(url="/contact", status_code=status.HTTP_302_FOUND)

    except Exception as e:
        logging.error(e)
        return RedirectResponse(url="/contact", status_code=status.HTTP_302_FOUND)
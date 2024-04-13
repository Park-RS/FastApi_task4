from fastapi import FastAPI, BackgroundTasks, Depends, Query, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from datetime import datetime
import logging

app = FastAPI()


def background_task():
    current_time = datetime.now().strftime("%H:%M:%S")
    print("Background task executed. Current time:", current_time)


@app.get("/get_time")
async def get_time(background_tasks: BackgroundTasks):
    current_time = datetime.now().strftime("%H:%M:%S")
    background_tasks.add_task(background_task)
    return {"current_time": current_time}


@app.exception_handler(404)
async def not_found(request, exc):
    return {"detail": "Not Found"}


async def check_name_parameter(name: str = Query(...)):
    if name:
        return name
    else:
        return "Параметр отсутствует"

@app.get("/check")
async def check_name(name: str = Depends(check_name_parameter)):
    return {"name": name}


async def log_requests(request: Request, call_next):

    logger = logging.getLogger("uvicorn.access")
    logging.basicConfig(filename='requests.log', level=logging.INFO)
    
  
    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)
    
    return response


app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.middleware("http")(log_requests)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

from fastapi import FastAPI
# FastAPI setup
fastapi_app = FastAPI()

@fastapi_app.get("/fastapi_route")
async def fastapi_route():
    return {"message": "Hello from FastAPI!"}
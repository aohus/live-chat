from fastapi import FastAPI
from api.v1 import router

def init_routers(app: FastAPI) -> None:
    app.include_router(router)
    
def create_app() -> FastAPI:
    app = FastAPI(
        title="Live Chat",
        description="Live Chatting Server",
        version="1.0.0",
    )
    init_routers(app=app)
    return app


app = create_app()
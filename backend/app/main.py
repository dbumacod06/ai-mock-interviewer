import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import applicant_router, chat_router, system_router

# Configure root logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def create_app() -> FastAPI:
    app = FastAPI(title="Interview Bot API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(system_router)
    app.include_router(chat_router)
    app.include_router(applicant_router)

    return app


app = create_app()

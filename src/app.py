from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from event_handlers import start_app_handler, stop_app_handler
from settings import server_settings


def get_app() -> FastAPI:
    fast_api_app = FastAPI(title=server_settings.app_name, version=server_settings.app_version)
    fast_api_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_api_app.add_event_handler("startup", start_app_handler(fast_api_app))
    fast_api_app.add_event_handler("shutdown", stop_app_handler(fast_api_app))
    fast_api_app.include_router(router)
    return fast_api_app


app = get_app()

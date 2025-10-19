import os
from fastapi import FastAPI


def create_app() -> FastAPI:
    app_name = os.getenv("APP_NAME", "genai-minimal-starter")
    app = FastAPI(title=app_name)

    @app.get("/")
    def root():
        return {"message": f"Welcome to {app_name}"}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()



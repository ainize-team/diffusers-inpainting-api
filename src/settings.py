from pydantic import BaseSettings


class ServerSettings(BaseSettings):
    app_name: str = "Inpainting Fast API Server"
    app_version: str = "0.1.0"


class CelerySettings(BaseSettings):
    broker_base_uri: str = "amqp://guest:guest@localhost:5672/"
    vhost_name: str = "/"


class FirebaseSettings(BaseSettings):
    firebase_app_name: str = "diffusers-inpainting"
    cred_path: str = "./key/serviceAccountKey.json"
    database_url: str
    storage_bucket: str


server_settings = ServerSettings()
celery_settings = CelerySettings()
firebase_settings = FirebaseSettings()

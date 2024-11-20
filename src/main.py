from fastapi import FastAPI
from controllers.TesteController import controller_teste
from fastapi.middleware.cors import CORSMiddleware

api = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000"
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(controller_teste)

from fastapi import FastAPI
from .controllers.PokeController import controller_poke
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='PokeAIAPI')
origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(controller_poke)

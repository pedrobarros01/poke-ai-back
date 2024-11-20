from fastapi import APIRouter, HTTPException
from services.TesteService import TesteService
from models.Teste import Teste
controller_teste = APIRouter()
service = TesteService()

@controller_teste.get('/teste/ola_mundo', status_code=200, tags=['teste'])
async def teste() -> Teste:
    try:
        return service.ola_mundo()
    except Exception as e:
        return HTTPException(status_code=500, detail=e.__str__())
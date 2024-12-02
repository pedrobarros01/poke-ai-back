from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any
import os
from dotenv import load_dotenv
from libraries.PokeAi import PokeAi
from services.PokeService import PokeService
from models.Pokemon import Pokemon, BatalhaHistoria

controller_poke = APIRouter()

# Inicializar a classe PokeAi com a chave da API a partir de uma variável de ambiente
load_dotenv()
api_key = os.getenv("GPT_API")
if not api_key:
  raise RuntimeError("A chave da API GPT_API não foi configurada.")

service = PokeService(api_key)

@controller_poke.post('/pokemon/gerar', status_code=200, tags=['pokemon'])
async def gerar_pokemon(
    base_corpo: str = Form(..., description="Base do corpo do Pokémon"),
    cor_principal: str = Form(..., description="Cor principal do Pokémon"),
    cor_secundaria: str = Form(..., description="Cor secundária do Pokémon"),
    tipo_1: str = Form(..., description="Primeiro tipo do Pokémon"),
    tipo_2: str = Form(None, description="Segundo tipo do Pokémon (opcional)"),
    geracao: int = Form(..., description="Geração do Pokémon"),
    peso: float = Form(..., description="Peso do Pokémon em kg"),
    altura: float = Form(..., description="Altura do Pokémon em metros"),
    detalhes_extras: str = Form(...,
                                description="Detalhes adicionais sobre o Pokémon")
) -> Pokemon:
  """
  Gera um Pokémon com seus detalhes, 4 ataques únicos e uma imagem baseada nos dados fornecidos.
  """
  try:
    # Montar os dados do Pokémon com as informações do formulário
    poke_data = {
        "base_corpo": base_corpo,
        "cor_principal": cor_principal,
        "cor_secundaria": cor_secundaria,
        "tipo_1": tipo_1,
        "tipo_2": tipo_2,
        "geracao": geracao,
        "peso": peso,
        "altura": altura,
        "detalhes_extras": detalhes_extras
    }
    return service.criar_pokemon(poke_data)
   
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@controller_poke.post('/batalha/enredo', status_code=200, tags=['batalha'])
async def gerar_enredo_batalha(user_poke_name: str, ai_poke_name: str) -> BatalhaHistoria:
  """
  Gera uma história para justificar uma batalha épica entre dois Pokémon.
  """
  try:
    # Carregar dados dos Pokémon a partir dos arquivos
    return service.gerar_enredo_batalha(user_poke_name, ai_poke_name)
  except FileNotFoundError as e:
    raise HTTPException(status_code=404, detail=f"Pokémon não encontrado: {e}")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

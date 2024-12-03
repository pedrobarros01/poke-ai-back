from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any
import os
from dotenv import load_dotenv
from ..libraries.PokeAi import PokeAi
from ..services.PokeService import PokeService
from ..models.Pokemon import Pokemon, BatalhaHistoria, IAForm, Ataque, FormPokemon

controller_poke = APIRouter()

# Inicializar a classe PokeAi com a chave da API a partir de uma variável de ambiente
load_dotenv()
api_key = os.getenv("GPT_API")
if not api_key:
  raise RuntimeError("A chave da API GPT_API não foi configurada.")

service = PokeService(api_key)

@controller_poke.post('/pokemon/gerar', status_code=200, tags=['pokemon'])
async def gerar_pokemon(
    info_poke: FormPokemon
) -> Pokemon:
  """
  Gera um Pokémon com seus detalhes, 4 ataques únicos e uma imagem baseada nos dados fornecidos.
  """
  try:
    # Montar os dados do Pokémon com as informações do formulário
    poke_data = {
        "base_corpo": info_poke.base_corpo,
        "cor_principal": info_poke.cor_principal,
        "cor_secundaria": info_poke.cor_secundaria,
        "tipo_1": info_poke.tipo_1,
        "tipo_2": info_poke.tipo_2,
        "geracao": info_poke.geracao,
        "peso": info_poke.peso,
        "altura": info_poke.altura,
        "detalhes_extras": info_poke.detalhes_extras
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
  

@controller_poke.post('/batalha/ia-escolhe', status_code=200, tags=['batalha'])
async def ia_escolhe_ataque(estado_batalha: IAForm) -> Ataque:

  try:
    return service.gerar_ataque_pokemon_ia(estado_batalha.ataques_ia, estado_batalha.stats_oponente)
  except FileNotFoundError as e:
    raise HTTPException(status_code=404, detail=f"Pokémon não encontrado: {e}")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

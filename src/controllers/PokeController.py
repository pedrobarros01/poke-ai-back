from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any
import os
from dotenv import load_dotenv
from libraries.PokeAi import PokeAi

controller_poke = APIRouter()

# Inicializar a classe PokeAi com a chave da API a partir de uma variável de ambiente
load_dotenv()
api_key = os.getenv("GPT_API")
if not api_key:
  raise RuntimeError("A chave da API GPT_API não foi configurada.")
poke_ai = PokeAi(api_key=api_key)


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
) -> Dict[str, Any]:
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

    # Gerar descrição e nome do Pokémon
    description, poke_name = poke_ai.poke_desc_generator(poke_data)

    # Gerar ataques para o Pokémon
    attacks = poke_ai.generate_attacks(poke_name)

    # Gerar a imagem do Pokémon
    image_url = poke_ai.poke_img_generator(description, poke_name)

    return {
        "nome": poke_name,
        "descricao": description,
        "attacks": attacks,
        "image_url": image_url
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@controller_poke.post('/batalha/enredo', status_code=200, tags=['batalha'])
async def gerar_enredo_batalha(user_poke_name: str, ai_poke_name: str) -> Dict[str, str | None]:
  """
  Gera uma história para justificar uma batalha épica entre dois Pokémon.
  """
  try:
    # Carregar dados dos Pokémon a partir dos arquivos
    user_poke = poke_ai.load_pokemon_by_name(user_poke_name)
    ai_poke = poke_ai.load_pokemon_by_name(ai_poke_name)

    # Gerar a história da batalha
    enredo = poke_ai.generate_battle_story(user_poke, ai_poke)

    return {"enredo": enredo}
  except FileNotFoundError as e:
    raise HTTPException(status_code=404, detail=f"Pokémon não encontrado: {e}")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

import os
from dotenv import load_dotenv

from libraries.PokeAi import PokeAi


if __name__ == '__main__':
    load_dotenv()
    GPT_API= os.getenv('GPT_API')

    poke_ai = PokeAi(GPT_API)

    dados_poke = {
        "base_corpo": "Raposa",
        "cor_principal": "Verde",
        "cor_secundaria": "Rosa",
        "tipo_1": "Fada",
        "tipo_2": "Dragão",
        "geracao": "1",
        "peso": 89,
        "altura": 2,
        "detalhes_extras": "Esta criatura surgiu nas florestas como a rainha das fadas."
    }

    descricao_poke, poke_name = poke_ai.poke_desc_generator(dados_poke)
    print(descricao_poke)
    imagem_pokemon = poke_ai.poke_img_generator(descricao_poke, poke_name)
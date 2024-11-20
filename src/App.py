import os
from dotenv import load_dotenv

from libraries.PokeAi import PokeAi


if __name__ == '__main__':
    load_dotenv()
    GPT_API= os.getenv('GPT_API')

    poke_ai = PokeAi(GPT_API)

    dados_pokemon = {
        "base_corpo": "Dragão",
        "cor_principal": "Vermelho",
        "cor_secundaria": "Preto",
        "tipo_1": "Fogo",
        "tipo_2": "Dark",
        "geracao": "1",
        "peso": 120,
        "altura": 2.3,
        "detalhes_extras": "Este Pokémon foi criado para proteger uma antiga civilização."
    }

    descricao_pokemon = poke_ai.poke_desc_generator(dados_pokemon)
    print(descricao_pokemon)
    imagem_pokemon = poke_ai.poke_img_generator(descricao_pokemon)
    nome_pokemon = poke_ai.get_pokemon_name(descricao_pokemon)

    pokemon = {
        "nome": nome_pokemon,
        "descricao": descricao_pokemon,
        "imagem": imagem_pokemon
    }

    poke_ai.save_pokemon_json(pokemon)
    poke_ai.save_pokemon_image(imagem_pokemon, pokemon)
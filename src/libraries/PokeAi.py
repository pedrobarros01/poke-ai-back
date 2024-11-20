import openai
import json
import os
import requests
import logging

class PokeAi:
    def __init__(self, api_key):    
        self.api_key = api_key
        openai.api_key = api_key

    def poke_desc_generator(self, poke_data):
        prompt = f"""
            Crie uma breve descrição de um Pokémon com as seguintes características:
            - Base do corpo: {poke_data['base_corpo']}
            - Cor principal: {poke_data['cor_principal']}
            - Cor secundária: {poke_data['cor_secundaria']}
            - Tipo 1: {poke_data['tipo_1']}
            - Tipo 2: {poke_data['tipo_2']}
            - Geração: {poke_data['geracao']}
            - Peso: {poke_data['peso']} kg
            - Altura: {poke_data['altura']} m
            - Detalhes extras: {poke_data['detalhes_extras']}
            Observação: no texto final, não cite o termo "pokemon", ao invés disso substitua por criatura. Sempre comece gerando o nome do Pokémon dessa forma "Nome: ".
         """
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        description = response.choices[0].message.content
        return description
    
    def poke_img_generator(self, description):
        prompt = f"""
            Crie uma pixel art de um monstrinho estilo jogo antigo com base nesta descrição:
            {description}
            O monstrinho deve estar virado para frente, olhando para tela.
            A imagem deve ter detalhes minimalistas mesmo sendo pixel art e deve ser num estilo cartunesco, infantilizado.
            O monstrinho deve ter uma aparência amigável e não assustadora, inspire-se em designs mais infantis e cartunescos, nada muito realista e amedrontador.
            O design do monstrinho pode ser inspirado em animes para crianças.
            A imagem deve ter um fundo branco, sem outros elementos além do monstrinho, nem texto.
            É IMPORTANTE QUE ELE SEJA AMIGÁVEL E CARTUNESCO.
        """
        
        response = openai.images.generate(
            prompt=prompt,
            size="1024x1024",
            model="dall-e-3",
            quality="standard",
        )

        image_url = response.data[0].url
        logging.info(f"Imagem gerada com sucesso: {image_url}")
        return image_url

    def get_pokemon_name(self, description):
        index = description.find("Nome: ")
        logging.info(f"Nome do Pokémon: {description[index + 6: description.find('\n', index)]}")
        return description[index + 6: description.find("\n", index)]
    
    def save_pokemon_json(self, pokemon):
        os.makedirs("pokes/descriptions", exist_ok=True)

        try:
            json_path = f"pokes/descriptions/{pokemon['nome']}.json"
            with open(json_path, "w") as file:
                json.dump(pokemon, file, indent=4)

            logging.info(f"JSON salvo com sucesso em {json_path}")

        except Exception as e:
            logging.error(f"Erro ao salvar o JSON: {e}")

    def save_pokemon_image(self, image_url, pokemon):
        os.makedirs("pokes/images", exist_ok=True)

        try:
            response = requests.get(image_url)
            response.raise_for_status()

            image_path = f"pokes/images/{pokemon['nome']}.png"
            with open(image_path, "wb") as file:
                file.write(response.content)
            
            logging.info(f"Imagem salva com sucesso em {image_path}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao salvar a imagem: {e}")

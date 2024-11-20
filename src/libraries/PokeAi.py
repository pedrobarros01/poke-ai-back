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
            Crie uma breve descrição de uma criatura com as seguintes características:
            - Base do corpo: {poke_data['base_corpo']}
            - Cor principal: {poke_data['cor_principal']}
            - Cor secundária: {poke_data['cor_secundaria']}
            - Tipo 1: {poke_data['tipo_1']}
            - Tipo 2: {poke_data.get('tipo_2', 'Nenhum')}
            - Geração: {poke_data['geracao']}
            - Peso: {poke_data['peso']} kg
            - Altura: {poke_data['altura']} m
            - Detalhes extras: {poke_data['detalhes_extras']}
            Observação: no texto final, não cite o termo "pokemon", ao invés disso substitua por criatura. Sempre comece gerando o nome da criatura dessa forma "Nome: ".
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

        full_description = response.choices[0].message.content

        poke_name = full_description.split("\n")[0].replace("Nome: ", "").strip()
        description = "\n".join(full_description.split("\n")[1:]).strip()

        description = description.replace("Descrição: ", "").strip()

        poke = {
            "nome": poke_name,
            "tipo_1": poke_data["tipo_1"],
            "tipo_2": poke_data.get("tipo_2"),
            "geracao": poke_data["geracao"],
            "peso": poke_data["peso"],
            "altura": poke_data["altura"],
            "descricao": description,
        }

        self.save_poke_json(poke, poke_name)

        return description, poke_name

    
    def poke_img_generator(self, description, poke_name):
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

        self.save_poke_image(image_url, poke_name)

        return image_url

    def get_poke_name(self, description):
        lines = description.split("\n")
        if lines and lines[0].startswith("Nome: "):
            return lines[0].replace("Nome: ", "").strip()
        return "Desconhecido"
    
    def save_poke_json(self, pokedex_info, poke_name):
        os.makedirs("pokes/descriptions", exist_ok=True)

        try:
            json_path = f"pokes/descriptions/{poke_name}.json"
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(pokedex_info, file, indent=4, ensure_ascii=False)

            logging.info(f"JSON salvo com sucesso em {json_path}")

        except Exception as e:
            logging.error(f"Erro ao salvar o JSON: {e}")
    
    def save_poke_image(self, image_url, poke_name):
        os.makedirs("pokes/images", exist_ok=True)

        try:
            image_path = f"pokes/images/{poke_name}.png"

            response = requests.get(image_url)
            response.raise_for_status()

            with open(image_path, "wb") as file:
                file.write(response.content)

            logging.info(f"Imagem salva com sucesso em {image_path}")

        except Exception as e:
            logging.error(f"Erro ao salvar a imagem: {e}")
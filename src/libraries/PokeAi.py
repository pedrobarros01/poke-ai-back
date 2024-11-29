import openai
import json
import os
import requests
import logging
import random
import ast


class PokeAi:
  def __init__(self, api_key):
    self.api_key = api_key
    openai.api_key = api_key

  def poke_desc_generator(self, poke_data):
    prompt = f"""
            Crie uma breve descrição, valores de ataque (atk), defesa (def) e saúde (hp) para uma criatura com as seguintes características:
            - Base do corpo: {poke_data['base_corpo']}
            - Cor principal: {poke_data['cor_principal']}
            - Cor secundária: {poke_data['cor_secundaria']}
            - Tipo 1: {poke_data['tipo_1']}
            - Tipo 2: {poke_data.get('tipo_2', 'Nenhum')}
            - Geração: {poke_data['geracao']}
            - Peso: {poke_data['peso']} kg
            - Altura: {poke_data['altura']} m
            - Detalhes extras: {poke_data['detalhes_extras']}
            Observação: no texto final, não cite o termo "pokemon", substitua por "criatura". Sempre inicie gerando o nome da criatura desta forma: "Nome: ".
            O retorno deve incluir:
            - Nome
            - Descrição
            - Valores de atk, def e hp (em uma linha separada no formato "atk: [valor], def: [valor], hp: [valor]").
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

    # Processar a resposta
    full_description = response.choices[0].message.content

    # Extrair nome da criatura
    poke_name = full_description.split("\n")[0].replace("Nome: ", "").strip()

    # Extrair descrição
    description = "\n".join(
        [line for line in full_description.split(
            "\n") if not line.startswith("atk:")]
    ).replace("Descrição: ", "").strip()

    # Extrair valores de atk, def e hp
    stats_line = [line for line in full_description.split(
        "\n") if line.startswith("atk:")][0]
    stats = {
        key.strip(): int(value.strip().replace(".", ""))  # Remover o ponto final
        for key, value in (stat.split(":") for stat in stats_line.split(","))
    }

    # Construir o Pokémon
    poke = {
        "nome": poke_name,
        "tipo_1": poke_data["tipo_1"],
        "tipo_2": poke_data.get("tipo_2"),
        "geracao": poke_data["geracao"],
        "peso": poke_data["peso"],
        "altura": poke_data["altura"],
        "descricao": description,
        "atk": stats["atk"],
        "def": stats["def"],
        "hp": stats["hp"],
    }

    # Salvar o Pokémon
    self.save_poke_json(poke, poke_name)

    return description, poke_name, stats["atk"], stats["def"], stats["hp"]

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

  def choose_user_pokemon(self):
    pokes = self.load_pokemons()
    if not pokes:
      print("Nenhum Pokémon encontrado! Criando um para você...")
      poke_data = self.generate_pokemon_data()
      _, poke_name = self.poke_desc_generator(poke_data)
      return self.load_pokemon_by_name(poke_name)

    print("Escolha seu Pokémon:")
    for i, poke in enumerate(pokes):
      print(
          f"{i + 1}. {poke['nome']} - Tipo: {poke['tipo_1']} / {poke.get('tipo_2', 'Nenhum')}")

    choice = int(input("Digite o número do Pokémon escolhido: ")) - 1
    return pokes[choice]

  def choose_ai_pokemon(self):
    pokes = self.load_pokemons()
    if not pokes:
      print("Nenhum Pokémon disponível para o adversário. Criando um novo...")
      poke_data = self.generate_pokemon_data()
      _, poke_name = self.poke_desc_generator(poke_data)
      return self.load_pokemon_by_name(poke_name)
    return random.choice(pokes)

  def load_pokemons(self):
    folder = "pokes/descriptions"
    if not os.path.exists(folder):
      return []

    pokes = []
    for file_name in os.listdir(folder):
      with open(os.path.join(folder, file_name), "r", encoding="utf-8") as file:
        pokes.append(json.load(file))
    return pokes

  def load_pokemon_by_name(self, poke_name):
    with open(f"pokes/descriptions/{poke_name}.json", "r", encoding="utf-8") as file:
      return json.load(file)

  def generate_pokemon_data(self):
    # Gere dados fictícios ou peça ao usuário para inserir
    return {
        "base_corpo": "Dragão",
        "cor_principal": "Azul",
        "cor_secundaria": "Vermelho",
        "tipo_1": "Fogo",
        "tipo_2": "Voador",
        "geracao": 1,
        "peso": 50.0,
        "altura": 2.0,
        "detalhes_extras": "Tem asas flamejantes.",
    }

  def generate_attacks(self, poke_name):
    # Supondo que a API esteja retornando ataques no formato correto
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em criar ataques de Pokémon."},
            {"role": "user", "content": f"Crie 4 ataques criativos e únicos para o Pokémon {poke_name}. me envie apenas os ataques em um dicionário python com as chaves 'nome', 'tipo' e 'dano' e nada mais. Por exemplo: {{'nome': 'bola de fogo', 'tipo': 'Fogo', 'dano': 50}}. O dano deve ser um número inteiro."}
        ]
    )

    # Processar a resposta e extrair os ataques
    content = response.choices[0].message.content

    # Ajustar o conteúdo para ser um formato válido de lista de dicionários
    # Remover a vírgula extra entre os dicionários e substituir quebras de linha
    content = "[{}]".format(content.replace('},\n', '},'))

    try:
      # Converte a string em lista de dicionários
      attacks = ast.literal_eval(content)
      print(f'{attacks=}')
    except Exception as e:
      print(f"Erro ao processar a resposta: {e}")
      attacks = []

    return attacks

  def generate_battle_story(self, user_poke, ai_poke):
    prompt = f"""
    Crie uma história para justificar uma batalha épica que irá ocorrer entre os seguintes dois Pokémons e seus treinadores:
    1. {user_poke['nome']} (Tipo: {user_poke['tipo_1']}/{user_poke['tipo_2']})
    2. {ai_poke['nome']} (Tipo: {ai_poke['tipo_1']}/{ai_poke['tipo_2']})
    Descreva com motivações e ações interessantes. 
    """

    try:
      response = openai.chat.completions.create(  # Corrigido para ChatCompletion
          model="gpt-4",  # Modelo compatível
          messages=[
              {"role": "system", "content": "Você é um mestre contador de histórias de batalhas de criaturas."},
              {"role": "user", "content": prompt}
          ],
          max_tokens=500  # Aumentando o limite de tokens
      )

      story = response.choices[0].message.content
      return story

    except Exception as e:
      print(f"Erro ao gerar história da batalha: {e}")
      return "Erro ao gerar história."

  def start_battle(self, user_poke, ai_poke):
    turn = 0
    while user_poke['hp'] > 0 and ai_poke['hp'] > 0:
      if turn % 2 == 0:  # Turno do jogador
        print(f"\nSeu turno! HP do adversário: {ai_poke['hp']}")
        for i, attack in enumerate(user_poke['attacks']):
          # Para cada ataque, extraímos o nome e o dano
          attack_name = attack['nome']
          damage = int(attack['dano'])
          print(f"{i + 1}. {attack_name} (Dano: {damage})")

        choice = int(input("Escolha seu ataque: ")) - 1
        # Novamente, extraímos o nome e o dano do ataque escolhido
        attack_chosen = user_poke['attacks'][choice]
        attack_name = attack_chosen['nome']
        damage = int(attack_chosen['dano'])
        ai_poke['hp'] -= damage
        print(f"Você usou {attack_name}! Causou {damage} de dano.")
      else:  # Turno da AI
        ai_attack = random.choice(ai_poke['attacks'])
        # Extrai o nome e dano do ataque da AI
        attack_name = ai_attack['nome']
        damage = int(ai_attack['dano'])
        user_poke['hp'] -= damage
        print(f"\nAdversário usou {attack_name}! Causou {damage} de dano.")

      turn += 1

    if user_poke['hp'] <= 0:
      print("\nVocê perdeu a batalha!")
    else:
      print("\nVocê venceu a batalha!")

  def battle(self):
    user_poke = self.choose_user_pokemon()
    ai_poke = self.choose_ai_pokemon()

    # Atribuir HP inicial
    user_poke['hp'] = 200
    ai_poke['hp'] = 200

    # Gerar ataques para ambos os Pokémons
    user_poke['attacks'] = self.generate_attacks(user_poke['nome'])
    print(f'{user_poke=}')
    ai_poke['attacks'] = self.generate_attacks(ai_poke['nome'])
    print(f'{ai_poke=}')

    # Gerar narrativa da batalha
    story = self.generate_battle_story(user_poke, ai_poke)
    print(story)

    # Iniciar a batalha
    self.start_battle(user_poke, ai_poke)

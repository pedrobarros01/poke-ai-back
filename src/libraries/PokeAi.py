import openai
import json
import os
import requests
import logging
import random
import ast
from ..models.Pokemon import Ataque, StatsPokemon

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
            - Valores de atk, def, hp e velocidade (em uma linha separada no formato "atk: [valor], def: [valor], hp: [valor], velocidade: [valor]").
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


    return description, poke_name, stats["atk"], stats["def"], stats["hp"], stats["velocidade"]

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


    return image_url

  def generate_attacks(self, poke_name, type_1, type_2):
    # Supondo que a API esteja retornando ataques no formato correto

    valid_types = [
            "bug", "dark", "dragon", "electric", "fairy", "fighting", "fire", "flying",
            "ghost", "grass", "ground", "ice", "normal", "poison", "psychic", "rock",
            "steel", "water"
        ]

    response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em criar ataques de Pokémon."},
                {"role": "user", "content": f"""Crie 4 ataques criativos e únicos para o Pokémon {poke_name} 
                com os tipos {type_1} e {type_2}. Retorne apenas os ataques em um array de objetos/dicionários, 
                sem id para cada objeto. Cada objeto deve conter as chaves 'nome', 'tipo' e 'dano' e nada mais. 
                Por exemplo: {{'nome': 'Bola de Fogo', 'tipo': 'Fire', 'dano': 50}}. O dano deve ser um número inteiro 
                entre 10 e 150. Certifique-se de que o tipo seja um destes: {', '.join(valid_types)}."""}
            ]
      )

    # Processar a resposta e extrair os ataques
    content = response.choices[0].message.content

    try:
      # Converte a string em lista de dicionários
      attacks = ast.literal_eval(content)
      print(f'{attacks=}')
    except Exception as e:
      print(f"Erro ao processar a resposta: {e}")
      attacks = []

    return attacks 
  
  def gpt_escolhe_ataque(self, ataques_ia: list[Ataque], stats_pokemon_user: StatsPokemon) -> str:
    prompt = 'Baseado em uma batalha pokemon, dado esses ataques: '
    for i, ataque in enumerate(ataques_ia):
      prompt += f' Atq {i} -> nome: {ataque.nome}, tipo: {ataque.tipo}, dano: {ataque.dano} \n'
    prompt += f' e dado os estados do seu oponente: hp {stats_pokemon_user.hp}, ataque: {stats_pokemon_user.ataque}, defesa: {stats_pokemon_user.defesa}, tipo1: {stats_pokemon_user.tipo1} e tipo2: {stats_pokemon_user.tipo2 if stats_pokemon_user.tipo2 else "Não tem"}\n'
    prompt += f'me diga qual o nome do melhor ataque para atacar esse oponente. Só me diga o nome do ataque'
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
    ataque_escolhido = response.choices[0].message.content
    return ataque_escolhido
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
from libraries.PokeAi import PokeAi
from models.Pokemon import Pokemon, BatalhaHistoria, Ataque, StatsPokemon
class PokeService:
    def __init__(self, api_key) -> None:
        self.poke_ai = PokeAi(api_key)


    def criar_pokemon(self, poke_data) -> Pokemon:
        # Gerar descrição e nome do Pokémon
        description, poke_name, stat_atk, stat_def, stat_hp = self.poke_ai.poke_desc_generator(
            poke_data)

        # Gerar ataques para o Pokémon
        attacks = self.poke_ai.generate_attacks(poke_name)

        # Gerar a imagem do Pokémon
        image_url = self.poke_ai.poke_img_generator(description, poke_name)

        return Pokemon(nome=poke_name, 
                       descricao=description, 
                       movimento=attacks, 
                       ataque=stat_atk, 
                       defesa=stat_def, 
                       hp=stat_hp, 
                       sprite=image_url)
    
    def gerar_enredo_batalha(self, poke1_name: str, poke2_name: str):
        user_poke = self.poke_ai.load_pokemon_by_name(poke1_name)
        ai_poke = self.poke_ai.load_pokemon_by_name(poke2_name)

        # Gerar a história da batalha
        enredo = self.poke_ai.generate_battle_story(user_poke, ai_poke)

        return BatalhaHistoria(enredo=enredo)
    
    def gerar_ataque_pokemon_ia(self, ataques_ia: list[Ataque], stats_pokemon_user: StatsPokemon) -> str:
        nome_ataque_escolhido = self.poke_ai.gpt_escolhe_ataque(ataques_ia, stats_pokemon_user)
        ataque = filter(lambda x:  x.nome == nome_ataque_escolhido , ataques_ia)
        return ataque[0].nome
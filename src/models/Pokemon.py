from pydantic import BaseModel, Field
from typing import Optional

class FormPokemon(BaseModel):
    base_corpo: str = Field(..., description="Base do corpo do Pokémon")
    cor_principal: str = Field(..., description="Cor principal do Pokémon")
    cor_secundaria: str = Field(..., description="Cor secundária do Pokémon")
    tipo_1: str = Field(..., description="Primeiro tipo do Pokémon")
    tipo_2: Optional[str] = Field(None, description="Segundo tipo do Pokémon (opcional)")
    geracao: int = Field(..., description="Geração do Pokémon")
    peso: float = Field(..., description="Peso do Pokémon em kg")
    altura: float = Field(..., description="Altura do Pokémon em metros")
    detalhes_extras: str = Field(..., description="Detalhes adicionais sobre o Pokémon")

class Ataque(BaseModel):
    nome: str
    tipo: str
    dano: int

class Pokemon(BaseModel):
    nome: str
    descricao: str
    movimento: list[Ataque]
    ataque: int
    defesa: int
    hp: int
    velocidade: int
    sprite: str | None


class BatalhaHistoria(BaseModel):
    enredo: str


class StatsPokemon(BaseModel):
    tipo1: str
    tipo2: str | None
    hp: int
    ataque: int
    defesa: int

class IAForm(BaseModel):
    ataques_ia: list[Ataque]
    stats_oponente: StatsPokemon
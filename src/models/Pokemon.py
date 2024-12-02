from pydantic import BaseModel    

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
    sprite: str | None


class BatalhaHistoria(BaseModel):
    enredo: str


class StatsPokemon(BaseModel):
    tipo1: str
    tipo2: str | None
    hp: int
    ataque: int
    defesa: int
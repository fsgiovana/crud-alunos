from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

# conexao com o mongodb
cliente = MongoClient(os.getenv("MONGODB_URI"))
banco = cliente["crud_alunos"]
alunos = banco["alunos"]

app = FastAPI(title="API de alunos")

# dados - aluno
class Aluno(BaseModel):
    nome: str
    idade: int
    curso: str


# cadastro - aluno
@app.post("/alunos", status_code=201)
def cadastrar(aluno: Aluno):
    resultado = alunos.insert_one(aluno.model_dump())
    return {"id": str(resultado.inserted_id), "mensagem": "aluno cadastrado"}


# lista - aluno
@app.get("/alunos")
def listar():
    lista = []

    for aluno in alunos.find():
        aluno["id"] = str(aluno.pop("_id"))
        lista.append(aluno)

    return lista


# consultar - aluno 
@app.get("/alunos/{id}")
def consultar(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalido")

    aluno = alunos.find_one({"_id": ObjectId(id)})

    if aluno is None:
        raise HTTPException(status_code=404, detail="aluno nao encontrado")

    aluno["id"] = str(aluno.pop("_id"))
    return aluno


# atualizar - aluno
@app.put("/alunos/{id}")
def atualizar(id: str, aluno: Aluno):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalido")

    resultado = alunos.update_one(
        {"_id": ObjectId(id)},
        {"$set": aluno.model_dump()}
    )

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="aluno nao encontrado")

    return {"mensagem": "aluno atualizado"}


# excluir - aluno
@app.delete("/alunos/{id}")
def excluir(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalido")

    resultado = alunos.delete_one({"_id": ObjectId(id)})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="aluno nao encontrado")

    return {"mensagem": "aluno excluido!"}
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from bson.errors import InvalidId 



def conectar_bd():
    uri = "mongodb://localhost:27017/"
    try:
        cliente = MongoClient(uri)
        cliente.admin.command('ping')
        return cliente
    except ConnectionFailure as e:
        print(f"Error al conectar a la base de datos MongoDB: {e}")
        return None

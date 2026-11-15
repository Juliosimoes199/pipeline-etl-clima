import requests
import json
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_weather_data(url:str) -> list:
    
    response = requests.get(url)
    
    if response.status_code != 200:
        logging.error("Erro na requisição")
        
        return []
    
    data = response.json()
    
    if not data:
        logging.warning("A requisição não retornou nada")
        return []
    
    output_path = Path(__file__).resolve().parent.parent / "data" / "weather_data.json" # Lugar aonde vou salvar os dados e o seu nome
    output_dir = Path(output_path).parent # O parâmetro "parent" é igual o comando "cd ../"
    output_dir.mkdir(parents=True, exist_ok=True) # Criando efectivamente os caminhos e o arquivo
    
    with open(output_path, "w") as f:
        
        json.dump(data, f, indent=4) # Escrevendo no arquivo {data: recebe o json, f: o arquivo criado}
        
    logging.info(f"Arquivo salvo em {output_path}")
        
    return data


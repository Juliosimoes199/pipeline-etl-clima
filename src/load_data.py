from sqlalchemy import create_engine, text # Para se conectar com o banco de dados
from urllib.parse import quote_plus # Para garantir segurança na interpretação da nossa senha de banco de dados
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(env_path)

user = os.getenv("user")
password = os.getenv("password")
database = os.getenv("database")
# Dentro do Docker, "localhost" é o próprio container. O compose define
# DB_HOST=host.docker.internal para chegar ao Postgres do teu PC.
host = os.getenv("DB_HOST", "localhost")

def get_engine():
    logging.info(f"Conectado em {host}:5432/{database}")
    return create_engine(
        f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5432/{database}"
    )
    

def load_weather_data(tabela_name:str, df):
    engine = get_engine()
    df.to_sql(
        name=tabela_name,
        con=engine,
        if_exists="append",
        index=False
    )
    logging.info("Dados carregados com sucesso")
    
    df_check = pd.read_sql(f'SELECT * FROM {tabela_name}', con=engine)
    logging.info(f"Total de registo na tabela {len(df_check)}")
from datetime import datetime, timedelta
from airflow.sdk import dag, task
from pathlib import Path
from dotenv import load_dotenv
import sys, os


sys.path.insert(0, '/opt/airflow/src') # Registrar o nosso caminho do src dentro do ambiente de desenvolvimento

# Os imports de pandas/sqlalchemy ficam DENTRO das tasks: assim o dag-processor
# não carrega bibliotecas pesadas a cada vez que lê este ficheiro.

env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("api_key")

url = f'https://api.openweathermap.org/data/2.5/weather?q=Sao Paulo,BR&units=metric&appid={API_KEY}'

@dag(
    dag_id="youtube_tutorial",
    default_args={
        "owner": "airflow", # O responsavel
        "depends_on_past":False, # A tarefa de hoje depende de ontem para rodar? False: Não
        "retries":2, # Duas tentativas se caso der erro
        "retry_delay":timedelta(minutes=5) # Com um tempo de espera de 5 minutos
    },
    description= "Pipeline ETL - Clima SP", # Descrição
    schedule= "0 */1 * * * ", # 0 -> minuto; */1 -> hora; * -> dia do mês; * -> é o mês; * -> dia da semana
    start_date=datetime(2026, 11, 7), # O dia que estou construindo o fluxo
    catchup=False, # Não quero que rode execuções passadas
    tags = ["weather", "etl", "Bora pra cima"]
)

def weather_pipeline():
    @task
    def extract():
        from extract_data import extract_weather_data
        extract_weather_data(url)
        
    @task
    def transform():
        from transform_data import data_transformations
        df = data_transformations()
        df.to_parquet("/opt/airflow/data/temp_data.parquet", index=False) # persistindo os dados porque as task não conseguem se comunicar cada task roda de forma isolada
        
    @task
    def save():
        import pandas as pd
        from load_data import load_weather_data
        df = pd.read_parquet("/opt/airflow/data/temp_data.parquet")
        load_weather_data("sp_weather", df)
        
    extract() >> transform() >> save()
    
    
weather_pipeline()
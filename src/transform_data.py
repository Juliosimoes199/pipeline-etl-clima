import pandas as pd
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

path_name = Path(__file__).parent.parent / "data" / "weather_data.json" # Criando o caminho novamente que é igual a isso "../data/weather_data.json"

columns_name_to_drop = ["weather", "weather_icon", "sys.type"]
columns_names_to_rename = {
        "base": "base",
        "visibility": "visibility",
        "dt": "datetime",
        "timezone": "timezone",
        "id": "city_id", 
        "name": "city_name",
        "cod": "code",
        "coord.lon": "longitude",
        "coord.lat": "latitude",
        "main.temp": "temperature",
        "main.feels_like": "feels_like",
        "main.temp_min": "temp_min",
        "main.temp_max": "temp_max",
        "main.pressure": "pressure",
        "main.humidity": "humidity",
        "main.sea_level": "sea_level",
        "main.grnd_level": "grnd_level",
        "wind.speed": "wind_speed",
        "wind.deg": "wind_deg",
        "wind.gust": "wind_gust",
        "clouds.all": "clouds", 
        "sys.type": "sys_type",                 
        "sys.id": "sys_id",                
        "sys.country": "country",                
        "sys.sunrise": "sunrise",                
        "sys.sunset": "sunset",
        # Campos opcionais: a API só os envia quando chove/neva
        "rain.1h": "rain_1h",
        "snow.1h": "snow_1h",
        # weather_id, weather_main, weather_description 
    }

# Esquema fixo da tabela. Colunas que a API não enviar ficam vazias (NULL),
# colunas novas/inesperadas são descartadas. Assim o INSERT nunca muda de forma.
final_columns = [
    "base", "visibility", "datetime", "timezone", "city_id", "city_name", "code",
    "longitude", "latitude", "temperature", "feels_like", "temp_min", "temp_max",
    "pressure", "humidity", "sea_level", "grnd_level", "wind_speed", "wind_deg",
    "wind_gust", "rain_1h", "snow_1h", "clouds", "sys_id", "country", "sunrise",
    "sunset", "weather_id", "weather_main", "weather_description",
]

columns_to_normalize_datetime = ["datetime", "sunrise", "sunset"]

# Função para criar o dataframe 
def created_dataframe(path_name:str) -> pd.DataFrame:
    logging.info("Criando DataFrame do arquivo Json...")
    
    path = path_name
    
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encntrado: {path}")
    
    with open(path) as f:
        data = json.load(f)
        
    df = pd.json_normalize(data)
    logging.info(f"Dataframe criando com {len(df)} linhas")
    
    return df

#função para normalizar o dataframe
def normalizer_weather_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_weather = pd.json_normalize(df["weather"].apply(lambda x: x[0])) # Itera nessa coluna e pega o primeiro item
    
    df_weather = df_weather.rename(columns={
        "id": "weather_id",
        "main": "weather_main",
        "description": "weather_description",
        "icon": "weather_icon"
    })
    
    df = pd.concat([df, df_weather], axis=1)
    logging.info(f"Coluna Weather foi normalizada - {len(df.columns)} colunas")
    
    return df
    
def drop_columns(df: pd.DataFrame, columns_name: list[str]) -> pd.DataFrame:  
    
    logging.info(f"Removendo Colunas: {columns_name}...")
    df = df.drop(columns=columns_name, errors="ignore") # ignora colunas que não vieram
    logging.info(f"Colunas foram removidas - {len(df.columns)} colunas restantes")
    
    return df

def rename_columns(df:pd.DataFrame, columns_name:dict[str,str]) -> pd.DataFrame:
    logging.info(f"Renomenado {len(columns_name)} colunas")
    df = df.rename(columns=columns_name)
    logging.info(f"Colunas renomeadas")
    return df

def normalize_datetime_columns(df:pd.DataFrame, columns_name:list[str]) -> pd.DataFrame:
    logging.info(f"Convertendo colunas para Datetime: {columns_name}")
    for name in columns_name:
        df[name] = pd.to_datetime(df[name], unit="s", utc=True).dt.tz_convert("America/Sao_Paulo")
    logging.info("Colunas convertidas para datetime")
    
    return df


def data_transformations():
    
    logging.info("Iniciando transformações")
    
    df = created_dataframe(path_name)
    df = normalizer_weather_columns(df)
    df = drop_columns(df, columns_name_to_drop)
    df = rename_columns(df, columns_names_to_rename)
    df = normalize_datetime_columns(df, columns_to_normalize_datetime)
    df = df.reindex(columns=final_columns) # garante sempre as mesmas colunas
    logging.info("Transformações concluidas")
    return df


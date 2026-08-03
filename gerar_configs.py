import os
import json
import random

os.makedirs("config", exist_ok=True)

perfis = [
    {"tipo": "caldeira", "base": 45.0},
    {"tipo": "estufa", "base": 35.0},
    {"tipo": "camara_fria", "base": -5.0},
    {"tipo": "ambiente", "base": 24.0}
]

for i in range(1, 31):
    perfil = random.choice(perfis)
    config = {
        "sensor_id": i,
        "base_temp": perfil["base"],
        "intervalo_envio_s": 0.1,
        "broker_ip": "127.0.0.1",
        "broker_porta": 1883  # Incluído com 'a' para compatibilidade total
    }
    
    with open(f"config/sensor_{i}.json", "w") as f:
        json.dump(config, f, indent=4)

print("✅ 30 arquivos JSON atualizados e gerados na pasta 'config/'!")
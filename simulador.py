import threading
import time
import random
import json
import paho.mqtt.client as mqtt

def sensor_worker(sensor_id):
    """
    Função executada por cada thread. Cada sensor possui
    sua própria vida, própria conexão MQTT e seu próprio
    arquivo de configuração.
    """
    caminho_arquivo = f"config/sensor_{sensor_id}.json"
    
    # 1. Leitura dinâmica do JSON
    with open(caminho_arquivo, 'r') as f:
        config = json.load(f)
    
    # 2. Configuração do cliente MQTT (usando Callback API v2 para evitar avisos)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    
    # Conectando usando a chave unificada 'broker_porta'
    client.connect(config['broker_ip'], config['broker_porta'], 60)
    
    print(f"[SENSOR {sensor_id}] Conectado ao broker. Iniciando transmissão...")

    while True:
        # Simulação física: Temperatura oscila levemente
        temp = config['base_temp'] + random.uniform(-1.0, 1.0)
        
        # 3. Lógica de injeção de anomalias (1% de chance de superar 60°C)
        if random.random() < 0.01:
            temp = random.uniform(62.0, 85.0)

        payload_dict = {
            "id": sensor_id,
            "temp": round(temp, 2),
            "timestamp": time.time()
        }
        
        # 4. Serialização e Publicação
        string_json = json.dumps(payload_dict)
        topico = f"factory/sensors/{sensor_id}"
        
        client.publish(topico, string_json, qos=0)
        
        # Respeita o intervalo configurado no JSON (0.1s)
        time.sleep(config.get('intervalo_envio_s', 0.1))

if __name__ == "__main__":
    TOTAL_SENSORES = 30
    threads_lista = []
    
    print(f"[*] Inicializando o ecossistema de simulação com {TOTAL_SENSORES} sensores...")

    # 5. Disparando as Threads em larga escala
    for i in range(1, TOTAL_SENSORES + 1):
        t = threading.Thread(target=sensor_worker, args=(i,))
        threads_lista.append(t)
        t.start()

    print(f"[*] Sucesso! {TOTAL_SENSORES} threads de sensores rodando em background.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Desligando simulador de sensores.")
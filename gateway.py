import paho.mqtt.client as mqtt
import threading
import time
import json
import smtplib
from email.message import EmailMessage
import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# ---------------------------------------------------------
# SEÇÃO 7: CONFIGURAÇÃO DO FIREBASE (Cloud Integration)
# ---------------------------------------------------------

FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")

try:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DB_URL
    })
    firebase_ativo = True
    print("[NUVEM] Conectado ao Firebase com sucesso!")
except Exception as e:
    firebase_ativo = False
    print(f"[AVISO NUVEM] Firebase não inicializado ({e}). Rodando modo local.")

def send_to_cloud(average_data):
    """Função solicitada na Seção 7 para persistir o histórico de médias na nuvem"""
    if firebase_ativo:
        ref = db.reference('/factory_stats')
        ref.push(average_data)

# ---------------------------------------------------------
# SEÇÃO 8: ALERTA POR E-MAIL (SMTP)
# ---------------------------------------------------------
def send_alert_email(sensor_id, temp):
    """Função solicitada na Seção 8 para disparar alerta imediato de superaquecimento"""
    EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
    EMAIL_SENHA = os.getenv("EMAIL_SENHA")
    EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO")
    
    msg = EmailMessage()
    msg.set_content(f"ALERTA: Sensor {sensor_id} detectou temperatura crítica: {temp}°C!")
    msg['Subject'] = 'Emergência Industrial - Superaquecimento'
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINATARIO
    
    try:
        # Configurar servidor SMTP e enviar (conforme orientação da Seção 8)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        print(f"📧 [SMTP] E-mail de emergência enviado com sucesso para o sensor {sensor_id}!")
    except Exception as e:
        print(f"❌ [ERRO SMTP] Falha ao enviar e-mail: {e}")

# Buffer em memória e controle de concorrência
buffer_dados = []
lock_buffer = threading.Lock()

BROKER_MQTT = "localhost"
PORTA_BROKER = 1883
TOPICO_FILTRO = "factory/sensors/+"

def ao_receber_mensagem(client, userdata, msg):
    texto_recebido = msg.payload.decode()
    try:
        dados_sensor = json.loads(texto_recebido)
    except json.JSONDecodeError:
        return

    sensor_id = dados_sensor.get('id')
    temperatura = dados_sensor.get('temp')

    with lock_buffer:
        buffer_dados.append(dados_sensor)

    # CAMINHO CRÍTICO: Reação imediata se a temperatura ultrapassar 60°C
    if temperatura and temperatura > 60.0:
        print(f"\n🔥 [CAMINHO CRÍTICO] Anomalia detectada! Sensor {sensor_id} a {temperatura}°C")
        # Descomente a linha abaixo para disparar o e-mail real configurado acima
        # send_alert_email(sensor_id, temperatura)

def processador_estatistico_borda():
    print("[*] Thread de processamento na borda (Tumbling Window) ativada.")
    
    while True:
        time.sleep(1) # Janela de tempo de 1 segundo

        with lock_buffer:
            total_pacotes_no_segundo = len(buffer_dados)
            if total_pacotes_no_segundo > 0:
                soma_temperaturas = sum([item['temp'] for item in buffer_dados])
                media_final = soma_temperaturas / total_pacotes_no_segundo
                
                print(f"\n[EDGE LOG] Janela de 1s encerrada. Pacotes Locais Recebidos: {total_pacotes_no_segundo}")
                print(f"[EDGE LOG] Média consolidada da fábrica: {media_final:.2f}°C")

                # Estrutura de dados padrão enviada para a nuvem
                average_data = {
                    'timestamp': time.time(),
                    'media_temperatura': round(media_final, 2),
                    'total_amostras': total_pacotes_no_segundo
                }
                
                # Chamada da função da Seção 7
                send_to_cloud(average_data)

                economia_lote = (1 - (1 / total_pacotes_no_segundo)) * 100
                print(f"[ECONOMIA DE BANDA] Lote reduzido de {total_pacotes_no_segundo} msgs para 1 resumo na Nuvem. Redução de {economia_lote:.2f}% neste segundo.")

                buffer_dados.clear()
            else:
                print("[EDGE LOG] Nenhum dado de sensor recebido no último segundo. Aguardando...")

if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = ao_receber_mensagem

    client.connect(BROKER_MQTT, PORTA_BROKER, 60)
    client.subscribe(TOPICO_FILTRO)
    
    print(f"[*] Gateway inscrito com sucesso no tópico: {TOPICO_FILTRO}")

    thread_borda = threading.Thread(target=processador_estatistico_borda)
    thread_borda.daemon = True
    thread_borda.start()

    client.loop_forever()
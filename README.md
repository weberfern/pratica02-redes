# Prática 02 - Programação em Ambiente de Rede

Projeto em Python para simulação de uma fábrica com sensores distribuídos, comunicação MQTT, processamento na borda, integração com Firebase e estrutura para alerta por e-mail.

## Visão geral

O sistema é composto por três partes principais:

- **gerador de configurações**: cria os arquivos JSON de cada sensor em `config/`.
- **simulador de sensores**: executa múltiplas threads, publica leituras de temperatura via MQTT e injeta anomalias aleatórias.
- **gateway**: recebe as mensagens MQTT, consolida dados em janela temporal, envia resumos para a nuvem e mantém a base para alertas críticos.

## Funcionalidades

- Simulação de **30 sensores** concorrentes.
- Publicação de dados no broker MQTT local (`127.0.0.1:1883`).
- Geração automática de configuração individual para cada sensor.
- Detecção de leituras críticas acima de 60°C.
- Consolidação estatística em janela de 1 segundo.
- Integração com Firebase Realtime Database.
- Estrutura para envio de alerta por e-mail via SMTP.

## Estrutura do projeto

- `gateway.py`: consumidor MQTT e processamento na borda.
- `simulador.py`: simulação dos sensores.
- `gerar_configs.py`: geração dos arquivos de configuração.
- `config.json`: parâmetros gerais do ecossistema.
- `config/`: arquivos individuais `sensor_1.json` até `sensor_30.json`.
- `.env`: variáveis sensíveis e credenciais de execução local.
- `config/serviceAccountKey.json`: chave da conta de serviço do Firebase.

## Requisitos

- Python 3.10+.
- Broker MQTT local em execução na porta `1883`.
- Conta e projeto Firebase configurados, caso deseje usar a integração com a nuvem.

## Instalação

1. Crie e ative um ambiente virtual, se desejar.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

Antes de executar o gateway, configure o arquivo `.env` com as variáveis esperadas pelo projeto:

- `FIREBASE_KEY_PATH`
- `FIREBASE_DB_URL`
- `EMAIL_REMETENTE`
- `EMAIL_SENHA`
- `EMAIL_DESTINATARIO`

O arquivo `config/serviceAccountKey.json` deve apontar para a chave válida da conta de serviço do Firebase.

## Execução

1. Gere ou regenere os arquivos dos sensores, se necessário:

```bash
python gerar_configs.py
```

2. Inicie o simulador de sensores:

```bash
python simulador.py
```

3. Em outro terminal, execute o gateway:

```bash
python gateway.py
```

## Observações

- O repositório ignora `.env` e `config/serviceAccountKey.json` para evitar o envio de segredos.
- O alerta por e-mail está implementado, mas a chamada automática pode ser habilitada no código quando necessário.

## Integrantes

| Nome completo | Matrícula |
| --- | --- |
| Everlir Richardson da Silva | 2023009842 |
| Genildo da Silva Ferreira | 2025013782 |
| Jefferson Rodrigues de Oliveira | 2025013432 |
| José Valbério da Silva Sousa | 2023009691 |
| Maria Fernanda Sousa Silva | 2025019580 |
| Weber Fernandes da Silva | 2025019356 |
| Yan Brasil Angelim de Brito | 2025019024 |

## Dependências principais

- `paho-mqtt`
- `firebase_admin`
- `python-dotenv`

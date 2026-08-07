# 🚀 Prática 02 - Programação em Ambiente de Rede

Projeto em Python para simulação de uma fábrica com sensores distribuídos, comunicação MQTT, processamento na borda, integração com Firebase e estrutura para alerta por e-mail.

## 📘 Visão geral

O sistema é composto por três partes principais:

- **gerador de configurações**: cria os arquivos JSON de cada sensor em `config/`.
- **simulador de sensores**: executa múltiplas threads, publica leituras de temperatura via MQTT e injeta anomalias aleatórias.
- **gateway**: recebe as mensagens MQTT, consolida dados em janela temporal, envia resumos para a nuvem e mantém a base para alertas críticos.

## ⚙️ Funcionalidades

- Simulação de **30 sensores** concorrentes.
- Publicação de dados no broker MQTT local (`127.0.0.1:1883`).
- Geração automática de configuração individual para cada sensor.
- Detecção de leituras críticas acima de 60°C.
- Consolidação estatística em janela de 1 segundo.
- Integração com Firebase Realtime Database.
- Estrutura para envio de alerta por e-mail via SMTP.

## 📂 Estrutura do projeto

- `gateway.py`: consumidor MQTT e processamento na borda.
- `simulador.py`: simulação dos sensores.
- `gerar_configs.py`: geração dos arquivos de configuração.
- `config.json`: parâmetros gerais do ecossistema.
- `config/`: arquivos individuais `sensor_1.json` até `sensor_30.json`.
- `.env`: variáveis sensíveis e credenciais de execução local.
- `config/serviceAccountKey.json`: chave da conta de serviço do Firebase.

## ✅ Requisitos

- Python 3.10+.
- Broker MQTT local em execução na porta `1883`.
- Conta e projeto Firebase configurados, caso deseje usar a integração com a nuvem.

## 🛠️ Instalação

1. Crie e ative um ambiente virtual, se desejar.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## 🔧 Configuração

Antes de executar o gateway, configure o arquivo `.env` com as variáveis esperadas pelo projeto:

- `FIREBASE_KEY_PATH`
- `FIREBASE_DB_URL`
- `EMAIL_REMETENTE`
- `EMAIL_SENHA`
- `EMAIL_DESTINATARIO`

O arquivo `config/serviceAccountKey.json` deve apontar para a chave válida da conta de serviço do Firebase.

## ▶️ Execução

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

## 📝 Observações

- O repositório ignora `.env` e `config/serviceAccountKey.json` para evitar o envio de segredos.
- O alerta por e-mail está implementado, mas a chamada automática pode ser habilitada no código quando necessário.

## Resposta às Questões para Análise (Seção 9)

**I. Economia de Banda**

**Calcule matematicamente a porcentagem de economia de banda alcançada pelo seu Gateway.**

**Resposta:** A arquitetura proposta utiliza o processamento na borda (Edge Analytics) por meio de uma Tumbling Window (janela temporal) de 1 segundo. No cenário simulado, temos 30 sensores operando com um intervalo de envio de 100 ms (0,1 s). Sendo assim, cada sensor envia 10 mensagens por segundo, totalizando 300 mensagens brutas recebidas pelo Gateway localmente a cada segundo. Ao invés de trafegar todas essas mensagens para a nuvem, o Gateway consolida os dados em uma média aritmética e envia apenas 1 pacote contendo o resumo estatístico. A economia de banda gerada é calculada da seguinte forma:

![Fórmula de economia de dados](https://drive.google.com/file/d/1eVg90nCSqbVtxpD3OVSOEPdQ_juO6RAp/view?usp=sharing)

**II. Latência de Alerta**

**No seu teste, quanto tempo levou entre o sensor detectar a anomalia e o e-mail chegar (ou ser processado pelo Gateway)? Por que esse tempo é menor do que se o sensor tivesse que enviar o dado para a Nuvem e a Nuvem disparar o e-mail?**

**Resposta:** O processamento da anomalia (temperatura > 60 °C) ocorre na ordem de milissegundos. Isso acontece porque a verificação do "Caminho Crítico" foi implementada diretamente na função de callback de recebimento do protocolo MQTT (on_message), reagindo instantaneamente à chegada do pacote sem aguardar o fechamento da janela de 1 segundo. Esse tempo é drasticamente menor do que uma arquitetura centralizada na nuvem porque elimina o Round-Trip Time (RTT). Enviar para a nuvem exigiria que o dado passasse pela rede externa, sofresse com a latência da internet, fosse processado por um servidor remoto e, só então, gerasse o gatilho de alerta, adicionando riscos de atraso que são inaceitáveis para a segurança de máquinas industriais.

**III. Falha de Conectividade**

**Se a conexão com a internet cair, seu Gateway para de funcionar? Quais funcionalidades continuariam ativas localmente?**

**Resposta:** Não, o Gateway continua operando de forma autônoma. Devido à sua natureza de Edge Computing, a dependência da internet restringe-se exclusivamente ao envio do resumo para o banco de dados (Firebase). Se houver interrupção de rede, as seguintes funcionalidades locais continuam 100% ativas: a recepção dos dados dos sensores via broker MQTT local, o armazenamento no buffer em memória, o cálculo das médias pela thread cronometrada e, principalmente, a detecção de anomalias no Caminho Crítico, garantindo que a fábrica continue sendo monitorada contra superaquecimentos mesmo totalmente offline.

**IV. Escalabilidade**

**Se em vez de 30 sensores, tivéssemos 3.000 sensores enviando dados a cada 10 ms, qual seria o principal gargalo do seu código atual? Como você resolveria isso usando conceitos de sistemas distribuídos?**

**Resposta:** Com 3.000 sensores a 10 ms, o sistema receberia 300.000 mensagens por segundo. O principal gargalo da implementação atual seria a saturação de concorrência. O uso de um único threading.Lock() geraria uma fila de espera massiva (lock contention) bloqueando a recepção de novas mensagens. Além disso, a memória do buffer_dados estouraria rapidamente e um único broker Mosquitto não suportaria a carga de conexões simultâneas.

Para resolver isso utilizando conceitos de sistemas distribuídos, a solução envolveria:

- Particionamento de Dados: substituir o MQTT simples por uma plataforma de streaming distribuída como o Apache Kafka.
- Balanceamento de Carga e Múltiplos Gateways: dividir a fábrica em zonas físicas (por exemplo, 500 sensores por zona), atribuindo um Gateway independente para cada setor (arquitetura Fog Computing descentralizada).
- Caches Distribuídos: utilizar ferramentas como Redis para gerenciar o estado do buffer, em vez de depender da memória local de um único script Python.

## 👥 Integrantes

| Nome completo | Matrícula |
| --- | --- |
| Everlir Richardson da Silva | 2023009842 |
| Genildo da Silva Ferreira | 2025013782 |
| Jefferson da Rocha Teodoro | 2025014000 |
| Jefferson Rodrigues de Oliveira | 2025013432 |
| José Valbério da Silva Sousa | 2023009691 |
| Maria Fernanda Sousa Silva | 2025019580 |
| Weber Fernandes da Silva | 2025019356 |
| Yan Brasil Angelim de Brito | 2025019024 |

## 📦 Dependências principais

- `paho-mqtt`
- `firebase_admin`
- `python-dotenv`

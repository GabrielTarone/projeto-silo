# ESP32 + MQTT + CrewAI

# Integrantes

Bruno Anselmo da Silva			    RM: 566521
Fernando de Almeida Godoi Martines 	RM: 564820
Gabriel Ber Soares Tarone			RM: 563520
Guilherme de Freitas Salgado		RM: 562494
Vinicius Ribeiro Dias				RM: 566468 

## Descrição:

Projeto acadêmico de IoT integrado com IA.

O **ESP32** gera dados mockados de:

- 🌡️ Temperatura
- 💧 Umidade
- 📦 Nível do silo

Os dados são enviados via **MQTT** para um código em **Python**, que utiliza **CrewAI** para analisar a situação do silo e definir a comunicação:

- ✅ **NORMAL** → Diretoria
- ⚠️ **ATENÇÃO** → Técnicos
- 🚨 **CRÍTICO** → Técnicos

## Estrutura

```text
esp32/
└── MQTT_ESP/
    └── MQTT_ESP.ino

python/
├── main.py
├── requirements.txt
└── .env.example
```

## Como executar

### ESP32

Abra `MQTT_ESP.ino` no Arduino IDE, configure o Wi-Fi e faça o upload para o ESP32.

### Python

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure sua chave da OpenAI no `.env`:

```env
OPENAI_API_KEY=sua_chave
```

Depois execute:

```bash
python main.py
```

O ESP32 enviará os dados via MQTT e o CrewAI realizará a análise automaticamente.

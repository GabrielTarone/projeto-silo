import json
import paho.mqtt.client as mqtt

from crewai import Agent, Task, Crew, Process

from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURAÇÕES MQTT
# ============================================================

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "projeto/silo/01/dados"


# ============================================================
# PARÂMETROS DO SILO
# ============================================================

# Temperatura
TEMPERATURA_NORMAL_MIN = 15.0
TEMPERATURA_NORMAL_MAX = 35.0
TEMPERATURA_ALERTA_MAX = 40.0

# Umidade
UMIDADE_NORMAL_MIN = 30.0
UMIDADE_NORMAL_MAX = 70.0
UMIDADE_ALERTA_MAX = 80.0

# Nível do silo
NIVEL_NORMAL_MIN = 20.0
NIVEL_NORMAL_MAX = 95.0

NIVEL_CRITICO_MIN = 10.0
NIVEL_CRITICO_MAX = 98.0

# ============================================================
# AGENTES
# ============================================================

monitor = Agent(
    role="Analista de monitoramento de silo",
    goal=(
        "Analisar os dados recebidos dos sensores do silo, "
        "identificar se os valores estão dentro dos parâmetros "
        "operacionais e apontar possíveis anomalias."
    ),
    backstory=(
        "Você é um especialista em monitoramento industrial e operações "
        "de armazenamento. Recebe dados de sensores de temperatura, "
        "umidade e nível de silo e deve analisar os valores com precisão."
    ),
    verbose=True
)


especialista_tecnico = Agent(
    role="Especialista técnico em operações de silo",
    goal=(
        "Investigar possíveis causas e riscos relacionados a valores "
        "anormais de temperatura, umidade ou nível do silo."
    ),
    backstory=(
        "Você é um especialista técnico com experiência em sensores, "
        "armazenamento de materiais, manutenção industrial e análise "
        "de falhas operacionais."
    ),
    verbose=True
)


analista_operacional = Agent(
    role="Analista de impacto operacional",
    goal=(
        "Avaliar o impacto das condições encontradas no silo sobre a "
        "operação, segurança, estoque e continuidade das atividades."
    ),
    backstory=(
        "Você trabalha com operações industriais e gestão de riscos. "
        "Sua função é transformar uma análise técnica em uma avaliação "
        "objetiva do impacto para o negócio."
    ),
    verbose=True
)


agente_comunicacao = Agent(
    role="Gerente de comunicação operacional",
    goal=(
        "Definir o destinatário adequado da comunicação e produzir uma "
        "mensagem clara, objetiva e profissional."
    ),
    backstory=(
        "Você é responsável pela comunicação de ocorrências operacionais. "
        "Quando tudo está normal, comunica a diretoria de forma resumida. "
        "Quando existe uma anomalia, comunica a equipe técnica destacando "
        "o problema e a ação recomendada."
    ),
    verbose=True
)


# ============================================================
# TASKS
# ============================================================

monitorar_silo = Task(
    description=(
        """
        Analise os dados recebidos do silo:

        {dados_silo}

        Classifique cada parâmetro utilizando EXATAMENTE as seguintes regras:

        TEMPERATURA:
        - NORMAL: entre 15.0 °C e 35.0 °C
        - ATENÇÃO: acima de 35.0 °C até 40.0 °C
        - CRÍTICO: abaixo de 15.0 °C ou acima de 40.0 °C

        UMIDADE:
        - NORMAL: entre 30.0 % e 70.0 %
        - ATENÇÃO: acima de 70.0 % até 80.0 %
        - CRÍTICO: abaixo de 30.0 % ou acima de 80.0 %

        NÍVEL DO SILO:
        - NORMAL: entre 20.0 % e 95.0 %
        - ATENÇÃO: entre 10.0 % e 20.0 %, ou entre 95.0 % e 98.0 %
        - CRÍTICO: abaixo de 10.0 % ou acima de 98.0 %

        REGRAS DA CLASSIFICAÇÃO GERAL:
        - Se todos os parâmetros estiverem NORMAIS → NORMAL
        - Se pelo menos um parâmetro estiver em ATENÇÃO e nenhum estiver CRÍTICO → ATENÇÃO
        - Se pelo menos um parâmetro estiver CRÍTICO → CRÍTICO

        Determine:
        1. Status da temperatura;
        2. Status da umidade;
        3. Status do nível do silo;
        4. Parâmetros em ATENÇÃO;
        5. Parâmetros CRÍTICOS;
        6. Classificação geral.

        Não altere os valores recebidos e não invente informações.
        """
    ),
    expected_output=(
        "Relatório estruturado contendo os valores recebidos, "
        "a classificação individual de cada sensor e a classificação "
        "geral como NORMAL, ATENÇÃO ou CRÍTICO."
    ),
    agent=monitor
)


diagnosticar_silo = Task(
    description=(
        """
        Com base nos dados do silo e na análise de monitoramento anterior:

        {dados_silo}

        Investigue as possíveis causas das anomalias identificadas.

        Para cada anomalia:
        - descreva possíveis causas;
        - indique quais evidências seriam necessárias;
        - indique verificações recomendadas;
        - indique riscos operacionais.

        Não trate uma hipótese como fato confirmado sem evidências.

        Caso todos os parâmetros estejam normais, informe que não foram
        identificadas anomalias técnicas relevantes.
        """
    ),
    expected_output=(
        "Diagnóstico técnico preliminar com possíveis causas, riscos "
        "e verificações recomendadas."
    ),
    agent=especialista_tecnico,
    context=[monitorar_silo]
)


avaliar_impacto = Task(
    description=(
        """
        Avalie o impacto operacional da situação encontrada no silo.

        Considere:
        - risco para o armazenamento;
        - risco operacional;
        - necessidade de intervenção;
        - urgência;
        - possível impacto no negócio.

        Classifique a situação como:
        - NORMAL;
        - ATENÇÃO;
        - CRÍTICO.

        Explique objetivamente o motivo da classificação.
        """
    ),
    expected_output=(
        "Avaliação objetiva do impacto operacional, nível de urgência "
        "e classificação da ocorrência."
    ),
    agent=analista_operacional,
    context=[monitorar_silo, diagnosticar_silo]
)


comunicar_ocorrencia = Task(
    description=(
        """
        Com base nas análises anteriores, produza a comunicação final.

        Regras:

        1. Se a situação for NORMAL:
           - destinatário: DIRETORIA;
           - informar que o silo está operando normalmente;
           - incluir temperatura, umidade e nível;
           - ser breve e objetiva.

        2. Se a situação for ATENÇÃO ou CRÍTICO:
           - destinatário: TÉCNICOS;
           - destacar o(s) parâmetro(s) anormal(is);
           - informar os valores observados;
           - informar o risco identificado;
           - apresentar a ação recomendada;
           - deixar clara a urgência.

        Não invente informações.

        Formato obrigatório:

        DESTINATÁRIO: [DIRETORIA ou TÉCNICOS]

        CLASSIFICAÇÃO: [NORMAL, ATENÇÃO ou CRÍTICO]

        MENSAGEM:
        [mensagem pronta para envio]
        """
    ),
    expected_output=(
        "Mensagem final pronta para envio, contendo destinatário, "
        "classificação e comunicação objetiva da situação."
    ),
    agent=agente_comunicacao,
    context=[monitorar_silo, diagnosticar_silo, avaliar_impacto]
)


# ============================================================
# CREW
# ============================================================

equipe = Crew(
    agents=[
        monitor,
        especialista_tecnico,
        analista_operacional,
        agente_comunicacao
    ],
    tasks=[
        monitorar_silo,
        diagnosticar_silo,
        avaliar_impacto,
        comunicar_ocorrencia
    ],
    process=Process.sequential,
    verbose=True
)


# ============================================================
# FUNÇÃO QUE PROCESSA A MENSAGEM MQTT
# ============================================================

def processar_dados_silo(dados):
    """
    Recebe o JSON do MQTT e executa o CrewAI.
    """

    print("\n========================================")
    print("DADOS RECEBIDOS DO ESP32")
    print("========================================")

    print(f"Temperatura: {dados['temperatura']} °C")
    print(f"Umidade: {dados['umidade']} %")
    print(f"Nível do silo: {dados['nivel_silo']} %")

    texto_dados = (
        f"Temperatura: {dados['temperatura']} °C\n"
        f"Umidade: {dados['umidade']} %\n"
        f"Nível do silo: {dados['nivel_silo']} %"
    )

    print("\nIniciando análise do CrewAI...\n")

    resultado = equipe.kickoff(
    inputs={
        "dados_silo": texto_dados
    }
)

    print("\n========================================")
    print("RESULTADO FINAL")
    print("========================================")
    print(resultado.raw)


# ============================================================
# CALLBACK MQTT - CONEXÃO
# ============================================================

def ao_conectar(client, userdata, flags, rc):
    if rc == 0:
        print("========================================")
        print("MQTT conectado com sucesso!")
        print(f"Broker: {MQTT_BROKER}")
        print(f"Tópico: {MQTT_TOPIC}")
        print("========================================")

        client.subscribe(MQTT_TOPIC)

        print("Aguardando dados do ESP32...\n")

    else:
        print(f"Erro ao conectar ao MQTT. Código: {rc}")


# ============================================================
# CALLBACK MQTT - MENSAGEM
# ============================================================

def ao_receber(client, userdata, msg):

    print("\n----------------------------------------")
    print("Mensagem MQTT recebida!")
    print(f"Tópico: {msg.topic}")
    print("----------------------------------------")

    try:
        payload = msg.payload.decode("utf-8")

        print(f"Payload: {payload}")

        dados = json.loads(payload)

        # Validação simples
        campos_obrigatorios = [
            "temperatura",
            "umidade",
            "nivel_silo"
        ]

        for campo in campos_obrigatorios:
            if campo not in dados:
                raise ValueError(
                    f"Campo obrigatório ausente: {campo}"
                )

        processar_dados_silo(dados)

    except json.JSONDecodeError:
        print("Erro: a mensagem recebida não é um JSON válido.")

    except ValueError as erro:
        print(f"Erro de validação: {erro}")

    except Exception as erro:
        print(f"Erro ao processar mensagem: {erro}")


# ============================================================
# MQTT CLIENT
# ============================================================

cliente = mqtt.Client()

cliente.on_connect = ao_conectar
cliente.on_message = ao_receber


# ============================================================
# INICIALIZAÇÃO
# ============================================================

print("Conectando ao broker MQTT...")

cliente.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)

cliente.loop_forever()
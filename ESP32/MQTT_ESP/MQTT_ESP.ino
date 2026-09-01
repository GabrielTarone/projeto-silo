#include <WiFi.h>
#include <PubSubClient.h>
#include <Arduino.h>

// =========================
// CONFIGURAÇÕES WI-FI
// =========================

const char* ssid = "NET_2G5CA23A";
const char* password = "515CA23A";

// =========================
// CONFIGURAÇÕES MQTT
// =========================

const char* mqtt_broker = "broker.hivemq.com";
const int mqtt_port = 1883;

// Tópico que será utilizado pelo projeto
const char* mqtt_topic = "projeto/silo/01/dados";

const char* mqtt_username = "";
const char* mqtt_password = "";

// =========================
// OBJETOS
// =========================

WiFiClient espClient;
PubSubClient client(espClient);

// =========================
// VARIÁVEIS
// =========================

unsigned long ultimoEnvio = 0;
const unsigned long intervalo = 40000;

// =========================
// CONEXÃO MQTT
// =========================

void conectarMQTT() {

  while (!client.connected()) {

    Serial.print("Conectando ao MQTT...");

    // ID único baseado no MAC do ESP32
    String client_id = "ESP32-SILO-";
    client_id += WiFi.macAddress();

    if (client.connect(
          client_id.c_str(),
          mqtt_username,
          mqtt_password
        )) {

      Serial.println(" conectado!");
      Serial.print("Client ID: ");
      Serial.println(client_id);

    } else {

      Serial.print(" falhou. Código: ");
      Serial.println(client.state());

      Serial.println("Tentando novamente em 2 segundos...");
      delay(2000);
    }
  }
}

// =========================
// SETUP
// =========================

void setup() {

  Serial.begin(115200);

  // -------------------------
  // Wi-Fi
  // -------------------------

  Serial.println();
  Serial.print("Conectando ao Wi-Fi");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi conectado!");

  Serial.print("IP do ESP32: ");
  Serial.println(WiFi.localIP());

  // -------------------------
  // MQTT
  // -------------------------

  client.setServer(mqtt_broker, mqtt_port);

  conectarMQTT();
}

// =========================
// LOOP
// =========================

void loop() {

  // Mantém conexão MQTT
  if (!client.connected()) {
    conectarMQTT();
  }

  client.loop();

  // Envia dados a cada 5 segundos
  if (millis() - ultimoEnvio >= intervalo) {

    ultimoEnvio = millis();

    // -------------------------
    // DADOS MOCKADOS
    // -------------------------

    float temperatura = random(200, 401) / 10.0;
    float umidade = random(300, 901) / 10.0;
    float nivelSilo = random(100, 991) / 10.0;

    // -------------------------
    // JSON
    // -------------------------

    String mensagem = "{";

    mensagem += "\"temperatura\":";
    mensagem += String(temperatura, 1);

    mensagem += ",\"umidade\":";
    mensagem += String(umidade, 1);

    mensagem += ",\"nivel_silo\":";
    mensagem += String(nivelSilo, 1);

    mensagem += "}";

    // -------------------------
    // PUBLICAÇÃO MQTT
    // -------------------------

    Serial.println();
    Serial.println("Enviando mensagem:");
    Serial.println(mensagem);

    client.publish(
      mqtt_topic,
      mensagem.c_str()
    );

    Serial.println("Mensagem publicada!");
  }
}
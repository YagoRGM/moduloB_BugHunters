#include <DHT.h>
#include <Servo.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// ----------------- DEFINIÇÕES -----------------
#define DHTPIN 2
#define DHTTYPE DHT11

#define SERVO_PIN 6
#define BUZZER_PIN 7
#define LED_VERDE 3
#define LED_VERMELHO 5

#define NODE_ID "Node1"

// ----------------- OBJETOS -----------------
DHT dht(DHTPIN, DHTTYPE);
Servo servoMotor;
RF24 radio(9, 10);  // CE, CSN

// Dois canais
const byte enderecoEnvio[6] = "00001";   // Transmissor envia dados
const byte enderecoRecebe[6] = "00002";  // Transmissor recebe comandos

struct Dados {
  char id[6];
  float temp;
  float umid;
};

struct Comando {
  char acao[16];
};

// ----------------- SETUP -----------------
void setup() {
  Serial.begin(9600);
  dht.begin();
  servoMotor.attach(SERVO_PIN);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_VERMELHO, OUTPUT);

  radio.begin();
  radio.openWritingPipe(enderecoEnvio);
  radio.openReadingPipe(1, enderecoRecebe);
  radio.startListening(); // já começa ouvindo comandos

  // Estado inicial
  servoMotor.write(0);
  digitalWrite(LED_VERDE, HIGH);
  digitalWrite(LED_VERMELHO, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.println("✅ Transmissor iniciado!");
}

// ----------------- LOOP -----------------
void loop() {
  float temp = dht.readTemperature();
  float umid = dht.readHumidity();

  if (isnan(temp) || isnan(umid)) {
    Serial.println("⚠️ Erro ao ler DHT11");
    delay(2000);
    return;
  }

  // Monta dados
  Dados dados;
  strncpy(dados.id, NODE_ID, sizeof(dados.id));
  dados.temp = temp;
  dados.umid = umid;

  // --- ENVIA DADOS ---
  radio.stopListening();
  bool enviado = radio.write(&dados, sizeof(dados));
  radio.startListening();

  if (enviado) {
    Serial.print("✅ Enviado: ");
    Serial.print(dados.id);
    Serial.print(" | Temp: ");
    Serial.print(dados.temp, 2);
    Serial.print("°C | Umid: ");
    Serial.println(dados.umid, 2);
  } else {
    Serial.println("❌ Erro na transmissão, tentando novamente...");
  }

  // --- LER COMANDOS POR 5 SEGUNDOS ---
  unsigned long startTime = millis();
  while (millis() - startTime < 5000) {
    if (radio.available()) {
      Comando cmd;
      radio.read(&cmd, sizeof(cmd));
      Serial.print("📩 Comando recebido: ");
      Serial.println(cmd.acao);

      if (strcmp(cmd.acao, "LIGAR_MOTOR") == 0) {
        servoMotor.write(0);
        digitalWrite(LED_VERDE, HIGH);
        digitalWrite(LED_VERMELHO, LOW);
        digitalWrite(BUZZER_PIN, LOW);
        Serial.println("✅ Esteira liberada");
      } 
      else if (strcmp(cmd.acao, "DESLIGAR_MOTOR") == 0) {
        servoMotor.write(90);
        digitalWrite(LED_VERDE, LOW);
        digitalWrite(LED_VERMELHO, HIGH);
        Serial.println("🔥 Esteira parada");
      } 
      else if (strcmp(cmd.acao, "ALARME_ON") == 0) {
        digitalWrite(BUZZER_PIN, HIGH);
        Serial.println("🔊 Alarme acionado");
      } 
      else if (strcmp(cmd.acao, "ALARME_OFF") == 0) {
        digitalWrite(BUZZER_PIN, LOW);
        Serial.println("🔕 Alarme desligado");
      }
    }
  }

  delay(1000); // espera 1s antes de enviar novamente
}

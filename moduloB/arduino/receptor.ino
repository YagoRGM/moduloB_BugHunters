#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// ----------------- OBJETOS -----------------
RF24 radio(9, 10); // CE, CSN

// Dois canais
const byte enderecoEnvio[6] = "00001";   // Receptor recebe dados
const byte enderecoRecebe[6] = "00002";  // Receptor envia comandos

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

  radio.begin();
  radio.openReadingPipe(0, enderecoEnvio);
  radio.openWritingPipe(enderecoRecebe);
  radio.startListening();

  Serial.println("📡 Receptor iniciado, aguardando dados...");
}

// ----------------- LOOP -----------------
void loop() {
  if (radio.available()) {
    Dados dados;
    radio.read(&dados, sizeof(dados));

    // Mostra dados recebidos
    Serial.print("Recebido: ");
    Serial.print(dados.id);
    Serial.print(" | Temp: "); Serial.print(dados.temp, 2);
    Serial.print("°C | Umid: "); Serial.println(dados.umid, 2);

    // Envia comandos de acordo com a temperatura
    Comando cmd1, cmd2;
    memset(&cmd1, 0, sizeof(cmd1));
    memset(&cmd2, 0, sizeof(cmd2));

    radio.stopListening(); // pausa a escuta para enviar

    if (dados.temp > 30.0) { //mude para 20.0 se quiser testar com temperaturas mais baixas
      strcpy(cmd1.acao, "DESLIGAR_MOTOR");
      radio.write(&cmd1, sizeof(cmd1));
      strcpy(cmd2.acao, "ALARME_ON");
      radio.write(&cmd2, sizeof(cmd2));
      Serial.println("⚠️ Comandos enviados: DESLIGAR_MOTOR + ALARME_ON");
    } else {
      strcpy(cmd1.acao, "LIGAR_MOTOR");
      radio.write(&cmd1, sizeof(cmd1));
      strcpy(cmd2.acao, "ALARME_OFF");
      radio.write(&cmd2, sizeof(cmd2));
      Serial.println("✅ Comandos enviados: LIGAR_MOTOR + ALARME_OFF");
    }

    radio.startListening(); // volta a escutar
  }
}
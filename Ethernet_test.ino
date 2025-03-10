#include <SPI.h>
#include <Ethernet.h>

//Пин реле
#define RELAY_PIN 7

// Пин CS
#define CS_PIN 10

#define SECRET_KEY ""


byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

// Статический IP
IPAddress ip(10, 10, 3, 59);

// Сервер на порту 80
EthernetServer server(80);

void setup() {
  // Инициализация последовательного порта для отладки
  Serial.begin(9600);
  while (!Serial);

  // Инициализируем пин реле как выход
  pinMode(RELAY_PIN, OUTPUT);
  // Задаём начальное состояние реле (например, выключено)
  digitalWrite(RELAY_PIN, LOW);

  // Инициализация Ethernet с указанием пина CS
  Ethernet.init(CS_PIN);
  
  Ethernet.begin(mac, ip);
  
  // Запускаем сервер
  server.begin();
  
  Serial.print("Сервер запущен. IP-адрес: ");
  Serial.println(Ethernet.localIP());

  digitalWrite(RELAY_PIN, HIGH);
}

void loop() {
    EthernetClient client = server.available();
    if (client) {
        boolean currentLineIsBlank = true;
        String request = "";
        String receivedSignature = "";
        String params = "";

        while (client.connected()) {
            if (client.available()) {
                char c = client.read();
                request += c;

                // Парсинг параметров
                if (request.startsWith("GET /")) {
                    int paramsStart = request.indexOf('?');
                    if (paramsStart != -1) {
                        params = request.substring(paramsStart + 1, request.indexOf(" HTTP/1.1"));
                    }
                }

                // Поиск подписи в заголовках
                if (request.indexOf("X-Lock-Signature: ") != -1) {
                    receivedSignature = request.substring(
                        request.indexOf("X-Lock-Signature: ") + 18,
                        request.indexOf("\n", request.indexOf("X-Lock-Signature: "))
                    );
                    receivedSignature.trim();
                }

                if (c == '\n' && currentLineIsBlank) {
                    // Проверка подписи
                    if (receivedSignature != SECRET_KEY) {
                        client.println("HTTP/1.1 403 Forbidden");
                        client.println("Content-Type: application/json");
                        client.println("Connection: close");
                        client.println();
                        client.println("{\"error\":\"invalid_signature\"}");
                        client.stop();
                        return;
                    }

                    // Обработка запроса
                    client.println("HTTP/1.1 200 OK");
                    client.println("Content-Type: application/json");
                    client.println("Access-Control-Allow-Origin: *");
                    client.println("Connection: close");
                    client.println();

                    if (request.indexOf("GET /status") >= 0) {
                        String state = (digitalRead(RELAY_PIN) == HIGH ? "closed" : "open");
                        client.println("{\"status\": \"" + state + "\"}");
                    }
                    else if (request.indexOf("GET /openRelay") >= 0) {
                        digitalWrite(RELAY_PIN, HIGH);
                        client.println("{\"action\": \"success\", \"message\": \"Relay opened successfully\"}");
                    }
                    else if (request.indexOf("GET /closeRelay") >= 0) {
                        digitalWrite(RELAY_PIN, LOW);
                        client.println("{\"action\": \"success\", \"message\": \"Relay closed successfully\"}");
                    }
                    else {
                        client.println("HTTP/1.1 404 Not Found");
                        client.println("{\"error\": \"Not Found\", \"message\": \"Invalid endpoint\"}");
                    }
                    break;
                }
                
                if (c == '\n') {
                    currentLineIsBlank = true;
                } 
                else if (c != '\r') {
                    currentLineIsBlank = false;
                }
            }
        }
        
        delay(1);
        client.stop();
    }
}

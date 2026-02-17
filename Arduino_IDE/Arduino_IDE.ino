#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN 26
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// --- Wi-Fi & MQTT Configuration ---
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "test.mosquitto.org";   // Free public broker
const int mqtt_port = 1883;
const char* topic = "jtown/study_area/data";      // Your project topic

WiFiClient espClient;
PubSubClient client(espClient);

// --- Functions ---
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_Client")) {
      Serial.println("connected ✅");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Booting ESP32...");
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (!isnan(temp) && !isnan(hum)) {
    char payload[50];
    sprintf(payload, "%.2f,%.2f", temp, hum);
    client.publish(topic, payload);
    Serial.print("Published: ");
    Serial.println(payload);
  } else {
    Serial.println("Sensor error");
  }

  delay(2000);
}

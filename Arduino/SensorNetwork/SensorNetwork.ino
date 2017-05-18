#include <dht.h>
#include "Adafruit_SI1145.h"
#include <Wire.h>

Adafruit_SI1145 uv = Adafruit_SI1145();
dht DHT;

float temp, hum, light;

#define DHT_PIN 3

void setup() {
  // put your setup code here, to run once:
  uv.begin();
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  
  // DISPLAY DATA
  DHT.read22(DHT_PIN);
  hum = DHT.humidity;
  temp = DHT.temperature;
  light = uv.readVisible();
  Serial.println("sensors:{\"temperature\": " + String(temp) + ", \"humidity\": " + String(hum) + ", \"light\": " + String(light) + "}");
  
  delay(1000);


  
  delay(1000);





  
}

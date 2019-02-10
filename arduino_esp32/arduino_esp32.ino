
/*
 * Example of Nano Callback Server Interface
 * Creates a USB charger, pay for charging with Nano
 * 0.1Nano = 10mins
 * 0.2Nano = 20mins
 * 0.5Nano = 60mins
 *
 * Based originally on
 * WebSocketClient.ino
 *
 *  Created on: 24.05.2015
 *
 */

#include <Arduino.h>

#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>
#include <U8g2lib.h>
#include <Wire.h>

#define SSID_NAME ""
#define SSID_PASS ""
#define TRACKING_ADDRESS ""

WiFiMulti WiFiMulti;
WebSocketsClient webSocket;

StaticJsonDocument<200> doc;
StaticJsonDocument<1024> rx_doc;

//U8X8_SSD1306_128X64_NONAME_SW_I2C u8x8(/* clock=*/ 15, /* data=*/ 4, /* reset=*/ 16);
U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2 (U8G2_R0,/* clock=*/ 15, /* data=*/ 4, /* reset=*/ 16);
uint64_t chipid;
int count = 0;

void hexdump(const void *mem, uint32_t len, uint8_t cols = 16) {
	const uint8_t* src = (const uint8_t*) mem;
	Serial.printf("\n[HEXDUMP] Address: 0x%08X len: 0x%X (%d)", (ptrdiff_t)src, len, len);
	for(uint32_t i = 0; i < len; i++) {
		if(i % cols == 0) {
			Serial.printf("\n[0x%08X] 0x%08X: ", (ptrdiff_t)src, i);
		}
		Serial.printf("%02X ", *src);
		src++;
	}
	Serial.printf("\n");
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {

  
	switch(type) {
		case WStype_DISCONNECTED:
			Serial.printf("[WSc] Disconnected!\n");
			break;
		case WStype_CONNECTED:
			Serial.printf("[WSc] Connected to url: %s\n", payload);

	 		// send message to server when Connected
      
      doc["address"] = TRACKING_ADDRESS;
      doc["api_key"] = "0";
      char output[512];
      serializeJson(doc, output);
      Serial.println(output);
			webSocket.sendTXT(output);
			break;
      
		case WStype_TEXT:
    {
			Serial.printf("[WSc] get text: %s\n", payload);
      deserializeJson(rx_doc, payload);
      String block_amount = rx_doc["amount"];
      
      long int noughtPointone = 100000;
      long int noughtPointtwo = 200000;
      Serial.println(block_amount);

      //Convert to nano
      int lastIndex = block_amount.length() - 24;
      block_amount.remove(lastIndex);

      Serial.println(block_amount);
      
      u8g2.clearBuffer();
      u8g2.setFont(u8g2_font_helvB14_tf);
      u8g2.drawStr(0, 40, "Block Detected!");
      u8g2.sendBuffer();
      int count = 0;
      // Check amount
      if (block_amount.toInt() >= 100000){
        if (block_amount.toInt() >= 500000){
          count = 3600;
        }
        else if (block_amount.toInt() >= 200000){
          count = 1200;
        }
        else {
          count = 600;
        }
        // Turn on Switch
        pinMode(18, OUTPUT);
        digitalWrite(18, HIGH);
        //Start Timer
        char current_time[40];
        
        while(count > 0){
          int seconds;
          int minutes;
              
          seconds = count % 60;
          minutes = (count - seconds) / 60;
              
          sprintf(current_time, "%02d:%02d", minutes, seconds);
          u8g2.clearBuffer();
          u8g2.setFont(u8g2_font_helvB14_tf);
          u8g2.drawStr(30, 40, current_time);
          u8g2.sendBuffer();
          count--;
          delay(1000);
        }
        
        digitalWrite(18, LOW);
      }
      else {
        u8g2.clearBuffer();
        u8g2.setFont(u8g2_font_helvB14_tf);
        u8g2.drawStr(0, 40, "Not Enough Funds");
        u8g2.sendBuffer();  
        delay(3000);      
      }
      
      u8g2.clearBuffer();
      u8g2.setFont(u8g2_font_helvB10_tf);
      u8g2.drawStr(0, 20, "0.1Nano = 10mins");
      u8g2.drawStr(0, 40, "0.2Nano = 20mins");
      u8g2.drawStr(0, 60, "0.5Nano = 60mins");
      u8g2.sendBuffer();
      
			// send message to server
			// webSocket.sendTXT("message here");
			break;
    }
		case WStype_BIN:
			Serial.printf("[WSc] get binary length: %u\n", length);
			hexdump(payload, length);

			// send data to server
			// webSocket.sendBIN(payload, length);
			break;
		case WStype_ERROR:			
		case WStype_FRAGMENT_TEXT_START:
		case WStype_FRAGMENT_BIN_START:
		case WStype_FRAGMENT:
		case WStype_FRAGMENT_FIN:
			break;
	}

}

void setup() {
  
	// Serial.begin(921600);
	Serial.begin(115200);

	//Serial.setDebugOutput(true);
	Serial.setDebugOutput(true);

	Serial.println();
	Serial.println();
	Serial.println();

  delay(5000);
  
	for(uint8_t t = 4; t > 0; t--) {
		Serial.printf("[SETUP] BOOT WAIT %d...\n", t);
		Serial.flush();
		delay(1000);
	}

  u8g2.begin();
  u8g2.setFont(u8g2_font_helvB14_tf);

  chipid=ESP.getEfuseMac();//The chip ID is essentially its MAC address(length: 6 bytes).
  Serial.printf("ESP32 Chip ID = %04X",(uint16_t)(chipid>>32));//print High 2 bytes
  Serial.printf("%08X\n",(uint32_t)chipid);//print Low 4bytes.

  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_helvB14_tf);
  u8g2.drawStr(0, 40, "Booting...");
  u8g2.sendBuffer();

	WiFiMulti.addAP(SSID_NAME, SSID_PASS);

	//WiFi.disconnect();
	while(WiFiMulti.run() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
		delay(100);
	}
 
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
      
	// server address, port and URL
	webSocket.begin("yapraiwallet.space", 80, "/call");

	// event handler
	webSocket.onEvent(webSocketEvent);

	// try ever 5000 again if connection has failed
	webSocket.setReconnectInterval(5000);

  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_helvB10_tf);
  u8g2.drawStr(0, 20, "0.1Nano = 10mins");
  u8g2.drawStr(0, 40, "0.2Nano = 20mins");
  u8g2.drawStr(0, 60, "0.5Nano = 60mins");
  u8g2.sendBuffer();

}

void loop() {
  webSocket.loop();

}

// EP2 S2: one repeated address request for an unambiguous scope capture.
// Copy into src/main.cpp; preserve your working platformio.ini.
// Wire: 3V3, GND, SDA GPIO8, SCL GPIO9. Keep AD0 low (default).
// First use the full scanner to confirm only 0x68 is present.
// Change REQUEST_ADDRESS: 0x68 -> 0x69 -> 0x68; reflash each time.
// Expected: ACK -> address NACK -> ACK, with all wires intact.
// Other nonzero Wire statuses are errors, not automatically an address NACK.
// Scope: A=SDA, B=SCL, grounds=GND; I2C seven-bit address decode.
// Restore examples/session02_mpu_read.cpp before recording motion.
#include <Arduino.h>
#include <Wire.h>

constexpr uint8_t REQUEST_ADDRESS = 0x68;

void setup() {
  Serial.begin(115200);
  delay(300);
  Wire.begin(8, 9);
  Wire.setClock(100000);  // 100 kHz SCL, not 100000 sensor readings/s
}

void loop() {
  Wire.beginTransmission(REQUEST_ADDRESS);
  uint8_t status = Wire.endTransmission();
  Serial.printf("Address 0x%02X: Wire status %u\n", REQUEST_ADDRESS, status);
  // Status 0: acknowledged; status 2: address not acknowledged.
  // Inspect any other status instead of calling every failure a NACK.
  delay(1000);           // One short request, then an idle gap for the scope.
}

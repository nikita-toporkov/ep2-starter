/*
 * Session 1 — blink a plain LED (the homework, on real hardware).
 * --------------------------------------------------------------------------
 * The blink in src/main.cpp uses the board's addressable RGB LED, which you
 * send a COLOUR to. This one uses an ordinary LED from your box, which you
 * switch ON and OFF. It is the same idea with simpler hardware — and it is
 * the same sketch you ran in the simulator.
 *
 * WIRING (power off while you wire):
 *   GPIO40 -> resistor (220-330 ohm) -> LED long leg (anode)
 *   LED short leg (cathode) -> GND
 *
 *   THE RESISTOR IS NOT OPTIONAL. Straight across a pin, an LED draws more
 *   current than the pin should give. 220 ohm is bright, 330 is comfortable,
 *   1k works but is dim. Long leg = positive.
 *
 * WHY GPIO40: it's free on this board, it's not a strapping pin (avoid
 * GPIO0/3/45/46), and it's clear of the I2C bus (8/9), the session-1 scope
 * signal (GPIO2) and the octal flash/PSRAM pins (33-37). Session 2's homework
 * reuses the same pin, so you can leave the LED where it is.
 *
 * THE HOMEWORK: make this blink YOURS. A rhythm, a pattern, morse code, a
 * heartbeat — something you designed. Then push it as `FINAL: my blink`.
 */
#include <Arduino.h>

#define LED_PIN 40

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(LED_PIN, OUTPUT);
  Serial.println();
  Serial.println("Plain LED blinking on GPIO40.");
}


void loop() {
  digitalWrite(LED_PIN, HIGH);   // on
  delay(500);                    // <-- wait half a second

  digitalWrite(LED_PIN, LOW);    // off
  delay(500);                    // <-- and again
}

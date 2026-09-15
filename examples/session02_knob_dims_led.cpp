/*
 * Session 2 — knob dims LED: class starting point + homework.
 * --------------------------------------------------------------------------
 * IN CLASS: copy into src/main.cpp, wire, build and test.
 * Commit and push as SETUP: knob works (ungraded save point).
 * The unchanged example is the starting point for the homework below.
 *
 * WIRING (power off while you wire):
 *   pot outer leg 1 -> 3V3
 *   pot outer leg 2 -> GND
 *   pot middle leg  -> GPIO4
 *
 *   GPIO40 -> resistor (220-330 ohm) -> LED long leg (anode)
 *   LED short leg (cathode) -> GND
 *
 *   THE RESISTOR IS NOT OPTIONAL. An LED straight across a pin draws more
 *   current than the pin should give and can damage it. Long leg = positive.
 *
 * Same LED pin as session 1's plain-LED blink, so if you wired one then, it is
 * already in the right place — you are only adding the potentiometer.
 *
 * NOT the on-board RGB LED, and not LED_BUILTIN. Use the plain LED from your
 * box on a plain GPIO. (LED_BUILTIN assumes GPIO48 and is wrong for our board;
 * the on-board RGB one needs neopixelWrite() and colours, not brightness.)
 *
 * THE ONE BIT OF ARITHMETIC
 *   analogRead()  gives 0..4095   (12-bit input)
 *   analogWrite() wants 0..255    (8-bit output)
 *   4095 / 16 = 255, so dividing by 16 maps one range onto the other.
 *
 * Does this fight the 1 kHz scope signal on GPIO2 from session 1? No.
 * analogWrite() takes LEDC channels counting down from the top, and the scope
 * signal holds channel 0. They coexist.
 *
 * HOMEWORK — tilt switches, knob dims:
 *   Combine this example with examples/session02_mpu_read.cpp in src/main.cpp.
 *   Keep one setup() and one loop(), and keep your working platformio.ini.
 *   MPU wiring: 3V3, GND, SDA GPIO8, SCL GPIO9. Keep the LED and pot above.
 *
 *   1. Choose one accelerometer axis. With its positive direction pointing up,
 *      enable the LED; held sideways or down, turn the LED off.
 *      Read the acceleration in those poses and choose a threshold between
 *      them. Judge orientation while held still, not during a shake.
 *   2. While enabled, the pot sets brightness. While disabled, the LED stays
 *      off at every knob setting. The existing raw / 16 mapping is fine.
 *   3. Test up -> sideways -> down -> up, plus two knob settings while enabled.
 *      Use a nonzero knob setting when checking the orientation switch.
 *   4. Add three comment lines at the top of src/main.cpp:
 *      - My chosen axis and threshold.
 *      - The readings I observed in the three poses.
 *      - One thing that surprised me when testing.
 *   5. Commit and push as FINAL: tilt switches, knob dims.
 *      Submit that commit's link in Moodle with your AI-use line.
 *
 *   Both controls must work; a brightness curve or perfectly flicker-free
 *   switching is not required. Optional: reduce flicker near the threshold.
 *   The unchanged knob-only example below is the class starting point.
 */
#include <Arduino.h>

#define POT_PIN 4
#define LED_PIN 40

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(LED_PIN, OUTPUT);
  Serial.println();
  Serial.println("Knob dims LED — turn the knob.");
}

void loop() {
  int raw  = analogRead(POT_PIN);         // 0 .. 4095
  int duty = raw / 16;                    // 0 .. 255
  if (duty > 255) duty = 255;             // guard the top end of the range

  analogWrite(LED_PIN, duty);

  Serial.printf("raw %4d -> duty %3d\n", raw, duty);
  delay(50);
}

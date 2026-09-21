/*
 * Session 2 — read the MPU-6050 and print CSV over serial at ~50 Hz.
 * --------------------------------------------------------------------------
 * Copy this into src/main.cpp. Sanity-check against physics you know:
 *   flat on the table -> Z is about +9.8 (that's gravity!), X and Y near 0.
 *
 * Record a dataset (one file per gesture) from your laptop:
 *   python tools/record_csv.py wave_01.csv
 * Close Serial Monitor first. Wait for GO; move until STOP (10 seconds).
 * Use PlatformIO's Python; see README for Windows/Mac commands.
 * ...then upload the CSVs to Edge Impulse next session.
 */
#include <Arduino.h>
#include <Adafruit_MPU6050.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

#define POT_PIN 4
#define LED_PIN 40

void setup() {
  Serial.begin(115200);
  delay(300);
  Wire.begin(8, 9);                   // SDA 8, SCL 9

  if (!mpu.begin()) {
    Serial.println("MPU-6050 not found — run the I2C scanner first.");
    while (true) delay(1000);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
}

void loop() {
  sensors_event_t a, g, t;
  mpu.getEvent(&a, &g, &t);           // acceleration in m/s^2

  Serial.printf("%.2f,%.2f,%.2f\n",
                a.acceleration.x, a.acceleration.y, a.acceleration.z);

  delay(20);                          // ~50 Hz — the rate you'll train AND deploy at



  if (a.acceleration.x > 0) {
    Serial.println("X-axis acceleration exceeded 0 m/s^2!");    
    int raw  = analogRead(POT_PIN);         // 0 .. 4095
    int duty = raw / 16;                    // 0 .. 255
    if (duty > 255) duty = 255;             // guard the top end of the range

    analogWrite(LED_PIN, duty);;
  }
  else {
    analogWrite(LED_PIN, 0);               // turn off LED if condition not met
  }
}

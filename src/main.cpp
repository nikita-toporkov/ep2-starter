/*
 * Session 2 — read the MPU-6050 and print CSV over serial at ~50 Hz.
 * --------------------------------------------------------------------------
 * Copy this into src/main.cpp. Sanity-check against physics you know:
 *   flat on the table -> Z is about +9.8 (that's gravity!), X and Y near 0.
 *
 * Record a dataset (one file per gesture) from your laptop:
 *   pio device monitor --quiet > wave_01.csv
 * ...then upload the CSVs to Edge Impulse next session.
 */
#include <Arduino.h>
#include <Adafruit_MPU6050.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

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

  delay(200);                          // ~50 Hz — the rate you'll train AND deploy at
}

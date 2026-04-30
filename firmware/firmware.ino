#include "Adafruit_TinyUSB.h"
#include <math.h>
#include <Adafruit_NeoPixel.h>
// #include <Keypad.h>

Adafruit_USBD_MIDI usb_midi;

#define VERSION 0.1

const int LED_PIN = 8;

const int MUX_0 = 21;
const int MUX_1 = 23;
const int MUX_2 = 20;
const int MUX_3 = 22;

const int MUX_RES = 26;

const int KEYS = 14;

const int VEL_THRESH = 105;
const int VEL_THRESH_LOW = 100;

const uint8_t ANALOG_NOTES[KEYS] = {
  60, 61, 62, 63, 64,
    65, 66, 67, 68,
  69, 70, 71, 72, 73
};

Adafruit_NeoPixel strip(1, LED_PIN, NEO_RGB + NEO_KHZ800);

bool pressedKeys[KEYS] = { false };

int lastVel[KEYS] = { 0 };

void setup() {
  Serial.begin(9600);
  usb_midi.begin();

  pinMode(MUX_0, OUTPUT);
  pinMode(MUX_1, OUTPUT);
  pinMode(MUX_2, OUTPUT);
  pinMode(MUX_3, OUTPUT);
  pinMode(MUX_RES, INPUT);

  strip.begin();
  strip.show();
}

int readMux(uint8_t index) {
  bool highA = (index & 0b00000001) == 0b00000001;
  bool highB = (index & 0b00000010) == 0b00000010;
  bool highC = (index & 0b00000100) == 0b00000100;
  bool highD = (index & 0b00001000) == 0b00001000;

  digitalWrite(MUX_0, highA ? HIGH : LOW);
  digitalWrite(MUX_1, highB ? HIGH : LOW);
  digitalWrite(MUX_2, highC ? HIGH : LOW);
  digitalWrite(MUX_3, highD ? HIGH : LOW);

  delayMicroseconds(20);
  analogRead(MUX_RES);
  return analogRead(MUX_RES);
}

uint8_t packet[4];
void loop() {
  int range = 127 - VEL_THRESH_LOW;
  for (int i = 0; i < KEYS; i++) {
    int unmod_velocity = (int)(readMux(i) / 1023.0 * 127);
    int velocity = ((unmod_velocity - VEL_THRESH_LOW) / (float)range) * 127;
    //Serial.println(velocity);
    if (unmod_velocity > VEL_THRESH) {
      if (!pressedKeys[i]) {
        const uint8_t noteOn[] = {0x09, 0x90, ANALOG_NOTES[i], velocity};
        usb_midi.writePacket(noteOn);
        pressedKeys[i] = true;
        Serial.print("pressed: ");
        Serial.println(i);
        lastVel[i] = velocity;
      } else {
        if (abs(velocity - lastVel[i]) > 6) {
        Serial.println(velocity);
          const uint8_t afterTouch[] = {0x0A, 0xA0, ANALOG_NOTES[i], velocity};
          usb_midi.writePacket(afterTouch);
          lastVel[i] = velocity;
        }
      }
    } else if (unmod_velocity < VEL_THRESH_LOW) {
      if (pressedKeys[i]) {
        const uint8_t noteOff[] = {0x08, 0x80, ANALOG_NOTES[i], 0};
        usb_midi.writePacket(noteOff);
        pressedKeys[i] = false;
        // Serial.println("release" + i);
        Serial.print("released: ");
        Serial.println(i);
      }
    }
  }
  while (usb_midi.available()) {
    usb_midi.readPacket(packet);
  }

  strip.setPixelColor(0, strip.Color(255, 0, 255));
  strip.show();
}

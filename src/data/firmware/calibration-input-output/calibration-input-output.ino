// -----------------------------------------------------------------------------
// calibration utility script


/*
Any board that would support this sketch must have an override configured here.
These definitions are sourced from the arguments passed to the compiler for
each board. The compiler output should list "-DARDUINO_<board>" as part of the
compiler flags. This is the key used for these checks.
If a board is not listed here it has never been tested or is not supported.
*/
#if defined(ARDUINO_TEENSY35) || defined(ARDUINO_TEENSY36)
//    #define SEND_NOW() Serial.send_now()
    #define ANALOG_READ() analogRead(0)
    #define ANALOG_WRITE(val) analogWrite(A21, val)
#elif defined(ARDUINO_ITSYBITSY_M4)
//    #define SEND_NOW() Serial.flush()
    #define ANALOG_READ() analogRead(A3)
    #define ANALOG_WRITE(val) analogWrite(DAC0, val)
#elif defined(ARDUINO_SAMD51_THING_PLUS)
//    #define SEND_NOW() Serial.flush()
    #define ANALOG_READ() analogRead(A1)
    #define ANALOG_WRITE(val) analogWrite(DAC0, val)
#else
    #error "Pins are not configured for the selected board. Seek assistance."
#endif

// -----------------------------------------------------------------------------
void setup() {
  analogWriteResolution(12);
  analogReadResolution(12);

  Serial.begin(115200);
  while (Serial.available()>0)  Serial.read();
}

// -----------------------------------------------------------------------------


int counter = 0;
// -----------------------------------------------------------------------------
void loop() {
  float avg = 0;  // mean value of inputVal

  for (int n = 0; n < 5; n++) {
    float inputVal = ANALOG_READ();
    delay(20);   // wait for new, digitized samples
    avg = (n/(n+1)) * avg + (1/(n+1)) * inputVal;
  }
  ANALOG_WRITE(avg);
  delay(50);
  Serial.println(int(counter));
  counter ++;
  if (counter > 4096) counter = 0;
}
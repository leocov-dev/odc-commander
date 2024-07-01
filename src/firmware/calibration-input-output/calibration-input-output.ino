#define SEND_NOW() Serial.flush()

#define ANALOG_READ() analogRead(A3)
#define ANALOG_WRITE(val) analogWrite(DAC0, val)

void setup() {
  analogWriteResolution(12);
  analogReadResolution(12);

  Serial.begin(115200);
  while (Serial.available()>0)  Serial.read();
}

const int m = 10;   // maximum number of averages
void loop() {
  float avg = 0;  // mean value of inputVal

  for (int n = 0; n < m; n++) {
    float inputVal = ANALOG_READ();
    delay(100);   // wait for new, digitized samples
    avg = (n/(n+1)) * avg + (1/(n+1)) * inputVal;
  }
  ANALOG_WRITE(avg);
  delay(50);
  Serial.println(int(avg));
}
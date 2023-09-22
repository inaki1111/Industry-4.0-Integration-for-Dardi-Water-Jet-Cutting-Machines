// MMA7361 Accelerometer Arduino Example
// VCC -> 3.3V
// GND -> GND
// XOUT -> A0
// YOUT -> A1
// ZOUT -> A2
// Sleep -> 3.3V (optional, can be left unconnected)

int xPin = A0; // Analog input pin for X-axis
int yPin = A1; // Analog input pin for Y-axis
int zPin = A2; // Analog input pin for Z-axis

void setup() {
  Serial.begin(9600);
}

void loop() {
  int xValue = analogRead(xPin); // Read X-axis value
  int yValue = analogRead(yPin); // Read Y-axis value
  int zValue = analogRead(zPin); // Read Z-axis value

  // Print the values to the serial monitor
  Serial.print("X-Axis: ");
  Serial.print(xValue);
  Serial.print("\tY-Axis: ");
  Serial.print(yValue);
  Serial.print("\tZ-Axis: ");
  Serial.println(zValue);

  delay(1000); // Delay for readability
}

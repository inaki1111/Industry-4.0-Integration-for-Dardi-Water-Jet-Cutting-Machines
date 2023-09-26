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
  float xValue = analogRead(xPin); // Read X-axis value
  float yValue = analogRead(yPin); // Read Y-axis value
  float zValue = analogRead(zPin); // Read Z-axis value

  float total;
  total = sqrt((xValue)*(xValue) + (yValue)*(yValue)+(zValue)*(zValue));

  // Print the values to the serial monitor
  Serial.println(total);

  delay(10); // Delay for readability
}

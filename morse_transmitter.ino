#include <SoftwareSerial.h>

// Initialize SoftwareSerial for Bluetooth (RX=2, TX=3)
SoftwareSerial BTSerial(2, 3); 

const int ledPin = 13;

// --- TIMING CONFIGURATION ---
// MUST MATCH PYTHON (T = 150ms)
const int T = 150; 

// Morse Code Dictionary (A-Z, 0-9)
const String letters[] = {
  ".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", 
  "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", "...", "-", 
  "..-", "...-", ".--", "-..-", "-.--", "--.."
};
const String numbers[] = {
  "-----", ".----", "..---", "...--", "....-", ".....", "-....", "--...", "---..", "----."
};

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);      // For computer debugging
  BTSerial.begin(9600);    // For HC-05 communication
  
  // Turn LED off initially
  digitalWrite(ledPin, LOW); 
  
  Serial.println("System Ready. Waiting for Bluetooth input...");
}

void loop() {
  if (BTSerial.available()) {
    String message = BTSerial.readString();
    message.toUpperCase();
    
    Serial.print("Transmitting: ");
    Serial.println(message);
    
    for (int i = 0; i < message.length(); i++) {
      char c = message[i];
      
      if (c >= 'A' && c <= 'Z') {
        blinkMorse(letters[c - 'A']);
      } 
      else if (c >= '0' && c <= '9') {
        blinkMorse(numbers[c - '0']);
      } 
      else if (c == ' ') {
        // Python WORD_GAP_MIN is 750ms. 
        // 7 * 150ms = 1050ms (Perfect trigger for a space)
        delay(7 * T); 
        continue; // Skip the inter-character gap below
      }

      // Inter-character gap: Wait 3T between letters of the same word.
      // Python CHAR_GAP_MIN is 300ms. 
      // 3 * 150ms = 450ms (Perfect trigger for a new character)
      if (i < message.length() - 1 && message[i+1] != ' ') {
        delay(3 * T); 
      }
    }
    
    Serial.println("Transmission Complete.");
  }
}

void blinkMorse(String sequence) {
  for (int i = 0; i < sequence.length(); i++) {
    
    digitalWrite(ledPin, HIGH);
    
    if (sequence[i] == '.') {
      delay(T);       // Dot = 1T (150ms)
    } else if (sequence[i] == '-') {
      delay(3 * T);   // Dash = 3T (450ms)
    }
    
    digitalWrite(ledPin, LOW);
    
    // Intra-character gap: Wait 1T between dots/dashes of the SAME letter
    if (i < sequence.length() - 1) {
      delay(T); // 150ms
    }
  }
}

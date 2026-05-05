import cv2
import time
import sys

# --- TIMING CONFIGURATION (Assuming Arduino T = 150ms / 0.15s) ---
T = 0.15

# Flexible boundaries to handle webcam lag and frame drops
DOT_MAX = T * 2.0      # Any ON duration less than 300ms is a DOT
DASH_MIN = T * 2.0     # Any ON duration more than 300ms is a DASH
DASH_MAX = T * 5.0     # Maximum acceptable DASH length

CHAR_GAP_MIN = T * 2.0 # OFF time > 300ms triggers character decoding
WORD_GAP_MIN = T * 5.0 # OFF time > 750ms triggers a space

# Reverse Morse Dictionary
MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', "...-": 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9'
}

# --- STATE VARIABLES ---
is_led_on = False
last_transition_time = time.time()
current_symbol = ""
last_print_was_word_gap = True

# Initialize Webcam (Change to 1 if you have multiple cameras and the wrong one opens)
cap = cv2.VideoCapture(0)

print("\n" + "="*40)
print(" OpenCV Morse Code Decoder Running")
print(" Point your camera at the blinking LED.")
print(" Press 'q' in the video window to quit.")
print("="*40 + "\n")

print("DECODED MESSAGE: ", end='', flush=True)

while True:
    ret, frame = cap.read()
    if not ret:
        print("\n[ERROR] Could not read from webcam.")
        break

    # Convert to grayscale and apply threshold
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # CALIBRATION: If the threshold window is too white, increase 200 to 240.
    # If the threshold window is completely black when the LED is on, lower 200 to 150.
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Check if LED is ON (count white pixels)
    bright_pixels = cv2.countNonZero(thresh)
    currently_on = bright_pixels > 10 

    current_time = time.time()
    delta_t = current_time - last_transition_time

    # --- STATE MACHINE: DETECT TRANSITIONS ---
    if currently_on != is_led_on:
        if not currently_on: 
            # LED just turned OFF. Classify how long it was ON.
            if delta_t < DOT_MAX:
                current_symbol += "."
            elif DASH_MIN <= delta_t < DASH_MAX:
                current_symbol += "-"
            last_print_was_word_gap = False
            
        is_led_on = currently_on
        last_transition_time = current_time

    # --- STATE MACHINE: DETECT GAPS (When LED is OFF) ---
    else:
        # If LED is OFF, check if it's been off long enough to decode a character
        if not is_led_on and len(current_symbol) > 0:
            if delta_t > CHAR_GAP_MIN:
                # Decode the accumulated dots and dashes
                if current_symbol in MORSE_CODE_DICT:
                    char = MORSE_CODE_DICT[current_symbol]
                    print(char, end='', flush=True)  # Print directly to terminal
                else:
                    print("?", end='', flush=True)   # Print ? if sequence is invalid
                current_symbol = "" 
                
        # Check if it's been off long enough to add a space between words
        if not is_led_on and delta_t > WORD_GAP_MIN and not last_print_was_word_gap:
            print(" ", end='', flush=True)
            last_print_was_word_gap = True

    # --- VIDEO DEBUGGING WINDOWS ---
    # Draw the current symbol on the camera feed for debugging
    cv2.putText(frame, f"Symbol Buffer: {current_symbol}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    cv2.imshow('1. Threshold Filter (LED View)', thresh)
    cv2.imshow('2. Main Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n\nDecoder Closed.")
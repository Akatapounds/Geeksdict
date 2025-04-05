import pyttsx3

# Initialize the engine
engine = pyttsx3.init()

# Set properties (optional)
engine.setProperty('rate', 150)  # Speed percent (default 200)
engine.setProperty('volume', 0.9)  # Volume 0-1

# Say something
engine.say("Hello, this is pyttsx3 speaking.")

# Run and wait
engine.runAndWait()
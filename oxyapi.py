import customtkinter
import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageSequence
import sqlite3
import threading
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import time

# Initialize appearance settings
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Load images
History_Button_Image = customtkinter.CTkImage(Image.open('images/history.png'), size=(30, 30))
Micro_Button_Image = customtkinter.CTkImage(Image.open('images/micro.png'), size=(30, 30))
Logo_Image = customtkinter.CTkImage(Image.open('images/updated logo.png'), size=(200, 200))
Speaker_Button_Image = customtkinter.CTkImage(Image.open('images/speaker.png'), size=(30, 30))

# Load the GIF
Loading_GIF = Image.open('images/Loading3.gif')
Loading_Frames = [frame.copy() for frame in ImageSequence.Iterator(Loading_GIF)]

class DictionaryApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("GEEK DICTIONARY")
        self.geometry("400x600")
        self.resizable(False, False)
        self.configure_layout()
        self.setup_database()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.recognizer = sr.Recognizer()  # Initialize recognizer once
        self.current_frame = 0  # Track the current frame of the GIF
        self.listening_for_keyword = False  # Track if listening for the keyword
        self.keyword = "geek"  # The keyword to activate speech-to-text

    def configure_layout(self):
        """Set up grid layout configuration"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def setup_database(self):
        """Initialize SQLite database connection"""
        self.conn = sqlite3.connect('history.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        """Create and place all GUI components"""
        # Background Image
        self.bg_image = customtkinter.CTkImage(Image.open("images/background2.png"), size=(400, 600))
        self.bg_label = customtkinter.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.grid(row=0, column=0, sticky="nsew")

        # Navigation Buttons
        self.create_navigation_buttons()
        
        # Logo
        self.logo_label = customtkinter.CTkLabel(self, text="", image=Logo_Image, 
                                               fg_color='#1b0c43', corner_radius=5)
        self.logo_label.place(x=95, y=45)

        # Search Components
        self.create_search_components()

        # Results Frame
        self.results_frame = customtkinter.CTkFrame(
            self,
            fg_color="white",
            border_color="#FFCC70",
            border_width=2,
            width=350,
            height=200,
            corner_radius=30
        )
        self.results_frame.place(x=25, y=380)

        # Speak Button
        self.speak_button = customtkinter.CTkButton(
            self,
            text="Play",
            image=Speaker_Button_Image,
            fg_color="#086b78",
            hover_color="#C850C0",
            border_width=2,
            width=15,
            height=15,
            border_color='#FFCC70',
            corner_radius=30,
            command=self.speak_definition
        )
        self.speak_button.place(x=0, y=320)

        # Definition Textbox
        self.definition_text = customtkinter.CTkTextbox(
            self.results_frame,
            fg_color="white",
            text_color="black",
            wrap="word",
            width=330,
            height=180,
            font=("Arial", 12)
        )
        self.definition_text.pack(padx=10, pady=10)

        # Loading Animation (initially hidden)
        self.loading_label = customtkinter.CTkLabel(
            self,
            text="",
            fg_color="transparent"
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the loading animation
        self.loading_label.place_forget()  # Hide it initially

        # Start listening for the keyword
        self.start_listening_for_keyword()

    def start_listening_for_keyword(self):
        """Start listening for the keyword in a background thread"""
        self.listening_for_keyword = True
        threading.Thread(target=self.listen_for_keyword, daemon=True).start()

    def listen_for_keyword(self):
        """Continuously listen for the keyword"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening_for_keyword:
                try:
                    print("Listening for keyword...")
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Heard: {text}")

                    # Check if the keyword is detected
                    if self.keyword in text:
                        print("Keyword detected! Activating speech-to-text...")
                        self.after(0, self.start_voice_input)  # Switch to speech-to-text mode
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Speech service error: {e}")
                except sr.WaitTimeoutError:
                    pass  # No speech detected, continue listening

    def start_voice_input(self):
        """Start voice recognition in a background thread"""
        self.listening_for_keyword = False  # Stop listening for the keyword
        threading.Thread(target=self.process_voice_input, daemon=True).start()

    def process_voice_input(self):
        """Handle voice input processing with proper resource management"""
        try:
            with sr.Microphone() as source:
                self.update_ui_listening_state(True)
                self.recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                except sr.WaitTimeoutError:
                    self.show_voice_error("No speech detected")
                    return

                try:
                    text = self.recognizer.recognize_google(audio)
                    self.handle_successful_voice_input(text)
                except sr.UnknownValueError:
                    self.show_voice_error("Could not understand audio")
                except sr.RequestError as e:
                    self.show_voice_error(f"Speech service error: {e}")

        except OSError as e:
            self.show_voice_error(f"Microphone error: {str(e)}")
        except Exception as e:
            self.show_voice_error(f"Voice input failed: {str(e)}")
        finally:
            self.update_ui_listening_state(False)
            self.start_listening_for_keyword()  # Resume listening for the keyword

    def update_ui_listening_state(self, listening):
        """Update UI elements based on listening state"""
        self.after(0, lambda: self.search_entry.configure(
            placeholder_text="Listening..." if listening else "     search         🔎"
        ))

    def handle_successful_voice_input(self, text):
        """Process successful voice recognition"""
        self.after(0, lambda: [
            self.search_entry.delete(0, tk.END),
            self.search_entry.insert(0, text),
            self.search_word()  # Automatically search for the recognized word
        ])

    def show_voice_error(self, message):
        """Show voice recognition errors"""
        self.after(0, lambda: messagebox.showerror("Voice Error", message))

    # Rest of your methods remain unchanged...

if __name__ == "__main__":
    app = DictionaryApp()
    app.mainloop()
import customtkinter
import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image
import sqlite3
import threading
import speech_recognition as sr
from gtts import gTTS
import pygame
import os

# Initialize appearance settings
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Load images
History_Button_Image = customtkinter.CTkImage(Image.open('images/history.png'), size=(30, 30))
Micro_Button_Image = customtkinter.CTkImage(Image.open('images/micro.png'), size=(30, 30))
Logo_Image = customtkinter.CTkImage(Image.open('images/updated logo.png'), size=(200, 200))
Play_button = customtkinter.CTkImage(Image.open('images/play buttom.png'), size=(30, 30))
# Pause_button = customtkinter.CTkImage(Image.open('images/pause.png'), size=(30, 30))

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
        self.audio_state = "stopped"  # Possible states: "stopped", "playing", "paused"
        self.history_window = None  # Add this line to track history window

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

        # Play/Pause Button
        self.speak_button = customtkinter.CTkButton(
            self,
            text="",
            image=Play_button,
            fg_color="#140431",
            hover_color="#707070",
            border_width=2,
            width=5,
            height=5,
            border_color='#140431',
            # corner_radius=30,
            command=self.toggle_audio
        )
        self.speak_button.place(x=30, y=320)

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

    def toggle_audio(self):
        """Toggle between play, pause, and resume actions"""
        if self.audio_state == "stopped":
            self.speak_definition()
        elif self.audio_state == "playing":
            self.pause_audio()
        elif self.audio_state == "paused":
            self.resume_audio()

    def speak_definition(self):
        """Convert definition text to speech using pygame..."""
        text_to_speak = self.definition_text.get("1.0", "end-1c").strip()
        
        if not text_to_speak:
            messagebox.showwarning("No Content", "No definition to speak.")
            return

        try:
            # Initialize pygame mixer if not already initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                
            # Stop any existing audio
            pygame.mixer.music.stop()
            
            # Generate temporary audio file
            tts = gTTS(text=text_to_speak, lang='en')
            tts.save("temp_definition.mp3")
            
            # Play the audio
            pygame.mixer.music.load("temp_definition.mp3")
            pygame.mixer.music.play()
            self.audio_state = "playing"
            self.speak_button.configure(image=Play_button)
            
        except Exception as e:
            messagebox.showerror("TTS Error", f"Text-to-speech failed: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists("temp_definition.mp3"):
                os.remove("temp_definition.mp3")

    def pause_audio(self):
        """Pause the currently playing audio"""
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.audio_state = "paused"
            self.speak_button.configure(image=Play_button)

    def resume_audio(self):
        """Resume the paused audio"""
        if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
            self.audio_state = "playing"
            self.speak_button.configure(image=Play_button)

    def create_navigation_buttons(self):
        """Create history and microphone buttons"""
        self.history_button = customtkinter.CTkButton(
            self,
            text="",
            image=History_Button_Image,
            fg_color="#140431",
            hover_color="#707070",
            width=30,
            height=30,
            command=self.show_history
        )
        self.history_button.grid(row=0, column=0, padx=10, pady=20, sticky="nw")

        self.microphone_button = customtkinter.CTkButton(
            self,
            text="",
            image=Micro_Button_Image,
            fg_color="#140431",
            hover_color="#707070",
            width=30,
            height=30,
            command=self.start_voice_input
        )
        self.microphone_button.place(x=350, y=20)

    def create_search_components(self):
        """Create search entry and lookup button"""
        self.search_entry = customtkinter.CTkEntry(
            self,
            placeholder_text="     search         🔎",
            fg_color='black',
            font=('bold', 20),
            border_color='#140431',
            width=230,
            height=35,
            border_width=2,
            corner_radius=30
        )
        self.search_entry.place(x=90, y=250)

        self.lookup_button = customtkinter.CTkButton(
            self,
            text="LOOK UP",
            command=self.search_word,
            fg_color="green",
            hover_color="#C850C0",
            border_width=2,
            width=80,
            height=35,
            border_color='#FFCC70',
            corner_radius=30
        )
        self.lookup_button.place(x=150, y=290)

    def add_to_history(self, word):
        """Add a searched word to history database"""
        self.cursor.execute("INSERT INTO search_history (word) VALUES (?)", (word,))
        self.conn.commit()

    def search_word(self):
        """Fetch and display word definitions"""
        word = self.search_entry.get().strip()
        if not word:
            messagebox.showwarning("Input Error", "Please enter a word.")
            return

        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            response.raise_for_status()
            self.display_definitions(response.json())
            self.add_to_history(word)
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"Failed to connect: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_definitions(self, data):
        """Display definitions in the text box"""
        self.definition_text.configure(state="normal")
        self.definition_text.delete("1.0", "end")
        
        for meaning in data[0]['meanings']:
            part_of_speech = meaning.get('partOfSpeech', '')
            self.definition_text.insert("end", f"{part_of_speech}\n", "bold")
            
            for idx, definition in enumerate(meaning['definitions'], 1):
                self.definition_text.insert("end", f"  {idx}. {definition['definition']}\n")
                
                if 'example' in definition:
                    self.definition_text.insert("end", f"     Example: {definition['example']}\n", "italic")
                
                if 'synonyms' in definition:
                    self.definition_text.insert("end", 
                        f"     Synonyms: {', '.join(definition['synonyms'][:3])}\n")
                
                self.definition_text.insert("end", "\n")
        
        self.definition_text.configure(state="disabled")

    def start_voice_input(self):
        """Start voice recognition in a background thread"""
        threading.Thread(target=self.process_voice_input, daemon=True).start()

    def process_voice_input(self):
        """Handle voice input processing with proper resource management"""
        try:
            # Check microphone availability
            if not sr.Microphone.list_microphone_names():
                self.show_voice_error("No microphone detected")
                return

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
            self.search_word()
        ])

    def show_voice_error(self, message):
        """Show voice recognition errors"""
        self.after(0, lambda: messagebox.showerror("Voice Error", message))


    def show_history(self):
        if self.history_window is not None and self.history_window.winfo_exists():
            self.history_window.lift()
            self.history_window.focus_force()
            return
        
        """Display search history window"""
        history_window = customtkinter.CTkToplevel(self)
        history_window.title("Search History")
        history_window.geometry("400x450")
        
        scroll_frame = customtkinter.CTkScrollableFrame(history_window, width=250, height=350)
        scroll_frame.pack(pady=10)
        
        self.populate_history_entries(scroll_frame)

    def populate_history_entries(self, parent):
        """Populate history entries in scrollable frame"""
        self.cursor.execute("""
            SELECT word, strftime('%Y-%m-%d %H:%M', timestamp, 'localtime') 
            FROM search_history 
            ORDER BY timestamp DESC
        """)
        records = self.cursor.fetchall()
        
        if not records:
            customtkinter.CTkLabel(parent, text="No search history yet.").pack()
        else:
            for word, timestamp in records:
                self.create_history_button(parent, word, timestamp)

    def create_history_button(self, parent, word, timestamp):
        """Create a history entry button"""
        btn = customtkinter.CTkButton(
            parent,
            text=f"{word} - {timestamp}",
            command=lambda w=word: self.select_history_word(w),
            width=200,
            anchor="w"
        )
        btn.pack(pady=2, fill='x')

    def select_history_word(self, word):
        """Handle history word selection"""
        if self.history_window is not None:
            self.history_window.destroy()
            self.history_window = None
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, word)
        self.search_word()

    def on_closing(self):
        """Handle application shutdown"""
        self.conn.close()
        self.destroy()

if __name__ == "__main__":
    app = DictionaryApp()
    app.mainloop()
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
import time
import io
import pyttsx3

# Initialize appearance settings
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Load images
History_Button_Image = customtkinter.CTkImage(Image.open('images/history.png'), size=(30, 30))
Micro_Button_Image = customtkinter.CTkImage(Image.open('images/micro.png'), size=(30, 30))
Logo_Image = customtkinter.CTkImage(Image.open('images/updated logo.png'), size=(200, 200))
Play_button = customtkinter.CTkImage(Image.open('images/play buttom.png'), size=(30, 30))
DeleteIcon = customtkinter.CTkImage(Image.open('images/delete_icon.png'), size=(20, 20))

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
        self.recognizer = sr.Recognizer()
        self.audio_state = "stopped"  # Can be: stopped, processing, playing, paused
        self.history_window = None
        self.last_search_time = 0
        
        # Initialize audio system
        self.audio_engine = self.init_pyttsx3()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.audio_buffer = {}
        self.buffer_size = 5  # Number of audio clips to keep in memory

    def init_pyttsx3(self):
        """Initialize pyttsx3 with optimal settings"""
        try:
            engine = pyttsx3.init()
            # Configure voice settings
            voices = engine.getProperty('voices')
            for voice in voices:
                if "female" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            engine.setProperty('rate', 160)
            engine.setProperty('volume', 0.95)
            # Warm up the engine
            engine.say('')
            engine.runAndWait()
            return engine
        except Exception as e:
            print(f"pyttsx3 initialization failed: {e}")
            return None

    def configure_layout(self):
        """Set up grid layout configuration"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def setup_database(self):
        """Initialize SQLite database connection with error handling"""
        try:
            self.conn = sqlite3.connect('history.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(word) ON CONFLICT REPLACE
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")

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
        if self.audio_state == "processing":
            messagebox.showinfo("Processing", "Audio is being processed, please wait")
            return
        elif self.audio_state == "stopped":
            self.speak_definition()
        elif self.audio_state == "playing":
            self.pause_audio()
        elif self.audio_state == "paused":
            self.resume_audio()

    def speak_definition(self):
        """Convert definition text to speech using hybrid approach"""
        text_to_speak = self.definition_text.get("1.0", "end-1c").strip()
        
        if not text_to_speak:
            messagebox.showwarning("No Content", "No definition to speak.")
            return

        if self.audio_state == "processing":
            messagebox.showinfo("Processing", "Audio is being generated, please wait")
            return

        self.audio_state = "processing"
        self.speak_button.configure(state="disabled")
        
        def _generate_and_play():
            try:
                # Try to use cached audio first
                if text_to_speak in self.audio_buffer:
                    audio_file = self.audio_buffer[text_to_speak]
                    audio_file.seek(0)
                else:
                    # Generate new audio
                    audio_file = io.BytesIO()
                    
                    # Try pyttsx3 first (offline)
                    if self.audio_engine:
                        temp_file = f"temp_tts_{time.time()}.wav"
                        self.audio_engine.save_to_file(text_to_speak, temp_file)
                        self.audio_engine.runAndWait()
                        
                        # Load the generated file into memory
                        with open(temp_file, 'rb') as f:
                            audio_file.write(f.read())
                        os.remove(temp_file)
                    else:
                        # Fall back to gTTS (requires internet)
                        try:
                            requests.get("https://www.google.com", timeout=3)
                            tts = gTTS(text=text_to_speak, lang='en')
                            tts.write_to_fp(audio_file)
                        except requests.ConnectionError:
                            messagebox.showerror("Network Error", 
                                "You need network access when offline TTS is unavailable")
                            return
                    
                    audio_file.seek(0)
                    
                    # Cache the audio
                    if len(self.audio_buffer) >= self.buffer_size:
                        self.audio_buffer.pop(next(iter(self.audio_buffer)))
                    self.audio_buffer[text_to_speak] = audio_file
                
                # Play with pygame
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy() and self.audio_state == "playing":
                    time.sleep(0.1)
                
            except Exception as e:
                messagebox.showerror("Audio Error", f"Failed to generate speech: {str(e)}")
            finally:
                self.audio_state = "stopped"
                self.after(0, lambda: self.speak_button.configure(state="normal"))

        # Run in separate thread
        threading.Thread(target=_generate_and_play, daemon=True).start()
        self.audio_state = "playing"

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
        """Add a searched word to history database with error handling"""
        if not word or time.time() - self.last_search_time < 2:
            return  # Prevent duplicate rapid additions
            
        self.last_search_time = time.time()
        
        try:
            self.cursor.execute("INSERT OR REPLACE INTO search_history (word) VALUES (?)", (word,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error adding to history: {e}")
            try:
                # Attempt to reconnect if connection was lost
                self.conn = sqlite3.connect('history.db', check_same_thread=False)
                self.cursor = self.conn.cursor()
                self.cursor.execute("INSERT OR REPLACE INTO search_history (word) VALUES (?)", (word,))
                self.conn.commit()
            except sqlite3.Error as e2:
                print(f"Failed to reconnect to database: {e2}")

    def search_word(self):
        """Fetch and display word definitions"""
        self.word = self.search_entry.get().strip().capitalize()
        
        if not self.word:
            messagebox.showwarning("Input Error", "Please enter a word.")
            return

        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{self.word}")
            response.raise_for_status()
            self.display_definitions(response.json())
            self.add_to_history(self.word)
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"Failed to connect: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        self.search_entry.delete(0, tk.END)

    def display_definitions(self, data):
        """Display definitions in the text box"""
        self.definition_text.configure(state="normal")
        self.definition_text.delete("1.0", "end")

        self.definition_text.insert("end", f"{self.word}\n\n", "bold")
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
        """Display search history window with improved database handling"""
        if self.history_window is not None and self.history_window.winfo_exists():
            self.history_window.lift()
            self.history_window.focus_force()
            return
            
        try:
            history_window = customtkinter.CTkToplevel(self)
            self.history_window = history_window
            history_window.title("Search History")
            history_window.geometry("400x500")  # Increased height to accommodate button
            history_window.protocol("WM_DELETE_WINDOW", self.on_history_window_close)
            
            # Main container frame
            container = customtkinter.CTkFrame(history_window)
            container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Scrollable frame for history items
            scroll_frame = customtkinter.CTkScrollableFrame(container, width=350, height=380)
            scroll_frame.pack(fill="both", expand=True)
            
            try:
                self.cursor.execute("""
                    SELECT word, strftime('%Y-%m-%d %H:%M', timestamp, 'localtime') 
                    FROM search_history 
                    ORDER BY timestamp DESC
                    LIMIT 50
                """)
                records = self.cursor.fetchall()
                
                if not records:
                    customtkinter.CTkLabel(scroll_frame, text="No search history yet.").pack()
                else:
                    for word, timestamp in records:
                        self.create_history_button(scroll_frame, word, timestamp)
                    
                # Add Clear History button at the bottom
                clear_button = customtkinter.CTkButton(
                    container,
                    text="Clear History",
                    image=DeleteIcon,
                    fg_color="#FF5555",
                    hover_color="#FF3333",
                    command=self.confirm_clear_history
                )
                clear_button.pack(pady=10)
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to load history: {str(e)}")
                history_window.destroy()
                self.history_window = None
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open history window: {str(e)}")
            if 'history_window' in locals():
                history_window.destroy()
            self.history_window = None

    def confirm_clear_history(self):
        """Show confirmation dialog before clearing history"""
        if self.history_window is None:
            return
            
        response = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear all search history?",
            parent=self.history_window
        )
        if response:
            self.clear_history()
            self.history_window.destroy()
            self.show_history()  # Refresh the history window

    def clear_history(self):
        """Clear all search history from the database"""
        try:
            self.cursor.execute("DELETE FROM search_history")
            self.conn.commit()
            messagebox.showinfo("Success", "Search history cleared successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to clear history: {str(e)}")

    def on_history_window_close(self):
        """Reset history window tracking when closed"""
        if self.history_window is not None:
            self.history_window.destroy()
            self.history_window = None

    def create_history_button(self, parent, word, timestamp):
        """Create a history entry button"""
        btn = customtkinter.CTkButton(
            parent,
            text=f"{word} - {timestamp}",
            command=lambda w=word: self.select_history_word(w),
            width=320,
            anchor="w",
            fg_color="#1b0c43",
            hover_color="#2a1a5e"
        )
        btn.pack(pady=2, padx=10, fill='x')

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
        try:
            # Clean up audio resources
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            
            # Clear audio cache
            for audio_file in self.audio_buffer.values():
                audio_file.close()
            self.audio_buffer.clear()
            
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            self.destroy()

if __name__ == "__main__":
    app = DictionaryApp()
    app.mainloop()
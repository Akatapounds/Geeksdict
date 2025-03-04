import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3  # For text-to-speech
from textblob import TextBlob  # For spelling correction
import sqlite3  # For local database (history and favorites)
import threading  # To handle database operations in a separate thread
from PIL import Image, ImageTk  # For image background
import requests
import json

# Constants for the app (API credentials)
app_id = "aa3b22cc"
app_key = "6b0ea8b2f150ab4c493e83752202fd9e"

# Initialize TTS engine
tts_engine = pyttsx3.init()

# Database setup for history and favorites
def init_db():
    conn = sqlite3.connect('audio_dictionary.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (word TEXT PRIMARY KEY)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS favorites (word TEXT PRIMARY KEY)''')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# Main Application Class
class AudioDictionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Dictionary with Spelling Checker")
        self.root.geometry("600x400")

        # Load background image (Optional)
        # self.bg_image = Image.open("images/Background.png")  # Replace with your image path
        # self.bg_image = self.bg_image.resize((600, 400), Image.ANTIALIAS)
        # self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)

        # Create a canvas for the background (Optional)
        # self.canvas = tk.Canvas(root, width=600, height=400)
        # self.canvas.pack(fill="both", expand=True)
        # self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")

        # Variables
        self.word_var = tk.StringVar()
        self.history_list = []
        self.favorites_list = []

        # Load history and favorites in a separate thread
        self.load_data_threaded()

        # GUI Layout
        self.create_widgets()

    def load_data_threaded(self):
        threading.Thread(target=self.load_data, daemon=True).start()

    def load_data(self):
        self.history_list = self.load_history()
        self.favorites_list = self.load_favorites()
        self.update_history_listbox()
        self.update_favorites_listbox()

    def create_widgets(self):
        # Header Frame
        header_frame = ttk.Frame(self.root)
        header_frame.place(relx=0.5, rely=0.1, anchor="center")

        ttk.Label(header_frame, text="Merriam-Webster", font=("Arial", 16, "bold"), background="white").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Label(header_frame, text="SINCE 1828", font=("Arial", 10), background="white").pack(side=tk.LEFT, padx=5, pady=5)

        # Search Frame
        search_frame = ttk.Frame(self.root)
        search_frame.place(relx=0.5, rely=0.2, anchor="center")

        self.word_entry = ttk.Entry(search_frame, textvariable=self.word_var, width=40, font=("Arial", 12))
        self.word_entry.grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(search_frame, text="Search", command=self.search_word).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(search_frame, text="Pronounce", command=self.pronounce_word).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="Add to Favorites", command=self.add_to_favorites).grid(row=0, column=3, padx=5, pady=5)

        # Result Frame
        result_frame = ttk.Frame(self.root)
        result_frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(result_frame, text="Definition:", background="white").pack(anchor=tk.W)
        self.definition_text = tk.Text(result_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.definition_text.pack(fill=tk.BOTH, expand=True)

        # Spelling Suggestions
        ttk.Label(result_frame, text="Spelling Suggestions:", background="white").pack(anchor=tk.W)
        self.suggestions_text = tk.Text(result_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)

        # History and Favorites Frame
        history_favorites_frame = ttk.Frame(self.root)
        history_favorites_frame.place(relx=0.5, rely=0.8, anchor="center")

        ttk.Label(history_favorites_frame, text="History:", background="white").grid(row=0, column=0, padx=5, pady=5)
        self.history_listbox = tk.Listbox(history_favorites_frame, height=5)
        self.history_listbox.grid(row=1, column=0, padx=5, pady=5)

        ttk.Label(history_favorites_frame, text="Favorites:", background="white").grid(row=0, column=1, padx=5, pady=5)
        self.favorites_listbox = tk.Listbox(history_favorites_frame, height=5)
        self.favorites_listbox.grid(row=1, column=1, padx=5, pady=5)

    def search_word(self):
        """
        Fetches the definition, part of speech, examples, synonyms, and antonyms
        of a given word from the Free Dictionary API.
        """
        word = self.word_var.get().strip()
        if not word:
            messagebox.showwarning("Input Error", "Please enter a word.")
            return

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

        # Sending GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            self.definition_text.config(state=tk.NORMAL)
            self.definition_text.delete(1.0, tk.END)

            # Iterate through the meanings and print definitions
            for meaning in data[0]['meanings']:
                for definition in meaning['definitions']:
                    try:
                        if definition['definition']:
                            self.definition_text.config(state=tk.NORMAL)
                            self.definition_text.insert(tk.END, f"Definition: {definition['definition']}\n")
                            self.definition_text.config(state=tk.DISABLED)
                    except KeyError:
                        pass

                    try:
                        if definition['example']:
                            self.definition_text.config(state=tk.NORMAL)
                            self.definition_text.insert(tk.END, f"Example: {definition['example']}\n")
                            self.definition_text.config(state=tk.DISABLED)
                    except KeyError:
                        pass

                    try:
                        if definition['synonyms']:
                            self.definition_text.config(state=tk.NORMAL)
                            self.definition_text.insert(tk.END, f"Synonyms: {', '.join(definition['synonyms'])}\n")
                            self.definition_text.config(state=tk.DISABLED)
                    except KeyError:
                        pass

                    try:
                        if definition['antonyms']:
                            self.definition_text.config(state=tk.NORMAL)
                            self.definition_text.insert(tk.END, f"Antonyms: {', '.join(definition['antonyms'])}\n")
                            self.definition_text.config(state=tk.DISABLED)
                    except KeyError:
                        pass
                    
        else:
            messagebox.showerror("Error", f"Unable to fetch data (Status code: {response.status_code})")

    def pronounce_word(self):
        word = self.word_var.get().strip()
        if not word:
            messagebox.showwarning("Input Error", "Please enter a word.")
            return

        # Pronounce the word using TTS
        tts_engine.say(word)
        tts_engine.runAndWait()

    def add_to_favorites(self):
        word = self.word_var.get().strip()
        if not word:
            messagebox.showwarning("Input Error", "Please enter a word.")
            return

        if word not in self.favorites_list:
            self.favorites_list.append(word)
            cursor.execute("INSERT OR IGNORE INTO favorites (word) VALUES (?)", (word,))
            conn.commit()
            self.update_favorites_listbox()

    def load_history(self):
        cursor.execute("SELECT word FROM history")
        return [row[0] for row in cursor.fetchall()]

    def load_favorites(self):
        cursor.execute("SELECT word FROM favorites")
        return [row[0] for row in cursor.fetchall()]

    def update_history_listbox(self):
        self.history_listbox.delete(0, tk.END)
        for word in self.history_list:
            self.history_listbox.insert(tk.END, word)

    def update_favorites_listbox(self):
        self.favorites_listbox.delete(0, tk.END)
        for word in self.favorites_list:
            self.favorites_listbox.insert(tk.END, word)

    def on_closing(self):
        conn.close()
        self.root.destroy()

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioDictionaryApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

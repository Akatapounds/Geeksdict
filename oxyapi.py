import customtkinter
import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image
import sqlite3  # For local database (history and favorites)
import threading

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


# Load images
History_Button_Image = customtkinter.CTkImage(Image.open('images/history.png'), size=(30, 30))
Micro_Button_Image = customtkinter.CTkImage(Image.open('images/micro.png'), size=(30, 30))
Logo_Image = customtkinter.CTkImage(Image.open('images/updated logo.png'), size=(200, 200))

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("GEEK DICTIONARY")
        self.geometry("400x600")
        self.resizable(True, True)
        
        # Background setup
        self.bg_image = customtkinter.CTkImage(Image.open("images/background2.png"), size=(400, 600))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image, text="")
        self.bg_image_label.grid(row=0, column=0, sticky="nsew")
        
        # History button
        self.history_button = customtkinter.CTkButton(
            master=self,
            text="",
            image=History_Button_Image,
            fg_color="#140431",
            hover_color="#707070",
            width=30,
            height=30,
            border_color='#140431',
            bg_color='#140431'
        )
        self.history_button.grid(row=0, column=0, padx=10, pady=20, sticky="nw")

        # Microphone button
        self.micro_button = customtkinter.CTkButton(
            master=self,
            text="",
            image=Micro_Button_Image,
            fg_color="#140431",
            hover_color="#707070",
            width=30,
            height=30,
            border_color='#140431',
            bg_color='#140431'
        )
        self.micro_button.place(x=350, y=20)

        # Logo
        self.logo_label = customtkinter.CTkLabel(master=self, text="", image=Logo_Image, 
                                               fg_color='#140431', corner_radius=60, bg_color='#140431')
        self.logo_label.place(x=95, y=45)

        # Search entry
        self.entry = customtkinter.CTkEntry(
            master=self,
            placeholder_text="     search         🔎",
            fg_color='black',
            font=('bold', 20),
            border_color='#140431',
            bg_color='#140431',
            width=230,
            height=35,
            border_width=2,
            corner_radius=30
        )
        self.entry.place(x=90, y=250)

        # Lookup button
        self.lookup_button = customtkinter.CTkButton(
            master=self,
            text="LOOK UP",
            command=self.search_word,
            fg_color="green",
            hover_color="#C850C0",
            border_width=2,
            width=80,
            height=35,
            border_color='#FFCC70',
            bg_color='#140431',
            corner_radius=30
        )
        self.lookup_button.place(x=150, y=290)

        # Results frame
        self.frame = customtkinter.CTkFrame(
            master=self,
            fg_color="white",
            border_color="#FFCC70",
            border_width=2,
            width=350,
            height=200,
            corner_radius=30,
            bg_color='#140431'
        )
        self.frame.place(x=0,y=380)

        # Text widget for definitions
        self.definition_text = customtkinter.CTkTextbox(
            master=self.frame,
            fg_color="white",
            text_color="black",
            wrap="word",
            width=380,
            height=180,
            font=("Arial", 12)
        )
        self.definition_text.pack(padx=10, pady=10)

    def search_word(self):
        """Fetch and display word definitions"""
        word = self.entry.get().strip()
        if not word:
            messagebox.showwarning("Input Error", "Please enter a word.")
            return

        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            response.raise_for_status()
            data = response.json()
            
            self.definition_text.configure(state="normal")
            self.definition_text.delete("1.0", "end")
            
            for meaning in data[0]['meanings']:
                part_of_speech = meaning.get('partOfSpeech', '')
                self.definition_text.insert("end", f"{part_of_speech}\n", "bold")
                
                for idx, definition in enumerate(meaning['definitions'], 1):
                    text = f"  {idx}. {definition['definition']}\n"
                    self.definition_text.insert("end", text)
                    
                    if 'example' in definition:
                        self.definition_text.insert("end", f"     Example: {definition['example']}\n", "italic")
                    
                    if 'synonyms' in definition:
                        self.definition_text.insert("end", f"     Synonyms: {', '.join(definition['synonyms'][:3])}\n")
                    
                    self.definition_text.insert("end", "\n")
            
            self.definition_text.configure(state="disabled")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"Failed to connect: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
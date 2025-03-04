import customtkinter
from PIL import Image
import sqlite3  # For local database (history and favorites)
import threading

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


# Load the button images with the correct resampling filter
History_Button_Image = customtkinter.CTkImage(Image.open('images/history.png'), size=(30, 30))
Micro_Button_Image= customtkinter.CTkImage(Image.open('images/micro.png'), size=(30, 30))
Play_Button_Image= customtkinter.CTkImage(Image.open('images/Play.png'), size=(30, 30))
Pause_Button_Image= customtkinter.CTkImage(Image.open('images/Pause.png'), size=(30, 30))
Logo_Image=customtkinter.CTkImage(Image.open('images/updated logo.png'),size=(200,200))
def slide_out():
    pass



def silde_back():
    pass



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("GEEK DICTIONARY")
        self.geometry("400x600")
        self.resizable(True, True)
    

        
        # Load and set the background image
        self.bg_image = customtkinter.CTkImage(Image.open("images/background2.png"), size=(400, 600))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image, text="")
        self.bg_image_label.grid(row=0, column=0, sticky="nsew")
        
        # Create a button with the menu button image
        self.button = customtkinter.CTkButton(
            master=self,
            text="",  # No text
            image=History_Button_Image,
            fg_color="#140431",  # Match the background color of your image or window
            hover_color="#707070",  # Match the background color
            border_width=2,  # Remove the border
            width=30,  # Set button width
            height=30,  # Set button height
            border_color='#140431',
            bg_color='#140431'
        
        )
        self.button.grid(row=0, column=0, padx=10, pady=20, sticky="nw")


        self.button = customtkinter.CTkButton(
            master=self,
            text="",  # No text
            image=Micro_Button_Image,
            fg_color="#140431",  # Match the background color of your image or window
            hover_color="#707070",  # Match the background color
            border_width=2,  # Remove the border
            width=30,  # Set button width
            height=30,  # Set button height
            border_color='#140431',
            bg_color='#140431')
        self.button.place(x=350, y=20)

        
        self.label = customtkinter.CTkLabel(master=self, text="",image=Logo_Image,fg_color='#140431',corner_radius=60,bg_color='#140431')
        self.label.place(x=95,y=45)


#search entry box
        self.entry = customtkinter.CTkEntry(master=self,
                               placeholder_text="search            ⌕",
                               fg_color='white',
                               font=('bold',30),
                               border_color='#140431',
                               bg_color='#140431',

                               width=250,
                               height=35,
                               border_width=2,
                               corner_radius=30)
        self.entry.place(x=60,y=250)
        self.button = customtkinter.CTkButton(
            master=self,
            text="LOOK UP",
            fg_color="#4158D0",  # Match the background color of your image or window
            hover_color="#C850C0",  # Match the background color
            border_width=2,  # Remove the border
            width=30,  # Set button width
            height=30,  # Set button height
            border_color='#FFCC70',
            bg_color='#140431',corner_radius=30)
        self.button.place(x=300, y=300)


#frame for word displaying definiens.
        self.frame=customtkinter.CTkFrame(master=self,fg_color="white",border_color="#FFCC70",border_width=2,width=400,height=250,corner_radius=30,bg_color='#140431')
        self.frame.place(x=0,y=350)




        self.button = customtkinter.CTkButton(
            master=self,
            text="",  # No text
            image=Play_Button_Image,
            fg_color="white",  # Match the background color of your image or window
            hover_color="#707070",  # Match the background color
            border_width=2,  # Remove the border
            width=30,  # Set button width
            height=30,  # Set button height
            border_color='white',
            bg_color='white')
        self.button.place(x=350, y=20)



       
            




if __name__ == "__main__":
    app = App()
    app.mainloop()
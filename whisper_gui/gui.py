import customtkinter as ctk

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # self.pack(padx=20, pady=20)
        
        # create tabs
        self.add("General")
        self.add("Settings")
        self.set("General")

        

        # General Tab widgets

        # Model output (editable and exportable)
        self.textbox = ctk.CTkTextbox(master=self.tab("General"), width=400, corner_radius=0)
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.insert("0.0", "Some example text!\n" * 50)

        self.button = ctk.CTkButton(master=self.tab("General"), text="Run Whisper", command=self.button_callback)
        self.button.grid(row=1, column=0, sticky="nsew")
        # self.button.pack(padx=20, pady=20)

    def button_callback(self):
        print("button clicked")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # self.geometry("600x500")
        self.title("Whisper-sens")

    
        self.tab_view = MyTabView(master=self)
        self.tab_view.grid(row=0, column=0, padx=5, pady=5)





if __name__ == '__main__':
    app = App()
    app.mainloop()


import customtkinter as ctk
from whisper import Whisper


class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # self.pack(padx=20, pady=20)
        
        # create tabs
        self.add("Settings")
        self.add("General")
        self.set("Settings")

        self.recording_file = None
        self.whisper = Whisper()
        self.predictions = ""
        

        # General Tab widgets

        # File selections and Model settings
        self.button = ctk.CTkButton(master=self.tab("Settings"), text="Select File", command=self.button_select_file)
        self.button.grid(row=0, column=0, sticky="nsew")

        # Model output (editable and exportable)
        self.textbox = ctk.CTkTextbox(master=self.tab("General"), width=400, corner_radius=0)
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.insert("0.0", "Trasctriptions...")
        self.button = ctk.CTkButton(master=self.tab("General"), text="Run Whisper", command=self.button_run_model)
        self.button.grid(row=1, column=0, sticky="nsew")
        # self.button.pack(padx=20, pady=20)

    def button_select_file(self):
        print("Select file...")
        self.recording_file = ctk.filedialog.askopenfilename(
            parent=self.tab("Settings"),
            title="Browse Audio/Video File",
            filetypes=(
                ("Audio Files", ("*.mp3", "*.wav")),
                ("Video Files", ("*.mp4",)),
                ("A/V Files", ("*.mp3", "*.wav", "*.mp4"))
            )
        )
        print(self.recording_file)
        if not self.recording_file:
            print("No file selected")
            return None
        else: 
            pass
            # return recording_file # TODO: buttons dont return. Use Whisper obj inside App somehow.


    def button_run_model(self):
        print("Running Whisper. do not click the button again!!!")
        # whisper = Whisper()
        self.whisper.load_models(model_path='/home/jayya931/UPPMAX/Whisper_project/Whisper-sens/models/')
        # predictions = whisper.pipeline()
        # print(predictions)
        self.predictions = self.whisper.pipeline(self.recording_file)
        print(self.predictions)
        self.textbox.delete("0.0", 'end')
        self.textbox.insert("0.0", self.predictions)



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
    



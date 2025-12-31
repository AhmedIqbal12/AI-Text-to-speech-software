import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyttsx3
import threading

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech Software")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.is_speaking = False
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Text-to-Speech Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Text input area
        text_frame = ttk.LabelFrame(main_frame, text="Enter Text", padding="5")
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                    width=50, height=10, font=("Arial", 11))
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        controls_frame.columnconfigure(1, weight=1)
        
        # Voice selection
        ttk.Label(controls_frame, text="Voice:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.voice_combo = ttk.Combobox(controls_frame, state="readonly", width=30)
        self.voice_combo.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        # Get available voices
        self.voices = self.engine.getProperty('voices')
        voice_names = [voice.name for voice in self.voices]
        self.voice_combo['values'] = voice_names
        if voice_names:
            self.voice_combo.current(0)
        
        # Rate control
        ttk.Label(controls_frame, text="Speed:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.rate_scale = ttk.Scale(controls_frame, from_=50, to=300, orient=tk.HORIZONTAL)
        self.rate_scale.set(150)
        self.rate_scale.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.rate_label = ttk.Label(controls_frame, text="150 WPM")
        self.rate_label.grid(row=1, column=2, padx=5)
        self.rate_scale.configure(command=self.update_rate_label)
        
        # Volume control
        ttk.Label(controls_frame, text="Volume:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.volume_scale = ttk.Scale(controls_frame, from_=0, to=1, orient=tk.HORIZONTAL)
        self.volume_scale.set(1.0)
        self.volume_scale.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.volume_label = ttk.Label(controls_frame, text="100%")
        self.volume_label.grid(row=2, column=2, padx=5)
        self.volume_scale.configure(command=self.update_volume_label)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, pady=10)
        
        self.speak_button = ttk.Button(buttons_frame, text="▶ Speak", command=self.speak_text)
        self.speak_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="⏹ Stop", command=self.stop_speaking, 
                                      state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.clear_button = ttk.Button(buttons_frame, text="Clear", command=self.clear_text)
        self.clear_button.grid(row=0, column=2, padx=5)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def update_rate_label(self, value):
        self.rate_label.config(text=f"{int(float(value))} WPM")
    
    def update_volume_label(self, value):
        self.volume_label.config(text=f"{int(float(value) * 100)}%")
    
    def speak_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("No Text", "Please enter some text to speak!")
            return
        
        self.is_speaking = True
        self.speak_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Speaking...")
        
        # Run speech in a separate thread to avoid freezing GUI
        thread = threading.Thread(target=self._speak_thread, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _speak_thread(self, text):
        try:
            # Set voice
            voice_index = self.voice_combo.current()
            if voice_index >= 0:
                self.engine.setProperty('voice', self.voices[voice_index].id)
            
            # Set rate
            rate = int(self.rate_scale.get())
            self.engine.setProperty('rate', rate)
            
            # Set volume
            volume = self.volume_scale.get()
            self.engine.setProperty('volume', volume)
            
            # Speak
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.is_speaking = False
            self.root.after(0, self._reset_buttons)
    
    def _reset_buttons(self):
        self.speak_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready")
    
    def stop_speaking(self):
        if self.is_speaking:
            self.engine.stop()
            self.is_speaking = False
            self._reset_buttons()
            self.status_label.config(text="Stopped")
    
    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.status_label.config(text="Text cleared")

def main():
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
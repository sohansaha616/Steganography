import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from stego_core import embed_in_image, extract_from_image, embed_in_audio, extract_from_audio
from stego_core import encode_text_stego, decode_text_stego, embed_in_video, extract_from_video

class StegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Steganography GUI")
        self.root.geometry("600x400")
        self.setup_ui()

    def setup_ui(self):
        self.action = tk.StringVar()
        self.method = tk.StringVar()
        self.file_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.message = tk.StringVar()
        self.key = tk.StringVar()
        self.frame_number = tk.IntVar()

        ttk.Label(self.root, text="Select Action:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.action, values=["Embed", "Extract"]).pack()

        ttk.Label(self.root, text="Select Media Type:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.method,
                     values=["Image", "Audio", "Text", "Video"]).pack()

        ttk.Label(self.root, text="File Path:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.file_path, width=50).pack()
        ttk.Button(self.root, text="Browse", command=self.browse_file).pack()

        ttk.Label(self.root, text="Output Path (for embed):").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.output_path, width=50).pack()
        ttk.Button(self.root, text="Browse Output", command=self.save_file).pack()

        ttk.Label(self.root, text="Message (for embed):").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.message, width=50).pack()

        ttk.Label(self.root, text="Key:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.key, show='*', width=50).pack()

        ttk.Label(self.root, text="Frame Number (for video only):").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.frame_number).pack()

        ttk.Button(self.root, text="Run", command=self.run_stego).pack(pady=10)

    def browse_file(self):
        self.file_path.set(filedialog.askopenfilename())

    def save_file(self):
        self.output_path.set(filedialog.asksaveasfilename())

    def run_stego(self):
        try:
            key = self.key.get().encode()
            method = self.method.get()
            action = self.action.get()
            if method == "Image":
                if action == "Embed":
                    embed_in_image(self.file_path.get(), self.message.get(), self.output_path.get(), key)
                    messagebox.showinfo("Success", "Message embedded in image.")
                else:
                    msg = extract_from_image(self.file_path.get(), key)
                    messagebox.showinfo("Extracted", f"Message: {msg}")

            elif method == "Audio":
                if action == "Embed":
                    embed_in_audio(self.file_path.get(), self.message.get(), self.output_path.get(), key)
                    messagebox.showinfo("Success", "Message embedded in audio.")
                else:
                    msg = extract_from_audio(self.file_path.get(), key)
                    messagebox.showinfo("Extracted", f"Message: {msg}")

            elif method == "Text":
                if action == "Embed":
                    encode_text_stego(self.file_path.get(), self.message.get(), self.output_path.get(), key)
                    messagebox.showinfo("Success", "Message embedded in text.")
                else:
                    msg = decode_text_stego(self.file_path.get(), key)
                    messagebox.showinfo("Extracted", f"Message: {msg}")

            elif method == "Video":
                if action == "Embed":
                    embed_in_video(self.file_path.get(), self.message.get(), self.frame_number.get(),
                                   self.output_path.get(), key)
                    messagebox.showinfo("Success", "Message embedded in video.")
                else:
                    msg = extract_from_video(self.file_path.get(), self.frame_number.get(), key)
                    messagebox.showinfo("Extracted", f"Message: {msg}")

            else:
                messagebox.showwarning("Invalid Input", "Choose valid media and action.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = StegoApp(root)
    root.mainloop()

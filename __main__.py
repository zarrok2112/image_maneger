import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame
from PIL import Image, ImageTk
import cv2
import os

class MasonryLayout:
    def __init__(self, root, folder):
        self.root = root
        self.folder = folder
        self.items = self.load_media_files(folder)

        self.canvas = Canvas(root, bg='black')
        self.scrollbar = Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.frame = Frame(self.canvas, bg='black')
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        
        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.columns = []
        self.column_frames = []

    def update_video(self, label, cap):
        """Actualiza los frames de un video en una etiqueta."""
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame.thumbnail((200, 200))
            tk_frame = ImageTk.PhotoImage(frame)
            label.configure(image=tk_frame)
            label.image = tk_frame
            label.after(33, lambda: self.update_video(label, cap))  # Asumiendo aproximadamente 30 fps

    def load_media_files(self, folder):
        """Carga todas las imágenes y videos de un directorio dado."""
        files = []
        for filename in os.listdir(folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.mp4')):
                files.append(os.path.join(folder, filename))
        return files

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Reorganiza el contenido según el ancho actual del canvas."""
        width = event.width
        col_width = 200
        num_cols = max(width // col_width, 1)

        if num_cols != len(self.columns):
            for col_frame in self.column_frames:
                col_frame.destroy()
            self.columns = [[] for _ in range(num_cols)]
            self.column_frames = [Frame(self.frame, bg='black') for _ in range(num_cols)]

            for i, col_frame in enumerate(self.column_frames):
                col_frame.grid(row=0, column=i, padx=5, pady=5)

            for item in self.items:
                self.place_media(item)

    def place_media(self, file_path):
        """Coloca un elemento multimedia en la columna más corta."""
        col_lengths = [sum(widget.winfo_reqheight() for widget in col) for col in self.columns]
        min_col = col_lengths.index(min(col_lengths))
        frame = self.column_frames[min_col]

        if file_path.endswith('.mp4'):
            cap = cv2.VideoCapture(file_path)
            ret, frame_img = cap.read()
            if ret:
                frame_img = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
                frame_img = Image.fromarray(frame_img)
                img = ImageTk.PhotoImage(frame_img)
                label = tk.Label(frame, image=img, bg='black')
                label.image = img
                label.pack(fill="both", expand=True)
                self.columns[min_col].append(label)
                # Aquí podría añadir código para actualizar el vídeo continuamente
                self.update_video(label, cap)
        else:
            img = Image.open(file_path)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=tk_img, bg='black')
            label.image = tk_img
            label.pack(fill="both", expand=True)
            self.columns[min_col].append(label)

def main():
    root = tk.Tk()
    root.title("Visor de Imágenes y Videos Dinámico")
    folder = "./test"  # Cambiar a la carpeta deseada
    app = MasonryLayout(root, folder)
    root.mainloop()

if __name__ == "__main__":
    main()

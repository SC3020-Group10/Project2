import tkinter as tk
from PIL import ImageTk, Image
import sv_ttk
from Database.engine import Engine
from Graph.graph import Graph

class App(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)
        self.engine = Engine()

        self.wm_title("Database Query Visualizer")
        self.geometry("800x600")
        self.config(bg="gray")

        # Create left and right frames
        self.left_frame = tk.Frame(self, width=400, height=600, bg='skyblue')
        self.left_frame.grid(row=0, column=0, padx=5, pady=5)
        self.left_frame.grid_propagate(False)

        self.right_frame = tk.Frame(self, width=400, height=600, bg='skyblue')
        self.right_frame.grid(row=0, column=1, padx=5, pady=5)
        # self.right_frame.grid_propagate(False)

        tk.Label(self.left_frame, text="Enter SQL Query").grid(row=0, column=0, padx=10, pady=10)
        self.input_box = tk.Entry(self.left_frame)
        self.input_box.grid(row=1, column=0, padx=10, pady=10)
        tk.Button(self.left_frame, text="Submit", command=self._on_submit).grid(row=2, column=0, padx=10, pady=10)

        tk.Label(self.right_frame, text="Your SQL Query").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.right_frame, text="", width=50, height=20).grid(row=1, column=0, padx=10, pady=10)

        sv_ttk.set_theme("light")

    def _load_plot(self, filename:str):
        self.plot_image = ImageTk.PhotoImage(Image.open(filename))
        tk.Label(self.right_frame, image=self.plot_image).grid(row=2,column=0, padx=5, pady=5)

    def _on_submit(self):
        raw_query = self.input_box.get()
        self.input_box.delete(0, tk.END)
        tk.Label(self.right_frame, text=raw_query, width=50, height=20, anchor='nw', font=('Courier')).grid(row=1, column=0, padx=10, pady=10)

        query_json = self.engine.get_query_plan(raw_query)
        graph = Graph(query_json, raw_query)

        filename = graph.save_graph_file()
        self._load_plot(filename)


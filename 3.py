import os
import psutil
import time
import socket
import tkinter as tk
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def log_event(event_type, event, log_file):
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.ctime()}] {event_type}: {event}\n")
    except PermissionError:
        print("Нет разрешения на запись в файл журнала")

def monitor_processes(text_widget, log_file):
    for proc in psutil.process_iter(['pid', 'name']):
        log_event("Запущен процесс", f"{proc.name()} [PID: {proc.pid}]", log_file)
        text_widget.insert(tk.END, f"Запущен процесс: {proc.name()} [PID: {proc.pid}]\n")
        text_widget.see(tk.END)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, text_widget, log_file):
        self.text_widget = text_widget
        self.log_file = log_file

    def on_modified(self, event):
        if not event.is_directory:
            log_event("Файл изменен", event.src_path, self.log_file)
            self.text_widget.insert(tk.END, f"Файл изменен: {event.src_path}\n")
            self.text_widget.see(tk.END)  

def monitor_network(text_widget, log_file):
    host = socket.gethostname()
    log_event("Сетевая активность", f"Хост: {host}", log_file)
    text_widget.insert(tk.END, f"Сетевая активность: Хост: {host}\n")
    text_widget.see(tk.END)

def select_log_path(log_path_entry):
    selected_path = filedialog.askdirectory()
    if selected_path:
        log_path_entry.delete(0, tk.END)
        log_path_entry.insert(tk.END, selected_path)

def create_gui():
    root = tk.Tk()
    root.title("Монитор событий")
    root.geometry("600x400")

    frame = tk.Frame(root, bg="lightgrey", padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    log_path_label = tk.Label(frame, text="Путь к файлу журнала:", bg="lightgrey")
    log_path_label.grid(row=0, column=0, sticky="w")

    log_path_entry = tk.Entry(frame, width=40)
    log_path_entry.grid(row=0, column=1, padx=5)

    log_path_button = tk.Button(frame, text="Выбрать путь", command=lambda: select_log_path(log_path_entry))
    log_path_button.grid(row=0, column=2, padx=5)

    text_widget = tk.Text(frame, wrap="word", width=60, height=20)
    text_widget.grid(row=1, column=0, columnspan=3, padx=5, pady=10)

    def start_monitoring():
        log_file = os.path.join(log_path_entry.get(), "events_log.txt")
        if not os.path.exists(log_file):
            with open(log_file, "w") as f:
                f.write("Журнал событий\n")

        monitor_processes(text_widget, log_file)
        monitor_network(text_widget, log_file)
        observer = Observer()
        observer.schedule(FileChangeHandler(text_widget, log_file), path='.', recursive=True)
        observer.start()
        root.monitor_observer = observer

    def stop_monitoring():
        if hasattr(root, "monitor_observer") and root.monitor_observer:
            root.monitor_observer.stop()
            root.monitor_observer.join()

    start_button = tk.Button(root, text="Начать мониторинг", command=start_monitoring)
    start_button.pack(side="left", padx=5, pady=5)

    stop_button = tk.Button(root, text="Остановить мониторинг", command=stop_monitoring)
    stop_button.pack(side="left", padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()

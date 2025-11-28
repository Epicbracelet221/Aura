import tkinter as tk
from tkinter import Label, Button, Frame, Scale, HORIZONTAL, StringVar, OptionMenu, Text, Scrollbar, Entry
from tkinter.ttk import Notebook
from PIL import Image, ImageTk
import threading
import time
import queue
import os
from datetime import datetime

from modules.comms import CommunicationManager
from modules.vision import VisionSystem
from modules.visualizer import SensorVisualizer
from modules.utils import KNOWN_WIDTHS, DEFAULT_FOCAL_LENGTH

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spider Bot | Advanced Vision & Control Command Center")
        self.root.geometry("1400x900")
        self.root.configure(bg="#101010")

        self.comms = CommunicationManager(log_callback=self.log_message)
        self.vision = VisionSystem()
        
        self.camera_mode = "BOTH" # RGB, THERMAL, BOTH
        self.running = False
        self.current_rgb = None
        self.current_thermal = None

        self.setup_ui()
        
        self.update_gui()

    def setup_ui(self): 
        sidebar = Frame(self.root, bg="#1a1a1a", width=320)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Header
        Label(sidebar, text="SPIDER BOT", font=("Segoe UI", 24, "bold"), fg="#00e676", bg="#1a1a1a").pack(pady=(20, 5))
        Label(sidebar, text="Command Center", font=("Segoe UI", 12), fg="#888", bg="#1a1a1a").pack()

        # Divider
        Frame(sidebar, bg="#333", height=1).pack(fill=tk.X, padx=20, pady=20)

        # System Controls
        ctrl_frame = Frame(sidebar, bg="#1a1a1a")
        ctrl_frame.pack(fill=tk.X, padx=20)
        
        self.btn_start = self.create_button(ctrl_frame, "▶ START SYSTEM", "#2e7d32", self.start_system)
        self.btn_start.pack(fill=tk.X, pady=5)
        
        self.btn_stop = self.create_button(ctrl_frame, "⏹ STOP SYSTEM", "#c62828", self.stop_system)
        self.btn_stop.pack(fill=tk.X, pady=5)

        # Camera Toggles
        Label(sidebar, text="CAMERA FEED", font=("Segoe UI", 10, "bold"), fg="#ccc", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=20, pady=(20, 5))
        
        cam_frame = Frame(sidebar, bg="#1a1a1a")
        cam_frame.pack(fill=tk.X, padx=20)
        
        self.create_button(cam_frame, "RGB Only", "#333", lambda: self.set_cam_mode("RGB")).pack(fill=tk.X, pady=2)
        self.create_button(cam_frame, "Thermal Only", "#333", lambda: self.set_cam_mode("THERMAL")).pack(fill=tk.X, pady=2)
        self.create_button(cam_frame, "Dual View", "#333", lambda: self.set_cam_mode("BOTH")).pack(fill=tk.X, pady=2)
        
        # Snapshot
        self.create_button(cam_frame, "📷 TAKE SNAPSHOT", "#f57f17", self.take_snapshot).pack(fill=tk.X, pady=(10, 2))

        # Bluetooth
        Label(sidebar, text="COMMUNICATION", font=("Segoe UI", 10, "bold"), fg="#ccc", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=20, pady=(20, 5))
        Label(sidebar, text="Select Port (USB / Bluetooth)", font=("Segoe UI", 8), fg="#666", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=20, pady=(0, 5))
        
        bt_frame = Frame(sidebar, bg="#1a1a1a")
        bt_frame.pack(fill=tk.X, padx=20)
        
        self.port_var = StringVar()
        self.port_menu = OptionMenu(bt_frame, self.port_var, "")
        self.port_menu.config(bg="#333", fg="white", bd=0, highlightthickness=0)
        self.port_menu.pack(fill=tk.X, pady=5)
        
        self.create_button(bt_frame, "↻ Refresh Ports", "#444", self.refresh_ports).pack(fill=tk.X, pady=2)
        self.btn_connect = self.create_button(bt_frame, "Connect", "#0277bd", self.toggle_connection)
        self.btn_connect.pack(fill=tk.X, pady=5)
        
        self.lbl_status = Label(bt_frame, text="Disconnected", font=("Segoe UI", 9), fg="#777", bg="#1a1a1a")
        self.lbl_status.pack(fill=tk.X)

        # Baud Rate
        Label(sidebar, text="BAUD RATE", font=("Segoe UI", 10, "bold"), fg="#ccc", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=20, pady=(10, 5))
        self.baud_var = StringVar(value="9600")
        baud_menu = OptionMenu(sidebar, self.baud_var, "9600", "38400", "115200")
        baud_menu.config(bg="#333", fg="white", bd=0, highlightthickness=0)
        baud_menu.pack(fill=tk.X, padx=20)

        # Robot Control
        Label(sidebar, text="MANUAL CONTROL", font=("Segoe UI", 10, "bold"), fg="#ccc", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=20, pady=(20, 10))
        
        grid_frame = Frame(sidebar, bg="#1a1a1a")
        grid_frame.pack(padx=20)
        
        self.create_button(grid_frame, "▲", "#333", lambda: self.comms.send_command('forward\r\n')).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        self.create_button(grid_frame, "◀", "#333", lambda: self.comms.send_command('left\r\n')).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        self.create_button(grid_frame, "⏹", "#d32f2f", lambda: self.comms.send_command('stop\r\n')).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        self.create_button(grid_frame, "▶", "#333", lambda: self.comms.send_command('right\r\n')).grid(row=1, column=2, padx=2, pady=2, sticky="ew")
        self.create_button(grid_frame, "▼", "#333", lambda: self.comms.send_command('back\r\n')).grid(row=2, column=1, padx=2, pady=2, sticky="ew")

        # Exit Button (Moved to end to prevent clipping)
        exit_frame = Frame(sidebar, bg="#1a1a1a")
        exit_frame.pack(fill=tk.X, padx=20, pady=20)
        self.create_button(exit_frame, "EXIT APPLICATION", "#b71c1c", self.on_closing).pack(fill=tk.X)

        # 2. Main Content (Right)
        main_content = Frame(self.root, bg="#101010")
        main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Top: Camera Feeds
        self.cam_container = Frame(main_content, bg="#000")
        self.cam_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.rgb_label = Label(self.cam_container, text="RGB FEED OFF", bg="black", fg="#333", font=("Segoe UI", 20))
        self.thermal_label = Label(self.cam_container, text="THERMAL FEED OFF", bg="black", fg="#333", font=("Segoe UI", 12))

        # Bottom: Notebook for Visualizer & Terminal
        bottom_panel = Frame(main_content, bg="#1a1a1a", height=300)
        bottom_panel.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        bottom_panel.pack_propagate(False)

        self.notebook = Notebook(bottom_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Visualizer
        vis_tab = Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(vis_tab, text="Sensors")
        self.visualizer = SensorVisualizer(vis_tab)

        # Tab 2: Terminal
        term_tab = Frame(self.notebook, bg="#101010")
        self.notebook.add(term_tab, text="Terminal")
        
        self.term_text = Text(term_tab, bg="#000", fg="#0f0", font=("Consolas", 10), state="disabled")
        self.term_scroll = Scrollbar(term_tab, command=self.term_text.yview)
        self.term_text.configure(yscrollcommand=self.term_scroll.set)
        
        self.term_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.term_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Command Entry
        cmd_frame = Frame(term_tab, bg="#222")
        cmd_frame.pack(side=tk.BOTTOM, fill=tk.X)
        Label(cmd_frame, text="CMD >", fg="#fff", bg="#222").pack(side=tk.LEFT, padx=5)
        self.cmd_entry = Entry(cmd_frame, bg="#333", fg="#fff", insertbackground="white")
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.cmd_entry.bind("<Return>", self.send_custom_command)
        Button(cmd_frame, text="SEND", bg="#444", fg="#fff", command=self.send_custom_command).pack(side=tk.RIGHT, padx=5)

        # Initial Layout
        self.set_cam_mode("BOTH")
        self.refresh_ports()

    def create_button(self, parent, text, color, cmd):
        return Button(parent, text=text, font=("Segoe UI", 10, "bold"), 
                      bg=color, fg="white", bd=0, activebackground=color,
                      command=cmd, cursor="hand2")

    def set_cam_mode(self, mode):
        self.camera_mode = mode
        # Clear current pack
        self.rgb_label.pack_forget()
        self.thermal_label.pack_forget()
        
        if mode == "RGB":
            self.rgb_label.pack(fill=tk.BOTH, expand=True)
        elif mode == "THERMAL":
            self.thermal_label.pack(fill=tk.BOTH, expand=True)
        else: # BOTH
            self.rgb_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            self.thermal_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

    def refresh_ports(self):
        ports = self.comms.get_available_ports()
        menu = self.port_menu["menu"]
        menu.delete(0, "end")
        for p in ports:
            menu.add_command(label=p, command=lambda value=p: self.port_var.set(value))
        if ports:
            self.port_var.set(ports[0])
        else:
            self.port_var.set("No Ports")

    def toggle_connection(self):
        if not self.comms.is_connected:
            port = self.port_var.get()
            if not port or port == "No Ports": return
            
            success, msg = self.comms.connect(port, baudrate=int(self.baud_var.get()))
            if success:
                self.btn_connect.config(text="Disconnect", bg="#c62828")
                self.lbl_status.config(text=msg, fg="#4caf50")
            else:
                self.lbl_status.config(text=msg, fg="red")
        else:
            self.comms.disconnect()
            self.btn_connect.config(text="Connect", bg="#0277bd")
            self.lbl_status.config(text="Disconnected", fg="#777")

    def start_system(self):
        if not self.running:
            self.running = True
            self.vision.start()

    def stop_system(self):
        self.running = False
        self.vision.stop()
        self.rgb_label.config(image='')
        self.thermal_label.config(image='')

    def update_gui(self):
        if self.running:
            try:
                img = self.vision.frame_queue.get_nowait()
                self.current_rgb = img
                imgtk = ImageTk.PhotoImage(image=img)
                self.rgb_label.imgtk = imgtk
                self.rgb_label.configure(image=imgtk)
            except queue.Empty:
                pass

            try:
                img_t = self.vision.thermal_queue.get_nowait()
                self.current_thermal = img_t
                imgtk_t = ImageTk.PhotoImage(image=img_t)
                self.thermal_label.imgtk = imgtk_t
                self.thermal_label.configure(image=imgtk_t)
            except queue.Empty:
                pass

            dist = self.comms.get_distance()
            self.visualizer.update(dist)

        self.root.after(30, self.update_gui)

    def take_snapshot(self):
        if not os.path.exists("snapshots"):
            os.makedirs("snapshots")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dist = self.comms.get_distance()
        
        if self.current_rgb:
            rgb_path = f"snapshots/snap_{timestamp}_rgb.jpg"
            self.current_rgb.save(rgb_path)
            self.log_message(f"Saved: {rgb_path}")
            
        if self.current_thermal:
            thermal_path = f"snapshots/snap_{timestamp}_thermal.jpg"
            self.current_thermal.save(thermal_path)
            self.log_message(f"Saved: {thermal_path}")
            
        data_path = f"snapshots/snap_{timestamp}_data.txt"
        with open(data_path, "w") as f:
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Distance: {dist} cm\n")
        self.log_message(f"Snapshot Data Saved")

    def log_message(self, msg):
        def _log():
            self.term_text.config(state="normal")
            self.term_text.insert(tk.END, f"{msg}\n")
            self.term_text.see(tk.END)
            self.term_text.config(state="disabled")
        self.root.after(0, _log)

    def send_custom_command(self, event=None):
        cmd = self.cmd_entry.get()
        if cmd:
            self.comms.send_command(cmd + "\r\n")
            self.cmd_entry.delete(0, tk.END)

    def on_closing(self):
        self.stop_system()
        self.comms.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

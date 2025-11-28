import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import collections

class SensorVisualizer:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        
        self.max_points = 50
        self.data_history = collections.deque([0]*self.max_points, maxlen=self.max_points)
        
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor='#101010')
        
        self.ax_graph = self.fig.add_subplot(211)
        self.ax_graph.set_facecolor('#1a1a1a')
        self.line, = self.ax_graph.plot([], [], color='#00e676', linewidth=2)
        self.ax_graph.set_title("Ultrasonic Distance (cm)", color='white', fontsize=10)
        self.ax_graph.tick_params(axis='x', colors='white')
        self.ax_graph.tick_params(axis='y', colors='white')
        self.ax_graph.set_ylim(0, 400)
        self.ax_graph.grid(True, color='#333')

        self.ax_radar = self.fig.add_subplot(212, projection='polar')
        self.ax_radar.set_facecolor('#1a1a1a')
        self.ax_radar.set_title("Surroundings Radar", color='white', fontsize=10, pad=10)
        self.ax_radar.tick_params(axis='x', colors='white')
        self.ax_radar.tick_params(axis='y', colors='white')
        self.ax_radar.set_theta_zero_location('N')
        self.ax_radar.set_theta_direction(-1)
        self.ax_radar.set_rlim(0, 400)
        self.ax_radar.grid(True, color='#333')
        
    
        self.radar_point, = self.ax_radar.plot([], [], 'ro', markersize=8)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

    def update(self, distance):
        
        self.data_history.append(distance)
        
        self.line.set_data(range(len(self.data_history)), self.data_history)
        self.ax_graph.set_xlim(0, len(self.data_history))
        
        if distance > 0:
            self.radar_point.set_data([0], [distance])
        else:
            self.radar_point.set_data([], [])

        self.canvas.draw()

# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:22:16 2020

@author: Naomi Hiebert
"""

import sys
import threading, time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPoint, QLine

from mpl_widget import MplWidget
from sir_model import SIRModel


class SIRViewer(MplWidget):
    """The frontend viewer for the simulation
    """   
    def __init__(self, parent):
        super().__init__(parent)
        self._plot_ref = None

        self.n_iter = 0
        self.model_time = 0
        self.plot_time = 0
        self.gui_time = 0
        self.start_time = time.perf_counter()
        
    def model_update(self):
        """Updates the QPoint lists with new values of locations of Nodes
        """
        if self._plot_ref is None:
            ref_s = self.plot(
                *self.prepare(self.model.list_susceptible()), 
                fmt='o', ms=4, c=[0.7, 0.7, 0], mec="black")
            ref_i = self.plot(
                *self.prepare(self.model.list_infected()), 
                fmt='o', ms=4, c=[1, 0, 0], mec="black")
            ref_r = self.plot(
                *self.prepare(self.model.list_recovered()), 
                fmt='o', ms=4, c=[0, 1, 0], mec="black")
            self._plot_ref = [ref_s[0], ref_i[0], ref_r[0]]
        else:
            for idx, method in enumerate([
                self.model.list_susceptible,
                self.model.list_infected,
                self.model.list_recovered]):
                self._plot_ref[idx].set_data(*self.prepare(method()))

        self.canvas.draw()
        self.canvas.flush_events()

    def prepare(self, data):
        if data.shape == (0,):
            return data.reshape(2, -1)
        return data.T[::-1]

    def attach_model(self, m):
        """Links the Viewer to the Model and begins the update

        Parameters
        ----------
        m : SIRModel
            The SIRModel to be linked to
        """
        self.model = m
        self.canvas.ax.imshow(m.sir_map.img)
        self.model_update()
        
    def force_update(self):
        """Steps and updates the model and viewer
        """
        if self.model:
            self.n_iter += 1
            start = time.perf_counter()
            self.model.model_step()
            self.model_time += time.perf_counter() - start
            start = time.perf_counter()
            self.model_update()
            self.plot_time += time.perf_counter() - start
            start = time.perf_counter()
            self.update()
            self.gui_time += time.perf_counter() - start

    def end(self):
        sys.exit()

    def run_sim(self, stop):
        print(type(stop))
        """Runs the simulation while the stop event is not set

        Parameters
        ----------
        stop : threading.Event
            The Event that stops the thread
        """
        while not stop.isSet():
            time.sleep(0.1)
            self.force_update()

    def thread_start(self):
        """Starts the thread for simulation
        """
        self.stop = threading.Event()
        self.c_thread = threading.Thread(target=self.run_sim, args=(self.stop,))
        self.c_thread.start() 

    def thread_cancel(self):
        """Kills the thread and ends the program
        """
        print('='*50)
        print('Simulation Statistics')
        print('-'*50)
        print(f'Final susceptible: {len(self.model.list_susceptible())}')
        print(f'Final infected: {len(self.model.list_infected())}')
        print(f'Final recovered: {len(self.model.list_recovered())}')

        print('='*50)
        print('Performance Statistics')
        print('-'*50)
        print(f'Total iterations: {self.n_iter}')
        print(f'Total run time: {time.perf_counter()-self.start_time}')
        print(f'Total model step time: {self.model_time}')
        print(f'Total plotting time: {self.plot_time}')
        print(f'Total gui update time: {self.gui_time}')

        print('-'*50)
        print(f'Avg iter time: {(time.perf_counter()-self.start_time)/self.n_iter}')
        print(f'Avg model step time: {self.model_time/self.n_iter}')
        print(f'Avg plotting time: {self.plot_time/self.n_iter}')
        print(f'Avg gui update time: {self.gui_time/self.n_iter}')
        print('='*50)

        self.stop.set()
        self.close()
        sys.exit() 


if __name__ == '__main__':
    
    app = QApplication (sys.argv)
    window = QWidget()
    window.setGeometry(50, 50, 800, 700)
    viewer = SIRViewer(parent = window)
    viewer.setGeometry(0, 0, 800, 600)

    begin_button = QPushButton('Begin', parent = window)
    begin_button.move(200, 600)

    stop_button = QPushButton('Stop', parent = window)
    stop_button.move(500, 600)
    
    model = SIRModel(
        population=200, 
        recovery_rate=0.01,
        mapfile='mapfiles/scenario_medium.png')
    viewer.attach_model(model)
    
    begin_button.clicked.connect(viewer.thread_start)
    stop_button.clicked.connect(viewer.thread_cancel)

    window.show()
    sys.exit(app.exec())

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

from sir_model import SIRModel


class SIRViewer(QWidget):
    """The frontend viewer for the simulation

       Attributes
        ----------
        points_s : list of QPoints
            The list of susceptible node coordinates in QPoints
        points_i : list of QPoints
            The list of infected node coordinates in QPoints
        points_r : list of QPoints
            The list of recovered node coordinates in QPoints
        points_walls : list of QPoints
            The list of tuples of wall end coordinates in QPoints
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.points_s = [QPoint(10, 10), QPoint(10, 20)]
        self.points_i = [QPoint(20, 10), QPoint(20, 20)]
        self.points_r = [QPoint(30, 10), QPoint(30, 20)]
        self.points_walls = []
        
    def model_update(self):
        """Updates the QPoint lists with new values of locations of Nodes
        """
        self.points_s = []
        self.points_i = []
        self.points_r = []
        self.points_walls = []
        
        for p in self.model.list_susceptible():
            self.points_s.append(self.make_point(p[0], p[1]))
        for p in self.model.list_infected():
            self.points_i.append(self.make_point(p[0], p[1]))
        for p in self.model.list_recovered():
            self.points_r.append(self.make_point(p[0], p[1]))
        for p in self.model.sir_map.wall_locs:
            self.points_walls.append((self.make_point(p[0], p[1]), self.make_point(p[2], p[3])))
            
    def make_point(self, x, y):
        """Creates a QPoint from x,y coordinates

        Parameters
        ----------
        x : integer
            The X coordinate
        y : integer
            The Y coordinate

        Returns
        -------
        QPoint
            The QPoint of the coordinates
        """
        new_x = ((x / self.model.get_model_size()[0]) \
                * (super().size().width()-20))
        new_y = ((y / self.model.get_model_size()[1]) \
                * (super().size().height()-20))
        new_x = int(new_x + 10)
        new_y = int(new_y + 10)
        return QPoint(new_x, new_y)
    
    def attach_model(self, m):
        """Links the Viewer to the Model and begins the update

        Parameters
        ----------
        m : SIRModel
            The SIRModel to be linked to
        """
        self.model = m
        self.model_update()
        
    def paintEvent(self, paintEvent):
        """Draws all of the Nodes in their respective colours on the Map

        Parameters
        ----------
        paintEvent : [type]
            [description]
        """
        p = QPainter(self)
        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setWidth(5)
        
        pen.setColor(QColor(182, 182, 0))
        p.setPen(pen)
        if self.points_s:
            p.drawPoints(*self.points_s)
        
        pen.setColor(QColor(255, 0, 0))
        p.setPen(pen)
        if self.points_i:
            p.drawPoints(*self.points_i)
        
        pen.setColor(QColor(0, 255, 0))
        p.setPen(pen)
        if self.points_r:
            p.drawPoints(*self.points_r)

        pen.setColor(QColor(0, 0, 0))
        p.setPen(pen)
        if self.points_walls:
            for pt in self.points_walls:
                p.drawLine(*pt)
        
        
    def force_update(self):
        """Steps and updates the model and viewer
        """
        if self.model:
            self.model.model_step()
            self.model_update()
            self.update()

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
            time.sleep(0.001)
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
    
    model = SIRModel()
    viewer.attach_model(model)
    
    begin_button.clicked.connect(viewer.thread_start)
    stop_button.clicked.connect(viewer.thread_cancel)

    window.show()
    sys.exit(app.exec())

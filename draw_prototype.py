# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:22:16 2020

@author: Naomi Hiebert
"""

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPoint

from sir_model import SIRModel


class SIRViewer(QWidget):

    
    def __init__(self, parent):
        super().__init__(parent)
        self.points_s = [QPoint(10, 10), QPoint(10, 20)]
        self.points_i = [QPoint(20, 10), QPoint(20, 20)]
        self.points_r = [QPoint(30, 10), QPoint(30, 20)]
        
    def model_update(self):
        
        self.points_s = []
        self.points_i = []
        self.points_r = []
        
        for p in self.model.list_susceptible():
            self.points_s.append(self.make_point(p[0], p[1]))
        for p in self.model.list_infected():
            self.points_i.append(self.make_point(p[0], p[1]))
        for p in self.model.list_recovered():
            self.points_r.append(self.make_point(p[0], p[1]))
            
    def make_point(self, x, y):
        new_x = ((x / self.model.get_model_size()[0]) \
                * (super().size().width()-20))
        new_y = ((y / self.model.get_model_size()[1]) \
                * (super().size().height()-20))
        new_x = int(new_x + 10)
        new_y = int(new_y + 10)
        return QPoint(new_x, new_y)
    
    def attach_model(self, m):
        self.model = m
        self.model_update()
        
    def paintEvent(self, paintEvent):
        
        p = QPainter(self)
        pen = QPen()
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
        
        
    def force_update(self):
        if self.model:
            self.model.model_step()
            self.model_update()
            self.update()




if __name__ == '__main__':
    
    app = QApplication (sys.argv)
    window = QWidget()
    window.setGeometry(50, 50, 800, 700)
    viewer = SIRViewer(parent = window)
    viewer.setGeometry(0, 0, 800, 600)
    button = QPushButton('Update', parent = window)
    button.move(400, 600)
    
    model = SIRModel()
    viewer.attach_model(model)
    
    button.clicked.connect(viewer.force_update)
    
    window.show()
    sys.exit(app.exec())

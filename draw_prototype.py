# -*- coding: utf-8 -*-
"""
Created on Tue May  5 13:22:16 2020

@author: Naomi Hiebert
"""

import sys, random
from enum import Enum

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPoint

class SIRStatus(Enum):
    SUSCEPTIBLE = 1
    INFECTED = 2
    RECOVERED = 3
    

class SIRViewer(QWidget):

    
    def __init__(self, parent):
        super().__init__(parent)
        self.points_s = [QPoint(10, 10), QPoint(20, 20)]
        self.points_i = [QPoint(20, 10), QPoint(30, 20)]
        self.points_r = [QPoint(30, 10), QPoint(40, 20)]
        
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

        
class SIRNode:
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.status = SIRStatus.SUSCEPTIBLE
        
    def convalesce(self, recovery_rate):
        if self.status is SIRStatus.INFECTED:
            if random.random() < recovery_rate:
                self.status = SIRStatus.RECOVERED
                
    def infect(self):
        self.status = SIRStatus.INFECTED
        
    def is_contagious(self):
        return (self.status is SIRStatus.INFECTED)
    
    def is_susceptible(self):
        return (self.status is SIRStatus.SUSCEPTIBLE)
    
    def expose(self, other, attack_rate):
        if self.is_susceptible() and other.is_contagious():
            if random.random() < attack_rate:
                self.infect()        
                
    def move(self):
        #This is a "random walk" in the technical sense
        rand = random.random()
        if rand < 0.25:
            self.x += 1
        elif rand < 0.5:
            self.x -= 1
        elif rand < 0.75:
            self.y += 1
        else:
            self.y -= 1


class SIRModel:
    
    def __init__(
            self, width=50, height=50, 
            population=400, carriers=8,
            attack_rate=0.8, recovery_rate=0.02):
        
        self.width = width
        self.height = height
        self.attack_rate = attack_rate
        self.recovery_rate = recovery_rate
        self.population = []
        
        for i in range(population):
            self.population.append(SIRNode(random.randint(0, width-1),
                                           random.randint(0, height-1)))
            
        #Node locations were random, so this doesn't have to be.
        for i in range(carriers):
            self.population[i].infect()
            
            
    def model_step(self):
        for p in self.population:
            p.convalesce(self.recovery_rate)
            p.move()
            #Force nodes to stay in the grid, wrapping around edges
            p.x %= self.width
            p.y %= self.height
            
        for p1 in self.population:
            for p2 in self.population:
                if p1.x == p2.x and p1.y == p2.y:
                    p1.expose(p2, self.attack_rate)

    def get_model_size(self):
        return (self.width, self.height)

    def list_susceptible(self):
        ret = []
        for p in self.population:
            if p.status is SIRStatus.SUSCEPTIBLE:
                ret.append((p.x, p.y))
        return ret
    
    def list_infected(self):
        ret = []
        for p in self.population:
            if p.status is SIRStatus.INFECTED:
                ret.append((p.x, p.y))
        return ret
    
    def list_recovered(self):
        ret = []
        for p in self.population:
            if p.status is SIRStatus.RECOVERED:
                ret.append((p.x, p.y))
        return ret



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

# -*- coding: utf-8 -*-
"""
Created on Thu May  7 13:01:19 2020

@author: Naomi Hiebert
"""

import random
from enum import Enum

import numpy as np


class SIRStatus(Enum):
    SUSCEPTIBLE = 1
    INFECTED = 2
    RECOVERED = 3
    

        
class SIRNode:
    
    def __init__(self, x=0, y=0, sir_map=None):
        self.x = x
        self.y = y
        self.status = SIRStatus.SUSCEPTIBLE
        if sir_map is not None:
            self.sir_map = sir_map
        
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
    
    def can_enter(self, x, y):
        if self.sir_map is not None:
            return self.sir_map.can_enter(x,y)
    
    def expose(self, other, attack_rate):
        if self.is_susceptible() and other.is_contagious():
            if random.random() < attack_rate:
                self.infect()
                
    def droplet_expose(self):
        if self.sir_map is not None and self.is_susceptible():
            virus_level = self.sir_map.virus_level(self.x, self.y)
            if random.randint(0, 255) < virus_level:
                self.infect()
                
    def droplet_spread(self):
        if self.sir_map is not None and self.is_contagious():
            self.sir_map.contaminate(self.x, self.y)
                
    def random_place(self, x_max, y_max):
        while(True):
            x = random.randint(0, x_max-1)
            y = random.randint(0, y_max-1)
            if self.can_enter(x, y):
                self.x = x
                self.y = y
                return
                
    def random_move(self):
        rand = random.random()
        if rand < 0.2 and self.can_enter(self.x+1, self.y):
            self.x += 1
        elif rand < 0.4 and self.can_enter(self.x-1, self.y):
            self.x -= 1
        elif rand < 0.6 and self.can_enter(self.x, self.y+1):
            self.y += 1
        elif rand < 0.8 and self.can_enter(self.x, self.y-1):
            self.y -= 1
        else:
            pass

class SIRMap:
    
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        self.layout = np.ones((width, height), np.uint8)
        self.miasma = np.zeros((width, height), np.uint8)
        
    def build_box(self):
        #For testing purposes - forbid the top-left corner
        for i in range(20):
            for j in range(20):
                self.layout[i,j] = np.uint8(0)
            
    def can_enter(self, x, y, role=0b00000001):
        #This function also enforces the edges of the map
        if x >= self.width or y >= self.height:
            return False
        elif x < 0 or y < 0:
            return False
        else:
            return (self.layout[x,y] & np.uint8(role))
        
    def virus_level(self, x, y):
        return self.miasma[x,y]
        
    def contaminate(self, x, y, concentration=0b01111111):
        self.miasma[x,y] |= np.uint8(concentration)
    
    def ventilate(self):
        for i in range(self.width):
            for j in range(self.height):
                self.miasma[i,j] >>= 2
    


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
        self.sir_map = SIRMap(width, height)
        
        #for testing
        self.sir_map.build_box()
        
        for i in range(population):
            self.population.append(SIRNode(0, 0, self.sir_map))
            
        for p in self.population:
            p.random_place(self.width, self.height)
            
        #Node locations were random, so this doesn't have to be.
        for i in range(carriers):
            self.population[i].infect()
            
            
    def model_step(self):
        for p in self.population:
            p.droplet_spread()
            p.convalesce(self.recovery_rate)
            
        for p in self.population:
            p.random_move()
            p.droplet_expose()
            
        self.sir_map.ventilate()
         
        '''
        for p1 in self.population:
            for p2 in self.population:
                if p1.x == p2.x and p1.y == p2.y:
                    p1.expose(p2, self.attack_rate)
                    '''

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

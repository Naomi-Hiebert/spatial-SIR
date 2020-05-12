# -*- coding: utf-8 -*-
"""
Created on Thu May  7 13:01:19 2020

@author: Naomi Hiebert
"""

import random
from enum import Enum

import numpy as np


class SIRStatus(Enum):
    """ An enum that represents the infection status of the SIRNodes
    """
    SUSCEPTIBLE = 1
    INFECTED = 2
    RECOVERED = 3

# # This is not used currently
class MapType(Enum):
    """ An enum that represents an area type on the SIRMap
    """
    OPEN = 1
    WALL = 2
    RESTRICTED = 3 

class Location:
    """A location on the map with coordinates

       Attributes
        ----------
        x : float
            The X coordinate.
        y : float
            The Y coordinate.
        type : MapType
            The area type
    """
    def __init__(self, x, y, type = MapType.OPEN):
        self.x = x
        self.y = y
        self.type = type

        
class SIRNode:
    """An individual on the Map whose status is tracked

       Attributes
        ----------
        x : integer
            The X coordinate.
        y : integer
            The Y coordinate.
        status : SIRStatus
            The infection state of the person
        """
    def __init__(self, x=0, y=0, sir_map=None):
        self.x = x
        self.y = y
        self.status = SIRStatus.SUSCEPTIBLE
        if sir_map is not None:
            self.sir_map = sir_map
        
    def convalesce(self, recovery_rate):
        """Simulates the possibility of a Node recovering from infection

        Parameters
        ----------
        recovery_rate : float
            The chance that an individual will recover (e.g. 0.02)
        """
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
        """Checks whether a coordinate is within bounds of the screen

        Parameters
        ----------
        x : integer
            The X coordinate.
        y : integer
            The Y coordinate.

        Returns
        -------
        boolean
            Whether the coordinate is valid
        """
        if self.sir_map is not None:
            return self.sir_map.can_enter(x,y)
    
    def expose(self, other, attack_rate):
        """Simulates whether another Node will infect this node

        Parameters
        ----------
        other : SIRNode
            The infected node
        attack_rate : float
            The aggressiveness of the disease
        """
        if self.is_susceptible() and other.is_contagious():
            if random.random() < attack_rate:
                self.infect()
                
    def droplet_expose(self):
        """Simulates infection due to residue disease in the air
        """
        if self.sir_map is not None and self.is_susceptible():
            virus_level = self.sir_map.virus_level(self.x, self.y)
            if random.randint(0, 255) < virus_level:
                self.infect()
                
    def droplet_spread(self):
        """Causes the area currently occupied by the individual to be at risk of disease
        """
        if self.sir_map is not None and self.is_contagious():
            self.sir_map.contaminate(self.x, self.y)
            
    def random_place(self, x_max, y_max):
        """Creates a random coordinate to place the Node at

        Parameters
        ----------
        x_max : integer
            The maximum X position
        y_max : integer
            The maximum Y position
        """
        while(True):
            x = random.randint(0, x_max-1)
            y = random.randint(0, y_max-1)
            if self.can_enter(x, y):
                self.x = x
                self.y = y
                return
                
    def random_move(self):
        """Simulates the movement of the Node
        """
        # TODO create fluid motion for SIRNodes
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
    """The map of the area being monitored

       Attributes
        ----------
        width : integer
            The width of the map
        height : integer
            The height of the map
        layout : ndarray
            A matrix specifying whether a position is filled
        miasma : ndarray
            A matrix specifying whether a position is infectious
        wall_locs : list of tuples
            The locations of the walls
    """
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        self.layout = np.ones((width, height), np.uint8)
        self.miasma = np.zeros((width, height), np.uint8)
        self.wall_locs = []
        
    # def build_box(self, loc1, loc2):
    #     #For testing purposes - forbid box from Location 1 to Location 2
    #     for i in range(loc1.x, loc2.x):
    #         for j in range(loc1.y, loc2.y):
    #             self.layout[i,j] = np.uint8(0)
    
    def h_wall(self, loc, x):
        #For testing purposes 
        self.wall_locs.append((loc.x, loc.y, x, loc.y))
        for i in range(loc.x, x):
                self.layout[i, loc.y] = np.uint8(0)
                

    def v_wall(self, loc, y):
        #For testing purposes 
        self.wall_locs.append((loc.x, loc.y, loc.x, y))
        for i in range(loc.y, y):
                self.layout[loc.x, i] = np.uint8(0)
            
    def can_enter(self, x, y, role=0b00000001):
        """Determines whether a position is valid within the map

        Parameters
        ----------
        x : integer
            The X coordinate.
        y : integer
            The Y coordinate.
        role : [type], optional
            [description], by default 0b00000001

        Returns
        -------
        boolean
            Whether the position is valid
        """
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
        """Simulates the ventilation of the map?
        """
        for i in range(self.width):
            for j in range(self.height):
                self.miasma[i,j] >>= 2
    


class SIRModel:
    """The map of the area being monitored

       Attributes
        ----------
        width : integer
            The width of the map
        height : integer
            The height of the map
        attack_rate : float
            The aggressiveness of the disease
        recovery_rate : float
            The possibility of recovery from disease
        population : list of SIRNodes
            The individuals within the Map
        sir_map : SIRMap
            The SIRMap connected
    """
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

        # Creates the walls
        # lower right box
        self.sir_map.h_wall(Location(0, 20), 10)
        self.sir_map.h_wall(Location(15, 20), 20)
        self.sir_map.v_wall(Location(20, 0), 20)

        # lower right box
        self.sir_map.h_wall(Location(30, 30), 35)
        self.sir_map.h_wall(Location(40, 30), 50)
        self.sir_map.v_wall(Location(30, 30), 50)



        for i in range(population):
            self.population.append(SIRNode(0, 0, self.sir_map))
            
        for p in self.population:
            p.random_place(self.width, self.height)
            
        #Node locations were random, so this doesn't have to be.
        for i in range(carriers):
            self.population[i].infect()
            
            
    def model_step(self):
        """Steps the simulation forward one iteration
        """
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
        """Creates a list of all coordinates of susceptible Nodes

        Returns
        -------
        list of tuples
            The list of susceptible node coordinates
        """
        ret = []
        for p in self.population:
            if p.status is SIRStatus.SUSCEPTIBLE:
                ret.append((p.x, p.y))
        return ret
    
    def list_infected(self):
        """Creates a list of all coordinates of infected Nodes

        Returns
        -------
        list of tuples
            The list of infected node coordinates
        """
        ret = []
        for p in self.population:
            if p.status is SIRStatus.INFECTED:
                ret.append((p.x, p.y))
        return ret
    
    def list_recovered(self):
        """Creates a list of all coordinates of recovered Nodes

        Returns
        -------
        list of tuples
            The list of recovered node coordinates
        """
        ret = []
        for p in self.population:
            if p.status is SIRStatus.RECOVERED:
                ret.append((p.x, p.y))
        return ret
    
    

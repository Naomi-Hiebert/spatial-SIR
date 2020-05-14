# -*- coding: utf-8 -*-
"""
Created on Thu May  7 13:01:19 2020

@author: Naomi Hiebert
"""

import random
from enum import Enum

import numpy as np
import networkx as nx
from matplotlib import image

from pathing import Terrain, create_graph, random_idx, dist


class SIRStatus(Enum):
    """ An enum that represents the infection status of the SIRNodes
    """
    SUSCEPTIBLE = 1
    INFECTED = 2
    RECOVERED = 3
    QUARANTINED = 4


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
        type_ : MapType
            The area type
    """
    def __init__(self, x, y, type_ = MapType.OPEN):
        self.x = x
        self.y = y
        self.type = type_

        
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

        self.urgency = 1
        self.path = []
        
    def convalesce(self, recovery_rate):
        """Simulates the possibility of a Node recovering from infection

        Parameters
        ----------
        recovery_rate : float
            The chance that an individual will recover (e.g. 0.02)
        """
        if self.is_contagious() or self.is_quarantined():
            if random.random() < recovery_rate:
                self.status = SIRStatus.RECOVERED
                self.pathfind(random_idx(self.sir_map.open))
                
    def infect(self):
        self.status = SIRStatus.INFECTED
        
    def is_contagious(self):
        return (self.status is SIRStatus.INFECTED)
            
    def is_quarantined(self):
        return (self.status is SIRStatus.QUARANTINED)
    
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
            
    def random_place(self):
        """Creates a random coordinate to place the Node at

        Parameters
        ----------
        x_max : integer
            The maximum X position
        y_max : integer
            The maximum Y position
        """
        self.x, self.y = random_idx(self.sir_map.start)

    def move(self):
        """Movement decision making for the Node
        """
        if self.is_quarantined():
            if len(self.path) > 0:
                self.x, self.y = self.path.pop(0)

        elif random.random() <= self.urgency:
            if self.is_contagious() and random.random() < 0.05:
                self.pathfind(random_idx(self.sir_map.quarantine))
                self.status = SIRStatus.QUARANTINED
            elif len(self.path) > 0:
                self.x, self.y = self.path.pop(0)
            else:
                self.new_task()
        else:
            pass
                
    def random_move(self):
        """Simulates random movement of the Node
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
    
    def new_task(self):
        """Defines a new task / path for the Node
        """
        rand = random.random()
        if rand < 0.1:
            self.pathfind(random_idx(self.sir_map.target))
        elif rand < 0.2:
            self.pathfind(random_idx(self.sir_map.start))
        elif rand < 0.5:
            self.pathfind(random_idx(self.sir_map.valid))
        else:
            self.random_move()

    def pathfind(self, target):
        """
        Computes the shortest path between two points subject 
        to optimization constraints in the a-star search algorithm

        Parameters
        ----------
        target : (int, int)
            `(x,y)` coordinate tuple to path to from the current Node position
        """        
        start = (self.x, self.y)
        self.path = nx.astar_path(
            self.sir_map.graph, start, target, heuristic=dist, weight='cost')


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
    """
    def __init__(self, mapfile):
        self.load_map(mapfile)
        self.miasma = np.zeros(self.shape, np.uint8)

    def load_map(self, mapfile):
        """
        Load in mapfile and compute terrain masks.

        Parameters
        ----------
        mapfile : str
            File path to map image (uncompressed).
        """
        # read image
        self.img = image.imread(mapfile)
        self.shape = self.img.shape[:2]

        # remove alpha from RGBA
        if self.img.shape[-1] == 4:
            self.img = self.img[:,:,:3]

        # compute terrain masks
        self.open = self._is_pixel_type(Terrain.OPEN)
        self.walls = self._is_pixel_type(Terrain.WALL)
        self.start = self._is_pixel_type(Terrain.START)
        self.target = self._is_pixel_type(Terrain.TARGET)
        self.quarantine = self._is_pixel_type(Terrain.QUARANTINE)
        self.valid = ~(self.quarantine | self.walls)

        # compute network graph
        self.graph = create_graph(self.walls)
    
    def _is_pixel_type(self, rgb):
        pixel_mask = np.all(self.img == rgb, axis=2)
        return pixel_mask
            
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
        if any(np.array((x,y)) >= self.shape):
            return False
        elif any(np.array((x,y)) < 0):
            return False
        else:
            return (self.valid[x,y] & np.uint8(role))
        
    def virus_level(self, x, y):
        return self.miasma[x,y]
        
    def contaminate(self, x, y, concentration=0b01111111):
        self.miasma[x,y] |= np.uint8(concentration)
    
    def ventilate(self):
        """Simulates the ventilation of the map?
        """
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
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
        self, mapfile, 
        population=400, carriers=8,
        attack_rate=0.8, recovery_rate=0.02):
    
        self.sir_map = SIRMap(mapfile)

        self.attack_rate = attack_rate
        self.recovery_rate = recovery_rate
        self.population = []

        for i in range(population):
            self.population.append(SIRNode(0, 0, self.sir_map))
            
        for p in self.population:
            p.random_place()
            p.pathfind(random_idx(self.sir_map.target))
            p.urgency = np.random.uniform(0.4, 0.95)
            
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
            p.move()
            p.droplet_expose()
            
        self.sir_map.ventilate()
         
        '''
        for p1 in self.population:
            for p2 in self.population:
                if p1.x == p2.x and p1.y == p2.y:
                    p1.expose(p2, self.attack_rate)
                    '''

    def get_model_size(self):
        return self.sir_map.shape

    def list_susceptible(self):
        """Creates a list of all coordinates of susceptible Nodes

        Returns
        -------
        list of tuples
            The list of susceptible node coordinates
        """
        ret = []
        for p in self.population:
            if p.is_susceptible():
                ret.append((p.x, p.y))
        return np.array(ret)
    
    def list_infected(self):
        """Creates a list of all coordinates of infected Nodes

        Returns
        -------
        list of tuples
            The list of infected node coordinates
        """
        ret = []
        for p in self.population:
            if p.is_contagious() or p.is_quarantined():
                ret.append((p.x, p.y))
        return np.array(ret)
    
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
        return np.array(ret)

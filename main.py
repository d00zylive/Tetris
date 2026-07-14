from __future__ import annotations
from typing import Self
import pygame
import random

class Pos():
    x: float
    y: float

    def __init__(self, x: float, y: float):
        if (x*2).is_integer() and (y*2).is_integer():
            self.x = x
            self.y = y
        else:
            raise ValueError("Point not on the grid or half-grid")

    def __repr__(self):
        return f"Pos(x={self.x},y={self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __add__(self, other: Pos) -> Pos:
        return Pos(x=self.x+other.x, y=self.y+other.y)
    
    def __sub__(self, other: Pos) -> Pos:
        return Pos(x=self.x-other.x, y=self.y-other.y)
    
    def rotate(self, clockwise:bool = True, set:bool = True) -> Pos:
        if clockwise:
            x = self.y
            y = -self.x
        else:
            x = -self.y
            y = self.x
        
        if set:
            self.x = x
            self.y = y
            return self
        else:
            return Pos(x, y)
        
    def index(self) -> int:
        if self.x >= 0 and self.y >= 0 and self.x < WIDTH and self.y < HEIGHT and self.x.is_integer() and self.y.is_integer():
            return int(WIDTH*self.y+self.x)
        else:
            raise ValueError("Point not on integer grid")


class Block():
    pos: Pos
    relPos: Pos
    colour: int

    def __init__(self, pos: Pos, relPos: Pos, colour: int):
        self.pos = pos
        self.relPos = relPos
        self.colour = colour

    def __repr__(self):
        return f"Block(pos={self.pos},relPos={self.relPos},colour={self.colour})"

    def clear(self):
        grid[self.pos.index()].colour = Tile.EMPTY

    def set(self) -> Self:
        tile = grid[self.pos.index()]
        tile.colour = self.colour
        return self

    def rotate(self, clockwise:bool = True, set:bool = True) -> Block:
        pivot = self.pos-self.relPos
        relPos = self.relPos.rotate(clockwise=clockwise,set=set)
        if set:
            self.pos = pivot+relPos
            return self
        else:
            return Block(pos=pivot+relPos, relPos=Pos(relPos.x,relPos.y), colour=self.colour)
        
    def drop(self, set:bool = True) -> bool:
        if self.pos.x > 0 and self.pos.y > 0 and self.pos.x < WIDTH and self.pos.y < HEIGHT:
            checkIndex = (self.pos-Pos(0,1)).index()
            if grid[checkIndex].colour == 0:
                if set:
                    self.pos = self.pos-Pos(0,1)
                return True
            
        return False


class Shape():
    pos: Pos
    relPositions: list[Pos]
    colour: int
    blocks: list[Block]|None

    def __init__(self, pos: Pos, relPositions: list[Pos], colour: int, blocks:list[Block]|None = None):
        self.pos = pos
        self.relPositions = relPositions
        self.colour = colour
        self.blocks = blocks

    def __repr__(self):
        return f"Shape(pos={self.pos},relPositions={self.relPositions},colour={self.colour},blocks={self.blocks})"

    def instantiate(self, pos:Pos|None = None) -> Shape:
        pos = self.pos if pos is None else pos
        shape = Shape(pos=Pos(pos.x, pos.y), relPositions=[Pos(relPos.x, relPos.y) for relPos in self.relPositions], colour=self.colour, blocks=[Block(pos=pos+relPos, relPos=Pos(relPos.x,relPos.y), colour=self.colour) for relPos in self.relPositions])
        assert shape.blocks is not None
        for block in shape.blocks:
            block.set()
        return shape
    
    def is_instantiated(self) -> bool:
        return isinstance(self.blocks, list) and len(self.blocks) > 0 and all(isinstance(block, Block) for block in self.blocks)

    def rotate(self, clockwise: bool = True) -> bool:
        if self.is_instantiated():
            assert self.blocks is not None
            for block in self.blocks:
                block.clear()
            for block in self.blocks:
                pos = block.rotate(clockwise=clockwise, set=False).pos
                if pos.x < 0 or pos.y < 0 or pos.x >= WIDTH or pos.y >= HEIGHT or grid[pos.index()].colour != 0:
                    for block in self.blocks:
                        block.set()
                    return False
            for block in self.blocks:
                block.rotate(clockwise=clockwise)
            for block in self.blocks:
                block.set()
            return True
        else:
            raise TypeError("Shape uninstantiated")
        
    def drop(self) -> bool:
        if self.is_instantiated():
            assert self.blocks is not None
            for block in self.blocks:
                block.clear()

            if all(block.drop(set=False) for block in self.blocks):
                for block in self.blocks:
                    block.drop()
                for block in self.blocks:
                    block.set()
                self.pos = self.pos-Pos(0,1)
                return True
                    
            for block in self.blocks:
                block.set()
            return False
        else:
            raise TypeError("Shape uninstantiated")


class Tile():

    pos: Pos
    colour: int

    COLOURS: dict[int, pygame.Color] = {
        0: pygame.Color(0,0,0), # black/empty
        1: pygame.Color(255,0,0), # red
        2: pygame.Color(0,255,0), # green
        3: pygame.Color(0,0,255), # blue
        4: pygame.Color(255,255,0), # yellow
        5: pygame.Color(255,0,255), # purple
        6: pygame.Color(0,255,255), # cyan
        7: pygame.Color(255,128,0), # orange
    }
    EMPTY = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    PURPLE = 5
    CYAN = 6
    ORANGE = 7

    def __init__(self, pos: Pos, colour: int):
        self.pos = pos
        self.colour = colour

    def __repr__(self):
        return f"Tile(pos={self.pos},colour={self.colour})"

    def draw(self, screen: pygame.Surface, size: int, offset: tuple[int, int] = (0, 0), gap: int = 0):
        pygame.draw.rect(screen, self.COLOURS[self.colour], pygame.Rect(self.pos.x*(size+gap)+offset[0], ((HEIGHT-1)-self.pos.y)*(size+gap)+offset[1], size, size))


WIDTH = 10
HEIGHT = 20
BLOCKSIZE = 32
BLOCKGAP = 1
XMARGIN = 5
YMARGIN = 5
DROPTIME = 1000 #ms

SHAPES = [
    Shape(pos=Pos((WIDTH-1)//2+0.5, HEIGHT-1.5), relPositions=[Pos(-1.5,0.5),Pos(-0.5,0.5),Pos(0.5,0.5),Pos(1.5,0.5)], colour=Tile.CYAN), # I
    Shape(pos=Pos((WIDTH-1)//2+1, HEIGHT-2), relPositions=[Pos(-1,1),Pos(-1,0),Pos(0,0),Pos(1,0)], colour=Tile.BLUE), # J
    Shape(pos=Pos((WIDTH-1)//2, HEIGHT-2), relPositions=[Pos(-1,0),Pos(0,0),Pos(1,0),Pos(1,1)], colour=Tile.ORANGE), # L
    Shape(pos=Pos((WIDTH-1)//2+0.5, HEIGHT-1.5), relPositions=[Pos(-0.5,0.5),Pos(0.5,0.5),Pos(0.5,-0.5),Pos(-0.5,-0.5)], colour=Tile.YELLOW), # O
    Shape(pos=Pos((WIDTH-1)//2, HEIGHT-2), relPositions=[Pos(-1,0),Pos(0,0),Pos(0,1),Pos(1,1)], colour=Tile.GREEN), # Z
    Shape(pos=Pos((WIDTH-1)//2, HEIGHT-2), relPositions=[Pos(-1,0),Pos(0,0),Pos(0,1),Pos(1,0)], colour=Tile.PURPLE), # T
    Shape(pos=Pos((WIDTH-1)//2+1, HEIGHT-2), relPositions=[Pos(1,0),Pos(0,0),Pos(0,1),Pos(-1,1)], colour=Tile.RED), # S
]

grid: list[Tile] = [Tile(pos=Pos(x,y), colour=0) for y in range(HEIGHT) for x in range(WIDTH)]

shape: Shape = random.choice(SHAPES).instantiate()
assert shape.blocks is not None
for block in shape.blocks: block.set()

pygame.init()
screen = pygame.display.set_mode((WIDTH*(BLOCKSIZE+BLOCKGAP)-BLOCKGAP+XMARGIN*2, HEIGHT*(BLOCKSIZE+BLOCKGAP)-BLOCKGAP+YMARGIN*2))
clock = pygame.time.Clock()
running = True
ticks = 1

while running:

    dropped = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w,pygame.K_UP):
                shape.rotate()
            elif event.key in (pygame.K_s,pygame.K_DOWN) and not dropped:
                if shape.drop():
                    dropped = True

    screen.fill("purple")

    if pygame.time.get_ticks() >= DROPTIME*ticks:
        if not dropped:
            if not shape.drop():
                shape = random.choice(SHAPES).instantiate()
        ticks += 1

    for tile in grid:
        tile.draw(screen=screen, size=BLOCKSIZE, offset=(XMARGIN, YMARGIN), gap=BLOCKGAP)

    pygame.display.flip()

    clock.tick(10)

pygame.quit()

# TODO: left and right
# TODO: row clear
# TODO: next block
# TODO: points?
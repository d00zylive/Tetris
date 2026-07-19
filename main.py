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
    
    def is_integer(self) -> bool:
        return self.x.is_integer() and self.y.is_integer()
    
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

    def rotate(self, clockwise:bool = True, set:bool = True, offset: Pos = Pos(0,0)) -> bool:
        pivot = self.pos-self.relPos
        relPos = self.relPos.rotate(clockwise=clockwise,set=set)
        pos = pivot+relPos+offset
        if pos.x < 0 or pos.y < 0 or pos.x >= WIDTH or pos.y >= HEIGHT or grid[pos.index()].colour != 0:
            return False
        else:
            if set:
                self.pos = pos
            return True
        
    def move(self, vector:Pos = Pos(0,-1), set:bool = True) -> bool:
        if vector.is_integer():
            if self.pos.x+vector.x >= 0 and self.pos.y+vector.y >= 0 and self.pos.x+vector.x < WIDTH and self.pos.y+vector.y < HEIGHT:
                checkIndex = (self.pos+vector).index()
                if grid[checkIndex].colour == 0:
                    if set:
                        self.pos = self.pos+vector
                    return True
            return False
        else:
            raise ValueError("Vector is not an integer Pos")


class Shape():
    pos: Pos
    relPositions: list[Pos]
    colour: int
    name: str
    rotation: int
    blocks: list[Block]|None

    NORMALWALLKICKTESTS = {
        "0cw":  [Pos(0,0),Pos(-1,0),Pos(-1,-1),Pos(0,+2),Pos(-1,+2)],
        "1ccw": [Pos(0,0),Pos(+1,0),Pos(+1,+1),Pos(0,-2),Pos(+1,-2)],
        "1cw": [Pos(0,0),Pos(+1,0),Pos(+1,+1),Pos(0,-2),Pos(+1,-2)],
        "2ccw": [Pos(0,0),Pos(-1,0),Pos(-1,-1),Pos(0,+2),Pos(-1,+2)],
        "2cw": [Pos(0,0),Pos(+1,0),Pos(+1,-1),Pos(0,+2),Pos(+1,+2)],
        "3ccw": [Pos(0,0),Pos(-1,0),Pos(-1,+1),Pos(0,-2),Pos(-1,-2)],
        "3cw": [Pos(0,0),Pos(-1,0),Pos(-1,-1),Pos(0,-2),Pos(-1,-2)],
        "0ccw": [Pos(0,0),Pos(+1,0),Pos(+1,-1),Pos(0,+2),Pos(+1,+2)]
    }
    IWALLKICKTESTS = {
        "0cw":  [Pos(0,0),Pos(-2,0),Pos(+1,0),Pos(-2,+1),Pos(+1,-2)],
        "1ccw": [Pos(0,0),Pos(+2,0),Pos(-1,0),Pos(+2,-1),Pos(-1,+2)],
        "1cw": [Pos(0,0),Pos(-1,0),Pos(+2,0),Pos(-1,-2),Pos(+2,+1)],
        "2ccw": [Pos(0,0),Pos(+1,0),Pos(-2,0),Pos(+1,+2),Pos(-2,-1)],
        "2cw": [Pos(0,0),Pos(+2,0),Pos(-1,0),Pos(+2,-1),Pos(-1,+2)],
        "3ccw": [Pos(0,0),Pos(-2,0),Pos(+1,0),Pos(-2,+1),Pos(+1,-2)],
        "3cw": [Pos(0,0),Pos(+1,0),Pos(-2,0),Pos(+1,+2),Pos(-2,-1)],
        "0ccw": [Pos(0,0),Pos(-1,0),Pos(+2,0),Pos(-1,-2),Pos(+2,+1)]
    }

    def __init__(self, pos: Pos, relPositions: list[Pos], colour: int, name: str, rotation:int = 0, blocks:list[Block]|None = None):
        self.pos = pos
        self.relPositions = relPositions
        self.colour = colour
        self.name = name
        self.rotation = rotation
        self.blocks = blocks

    def __repr__(self):
        return f"Shape(pos={self.pos},relPositions={self.relPositions},colour={self.colour},blocks={self.blocks})"

    def instantiate(self, pos:Pos|None = None) -> tuple[Shape, bool]:
        pos = self.pos if pos is None else pos
        shape = Shape(pos=Pos(pos.x, pos.y), relPositions=[Pos(relPos.x, relPos.y) for relPos in self.relPositions], colour=self.colour, name=self.name, rotation=self.rotation, blocks=[Block(pos=pos+relPos, relPos=Pos(relPos.x,relPos.y), colour=self.colour) for relPos in self.relPositions])
        assert shape.blocks is not None
        overlap = False
        for block in shape.blocks:
            if grid[block.pos.index()].colour != 0:
                overlap = True
            block.set()
        return shape, overlap
    
    def is_instantiated(self) -> bool:
        return isinstance(self.blocks, list) and len(self.blocks) > 0 and all(isinstance(block, Block) for block in self.blocks)
    
    def test_rotation(self, clockwise: bool, offset:Pos) -> bool:
        assert self.blocks is not None
        return all(block.rotate(clockwise=clockwise, set=False, offset=offset) for block in self.blocks)
        
    def rotate(self, clockwise: bool = True) -> bool:
        if self.is_instantiated():
            assert self.blocks is not None
            for block in self.blocks:
                block.clear()
            if self.name == "I":
                wall_kick_dict: dict[str, list[Pos]] = self.IWALLKICKTESTS
            else:
                wall_kick_dict: dict[str, list[Pos]] = self.NORMALWALLKICKTESTS
            wall_kick_tests: list[Pos] = wall_kick_dict[f"{self.rotation}{"c" if not clockwise else ""}cw"]
            offset = None
            for test in wall_kick_tests:
                if self.test_rotation(clockwise=clockwise,offset=test):
                    offset = test
                    break
            if offset is None:
                for block in self.blocks:
                    block.set()
                return False
            for block in self.blocks:
                block.rotate(clockwise=clockwise, offset=offset)
            for block in self.blocks:
                block.set()
            self.rotation = (self.rotation+(1 if clockwise else -1))%4
            return True
        else:
            raise TypeError("Shape uninstantiated")
        
    def move(self, vector:Pos = Pos(0,-1), set:bool = True) -> bool:
        if not vector.is_integer():
            raise ValueError("Vector is not an integer Pos")
        if self.is_instantiated():
            assert self.blocks is not None
            for block in self.blocks:
                block.clear()

            if all(block.move(vector=vector, set=False) for block in self.blocks):
                if set:
                    for block in self.blocks:
                        block.move(vector=vector)
                for block in self.blocks:
                    block.set()
                self.pos = self.pos+vector
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
        0: pygame.Color(7,7,56), # black/empty
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
    
    def drop(self, grid: list[Tile]):
        grid[(self.pos-Pos(0,1)).index()].colour = self.colour
        self.colour = 0

    def draw(self, screen: pygame.Surface, size: int, offset: tuple[int, int] = (0, 0), gap: int = 0):
        pygame.draw.rect(screen, self.COLOURS[self.colour], pygame.Rect(self.pos.x*(size+gap)+offset[0], ((HEIGHT-1)-self.pos.y-(HEIGHT-DISPLAYHEIGHT))*(size+gap)+offset[1], size, size))


def get_shuffled(list: list) -> list:
    shuffled = [item for item in list]
    random.shuffle(shuffled)
    return shuffled

def check_landed():
    global landed
    global landTime
    if not shape.move(set=False):
        if not landed:
            landTime = pygame.time.get_ticks()
            landed = True
    else:
        landed = False

WIDTH = 10
DISPLAYHEIGHT = 20
HEIGHT = 40
BLOCKSIZE = 32
BLOCKGAP = 1
NEXTGAP = 10
LEFTMARGIN, RIGHTMARGIN = 5,10
TOPMARGIN, BOTTOMMARGIN = 5,5
NEXTOFFSET = Pos(LEFTMARGIN+(BLOCKSIZE+BLOCKGAP)*WIDTH-BLOCKGAP+NEXTGAP+(BLOCKSIZE*4+BLOCKGAP*3)//2+RIGHTMARGIN, BLOCKSIZE*3+TOPMARGIN)
DROPTIME = 1000 #ms
LOCKTIME = 500 #ms
DASTIME = 167 #ms

SHAPES = [
    Shape(pos=Pos((WIDTH-1)//2+0.5, DISPLAYHEIGHT-1.5), relPositions=[Pos(-1.5,0.5),Pos(-0.5,0.5),Pos(0.5,0.5),Pos(1.5,0.5)], colour=Tile.CYAN, name="I"), # I
    Shape(pos=Pos((WIDTH-1)//2+1, DISPLAYHEIGHT-2), relPositions=[Pos(-1,1),Pos(-1,0),Pos(0,0),Pos(1,0)], colour=Tile.BLUE, name="J"), # J
    Shape(pos=Pos((WIDTH-1)//2, DISPLAYHEIGHT-2), relPositions=[Pos(-1,0),Pos(0,0),Pos(1,0),Pos(1,1)], colour=Tile.ORANGE, name="L"), # L
    Shape(pos=Pos((WIDTH-1)//2+0.5, DISPLAYHEIGHT-1.5), relPositions=[Pos(-0.5,0.5),Pos(0.5,0.5),Pos(0.5,-0.5),Pos(-0.5,-0.5)], colour=Tile.YELLOW, name="O"), # O
    Shape(pos=Pos((WIDTH-1)//2, DISPLAYHEIGHT-2), relPositions=[Pos(-1,0),Pos(0,0),Pos(0,1),Pos(1,1)], colour=Tile.GREEN, name="Z"), # Z
    Shape(pos=Pos((WIDTH-1)//2, DISPLAYHEIGHT-2), relPositions=[Pos(-1,0),Pos(0,0),Pos(0,1),Pos(1,0)], colour=Tile.PURPLE, name="T"), # T
    Shape(pos=Pos((WIDTH-1)//2+1, DISPLAYHEIGHT-2), relPositions=[Pos(1,0),Pos(0,0),Pos(0,1),Pos(-1,1)], colour=Tile.RED, name="S"), # S
]

grid: list[Tile] = [Tile(pos=Pos(x,y), colour=0) for y in range(HEIGHT) for x in range(WIDTH)]

bag: list[Shape] = get_shuffled(SHAPES)
shape: Shape = bag.pop(0).instantiate()[0]
assert shape.blocks is not None

pygame.init()
screen = pygame.display.set_mode((WIDTH*(BLOCKSIZE+BLOCKGAP)-BLOCKGAP+LEFTMARGIN+(RIGHTMARGIN+NEXTGAP+BLOCKSIZE*4+BLOCKGAP*3), DISPLAYHEIGHT*(BLOCKSIZE+BLOCKGAP)-BLOCKGAP+TOPMARGIN+BOTTOMMARGIN))
clock = pygame.time.Clock()
running = True
ticks = 1
landed = False
landTime = 0
moveTime = 0

while running:

    dropped = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w,pygame.K_UP,pygame.K_e):
                shape.rotate(clockwise=True)
                check_landed()
            if event.key in (pygame.K_q,pygame.K_z):
                shape.rotate(clockwise=False)
                check_landed()
            if event.key in (pygame.K_a,pygame.K_LEFT):
                moveTime = pygame.time.get_ticks()
                shape.move(Pos(-1,0))
                check_landed()
            if event.key in (pygame.K_d,pygame.K_RIGHT):
                moveTime = pygame.time.get_ticks()
                shape.move(Pos(1,0))
                check_landed()

    keys = pygame.key.get_pressed()
    if any(keys[key] for key in (pygame.K_s,pygame.K_DOWN)) and not dropped:
        if shape.move():
            dropped = True
            check_landed()
    if any(keys[key] for key in (pygame.K_a,pygame.K_LEFT)) and pygame.time.get_ticks()-moveTime >= DASTIME:
        shape.move(Pos(-1,0))
        check_landed()
    if any(keys[key] for key in (pygame.K_d,pygame.K_RIGHT)) and pygame.time.get_ticks()-moveTime >= DASTIME:
        shape.move(Pos(1,0))
        check_landed()

    screen.fill("black")
    
    if landed and pygame.time.get_ticks()-landTime >= LOCKTIME:
        yLevels = set(int(block.pos.y) for block in shape.blocks)
        rowsCleared = 0
        for y in yLevels:
            if all(grid[Pos(x,y-rowsCleared).index()].colour != 0 for x in range(WIDTH)):
                for x in range(WIDTH):
                    grid[Pos(x,y-rowsCleared).index()].colour = 0
                for dropy in range(y+1-rowsCleared,HEIGHT):
                    for x in range(WIDTH):
                        grid[Pos(x,dropy).index()].drop(grid=grid)
                rowsCleared += 1
                
        if len(bag) == 0:
            bag = get_shuffled(SHAPES)
        shape, lost = bag.pop(0).instantiate()
        if lost:
            grid: list[Tile] = [Tile(pos=Pos(x,y), colour=0) for y in range(HEIGHT) for x in range(WIDTH)]
            bag: list[Shape] = get_shuffled(SHAPES)
            shape: Shape = bag.pop(0).instantiate()[0]
            landed = False
            landTime = 0
        assert shape.blocks is not None
        landed = False

    if len(bag) == 0:
        bag = get_shuffled(SHAPES)
    for relPos in bag[0].relPositions:
        pygame.draw.rect(screen, color=Tile.COLOURS[bag[0].colour], rect=pygame.Rect((relPos.x*BLOCKSIZE+NEXTOFFSET.x-BLOCKSIZE,relPos.y*BLOCKSIZE+NEXTOFFSET.y-BLOCKSIZE),(BLOCKSIZE,BLOCKSIZE)))

    if pygame.time.get_ticks() >= DROPTIME*ticks:
        if not dropped:
            shape.move()
            check_landed()
        ticks += 1

    for tile in grid:
        if tile.pos.y < DISPLAYHEIGHT:
            tile.draw(screen=screen, size=BLOCKSIZE, offset=(LEFTMARGIN, TOPMARGIN), gap=BLOCKGAP)
        else:
            break

    pygame.display.flip()

    clock.tick(20)

pygame.quit()

# TODO: next block
# TODO: points?
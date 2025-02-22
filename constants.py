"""
Global constants
"""
import glob
import os

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Screen dimensions
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
BORDERS = [40, 120, 90, 210]


BACKGROUNDS = glob.glob('images/backgrounds/*.png')
CREATURES_NAMES = os.listdir('images/creature')

STRATEGY = ['follow', 'retreat', 'flank', 'attack']

pop_size = 5

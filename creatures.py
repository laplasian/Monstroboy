from functions import *
import random

GLOBAL_BUFF_IMAGES = dict()


class Creature(pygame.sprite.Sprite):
    change_x = 0
    change_y = 0
    ACTIONS = None

    def __init__(self, power=1):
        super().__init__()
        self.sprite_list = []
        self.rect = pygame.Rect(0, 0, 128, 128)
        self.rect.x = round(random.random() * (SCREEN_WIDTH - 90)) - 40
        self.rect.y = round(random.random() * (SCREEN_HEIGHT - 330)) + 120
        self.image = None
        self.health = 100
        self.stamina = 100
        self.power = power
        self.direction = 'R'
        self.act = 'idle'
        self.buff_frames = []
        self.time = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        # borders
        if self.rect.x < -BORDERS[0]:
            self.rect.x = -BORDERS[0]
        if self.rect.y < BORDERS[1]:
            self.rect.y = BORDERS[1]
        if self.rect.x > SCREEN_WIDTH - BORDERS[2]:
            self.rect.x = SCREEN_WIDTH - BORDERS[2]
        if self.rect.y > SCREEN_HEIGHT - BORDERS[3]:
            self.rect.y = SCREEN_HEIGHT - BORDERS[3]

        # update stamina
        if self.act == 'idle':
            self.stamina += 0.9 if self.stamina < 100 else 0
        elif self.act == 'attack1':
            self.stamina -= 0.5
        else:
            self.stamina -= 0.1
        if self.stamina <= 0:
            self.stop(True, True)
        self.animate()

    def animate(self):
        pos = self.rect.x if self.change_x != 0 else self.rect.y

        if self.act == "run":
            frame = (pos // 30) % len(self.ACTIONS[self.act + self.direction])
            self.image = self.ACTIONS[self.act + self.direction][frame]
        elif self.act == 'idle':
            self.image = self.ACTIONS[self.act + self.direction][
                round(pygame.time.get_ticks() / 120) % len(self.ACTIONS[self.act + self.direction])]
        elif self.act == 'attack1' or self.act == 'death':
            self.image = self.buff_frames[0]
            if self.buff_frames.__len__() != 0 and pygame.time.get_ticks() - self.time > 40:
                self.buff_frames.pop(0)
                self.time = pygame.time.get_ticks()
            if self.buff_frames.__len__() == 0:
                self.act = 'idle'
        elif self.act == 'death':
            self.image = self.buff_frames[0]
            if self.buff_frames.__len__() != 0 and pygame.time.get_ticks() - self.time > 500:
                self.buff_frames.pop(0)
                self.time = pygame.time.get_ticks()

    def run_left(self):
        if self.buff_frames.__len__() != 0:
            return 0
        self.act = 'run'
        self.direction = 'L'
        self.change_x = -4

    def run_right(self):
        if self.buff_frames.__len__() != 0:
            return 0
        self.act = 'run'
        self.direction = 'R'
        self.change_x = 4

    def run_up(self):
        if self.buff_frames.__len__() != 0:
            return 0
        self.change_y = -4
        self.act = 'run'

    def run_down(self):
        if self.buff_frames.__len__() != 0:
            return 0
        self.change_y = 4
        self.act = 'run'

    def attack(self, enemies, genome=None):
        """
        :param enemies: list of mortal object
        :param genome: Default: None, if self is monster and Train _mode: genome
        :return: None or 0 if nothing needs
        """

        if self.act == 'attack1':
            return 0
        self.stop(True, True)
        self.act = 'attack1'
        self.buff_frames = self.ACTIONS[self.act + self.direction].copy()
        for enemy in enemies:
            if ((self.direction == "R" if self.rect.x - enemy.rect.x <= 0 else self.direction == "L")
                    and get_distance(self, enemy) <= 100):
                power_coficent = (140 - get_distance(self, enemy)) / 100
                enemy.health -= 10 * self.power * power_coficent
                if genome:
                    genome[1].fitness += 10
        if genome:
            genome[1].fitness -= 0.5
        self.time = pygame.time.get_ticks()

    def stop(self, x=False, y=False):
        if x:
            self.change_x = 0
        if y:
            self.change_y = 0
        if self.change_x == 0 and self.change_y == 0 and self.buff_frames.__len__() == 0:
            self.act = 'idle'

    def death(self):
        self.stop(True, True)
        self.act = 'death'
        self.buff_frames = self.ACTIONS[self.act + self.direction].copy()
        self.time = pygame.time.get_ticks()


class Player(Creature):
    def __init__(self, name="Samurai"):
        global GLOBAL_BUFF_IMAGES
        super().__init__()
        if name not in GLOBAL_BUFF_IMAGES:
            GLOBAL_BUFF_IMAGES[name] = create_creature(name)
        self.ACTIONS = GLOBAL_BUFF_IMAGES[name]
        self.image = self.ACTIONS[self.act + self.direction][0]
        self.last_act = 0
        self.health = 2000
        self.stamina = 5000
        self.power = 200


class Monster(Creature):
    def __init__(self, name='Kitsune', uniq_name=''):
        global GLOBAL_BUFF_IMAGES
        super().__init__()
        self.uniq_name = name + uniq_name
        if name not in GLOBAL_BUFF_IMAGES:
            GLOBAL_BUFF_IMAGES[name] = create_creature(name)
        self.ACTIONS = GLOBAL_BUFF_IMAGES[name]
        self.image = self.ACTIONS[self.act + self.direction][0]
        self.last_act = 0

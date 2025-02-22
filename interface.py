import pygame
from constants import *
from functions import split_sprites


class GUI:
    level = None
    start = None
    scr = None
    font = None
    buttons = None
    button1 = None
    button2 = None
    button3 = None
    button4 = None
    button5 = None
    button6 = None
    button7 = None
    button8 = None
    text1 = None
    text2 = None
    text3 = None
    text4 = None
    text5 = None
    text6 = None
    text7 = None
    text8 = None
    text_rect1 = None
    text_rect2 = None
    text_rect3 = None
    text_rect4 = None
    text_rect5 = None
    text_rect6 = None
    text_rect7 = None
    text_rect8 = None
    level_background = None
    start_background = None
    serf1 = None
    serf2 = None
    image1 = None
    image2 = None
    button_text = None

    def __init__(self):
        pygame.init()
        self.scr = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.rect = (SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.set_caption("МонстроБой")
        self.font = pygame.font.SysFont("Roboto Condensed", 30)
        self.button1 = pygame.Rect((5, 5), (100, 50))
        self.text1 = self.font.render('menu', True, BLACK)
        self.text_rect1 = self.text1.get_rect(center=self.button1.center)
        self.button2 = pygame.Rect((round(SCREEN_WIDTH / 2) - 50, round(SCREEN_HEIGHT / 2) - 60), (100, 50))
        self.text2 = self.font.render('continue', True, BLACK)
        self.text_rect2 = self.text2.get_rect(center=self.button2.center)
        self.button3 = pygame.Rect((round(SCREEN_WIDTH / 2) - 50, round(SCREEN_HEIGHT / 2)), (100, 50))
        self.text3 = self.font.render('save', True, BLACK)
        self.text_rect3 = self.text3.get_rect(center=self.button3.center)
        self.button4 = pygame.Rect((round(SCREEN_WIDTH / 2) - 50, round(SCREEN_HEIGHT / 2) + 60), (100, 50))
        self.text4 = self.font.render('exit', True, BLACK)
        self.text_rect4 = self.text4.get_rect(center=self.button4.center)
        self.action = 'menu'
        self.edit_options = [1, 13]

    def init_level(self, background=None):
        self.level_background = pygame.image.load(background).convert()
        self.level_background = pygame.transform.scale(self.level_background, self.rect)
        self.buttons = [self.button1]

    def init_start(self):
        self.button_text = [self.font.render('medium', True, BLACK),
                            self.font.render('easy', True, BLACK),
                            self.font.render('train mode', True, BLACK),
                            self.font.render('hard', True, BLACK)]

        self.button5 = pygame.Rect((round(SCREEN_WIDTH / 2) - 220, round(SCREEN_HEIGHT / 2) - 120), (150, 50))
        self.text5 = self.font.render('edit game', True, BLACK)
        self.text_rect5 = self.text5.get_rect(center=self.button5.center)
        self.button6 = pygame.Rect((round(SCREEN_WIDTH / 2) + 80, round(SCREEN_HEIGHT / 2) - 120), (150, 50))
        self.text6 = self.button_text[0]
        self.text_rect6 = self.text6.get_rect(center=self.button6.center)
        self.button7 = pygame.Rect((round(SCREEN_WIDTH / 2) - 70, round(SCREEN_HEIGHT / 2)), (150, 50))
        self.text7 = self.font.render('play', True, BLACK)
        self.text_rect7 = self.text7.get_rect(center=self.button7.center)
        self.buttons = [self.button5, self.button6, self.button7]

        self.start_background = pygame.image.load('images/start.png').convert()
        self.start_background = pygame.transform.scale(self.start_background, self.rect)

    def init_edit(self):
        self.serf1 = pygame.Rect((330, 200), (128, 200))
        self.serf2 = pygame.Rect((600, 120), (264, 264))
        self.button8 = pygame.Rect((490, 360), (100, 50))
        self.text8 = self.font.render('apply', True, BLACK)
        self.text_rect8 = self.text8.get_rect(center=self.button8.center)
        self.image1 = pygame.transform.scale(pygame.image.load(BACKGROUNDS[self.edit_options[0]]).convert(),
                                             (128, 200))
        self.image2 = pygame.transform.scale(split_sprites(r'images/creature/'+CREATURES_NAMES[self.edit_options[1]] +
                                                           '/Idle.png')[0], (264, 264))

    def draw(self, info=None):
        if self.action == 'menu':
            self.scr.blit(self.start_background, (0, 0))
            self.buttons = [self.button5, self.button6, self.button7]
            pygame.draw.rect(self.scr, RED if info[0] else WHITE, self.button5)
            self.scr.blit(self.text5, self.text_rect5)
            pygame.draw.rect(self.scr, RED if info[1] else WHITE, self.button6)
            self.scr.blit(self.text6, self.text_rect6)
            pygame.draw.rect(self.scr, RED if info[2] else WHITE, self.button7)
            self.scr.blit(self.text7, self.text_rect7)
        if self.action == 'game':
            self.scr.blit(self.level_background, (0, 0))
            self.buttons = [self.button1]
            pygame.draw.rect(self.scr, RED if info[0] else WHITE, self.button1)
            self.scr.blit(self.text1, self.text_rect1)
        if self.action == 'settings':
            self.scr.blit(self.level_background, (0, 0))
            self.buttons = [self.button2, self.button3, self.button4]
            pygame.draw.rect(self.scr, RED if info[0] else WHITE, self.button2)
            self.scr.blit(self.text2, self.text_rect2)
            pygame.draw.rect(self.scr, RED if info[1] else WHITE, self.button3)
            self.scr.blit(self.text3, self.text_rect3)
            pygame.draw.rect(self.scr, RED if info[2] else WHITE, self.button4)
            self.scr.blit(self.text4, self.text_rect4)
        if self.action == 'edit':
            self.scr.blit(self.start_background, (0, 0))
            self.buttons = [self.button8]
            self.scr.blit(self.image1, self.serf1)
            self.scr.blit(self.image2, self.serf2)
            pygame.draw.rect(self.scr, RED if info[0] else WHITE, self.button8)
            self.scr.blit(self.text8, self.text_rect8)

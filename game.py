import random

import neat
import pygame.sprite

from creatures import *
from interface import *

score: int
generation = 0
dead_list = list()
gui: GUI
clock: pygame.time.Clock
player: Player


def main(genomes, conf, train_mode=False):
    global score, generation, dead_list, gui, clock, player, info, _mode
    generation += 1
    score = 0
    monsters = []
    dead_list = []
    nets = []
    info = [False]

    # init genomes, monsters and player
    if genomes.__len__() > pop_size:
        genomes = genomes[0:pop_size]
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, conf)
        nets.append(net)
        g.fitness = 0
        monsters.append(Monster(CREATURES_NAMES[random.randint(0, len(CREATURES_NAMES))-1], str(i)))
        if _mode == 'hard':
            monsters[-1].power = 2
            monsters[-1].stamina = 200
        elif _mode == 'easy':
            monsters[-1].power = 0.5
            monsters[-1].stamina = 50

    iter_time = pygame.time.get_ticks()
    timer = iter_time
    lasy_mode = False
    pause = False
    done = False
    # -------- Main Program Loop -----------
    while not done:
        act = False
        if player.health <= 0 and not train_mode:
            game_over_win(False)
        if pygame.time.get_ticks() - timer > 10000 and lasy_mode and train_mode:
            if generation % 7 == 6:
                with open(r"trained/auto_save" + str(glob.glob(r"trained/*.pkl").__len__() + 1) + r".pkl",
                          "wb") as file:
                    pickle.dump(max(genomes, key=lambda x: x[1].fitness), file)
            done = True

        info, act, done, lasy_mode = operations_control_player(player, monsters, pause, train_mode, gui, info,
                                                               act, genomes, done, lasy_mode)
        gui.draw(info)
        info, pause = update_buttons(gui, act, info, pause)

        if not pause:
            if len(monsters) == 0 and len(dead_list) == 0 and train_mode:
                done = True
            if len(monsters) == 0 and len(dead_list) == 0 and not train_mode:
                game_over_win(True)
            # control
            if pygame.time.get_ticks() - iter_time > 100:
                if lasy_mode and train_mode:  # lazy mode
                    lazy_player(player, monsters, nets[genomes.index(max(genomes, key=lambda x: x[1].fitness))])
                iter_time = pygame.time.get_ticks()
                control_monster(monsters, nets, player, genomes if train_mode else None)
                if train_mode:
                    update_monster_fitness(monsters, genomes)
            # update all and draw
            player.update()
            player.draw(gui.scr)
            for i, monster in enumerate(monsters):
                if monster.health <= 0:
                    dead_list.append(monster)
                    monster.death()
                    genomes.pop(i)
                    nets.pop(i)
                    monsters.pop(i)
                monster.update()
                monster.draw(gui.scr)
            for dead_body in dead_list:
                if dead_body.buff_frames.__len__() == 0:
                    dead_list.remove(dead_body)
                else:
                    dead_body.update()
                    dead_body.draw(gui.scr)

        if train_mode:
            # show generation
            for i, monster in enumerate(monsters):
                label = gui.font.render(monster.uniq_name + ' h:' + str(round(monster.health)), True, (0, 0, 0))
                label_rect = label.get_rect()
                label_rect.center = (SCREEN_WIDTH - 100, 20 + (i * 15))
                gui.scr.blit(label, label_rect)
            label = gui.font.render("Generation: " + str(generation), True, (0, 0, 0))
            label_rect = label.get_rect()
            label_rect.center = (SCREEN_WIDTH / 2, 150)
            gui.scr.blit(label, label_rect)

        clock.tick(60)
        pygame.display.flip()


def menu():
    global _mode, clock, gui, info
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                info = [button.collidepoint(event.pos) for button in gui.buttons]
            if event.type == pygame.MOUSEBUTTONDOWN:
                if gui.action == 'menu':
                    if gui.button5.collidepoint(event.pos):
                        gui.action = 'edit'
                        info = [False]
                    if gui.button6.collidepoint(event.pos):
                        gui.text6 = gui.button_text[gui.button_text.index(gui.text6) - 1]
                        _mode = mods[gui.button_text.index(gui.text6)]
                    if gui.button7.collidepoint(event.pos):
                        gui.action = 'game'
                if gui.action == 'edit':
                    if gui.button8.collidepoint(event.pos):
                        gui.action = 'menu'
                        info = [False, False, False]
                    if gui.serf1.collidepoint(event.pos):
                        gui.edit_options[0] += 1 if BACKGROUNDS.__len__() > gui.edit_options[
                            0] + 1 else - BACKGROUNDS.__len__()
                        gui.image1 = pygame.transform.scale(
                            pygame.image.load(BACKGROUNDS[gui.edit_options[0]]).convert(),
                            (128, 200))
                    if gui.serf2.collidepoint(event.pos):
                        gui.edit_options[1] += 1 if CREATURES_NAMES.__len__() > gui.edit_options[
                            1] + 1 else - CREATURES_NAMES.__len__()
                        gui.image2 = pygame.transform.scale(split_sprites(r'images/creature/' + CREATURES_NAMES[
                            gui.edit_options[1]] + '/Idle.png')[0], (264, 264))
        if gui.action == 'game':
            background = BACKGROUNDS[gui.edit_options[0]]
            name = CREATURES_NAMES[gui.edit_options[1]]
            select_mode(background, name)
        gui.draw(info)
        clock.tick(60)
        pygame.display.flip()


def select_mode(background, player_type):
    global _mode, clock, gui, info, player
    gui.init_level(background)
    player = Player(player_type)
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    if _mode == 'train mode':
        # init NEAT
        p = neat.Population(config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        # run NEAT
        p.run(lambda genomes, conf: main(genomes, conf, True), 500)
    else:
        # load ai logic
        with open(gen_path, "rb") as f:
            genome = pickle.load(f)

        main([genome] * pop_size, config)


def game_over_win(won):
    global clock, gui
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        image = pygame.transform.scale(pygame.image.load(r'images/win.webp').convert(),
                                       (SCREEN_WIDTH, SCREEN_HEIGHT)) if won \
            else pygame.transform.scale(pygame.image.load(r'images/game over.webp').convert(),
                                        (SCREEN_WIDTH, SCREEN_HEIGHT))
        gui.scr.blit(image, (0, 0))
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    # init game interface
    gui = GUI()
    gui.init_edit()
    gui.init_start()
    info = [False, False, False]
    mods = ['medium', 'easy', 'train mode', 'hard']
    _mode = mods[0]
    menu()
    pygame.quit()

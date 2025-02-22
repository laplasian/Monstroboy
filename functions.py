import pygame
import math
from constants import *
import sys
import pickle
from PIL import Image


def create_creature(name):
    path = r'images/creature/' + name

    attack1_r = split_sprites(path + '/Attack_1.png')
    attack1_l = [pygame.transform.flip(image, True, False) for image in attack1_r]

    dead_r = split_sprites(path + '/Dead.png')
    dead_l = [pygame.transform.flip(image, True, False) for image in dead_r]

    hurt_r = split_sprites(path + '/Hurt.png')
    hurt_l = [pygame.transform.flip(image, True, False) for image in hurt_r]

    idle_r = split_sprites(path + '/Idle.png')
    idle_l = [pygame.transform.flip(image, True, False) for image in idle_r]

    run_r = split_sprites(path + '/Run.png')
    run_l = [pygame.transform.flip(image, True, False) for image in run_r]

    actions = {"runL": run_l, "runR": run_r, "idleL": idle_l,
               "idleR": idle_r, "attack1L": attack1_l,
               "attack1R": attack1_r, 'hurtL': hurt_l,
               'hurtR': hurt_r, 'deathR': dead_r, 'deathL': dead_l}
    return actions


def split_sprites(image_path):
    sprite_sheet = Image.open(image_path).convert("RGBA")
    sheet_width, sheet_height = sprite_sheet.size

    sprite_width = sheet_height
    sprite_height = sheet_height

    cols = sheet_width // sprite_width
    buff = []
    for row in range(1):
        for col in range(cols):
            # Define the bounding box for each sprite
            left = col * sprite_width
            upper = row * sprite_height
            right = left + sprite_width
            lower = upper + sprite_height

            # Crop the sprite and save it
            sprite = sprite_sheet.crop((left, upper, right, lower))
            mode = sprite.mode
            size = sprite.size
            data = sprite.tobytes()

            # Create a Pygame surface from PIL image data
            pygame_image = pygame.image.fromstring(data, size, mode).convert_alpha()

            buff.append(pygame_image.convert_alpha())
    return buff


def get_distance(c1, c2):
    return math.sqrt((c1.rect.x - c2.rect.x) ** 2 + (c1.rect.y - c2.rect.y) ** 2)


def stack(data):
    buff = []
    for i in data:
        for j in i:
            buff.append(j / 100)
    return buff


def update_each_data(enemy, enemies, player):
    """data size is fixed"""  # 6 * 6 + 4 = 40
    data = []  # [angle, distance, last_act, stamina, health]
    for monster in enemies:
        if monster != enemy:
            angle = math.atan2(enemy.rect.x - monster.rect.x, enemy.rect.y - monster.rect.y) * 10
            data.append([angle, get_distance(monster, enemy), monster.last_act,
                         -10 if monster != player else 10, monster.stamina, monster.health])
    data.sort(key=lambda x: x[1])
    dist_left_wall = enemy.rect.x + 40
    dist_right_wall = SCREEN_WIDTH - 50 - enemy.rect.x
    dist_up_wall = enemy.rect.y - 120
    dist_down_wall = SCREEN_HEIGHT - 210 - enemy.rect.y
    data.append([dist_left_wall, dist_right_wall, dist_up_wall, dist_down_wall, enemy.last_act, enemy.stamina])

    for _ in range(pop_size + 1 - data.__len__()):
        data.append([0, 0, 0, 0, 0, 0])
    return data


def control_monster(monsters, nets, player, genomes=None):
    for i, monster in enumerate(monsters):
        inp = update_each_data(monster, list(monsters + [player]), player)  # update data
        output = nets[i].activate(stack(inp))  # get output
        strategy = STRATEGY[output.index(max(output))]
        monster.last_act = output.index(max(output)) * 10
        decide_action(player, monster, strategy, genomes[i] if genomes else None)


def decide_action(player, monster, strategy, genome=None):
    """
    Определяет действия персонажа в зависимости от стратегии и положения монстра.
    :param genome: Default: None
    :param monster
    :param player
    :param strategy:  'follow', 'retreat', 'flank', 'attack'
    """

    distance_x = monster.rect.x - player.rect.x
    distance_y = monster.rect.y - player.rect.y

    if abs(distance_x) > abs(distance_y):
        if distance_x > 0:
            case = 0
        else:
            case = 1
    else:
        if distance_y > 0:
            case = 2
        else:
            case = 3
    local_act_follow = [monster.run_right, monster.run_left, monster.run_down, monster.run_up]
    local_act_retreat = [monster.run_left, monster.run_right, monster.run_up, monster.run_down]
    local_act_flank = [monster.run_down, monster.run_up, monster.run_right, monster.run_left]
    if strategy == 'follow':
        local_act_follow[case]()
    elif strategy == 'retreat':
        local_act_retreat[case]()
    elif strategy == 'flank':
        local_act_flank[case]()
    elif strategy == 'attack':
        if get_distance(monster, player) <= 100:
            monster.attack([player], genome)


def operations_control_player(player, enemies, pause, train_mode, gui, info, act, genomes, done, lasy_mode):
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_q and train_mode:
                done = True
            if e.key == pygame.K_l:
                lasy_mode = False if lasy_mode else True
        if e.type == pygame.MOUSEMOTION:
            info = [button.collidepoint(e.pos) for button in gui.buttons]
        if e.type == pygame.MOUSEBUTTONDOWN:
            act = info[0] if gui.action == 'game' else True
            if gui.action != 'game' and train_mode:
                if info[1]:
                    with open(r"trained/manual_save" + str(glob.glob(r"trained/*.pkl").__len__() + 1) + r".pkl",
                              "wb") as file:
                        pickle.dump(max(genomes, key=lambda x: x[1].fitness), file)
        if not pause:
            if e.type == pygame.KEYDOWN:
                if not pygame.key.get_mods():
                    if e.key == pygame.K_a:
                        player.run_left()
                    if e.key == pygame.K_d:
                        player.run_right()
                    if e.key == pygame.K_w:
                        player.run_up()
                    if e.key == pygame.K_s:
                        player.run_down()
                if e.key == pygame.K_SPACE:
                    player.last_act = 30
                    player.attack(enemies)
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT or pygame.K_RIGHT:
                    player.stop(x=True)
                if e.key == pygame.K_UP or pygame.K_DOWN:
                    player.stop(y=True)
    return info, act, done, lasy_mode


def update_buttons(gui, act, info, pause):
    if gui.action == 'game' and act:
        pause = True
        gui.action = 'settings'
        info = [False, False, False]
    elif gui.action == 'settings' and act:
        if info[0]:
            pause = False
            gui.action = 'game'
            info = [False]
        elif info[2]:
            pygame.quit()
            sys.exit()
    return info, pause


def update_monster_fitness(monsters, genomes):
    for i, monster in enumerate(monsters):
        if monster.stamina < 50:
            genomes[i][1].fitness -= monster.stamina / 1000
        if monster.last_act == 0 or 10 or 20:
            genomes[i][1].fitness -= 0.01
        if (monster.rect.x == -40 or monster.rect.y == 120 or
                monster.rect.x == SCREEN_WIDTH - 90 or monster.rect.y == SCREEN_HEIGHT - 210):
            genomes[i][1].fitness -= 0.04


def lazy_player(player, monsters, net):
    inp = update_each_data(player, list(monsters + [player]), player)  # update data
    output = net.activate(stack(inp))  # get output
    strategy = STRATEGY[output.index(max(output))]
    dist = []
    for enemy in monsters:
        dist.append(get_distance(player, enemy))
    monster = monsters[dist.index(min(dist))]
    distance_x = player.rect.x - monster.rect.x
    distance_y = player.rect.y - monster.rect.y

    if strategy == 'follow':
        if abs(distance_x) > abs(distance_y):
            if distance_x > 0:
                player.run_right()
            else:
                player.run_left()
        else:
            if distance_y > 0:
                player.run_down()
            else:
                player.run_up()

    elif strategy == 'retreat':
        if abs(distance_x) > abs(distance_y):
            if distance_x > 0:
                player.run_left()
            else:
                player.run_right()
        else:
            if distance_y > 0:
                player.run_up()
            else:
                player.run_down()

    elif strategy == 'flank':
        if abs(distance_x) > abs(distance_y):
            if distance_y > 0:
                player.run_down()
            else:
                player.run_up()
        else:
            if distance_x > 0:
                player.run_right()
            else:
                player.run_left()

    elif strategy == 'attack':
        if get_distance(monster, player) <= 100:
            player.attack(monsters)

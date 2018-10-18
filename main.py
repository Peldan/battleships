import sys, pygame, math, fnmatch
from random import randint, choice

black = [0, 0, 0]
white = [190, 190, 190]
red = [255, 0, 0]
shipPositions = []
sunken_player_ships = 0
shipSizes = []

def init():
    pygame.init()
    pygame.mouse.set_cursor(*pygame.cursors.broken_x)
    shipFont = pygame.font.SysFont("monospace", 30)
    gameArea = GameArea()
    size = width, height = 825, 625
    screen = pygame.display.set_mode(size)
    shipAreaWidth = 200
    shipAreaHeight = gameArea.height
    gameAreaRect = [0, 0, gameArea.width, gameArea.height]
    shipAreaRect = [gameArea.width, 0, screen.get_width() - 200, gameArea.height]
    tileSize = [math.sqrt(math.sqrt(625)), math.sqrt(math.sqrt(625))]
    matrix = makeTiles(gameArea.width, gameArea.height)
    availableShips = makeShips(gameArea.width, gameArea.height, False, matrix)
    enemy = Enemy(makeShips(gameArea.width, gameArea.height, True, matrix), gameArea.width, gameArea.height)
    gameLoop(gameArea, shipAreaRect, screen, matrix, availableShips, shipFont, enemy)


def makeTiles(gameAreaWidth, gameAreaHeight):
    matrix = [0] * int(math.sqrt(gameAreaWidth))
    for i in range(len(matrix)):
        matrix[i] = [0] * int(math.sqrt(gameAreaHeight))
    return matrix

def gameLoop(gameArea, shipAreaRect, screen, matrix, availableShips, shipFont, enemy):
    placed_ships = 0
    chosenship = None
    movingship = False
    shipinitialx = 0
    shipinitialy = 0
    hovered_rect = None
    players_turn = True
    clicked_row = None
    clicked_column = None
    missed_shots = []
    hits_by_player = []
    hits_by_enemy = []
    shoot_ticks = 0
    while sunken_player_ships < len(availableShips) and enemy.sunken_enemy_ships < len(enemy.enemyships):
        screen.fill(black, gameArea.rect)
        screen.fill(white, shipAreaRect)
        if not players_turn:
            enemy_shoot(gameArea, enemy, hits_by_enemy, matrix, availableShips)
            players_turn = True
        if hovered_rect != None:
            screen.fill((50, 50, 50), hovered_rect)
        if movingship:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            if pygame.mouse.get_pos()[0] % 25 == 0:
                chosenship.x = pygame.mouse.get_pos()[0]
            if pygame.mouse.get_pos()[1] % 25 == 0:
                chosenship.y = pygame.mouse.get_pos()[1]

        for tile in range(len(missed_shots)):
            pygame.draw.lines(screen, red, False, [(missed_shots[tile][0] * 25, missed_shots[tile][1] * 25),
                (missed_shots[tile][0] * 25 + 25, missed_shots[tile][1] * 25 + 25),
                (missed_shots[tile][0] * 25, missed_shots[tile][1] * 25 + 25),
                (missed_shots[tile][0] * 25 + 25, missed_shots[tile][1] * 25)])

        draw_grid(gameArea, screen, matrix)
        drawShips(availableShips, screen, gameArea.width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEMOTION:
                if not movingship and gameArea.rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                    hovered_x = int(math.ceil(pygame.mouse.get_pos()[0] / 25) * 25) - 25
                    hovered_y = int(math.ceil(pygame.mouse.get_pos()[1] / 25) * 25) - 25
                    hovered_rect = [hovered_x, hovered_y, 25, 25]
                elif not gameArea.rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if movingship and gameArea.rect.collidepoint(pygame.mouse.get_pos()):
                    temp_rect = pygame.Rect(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], chosenship.width, chosenship.height)
                    for ship in availableShips:
                        while ship != chosenship and temp_rect.colliderect(ship.rect):
                            print("Finns redan ett skepp här")
                            
                    if gameArea.rect.contains(temp_rect):
                        movingship = False
                        place_ship(gameArea, chosenship, matrix, shipinitialx, shipinitialy)
                        placed_ships+=1
                elif not gameArea.rect.collidepoint(pygame.mouse.get_pos()):
                    movingship = False
                    for ship in availableShips:
                        shiprect = pygame.Rect(ship.x, ship.y, ship.width, ship.height)
                        if shiprect.collidepoint(pygame.mouse.get_pos()):
                            shipinitialx = ship.x
                            shipinitialy = ship.y
                            movingship = True if movingship == False and not gameArea.playerrect.collidepoint(pygame.mouse.get_pos()) else False
                            chosenship = ship
                elif not movingship and gameArea.rect.collidepoint(pygame.mouse.get_pos()) and \
                    players_turn and int(pygame.mouse.get_pos()[1] / 25) < int((gameArea.height / 2) / 25) and placed_ships == len(availableShips):
                    clicked_column = int(pygame.mouse.get_pos()[0] / 25)
                    clicked_row = int(pygame.mouse.get_pos()[1] / 25)
                    if [clicked_column, clicked_row] not in missed_shots and [clicked_column, clicked_row] not in hits_by_player:
                        if matrix[clicked_column][clicked_row] == 1:
                            for ship in enemy.enemyships:
                                if ship.rect.collidepoint(clicked_column*25, clicked_row*25):
                                    ship.was_hit()
                                    if ship.did_sink():
                                        enemy.sunken_enemy_ships += 1
                            hits_by_player.append([clicked_column, clicked_row])
                        else:
                            missed_shots.append([clicked_column, clicked_row])
                        players_turn = False

        for tile in range(len(hits_by_enemy)):
            screen.fill((150, 100, 100), [hits_by_enemy[tile][0] * 25, hits_by_enemy[tile][1] * 25, 25, 25])
        for tile in range(len(hits_by_player)):
            screen.fill(red, [hits_by_player[tile][0] * 25, hits_by_player[tile][1] * 25, 25, 25])
        screen.blit(shipFont.render("Fartyg", 1, black), shipAreaRect)
        pygame.display.flip()


def place_ship(gameArea, chosenship, matrix, shipinitialx, shipinitialy):
    column = int(chosenship.x / 25)
    row = int(chosenship.y / 25)
    if chosenship.y < gameArea.height / 2:
        chosenship.x = shipinitialx
        chosenship.y = shipinitialy
    else:
        for i in range(int(chosenship.height / 25)):
            matrix[column][row + i] = 1

def draw_grid(gameArea, screen, matrix):
    for tile in range(len(matrix)):
        screen.fill(white, [tile*25, 0, 1, gameArea.height])
        for y in range(0, int(math.sqrt(gameArea.height))):
            if y > 12:
                screen.fill(white, [0, y*25, gameArea.width, 1])
            elif y == 12:
                screen.fill(red, [0, y*25, gameArea.width, 25])
            else:
                screen.fill((50, 50, 50), [0, y*25, gameArea.width, 1])

def enemy_shoot(gameArea, enemy, hits_by_enemy, matrix, availableShips):
    shot = enemy.shoot(gameArea.width, gameArea.height, matrix)
    if shot == None or shot[0] == None or shot[1] == None \
        or matrix[shot[0]][shot[1]] == 'X':
        enemy.new_random_shot(gameArea.width, gameArea.height, matrix)
    else:
        if matrix[shot[0]][shot[1]] == 1:
            hits_by_enemy.append([shot[0], shot[1]])
            for ship in availableShips:
                if ship.rect.collidepoint((shot[0]*25, shot[1]*25)):
                    ship.was_hit()
                    if ship.did_sink():
                        sunken_player_ships += 1
            enemy.did_hit(True)
        else:
            enemy.did_hit(False)
        matrix[shot[0]][shot[1]] = "X"

def drawShips(availableShips, screen, gameAreaWidth):
    for i in range(len(availableShips)):
        screen.fill(red, [(availableShips[i].x), (availableShips[i].y), availableShips[i].width, availableShips[i].height])

def makeShips(gameAreaWidth, gameAreaHeight, is_enemy, matrix):
    availableShips = []
    offsetx = 0
    offsety = 30
    for i in range(0, 5):
        width = 1*math.sqrt(gameAreaWidth)
        height = randint(2, 5)*math.sqrt(gameAreaHeight)
        if is_enemy:
            height = shipSizes[i]
            x = randint(0, int(gameAreaWidth) - width)
            y = randint(0, int(gameAreaHeight / 2) - height)
            column = int(math.ceil(x / 25))
            row = int(math.ceil(y / 25))
            curr = 0
            try:
                while curr < int(height / 25):
                    if (matrix[column][row + curr] == 1 or matrix[column + 1][row + curr] == 1 or \
                            matrix[column - 1][row + curr] == 1 or (curr == 0 and matrix[column][row - 1] == 1)):
                        x = randint(0, int(gameAreaWidth) - width)
                        y = randint(0, int(gameAreaHeight / 2) - height)
                        column = int(math.ceil(x / 25))
                        row = int(math.ceil(y / 25))
                        curr = 0
                    else:
                        matrix[column][row + curr] = 1
                        if column - 1 >= 0 and column + 1 < len(matrix) and row + curr < len(matrix[column]):
                            curr += 1
            except:
                pass
        else:
            x = gameAreaWidth + offsetx
            y = 0 + offsety
        shipSizes.append(height)
        ship = Ship(x, y, width, height)
        availableShips.append(ship)
        offsetx += 27
    return availableShips

class Enemy:
    enemyships = []
    previous_shots = [] # index: 0 = x, 1 = y, 2 = did_hit, 3 = negative or positive y-direction from last shot (-1 or 1)
    next_shot = None
    sunken_enemy_ships = 0
    w = 0
    h = 0
    x = 0
    y = 0
    def __init__(self, enemyships, w, h):
        self.enemyships = enemyships
        self.w = w
        self.h = h
    def did_hit(self, did_hit):
        if did_hit:
            self.previous_shots[len(self.previous_shots) - 1][2] = True

    def shoot(self, gameAreaWidth, gameAreaHeight, matrix):
        x = randint(0, int(gameAreaWidth - 25))
        y = randint(int((gameAreaHeight - 25) / 2), int(gameAreaHeight - 25))
        self.x = x
        self.y = y
        column = None
        row = None
        previous_shot = self.previous_shots[len(self.previous_shots) - 1] if len(self.previous_shots) >= 1 else None
        previous_previous_shot = self.previous_shots[len(self.previous_shots) - 2] if len(self.previous_shots) >= 2 else None
        if previous_shot != None and previous_shot[2] == False and previous_previous_shot != None and previous_previous_shot[2] == True:
            return self.hit_streak_ended_shot(previous_previous_shot, matrix)
        elif previous_shot != None and previous_shot[2] == True:
            return self.hit_last_shot()
        else:
            return self.randomized_shot(matrix)

    def hit_last_shot(self):
        column = self.previous_shots[len(self.previous_shots) - 1][0]
        previous_row = self.previous_shots[len(self.previous_shots) - 1][1]
        if previous_row > 0 and previous_row < math.sqrt(self.h) - 1:
            negpos = -1 if self.previous_shots[len(self.previous_shots) - 1][3] == -1 else 1
            new_row = previous_row + negpos
            while self.has_shot_here(column, new_row):
                new_row = (previous_row + 1 if (negpos == -1) else previous_row - 1)
                new_negpos = 1 if negpos == -1 else -1
            else:
                self.previous_shots.append([column, new_row, False, negpos])
                return[column, new_row]
            self.previous_shots[len(self.previous_shots) - 2][3] = negpos

    def hit_streak_ended_shot(self, previous_previous_shot, matrix):
        column = self.previous_shots[len(self.previous_shots) - 2][0]
        beforelast_row = self.previous_shots[len(self.previous_shots) - 2][1]
        if beforelast_row > 0 and beforelast_row < math.sqrt(self.h) - 1:
            negpos = (1 if (previous_previous_shot[3] == -1) else -1)
            new_row = self.decide_shot()
            if new_row != None and column != None and not self.has_shot_here(column, new_row):
                self.previous_shots.append([column, new_row, False, negpos])
                return[column, new_row]
            else:
                return self.randomized_shot(matrix)

    def randomized_shot(self, matrix):
        x = self.x
        y = self.y
        column = None
        row = int(math.ceil(self.y / 25))
        if len(self.previous_shots) > 5:
            blindspots_per_column = self.calc_most_probable(matrix)
            if len(blindspots_per_column) > 0:
                best = blindspots_per_column[0]
                for i in range(len(blindspots_per_column)):
                    if blindspots_per_column[i]['Value'] > best['Value']:
                        best = blindspots_per_column[i]
                column = best['Column']
                while self.has_shot_here(column, row):
                    column += choice((-1, 1))
                self.previous_shots.append([column, row, False, 0])
            else:
                column = int(math.ceil(self.x / 25))
                while self.has_shot_here(column, row):
                    x = randint(0, int(self.w - 25))
                    y = randint(int((self.h / 2) - 25), int(self.h - 25))
                    column = int(math.ceil(x / 25))
                    row = int(math.ceil(y / 25))
            return [column, row]
        else:
            column = int(math.ceil(self.x / 25))
            while self.has_shot_here(column, row):
                x = randint(0, int(self.w - 25))
                y = randint(int((self.h / 2) - 25), int(self.h - 25))
                column = int(math.ceil(x / 25))
                row = int(math.ceil(y / 25))
            self.previous_shots.append([column, row, False, 0])
            return [column, row]

    def calc_most_probable(self, matrix):
        columns = []
        for i in range(len(matrix)):
            cnt = 0
            biggest_val = 0
            hits_on_row = 0
            for j in range(13, len(matrix[i])):
                if matrix[i][j] == 0 or matrix[i][j] == 1:
                    cnt+=1
                else:
                    hits_on_row += 1
                    if cnt > biggest_val:
                        biggest_val = cnt
                    cnt = 0
                if j == len(matrix) - 1 and biggest_val == 0:
                    biggest_val = cnt
            if hits_on_row == 0:
                biggest_val = 25
            if biggest_val > 2:
                entry = {'Column': i, 'Value': biggest_val}
                columns.append(entry)
        return columns

    def new_random_shot(self, gameAreaWidth, gameAreaHeight, matrix):
        self.previous_shots[len(self.previous_shots) - 2][2] = False
        self.previous_shots[len(self.previous_shots) - 2][3] = None
        self.previous_shots[2] = False
        return self.randomized_shot(matrix)

    def has_shot_here(self, column, row):
        if [column, row, False, -1] in self.previous_shots or [column, row, True, 1] in self.previous_shots \
            or [column, row, False, 1] in self.previous_shots or [column, row, True, -1] in self.previous_shots:
            return True
        return False
    def decide_shot(self):
        start = self.previous_shots[len(self.previous_shots) - 2] #Senaste skottet som träffade
        curr_row = start
        for i in range(self.previous_shots.index(start), 0, -1):
            print("Positiv: ", " X, Y: " , self.previous_shots[i][0], curr_row[1])
            curr_row = self.previous_shots[i]
            negpos = -1 if start[3] == -1 else 1
            if self.previous_shots[i - 1][0] != self.previous_shots[i][0]:
                break
        to_return = curr_row[1] + 1 if curr_row[3] == -1 else curr_row[1] - 1
        return to_return


class GameArea:
    x = 0
    y = 0
    width = 625
    height = 625
    rect = None
    playerrect = None
    def __init__(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.playerrect = pygame.Rect(self.x, self.height / 2, self.width, self.height / 2)

class Ship:
    x = 0
    y = 0
    width = 0
    height = 0
    rect = None
    hit_tiles = 0
    sunk = False
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    def update_x(self, x):
        self.x = x
        self.rect.x = self.x
    def update_y(self, y):
        self.y = y
        self.rect.y = self.y
    def was_hit(self):
        self.hit_tiles += 1
        if self.hit_tiles == self.height:
            self.sunk = True
    def did_sink(self):
        return self.sunk

init()

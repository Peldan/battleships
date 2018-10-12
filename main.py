import sys, pygame, math
from random import randint, choice

black = [0, 0, 0]
white = [190, 190, 190]
red = [255, 0, 0]
shipPositions = []

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
    while True:
        screen.fill(black, gameArea.rect)
        screen.fill(white, shipAreaRect)
        if not players_turn:
            shot = enemy.shoot(gameArea.width, gameArea.height)
            print("Motståndaren sköt på: ", shot[0], shot[1])
            if matrix[shot[0]][shot[1]] == 1:
                hits_by_enemy.append([shot[0], shot[1]])
                print("Motståndaren träffade")
                enemy.did_hit(True)
            else:
                enemy.did_hit(False)
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

        for tile in range(len(matrix)):
            screen.fill(white, [tile*25, 0, 1, gameArea.height])
            for y in range(0, int(math.sqrt(gameArea.height))):
                if y > 12:
                    screen.fill(white, [0, y*25, gameArea.width, 1])
                elif y == 12:
                    screen.fill(red, [0, y*25, gameArea.width, 25])
                else:
                    screen.fill((50, 50, 50), [0, y*25, gameArea.width, 1])
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
                    movingship = False
                    column = int(chosenship.x / 25)
                    row = int(chosenship.y / 25)
                    if chosenship.y < gameArea.height / 2:
                        chosenship.x = shipinitialx
                        chosenship.y = shipinitialy
                    else:
                        placed_ships += 1
                        for i in range(int(chosenship.height / 25)):
                            matrix[column][row + i] = 1
                    break
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
                    players_turn and pygame.mouse.get_pos()[1] < gameArea.height / 2 and placed_ships == len(availableShips):
                    clicked_column = int(pygame.mouse.get_pos()[0] / 25)
                    clicked_row = int(pygame.mouse.get_pos()[1] / 25)
                    if [clicked_column, clicked_row] not in missed_shots:
                        if matrix[clicked_column][clicked_row] == 1:
                            hits_by_player.append([clicked_column, clicked_row])
                        else:
                            missed_shots.append([clicked_column, clicked_row])
                        players_turn = False

        for tile in range(len(hits_by_enemy)):
            screen.fill((150, 25, 25), [hits_by_enemy[tile][0] * 25, hits_by_enemy[tile][1] * 25, 25, 25])
        for tile in range(len(hits_by_player)):
            screen.fill(red, [hits_by_player[tile][0] * 25, hits_by_player[tile][1] * 25, 25, 25])
        screen.blit(shipFont.render("Fartyg", 1, black), shipAreaRect)
        pygame.display.flip()

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
        ship = Ship(x, y, width, height)
        availableShips.append(ship)
        offsetx += 27
    return availableShips

class Enemy:
    enemyships = []
    previous_shots = []
    hit_last = False
    hit_beforelast = False
    hitdir_beforelast = None
    next_shot = None
    def __init__(self, enemyships, w, h):
        self.enemyships = enemyships
    def did_hit(self, did_hit):
        if self.hit_last and not did_hit:
            self.hit_beforelast = True
        else:
            self.hit_beforelast = False
        self.hit_last = did_hit
    def shoot(self, gameAreaWidth, gameAreaHeight):
        x = randint(0, int(gameAreaWidth))
        y = randint(int(gameAreaHeight / 2), int(gameAreaHeight))
        column = None
        row = None
        if not self.hit_last and self.hit_beforelast:
            column = self.previous_shots[len(self.previous_shots) - 2][0]
            beforelast_row = self.previous_shots[len(self.previous_shots - 2)][1]
            if beforelast_row > 0 and beforelast_row < math.sqrt(gameAreaHeight) - 1:
                negpos = (1 if (hitdir_beforelast == -1) else -1)
                if [column, beforelast_row + negpos] not in previous_shots:
                    self.hitdir_beforelast = negpos
                    return[column, beforelast_row + negpos]
                else:
                    self.hitdir_beforelast = None
                    self.hit_last = False
                    self.hit_beforelast = False
                    self.shoot(gameAreaWidth, gameAreaHeight)
        if self.hit_last and len(self.previous_shots) > 0:
            column = self.previous_shots[len(self.previous_shots) - 1][0]
            previous_row = self.previous_shots[len(self.previous_shots) - 1][1]
            if previous_row > 0 and previous_row < math.sqrt(gameAreaHeight) - 1:
                negpos = choice([-1, 1])
                new_row = previous_row + negpos
                if [column, new_row] in self.previous_shots:
                    new_try = (previous_row + 1 if (negpos == -1) else previous_row - 1)
                    if [column, new_try] in self.previous_shots:
                        self.hit_last = False
                        self.shoot(gameAreaWidth, gameAreaHeight)
                    else:
                        return[column, new_try]
                else:
                    return[column, new_row]
                hitdir_beforelast = negpos
        else:
            column = int(math.ceil(x / 25)) - 1
            row = int(math.ceil(y / 25)) - 1
            while [column, row] in self.previous_shots:
                x = randint(0, int(gameAreaWidth))
                y = randint(int(gameAreaHeight / 2), int(gameAreaHeight))
                column = int(math.ceil(x / 25)) - 1
                row = int(math.ceil(y / 25)) - 1
            self.previous_shots.append([column, row])
            return [column, row]

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
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

init()

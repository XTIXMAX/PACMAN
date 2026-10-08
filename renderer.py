import mazegenerator
import pygame
from itertools import cycle
import random


class render():
    def __init__(self):
        self.config = {}
        self.extract_config()
        self.largeur_fenetre = 0
        self.hauteur_fenetre = 0
        maze = mazegenerator.MazeGenerator()
        maze.generate(42)
        self.mazze = maze.maze

        self.size_cel = self.cell_and_windows_size(self.mazze)
        self.fenetre = pygame.display.set_mode((self.largeur_fenetre,
                                                self.hauteur_fenetre))

    def extract_config(self):
        with open("config.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, values = line.split("=", 1)
                self.config[key.strip()] = values.strip()

    def extract_color(self, color: tuple) -> list[int]:
        new = []      
        color = color.strip("(")
        color = color.strip(")")
        new = color.split(",")
        return tuple(int(morceu.strip()) for morceu in new)

    def check_bits(self, de: int) -> dict:
        result = {
            "nord": False,
            "sud": False,
            "est": False,
            "ouest": False
        }
        if de & 1:
            result["nord"] = True
        if de & 2:
            result["est"] = True
        if de & 4:
            result["sud"] = True
        if de & 8:
            result["ouest"] = True
        return result

    def cell_and_windows_size(self, mazze: list[list[int]]) -> int:
        largueur = int(self.config["WIDTH"])
        hauteur = int(self.config["HEIGHT"])
        size_cell_largeur = largueur // len(mazze[0])
        size_cel_hauteur = hauteur // len(mazze)
        if size_cel_hauteur >= size_cell_largeur:
            size_cell_final = size_cell_largeur
        else:
            size_cell_final = size_cel_hauteur
        self.largeur_fenetre = int(len(mazze[0]) * size_cell_final)
        self.hauteur_fenetre = int(len(mazze) * size_cell_final)
        return size_cell_final

    def cell_to_pixel(self, cordonne: tuple[int, int]) -> None:
        row, col = cordonne
        self.size_cel = self.cell_and_windows_size(self.mazze)
        y = row * self.size_cel
        x = col * self.size_cel
        direction = self.check_bits(self.mazze[row][col])
        return (x, y, direction)

    def wall_bands(self):
        w = self.wall_epaisseur
        c = self.size_cel
        return {
            "nord": (0, 0, c, w),
            "sud": (0, c - w, c, w),
            "est": (c - w, 0, w, c),
            "ouest": (0, 0, w, c),
            }

    def draw(self, fenetre, x, y, largeur, hauteur, couleur):
        for dy in range(hauteur):
            for dx in range(largeur):
                fenetre.set_at((x + dx, y + dy), couleur)
        return fenetre

    def cremaze(self):
        self.wall_epaisseur = 5
        self.color_fond = self.extract_color(self.config["COLOR_FOND"])
        self.color_wall = self.extract_color(self.config["COLOR_WALL"])
        self.fenetre.fill(self.color_fond)
        bande_mur = self.wall_bands()
        for row in range(len(self.mazze)):
            for col in range(len(self.mazze[row])):
                x, y, direction = self.cell_to_pixel((row, col))
                for key, valus in direction.items():
                    if valus is True:
                        xloca, yloca, c, w = bande_mur[key]
                        y_final = y + yloca
                        x_final = x + xloca
                        self.fenetre = self.draw(self.fenetre,
                                                 x_final, y_final,
                                                 c, w, self.color_wall)


class Player():
    def __init__(self, size_cel, row, col, direction_de_depart):
        self.row = row
        self.col = col
        self.base_row = row
        self.base_col = col
        self.cel_size = size_cel
        self.direction = direction_de_depart
        self.next_direction = direction_de_depart
        # self.mouth_open = False

        self.pacman_bouche_fermer = pygame.image.load("pacman_fermer.png")
        self.pacman_bouche_fermer = pygame.transform.scale(
            self.pacman_bouche_fermer, (self.cel_size / 2, self.cel_size / 2))
        self.pacman_bouche_semiouvert = pygame.image.load("pacman_semi_ouvert.png")
        self.pacman_bouche_semiouvert = pygame.transform.scale(
            self.pacman_bouche_semiouvert, (self.cel_size / 2, self.cel_size / 2))
        self.pacman_bouche_ouvert = pygame.image.load("pacman_ouvert.png")
        self.pacman_bouche_ouvert = pygame.transform.scale(
                    self.pacman_bouche_ouvert, (self.cel_size / 2,
                                                self.cel_size / 2))
        self.list_position = [self.pacman_bouche_semiouvert,
                              self.pacman_bouche_semiouvert,
                              self.pacman_bouche_fermer,
                              self.pacman_bouche_fermer,
                              self.pacman_bouche_semiouvert,
                              self.pacman_bouche_semiouvert,
                              self.pacman_bouche_ouvert,
                              self.pacman_bouche_ouvert]
        self.cycle = cycle(self.list_position)
        self.decelage = ((self.cel_size - self.cel_size / 2) / 2)

        pacgums = pygame.image.load("pacgums.png")
        self.size_pacgums = self.cel_size // 1.5
        self.pacgums = pygame.transform.scale(
            pacgums, (self.size_pacgums, self.size_pacgums))
        self.lis_pacgums = []
        self.lis_superpacgums = []
        self.nombre_pacgums_manger = 0
        ubuntu_logo = pygame.image.load("Ubuntu.png")
        self.ubuntu_logo = pygame.transform.scale(ubuntu_logo, 
                                                  (self.size_pacgums, 
                                                   self.size_pacgums))
        self.restard = False

    def at_center(self):
        return (abs(self.row - round(self.row)) < 0.001 and
                abs(self.col - round(self.col)) < 0.001)

    def update(self, maze, check_bits):
        if self.at_center():
            self.row = round(self.row)
            self.col = round(self.col)
            murs = check_bits(maze[self.row][self.col])
            if not murs[self.next_direction]:
                self.direction = self.next_direction
            if murs[self.direction]:
                return
        self.deplacement()

    def check_wall(self, maze):
        list = re.check_bits(maze[(self.row)][(self.col)])
        if list["nord"] is False and self.direction == "nord":
            return True
        if list["sud"] is False and self.direction == "sud":
            return True
        if list["ouest"] is False and self.direction == "ouest":
            return True
        if list["est"] is False and self.direction == "est":
            return True
        return False
 
    def rotate(self):
        if self.direction == "sud":
            image = pygame.transform.rotate(next(self.cycle), 270)
        elif self.direction == "nord":
            image = pygame.transform.rotate(next(self.cycle), 90)
        elif self.direction == "ouest":
            image = pygame.transform.rotate(next(self.cycle), 180)
        elif self.direction == "est":
            image = pygame.transform.rotate(next(self.cycle), 0)
        else:
            image = next(self.cycle)
        return image

    def draw_player(self, fenetre):
        y = self.row * self.cel_size
        x = self.col * self.cel_size
        y += self.decelage
        x += self.decelage
        image = self.rotate()
        fenetre.blit(image, (x, y))

    def deplacement(self):
        if self.direction == "sud":
            self.row += 0.05
        elif self.direction == "nord":
            self.row -= 0.05
        elif self.direction == "ouest":
            self.col -= 0.05
        elif self.direction == "est":
            self.col += 0.05

    def direction_deplacement(self, direction):
        if direction == pygame.K_UP:
            self.next_direction = "nord"
        elif direction == pygame.K_DOWN:
            self.next_direction = "sud"
        elif direction == pygame.K_LEFT:
            self.next_direction = "ouest"
        elif direction == pygame.K_RIGHT:
            self.next_direction = "est"

    def ajoute_super(self, maze: list[list[int]]):
        tailley = len(maze[0]) - 1
        taillex = len(maze) - 1
        self.lis_superpacgums.append((0, 0))
        self.lis_superpacgums.append((0, tailley))
        self.lis_superpacgums.append((taillex, 0))
        self.lis_superpacgums.append((taillex, tailley))     

    def afficher_superpacgums(self, fenetre):
        for row, col in self.lis_superpacgums:
            x = col * self.cel_size
            y = row * self.cel_size
            self.decalge = (self.cel_size - self.size_pacgums) / 2 
            fenetre.blit(self.ubuntu_logo,
                         (x + self.decalge, y + self.decalge))

    def ajoute_pacgums(self, fenetre, maze: list[list[int]],
                       case: tuple[int, int], pixel):
        if ((case[0], case[1]) not in self.lis_pacgums and maze[case[0]][case[1]] < 15):
            self.lis_pacgums.append((case[0], case[1]))
            fenetre.blit(self.pacgums, (pixel[0], pixel[1]))
            return True
        return False

    def papacgums(self, fenetre, nombre, mazze):
        tailley = len(mazze[0])
        taillex = len(mazze)
        
        while len(self.lis_pacgums) < nombre:
            row = random.randint(0, taillex - 1)
            col = random.randint(0, tailley - 1)
            self.ajoute_pacgums(fenetre, mazze, (row, col), (col * self.cel_size, row * self.cel_size))
    
    def afficher_pacgums(self, fenetre):
        for row, col in self.lis_pacgums:
            x = col * self.cel_size
            y = row * self.cel_size
            self.decalge = (self.cel_size - self.size_pacgums) / 2 
            fenetre.blit(self.pacgums, (x + self.decalge, y + self.decalge))

    def sup_pacgums(self):
        position_pacman = (round(self.row), round(self.col))
        if position_pacman in self.lis_pacgums:
            self.lis_pacgums.remove(position_pacman)
            self.nombre_pacgums_manger += 1
        if position_pacman in self.lis_superpacgums:
            self.lis_superpacgums.remove(position_pacman)


class Phantom():
    def __init__(self, row, col, cel_size, image):
        self.row = row
        self.col = col
        self.base_row = row
        self.base_col = col
        self.cel_size = cel_size
        self.phantom = pygame.transform.scale(image, (self.cel_size // 2, 
                                                      self.cel_size // 2))
        self.decalage = (self.cel_size - self.cel_size / 2) / 2 
        self.direction = "est"
        self.restart = False

    def draw_phantom(self, fenetre):
        y = self.row * self.cel_size
        x = self.col * self.cel_size
        y += self.decalage
        x += self.decalage
        fenetre.blit(self.phantom, (x, y))

    def update(self, mazze, row, col, check_bits, Player):
        if self.at_center():
            self.row = round(self.row)
            self.col = round(self.col)
            chemin = self.bfs(mazze, row, col, check_bits)
            if len(chemin) == 1:
                Player.restard = True
                return
            self.deplace_vers_joueur(chemin)
        self.deplacement()
    
    def at_center(self):
        return (abs(self.row - round(self.row)) < 0.001 and
                abs(self.col - round(self.col)) < 0.001)
    
    def deplace_vers_joueur(self, chemin):
        prochain_row, prochain_col = chemin[1]
        if prochain_row > self.row:
            self.direction = "sud"
        elif prochain_row < self.row:
            self.direction = "nord"
        elif prochain_col > self.col:
            self.direction = "ouest"
        elif prochain_col < self.col:
            self.direction = "est"
        if (self.row > prochain_row):
            if self.row - prochain_row <= 0.4:
                self.direction = None
        if (self.row < prochain_row):
            if prochain_row - self.row <= 0.4:
                self.direction = None
            self.deplacement()

    def deplacement(self):
        if self.direction == "sud":
            self.row += 0.05
        elif self.direction == "nord":
            self.row -= 0.05
        elif self.direction == "est":
            self.col -= 0.05
        elif self.direction == "ouest":
            self.col += 0.05
        return

    def get_neighbors(self, mazze, x, y, check_bits) -> list:
        if not (0 <= x < len(mazze) and 0 <= y < len(mazze[0])):
            return []
        murs = check_bits(mazze[x][y])
        deplacements = {
            "nord": (-1, 0),
            "sud": (1, 0),
            "est": (0, 1),
            "ouest": (0, -1),
            }
        voisins = []
        for (direction, (dx, dy)) in deplacements.items():
            if not murs[direction]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(mazze) and 0 <= ny < len(mazze[0]) :
                    voisins.append((nx, ny))
        return voisins
    
    def bfs(self, mazze, pacman_row, pacman_col, check_bits):
        queu = []
        dejavisit = []
        depart = (int(round(self.row)), int(round(self.col)))
        arive = (int(pacman_row), int(pacman_col))
        queu = [depart]
        dejavisit = [depart]
        dictparent = {}
        while queu:
            va = queu.pop(0)
            if va == arive:
                break
            diretiion = self.get_neighbors(mazze, va[0], va[1], check_bits)
            for (vx, vy) in diretiion:
                if (vx, vy) not in dejavisit:
                    dejavisit.append((vx, vy))
                    queu.append((vx, vy))
                    dictparent[(vx, vy)] = (va[0], va[1])
        chemin = []
        p = arive
        if arive != depart and arive not in dictparent:
            vide = []
            return vide
        while p != depart:
            chemin.append(p)
            p = dictparent[p]

        chemin.append(depart)
        chemin.reverse()

        return chemin


if __name__ == "__main__":
    pygame.init()
    re = render()
    re.extract_config()
    Maze = mazegenerator.MazeGenerator()
    Maze.generate()

    play = Player(re.size_cel, (len(re.mazze) // 2), len(re.mazze[0]) // 2,
                  "est")
    phantom1 = Phantom(0, 0, re.size_cel, pygame.image.load("image_phantom/1.png"))
    phantom2 = Phantom(0, len(re.mazze[0]) - 1, re.size_cel, pygame.image.load("image_phantom/2.png"))
    phantom3 = Phantom(len(re.mazze) - 1, 0, re.size_cel, pygame.image.load("image_phantom/3.png"))
    phantom4 = Phantom(len(re.mazze) - 1, len(re.mazze[0]) - 1, re.size_cel, pygame.image.load("image_phantom/4.png"))
    list_fantomes = [phantom1, phantom2, phantom3, phantom4]
    play.papacgums(re.fenetre, 207, re.mazze)
    play.ajoute_super(re.mazze)
    continuer = True
    clock = pygame.time.Clock()
    while continuer:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                if event.key == pygame.K_ESCAPE:
                    continuer = False
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or\
                        event.key == pygame.K_LEFT or\
                        event.key == pygame.K_RIGHT:
                    play.direction_deplacement(event.key)
        play.update(re.mazze, re.check_bits)
        re.cremaze()
        play.afficher_pacgums(re.fenetre)
        play.afficher_superpacgums(re.fenetre)

        for phanto in list_fantomes:
            phanto.draw_phantom(re.fenetre)
            phanto.update(re.mazze, round(play.row), round(play.col), re.check_bits, play)
            if play.restard:
                for phanto in list_fantomes:
                    phanto.row = phanto.base_row
                    phanto.col = phanto.base_col
                play.row = play.base_row
                play.col = play.base_col
                play.restard = False
        play.sup_pacgums()
        play.draw_player(re.fenetre)
        pygame.display.flip()
    pygame.quit()

    # def drawcyrcle(self, fenetre, centre_x, centre_y, rayon, couleur):
    #     for y in range(centre_y - rayon, centre_y + rayon):
    #         for x in range(centre_x - rayon, centre_x + rayon):
    #             if (((x - centre_x)**2 + (y - centre_y) ** 2) <= rayon ** 2):
    #                 fenetre.set_at((x, y), couleur)
    #     return fenetre


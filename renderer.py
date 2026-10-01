import mazegenerator
import pygame
from itertools import cycle
import time


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
            result["sud"] = True
        if de & 4:
            result["est"] = True
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
            "sud": (c - w, 0, w, c),
            "est": (0, c - w, c, w),
            "ouest": (0, 0, w, c),
            }

    def draw(self, fenetre, x, y, largeur, hauteur, couleur):
        for dy in range(hauteur):
            for dx in range(largeur):
                fenetre.set_at((x + dx, y + dy), couleur)
        return fenetre

    def cremaze(self):
        print(self.size_cel)
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
        self.cel_size = size_cel
        self.direction = direction_de_depart
        self.mouth_open = False

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

    def draw_player(self, fenetre):
        y = self.row * self.cel_size
        x = self.col * self.cel_size
        y += self.decelage
        x += self.decelage
        image = next(self.cycle)
        print(image)
        fenetre.blit(image, (x, y))

    def deplacement(self):
        if self.direction == "nord":
            self.row += 0.05
        elif self.direction == "sud":
            self.row -= 0.05
        elif self.direction == "ouest":
            self.col -= 0.05
        elif self.direction == "est":
            self.col += 0.05

    def direction_deplacement(self, direction):
        if direction == pygame.K_UP:
            self.direction = "sud"
        elif direction == pygame.K_DOWN:
            self.direction = "nord"
        elif direction == pygame.K_LEFT:
            self.direction = "ouest"
        elif direction == pygame.K_RIGHT:
            self.direction = "est"
        # self.deplacement()


if __name__ == "__main__":
    re = render()
    re.extract_config()
    Maze = mazegenerator.MazeGenerator()
    Maze.generate()
    play = Player(re.size_cel, (len(re.mazze) // 2), len(re.mazze[0]) // 2,
                  True)
    pygame.init()
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
        play.deplacement()
        re.cremaze()
        play.draw_player(re.fenetre)
        pygame.display.flip()
    pygame.quit()

    # def drawcyrcle(self, fenetre, centre_x, centre_y, rayon, couleur):
    #     for y in range(centre_y - rayon, centre_y + rayon):
    #         for x in range(centre_x - rayon, centre_x + rayon):
    #             if (((x - centre_x)**2 + (y - centre_y) ** 2) <= rayon ** 2):
    #                 fenetre.set_at((x, y), couleur)
    #     return fenetre
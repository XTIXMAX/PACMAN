    # def bfs(self):
    # queu = []
    # dejavisit = []
    # depart = tuple(map(int, config["ENTRY"].split(",")))
    # arive = tuple(map(int, config["EXIT"].split(",")))
    # queu = [depart]
    # dejavisit = [depart]
    # dictparent = {}
    # while queu:
    #     va = queu.pop(0)
    #     if va == arive:
    #         break
    #     diretiion = self.get_neighbors(va[0], va[1])
    #     for ((vx, vy), direct) in diretiion:
    #         if not self.cells[va[0]][va[1]] & direct:
    #             if (0 <= vx < self.width and 0 <= vy < self.height and
    #                 (vx, vy) not in dejavisit and
    #                     (vx, vy) not in self.log):
    #                 dejavisit.append((vx, vy))
    #                 queu.append((vx, vy))
    #                 dictparent[(vx, vy)] = (va[0], va[1])
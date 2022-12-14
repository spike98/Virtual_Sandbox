import math
from types import new_class
from blocks import BucketBlock, SandBlock, WaterBlock, StoneBlock

class TileMap():
    def __init__(self, screen_width, screen_height, particle_size):
        self.width = int(screen_width/particle_size)
        self.height = int(screen_height/particle_size)
        self.map = [[None for i in range(self.height)] for j in range(self.width)]
        self.moves = None

    def update(self, mouse_pos, block_to_be_drawn, old_bucket_vertices, new_bucket_vertices):
        # apply forces on blocks and move them
        # draw bucket
        # add new blocks
        # calculate possible changes for blocks
        # update blocks

        print("at top of update", self.count_tiles())

        if (new_bucket_vertices):
            new_bucket_tiles = self.get_line_points(new_bucket_vertices[0], new_bucket_vertices[1]) + self.get_line_points(new_bucket_vertices[1], new_bucket_vertices[2]) + self.get_line_points(new_bucket_vertices[2], new_bucket_vertices[3])
        else:
            new_bucket_tiles = None
        
        if (old_bucket_vertices):
            old_bucket_tiles = self.get_line_points(old_bucket_vertices[0], old_bucket_vertices[1]) + self.get_line_points(old_bucket_vertices[1], old_bucket_vertices[2]) + self.get_line_points(old_bucket_vertices[2], old_bucket_vertices[3])

            # remove old bucket tiles from map
            for i, array in enumerate(self.map):
                for j, tile in enumerate(array):
                    #if not self.point_in_bounds(tile): continue
                    if (tile != None and tile.__class__.__name__ == "BucketBlock"):
                        self.map[i][j] = None
        else:
            old_bucket_tiles = None

        print("after calculating bucket tiles", self.count_tiles())

        moved_tiles = self.get_moved_tiles(old_bucket_tiles, new_bucket_tiles)

        if (old_bucket_vertices != None and new_bucket_vertices != None):
            # need to also get point change for changes in angles
            fx, fy = self.get_point_change(old_bucket_vertices[0], new_bucket_vertices[0])
        else:
            fx, fy = 0, 0

        print("after calculating fx", self.count_tiles())

        # apply forces to tiles moved by bucket
        if moved_tiles:
            for point in moved_tiles:
                if fy == fx == 0: continue
                new_point = self.resolve_forces(point, fx, fy, new_bucket_tiles)

                self.map[new_point[0]][new_point[1]] = self.map[point[0]][point[1]]

                self.map[new_point[0]][new_point[1]].update_position(new_point)
                self.map[point[0]][point[1]] = None
        
        print('after resolving forces', self.count_tiles())

        if (new_bucket_tiles):
            # add bucket blocks to tilemap
            for point in new_bucket_tiles:
                if (not self.point_in_bounds(point)): continue

                # sand is being deleted by bucket
                if self.map[point[0]][point[1]] != None: 
                    # print(self.map[point[0]][point[1]]) 
                    continue
                # print(self.map[point[0]][point[1]]) 

                self.map[point[0]][point[1]] = BucketBlock(point[0], point[1])

        print('after bucket block', self.count_tiles())

        if (mouse_pos != None):
            line_points = [mouse_pos[1]] if mouse_pos[0] == None else self.get_line_points(mouse_pos[0], mouse_pos[1])

            for point in line_points:
                if self.map[point[0]][point[1]] == None:
                    if (block_to_be_drawn == 1):
                        self.map[point[0]][point[1]] = SandBlock(point[0], point[1])
                    elif (block_to_be_drawn == 2):
                        self.map[point[0]][point[1]] = WaterBlock(point[0], point[1])
                    elif (block_to_be_drawn == 3):
                        self.map[point[0]][point[1]] = StoneBlock(point[0], point[1])

        # clear array
        self.moves = []

        # calculate desired move for each tile
        for row, array in enumerate(self.map):
            for column, tile in enumerate(array):
                if tile != None: 
                    new_point = tile.get_move(self.map)
                    
                    # if immovable object
                    if new_point == None: continue
                    self.moves.append(((row, column), new_point),)

        # sort moves list by destination; shuffle results
        if self.moves:
            # random.shuffle(self.moves.sort(key = lambda x: x[1]))
            self.moves.sort(key = lambda x: x[1])

            curr_move = None

            for move in self.moves:
                # skip if position is filled
                if (move[1] == curr_move): continue

                old_point = move[0]
                new_point = move[1]

                old_tile = self.map[old_point[0]][old_point[1]]

                if self.map[new_point[0]][new_point[1]] == None:
                    old_tile.update_position((new_point[0], new_point[1]))
                    self.map[new_point[0]][new_point[1]] = old_tile
                    self.map[old_point[0]][old_point[1]] = None
                    curr_move = new_point
                elif self.map[new_point[0]][new_point[1]].density < old_tile.density:
                    # density physics
                    less_dense_block = self.map[new_point[0]][new_point[1]]
                    self.map[new_point[0]][new_point[1]] = old_tile

                    i = 1

                    # while (new_point[1] - i > 0 and self.map[new_point[0]][new_point[1] - i] != None):
                    #     i += 1

                    self.map[old_point[0]][old_point[1]] = less_dense_block
                    
                    old_tile.update_position((new_point[0], new_point[1]))
                    less_dense_block.update_position((new_point[0], new_point[1] - i))
        print("after moving everything", self.count_tiles())
        print("--------------------------------------")

    def clear(self):
        print("clear")
        self.map = [[None for i in range(self.height)] for j in range(self.width)]

    def point_in_bounds(self, point):
        return point[0] >= 0 and point[0] < self.width and point[1] >= 0 and point[1] < self.height

    @staticmethod
    def get_line_points(naught, final):
        # 20, 20, 20, 10
        distance = math.dist(naught, final)
        
        if distance == 0: return [final]

        dx = (final[0] - naught[0]) / distance
        dy = (final[1] - naught[1]) / distance

        points = []

        start_x, end_x = (naught[0], final[0])
        start_y, end_y = (naught[1], final[1])

        for i in range(math.ceil(distance)):
            points.append((math.floor(start_x), math.floor(start_y)))
            start_x += dx
            start_y += dy
        
        return points

    @staticmethod
    def get_point_change(naught, final):
        fx = final[0] - naught[0]
        fy = final[1] - naught[1]
        return fx, fy

    def get_moved_tiles(self, old_bucket_tiles, new_bucket_tiles):
        if new_bucket_tiles == None: return

        moved_tiles = []

        # bucket tiles can be between 27 and 28 tiles for some reason
        for i in range(28):
            if old_bucket_tiles == None:
                line = new_bucket_tiles
            else:
                line = self.get_line_points(old_bucket_tiles[i], new_bucket_tiles[i])

            for point in line:
                if (self.point_in_bounds(point) and self.map[point[0]][point[1]] != None and point not in moved_tiles): 
                    moved_tiles.append(point)
        
        return moved_tiles

    def add_new_block(self, mouse_pos, block_type):
        pass

    def resolve_forces(self, point, fx, fy, new_bucket_tiles):
        if (fx == fy == 0): return point
        x = point[0]
        y = point[1]

        sign = lambda x: x and (1, -1)[x<0]

        dx = sign(fx)
        dy = sign(fy)

        if (x + fx > 0 and x + fx < self.width - 1):
            x += fx

        if (y + fy > 0 and y + fy < self.height - 1):
            y += fy

        loop_num = 0

        while (self.map[x][y] != None or (x,y) in new_bucket_tiles):
            loop_num += 1

            if (loop_num > 10000):
                # prevents occasional infinite loop
                # block will be overwritten and deleted
                break
            # elif (x + fx <= 0 or x + fx >= self.width):
            #     if (y > 1):
            #         y -= 1
            #     else:
            #         y += 1
            # elif (y + fy >= self.height or y + fy <= 0):
            #     if (x > 1):
            #         x -= 1
            #     else:
            #         x += 1
            elif (self.point_in_bounds((x + dx, y + dy))):
                x += dx
                y += dy
            elif (y > 2):
                y -= 1
            elif (x + 1 < self.width - 1):
                x += 1
            elif (x - 1 > 0):
                x -= 1
            else: 
                break
                
                
        # print((x,y) in new_bucket_tiles)
        return(x,y)

    def count_tiles(self):
        count = 0
        for array in self.map:
            for tile in array:
                if (tile != None and tile.__class__.__name__ != "BucketBlock"):
                    count += 1
        
        return count
#!/usr/bin/env  python3

import pygame as pg
import os
import random
import time

class Block(pg.Rect):
  '''
  This class include color and rectangle information
  that consist of every object of this game.
  '''

  def __init__(self, color, *args, **kwargs):
    self.color = color
    super().__init__(*args, **kwargs)


# screen is divide by each Panel which perform diffrent function
class Panel(Block):
  '''Just add edge drawing function'''
    
  def __init__(self, window, color, *args, **kwargs):
    self.screen = window
    super().__init__(color, *args, **kwargs)

  def draw_edge(self, width):
    pg.draw.rect(self.screen, self.color, self, width)


# main game panel 
class GamePanel(Panel):
  '''
  Main game panel has 15 x 25 size block map which each block is 
  consist of exist bit and color variable
  '''
  size = (15,25)
  base = (200,200)

  def __init__(self, window, color):
    super().__init__(window, color, GamePanel.base, (GamePanel.size[0]*
          Unit.unit_size, GamePanel.size[1]*Unit.unit_size))
    # 15 X 25 map for represent each block is filled with specified color
    self.blockmap = \
      [[[0, Game.black] for j in range(GamePanel.size[0])]\
          for i in range(GamePanel.size[1])]
    # this is for identify unit
    self.unit_number = 0
    # this variable represent current unit's position
    self.unit_on_blockmap = []
    # we should track of current unit
    self.current_unit = None
      

  def spawn(self, ):
    '''
    Check if block is already there
    if block is not there then add it to the blockmap and locate the 
    block at the top middle of the game panel
    '''

    self.get_next_unit()
    self.unit_number+=1
     
    top_middle = GamePanel.size[0]//2 - self.current_unit.center_block.x
    for block in self.current_unit.block_list:
      # position to the top middle
      block.x += top_middle
      #  if block is there then game is over
      if self.blockmap[block.y][block.x][0] != 0:
        return Game.exit_code  

    # drawing on the block map
    self.unit_on_blockmap = self.get_unit_map(self.current_unit)
    self.mask_unit_on_blockmap(self.unit_on_blockmap, 1, 
      self.current_unit.color)


  def move_unit(self, direction):
    '''
    Get the next position on the block map and validate the next 
    location, mark the new location on the block map
    '''
      # move current unit to one block downward 
      # event key check --> implement unit movement by key press
      # and deformation
      # check many conditions like unit hits the stacked block,
      # the unit reach the outside of the boundary, 
      # check every line in the tetris block and if every line is 
      # filled then clear the line and change score
   
    # when the direction is up, get the rotated unit's coordinate list
    if direction == "UP":
      center_point = self.unit_on_blockmap[2]
      tmp_map = self.rotate_unit(self.unit_on_blockmap, center_point)
    else:
    # when the direction is other, get the shifted unit's coordinate list
      tmp_map = self.shift_unit(self.unit_on_blockmap, direction)

    for x,y in tmp_map:
      # just check the newly positioned block
      if (x,y) in self.unit_on_blockmap:  
        continue

      # boundary check
      elif direction != "DOWN":
        if x >= GamePanel.size[0] or x < 0 or y < 0 \
          or self.blockmap[y][x][0] == 1:
          return

      # when the direction is Downward check if new block position fills 
      # the gap or if there's no place to position the new block
      elif direction == "DOWN":
        if y== GamePanel.size[1] or self.blockmap[y][x][0] == 1:
          score_up = self.check_line_filled()
          del self.current_unit
          if self.spawn() == Game.exit_code:
            return Game.exit_code
          return score_up
          
    # erase on block map and remap unit to new location
    self.mask_unit_on_blockmap(self.unit_on_blockmap, 0, Game.black)   
    self.mask_unit_on_blockmap(tmp_map, 1, self.current_unit.color)
    self.unit_on_blockmap = tmp_map
    

  # get the new position list of shifted unit
  def shift_unit(self, unit_map, direction):
    new_pos_map = []
    if direction == 'RIGHT':
      for pos in unit_map:
        new_pos_map.append((pos[0] + 1, pos[1]))
    elif direction == 'LEFT':
      for pos in unit_map:
        new_pos_map.append((pos[0] - 1, pos[1]))
    elif direction == 'DOWN':
      for pos in unit_map:
        new_pos_map.append((pos[0], pos[1] + 1))

    return new_pos_map
    
  # get the new postion list of rotated unit
  def rotate_unit(self, unit_map, center_point):
    # rotation matrix [ cos, -sin ] (x)  
    #                 [ sin,  cos ] (y)
    # 90 degree rotate --> (-y,x)

    new_pos_map = [] 
     
    x_back, y_back = center_point[0], center_point[1]
    for pos in unit_map:
      new_x = tmp = pos[0] - x_back
      new_y = pos[1] - y_back
      new_x = -new_y
      new_y = tmp 
      new_pos_map.append((new_x + x_back, new_y + y_back))

    return new_pos_map

  # get next unit 
  def get_next_unit(self, ):
    self.current_unit = NextUnitPanel.next_unit 
    NextUnitPanel.set_next_unit()

  # return the unit's coordinate on the block map
  def get_unit_map(self, unit):
    return [(block.x,block.y) for block in unit.block_list]
      
  # mark the unit's position on the block map
  def mask_unit_on_blockmap(self, maplist, val, color):
    for x,y in maplist:
      self.blockmap[y][x][0],self.blockmap[y][x][1] = val,color

  # drawing contants of the block map on the game panel
  def draw_game_panel(self,):
    for row, line in enumerate(self.blockmap):  
      for col, rect in enumerate(line):
        # draw block map's contant
        pg.draw.rect(self.screen, rect[1], pg.Rect((GamePanel.base[0] +
          Unit.unit_size*col, GamePanel.base[1] + Unit.unit_size*row),
          (Unit.unit_size, Unit.unit_size)))
        # draw grid
        pg.draw.rect(self.screen, Game.grey, pg.Rect((GamePanel.base[0] +
          Unit.unit_size*col + 1, GamePanel.base[1] + Unit.unit_size*row + 1),
          (Unit.unit_size-1, Unit.unit_size-1)), 2)
    
  # check if all block of each line is filled 
  def check_line_filled(self, ):
    count = 0
    for i, line in enumerate(self.blockmap):
      # get the list of fill bit
      is_filled = zip(*line).__next__()
      if 0 not in is_filled:
        # pop the filled line and push it to the first line 
        self.blockmap.insert(0,self.blockmap.pop(i))
        # cover it with black and unmask
        self.mask_unit_on_blockmap([(x,0) for x in range(GamePanel.size[0])]\
          , 0, Game.black)
        count+=1
        Game.bubble_sound.play()
    # as many line you fill with at the same time 
    return 10*pow(count,3)


  # debuging purpose
  def print_blockmap(self, ):
    for line in self.blockmap:
      print(''.join(map(str, zip(*line).__next__())))
    print('----------------------------------------------------')


class NextUnitPanel(Panel):
  '''
  This panel shows next unit on the panel
  '''

  size = (6,6)
  base = (900,400)
  next_unit = None

  def __init__(self, window, color):
    super().__init__(window, color, NextUnitPanel.base, 
      (NextUnitPanel.size[0]*Unit.unit_size, NextUnitPanel.size[1]\
        *Unit.unit_size))

  # set the randomly choose unit 
  @staticmethod
  def set_next_unit():
    _, NextUnitPanel.next_unit = Unit.random_unit()  

  # drawing on the middle of the panel
  def draw_unit_in_the_middle(self, ):
    unit = self.next_unit
    tmp = pg.Rect((unit.center_block.x*Unit.unit_size, 
        unit.center_block.y*Unit.unit_size), (Unit.unit_size,Unit.unit_size))

    for block in unit.block_list:
      pg.draw.rect(self.screen, block.color, pg.Rect((self.centerx - 
          tmp.centerx + block.x*Unit.unit_size, self.centery - 
          tmp.centery + block.y*Unit.unit_size),(Unit.unit_size-1,\
            Unit.unit_size-1)))


class ScorePanel(Panel):
  '''
  This panel shows score and level
  '''
  size = (7,7)
  base = (900,0)

  def __init__(self, window, text_color, fontsize):
    self.rect = pg.Rect(ScorePanel.base, (ScorePanel.size[0]*Unit.unit_size,
        ScorePanel.size[1]*Unit.unit_size))
    super().__init__(window, Game.black, self.rect)
    self.font = pg.font.SysFont("comicsansms", GamePanel.size[0]*fontsize)
    self.textcolor = text_color

  # draw score and level on the panel 
  def draw_score_and_level(self, score, level):
    self.scoretext = self.font.render("Score: {}".format(score), True, 
      self.textcolor)
    self.leveltext = self.font.render("Level: {}".format(level), True, 
      self.textcolor)
    pg.draw.rect(self.screen, Game.black, self.rect)

     
    self.screen.blit(self.scoretext, ( (self.rect.width
      - self.scoretext.get_width())//2 + ScorePanel.base[0], (self.rect.height
      - self.scoretext.get_height())//2 + ScorePanel.base[1] ) )

    self.screen.blit(self.leveltext, ( (self.rect.width
      - self.leveltext.get_width())//2 + ScorePanel.base[0], (self.rect.height
      - self.leveltext.get_height())//2 + ScorePanel.base[1] + 60) )



class Unit(object):
  '''
  Unit object is consist of block object.
  We should collect the center point coordinate's to rotate unit
  The 3'rd coordinate of each unit has a center position
  '''
  unit_list = {}
  unit_size = 30

  def __init__(self, name, coord_list, color):
    self.name = name
    self.block_list = []
    self.color = color
    for i,coord in enumerate(coord_list):
      block = Block(self.color, coord, (Unit.unit_size, Unit.unit_size))
      # center position
      if i == 2:
        self.center_block = block
      self.block_list.append(block)
    Unit.unit_list[self.name] = self


  @classmethod
  def random_unit(cls, ):
    name,unit = random.choice(list(cls.unit_list.items()))
    return name,unit



class Game(object):
  '''Overall game settings.'''
  
  # color
  skyblue     =    (0,255,255)
  purple      =    (127,0,255)
  green       =    (0,255,0)
  yellow      =    (255,255,0)
  orange      =    (255,128,0)
  red         =    (255,0,0)
  blue        =    (0,128,255)
  light_green =    (128,255,0)
  indigo      =    (0,0,255)
  pink        =    (255,0,127)
  magenta     =    (255,0,255)
  grey        =    (128,128,128)
  white       =    (255,255,255)
  black       =    (0,0,0)

  # static variables
  screen_width,screen_height = 1200,1000
  level_time_interval = 30
  key_press_interval = 0.07
  bgm = 'Tetris.mp3'
  exit_code = -1
  # this variable is for preventing window appears right next to the
  # edge of the screen 
  os.environ['SDL_VIDEO_WINDOW_POS'] = '{} {}'.format(300,100)
  pg.mixer.init()
  bubble_sound = pg.mixer.Sound('bubble.wav')
  pg.mixer.music.load(bgm)
  pg.mixer.music.play(-1)

  def __init__(self, ):
    pg.init() 
    pg.display.set_caption('Tetris')
    self.clock = pg.time.Clock()  
    # it can change the level as time goes by 
    self.playtime = time.time()

    self.screen = pg.display.set_mode((self.screen_width, self.screen_height))  
    self.gamespeed = 1000
    self.level = 0
    self.score = 0
    # these are for measure the time key pressed
    self.pressed_right, self.pressed_left, self.pressed_down \
          = False, False, False
    self.pressed_right_time, self.pressed_left_time, self.pressed_down_time \
      = 0,0,0
    # current unit is moving downward automatically
    pg.time.set_timer(pg.USEREVENT, self.gamespeed)

    # each unit's names are represented by these symbol 
    # middle coordinate of block list should be the center of unit
    # initialize units
    Unit('j', [(0,0), (0,1), (0,2), (0,3), (1,3)], Game.skyblue)
    Unit('U', [(0,0), (2,0), (1,1), (0,1), (2,1)], Game.purple)
    Unit('+', [(1,0), (0,1), (1,1), (2,1), (1,2)], Game.green)
    Unit('z', [(0,0), (1,0), (2,0), (2,1), (3,1)], Game.yellow)
    Unit('b', [(0,0), (0,2), (0,1), (1,1), (1,2)], Game.orange)
    Unit('l', [(0,0), (0,1), (0,2), (0,3), (0,4)], Game.red)
    Unit('w', [(1,0), (2,0), (1,1), (0,1), (0,2)], Game.blue)
    Unit('Y', [(1,0), (0,1), (1,1), (2,1), (3,1)], Game.light_green)
    Unit('Z', [(0,0), (0,1), (1,1), (2,1), (2,2)], Game.indigo)
    Unit('y', [(1,0), (0,1), (1,1), (2,1), (2,2)], Game.pink)
    Unit('T', [(0,0), (1,0), (1,1), (2,0), (1,2)], Game.magenta)
    Unit('L', [(0,0), (0,1), (0,2), (1,2), (2,2)], Game.white)
  
    # initialize each panel
    self.score_panel = ScorePanel(self.screen, self.purple, 4)
    self.next_unit_panel = NextUnitPanel(self.screen, self.orange)
    self.next_unit_panel.set_next_unit()
    self.game_panel = GamePanel(self.screen, self.skyblue)
    # position the first unit on top middle 
    self.game_panel.spawn()


  def run(self, ):
    while True:
      '''Actual game loop'''


      # adjust FPS 
      self.clock.tick(120)
      self.screen.fill((0,0,0))

      # as time goes by, level is getting high until it reach level10 
      # and also speed is getting faster
      new_time = time.time()
      if new_time - self.playtime > self.level_time_interval:
        if self.level >= 10:
          pass
        else:
          self.level+=1  
          self.gamespeed -= 90
          pg.time.set_timer(pg.USEREVENT, self.gamespeed)
          self.playtime = new_time
        
    
      # drawing the panels and panels edge
      self.game_panel.draw_edge(8)
      self.game_panel.draw_game_panel()
      self.next_unit_panel.draw_edge(5)
      self.next_unit_panel.draw_unit_in_the_middle()
      self.score_panel.draw_score_and_level(self.score, self.level)

      if self.key_check() == self.exit_code:
        return
      pg.display.flip()

  def key_check(self, ):
    '''
    Key event handling
    
    Measuring the time between key press down and key up
    and makes unit keep moving while key down
    
    '''

    for event in pg.event.get(): 
      self.exit_check(event) 
      
      # toggle the key pressed flag
      if event.type == pg.KEYDOWN:
        if event.key == pg.K_RIGHT:
          self.pressed_right = True
          self.pressed_right_time = time.time()

        elif event.key == pg.K_LEFT:
          self.pressed_left  = True
          self.pressed_left_time = time.time()

        elif event.key == pg.K_UP:
          val = self.game_panel.move_unit("UP")
          if val == self.exit_code: return self.exit_code
          elif val != None: self.score += val

        elif event.key == pg.K_DOWN:
          self.pressed_down  = True
          self.pressed_down_time = time.time()

        elif event.key == pg.K_SPACE:
          # separate unit 
          num = self.game_panel.unit_number
          while self.game_panel.unit_number == num:
            val = self.game_panel.move_unit("DOWN")
            if val == self.exit_code: return self.exit_code
            elif val != None: self.score += val

      elif event.type == pg.KEYUP:
        if event.key == pg.K_RIGHT:
          self.pressed_right_time = time.time()
          self.pressed_right = False

        elif event.key == pg.K_LEFT:
          self.pressed_left_time = time.time()
          self.pressed_left  = False

        elif event.key == pg.K_DOWN:
          self.pressed_down_time = time.time()
          self.pressed_down  = False

      elif event.type == pg.USEREVENT:
          val = self.game_panel.move_unit("DOWN")
          if val == self.exit_code: return self.exit_code
          elif val != None: self.score += val


    time_tmp = time.time()
    if self.pressed_right and time_tmp - self.pressed_right_time >\
        self.key_press_interval:
      val = self.game_panel.move_unit("RIGHT")
      if val == self.exit_code: return self.exit_code
      elif val != None: self.score += val
      self.pressed_right_time = time.time()

    if self.pressed_left and time_tmp - self.pressed_left_time >\
        self.key_press_interval:
      val = self.game_panel.move_unit("LEFT")
      if val == self.exit_code: return self.exit_code
      elif val != None: self.score += val
      self.pressed_left_time = time.time()

    if self.pressed_down and time_tmp - self.pressed_down_time >\
        self.key_press_interval:
      val = self.game_panel.move_unit("DOWN")
      if val == self.exit_code: return self.exit_code
      elif val != None: self.score += val
      self.pressed_down_time = time.time()


  # quit the game if one of esc or alt+F4 or exit button is pressed 
  @staticmethod
  def exit_check(event):
    pressed_keys = pg.key.get_pressed() 
    alt_pressed = pressed_keys[pg.K_LALT] or pressed_keys[pg.K_RALT]
    x_button = event.type == pg.QUIT
    altF4 = alt_pressed and event.type == pg.KEYDOWN and event.key == pg.K_F4
    escape = event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
    if x_button or altF4 or escape:
      exit()
    

  # suspend game while waiting for Space button to restart game
  def hold(self, ):
    font = pg.font.SysFont("comicsansms", 96)
    text = font.render("Press SPACE Button To Restart", True, self.green) 
    while True:
      self.clock.tick(120)
      self.screen.blit(text, ((self.screen_width - text.get_width())//2,
        (self.screen_height - text.get_height())//2))
      pg.display.flip()
      for event in pg.event.get():
        self.exit_check(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
          return
    


if __name__ == '__main__':
  while True:
    game = Game()
    game.run()
    game.hold()

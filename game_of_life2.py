import pygame
import random
#import sys
#import os

class Cell(object):
    def __init__(self,color):         
        self.age = 0
        self.color = color
        self.sleep = False

class Game_state(object):
    def __init__(self,location,screen,text,init_value):
        self.text = text    
        self.location = location
        self.screen = screen
        self.update_drawing(str(init_value))
    
    def update_drawing(self,new_value):
        to_show = self.text + " :"  + str(new_value)    
        self.value = new_value       
        pygame.draw.rect(self.screen,(0,0,0),(self.location[0],self.location[1],150,50))  
        font = pygame.font.SysFont(None, 30)        
        img = font.render(to_show, True, (100,100,100))       
        self.screen.blit(img, self.location)

class Button(object):
    def __init__(self,screen,rect,color,text,callback,*args):
        self.rect = rect
        self.text = text
        self.color = color
        self.callback = callback   
        self.args = args
        self.img = None   
        self.screen = screen
        self.highlighted = False

    def set_text(self,text):
        self.text = text
        self.set_highlighted(False)         

    def draw_text(self):          
        font = pygame.font.SysFont(None, 50)        
        img = font.render(self.text, True, (100,100,100))       
        self.screen.blit(img, self.rect.topleft)

    def set_highlighted(self,val):        
        if val:
            new_color_list = list(self.color)
            for index, item in enumerate(new_color_list):
                new_color_list[index] = item + 20
            pygame.draw.rect(self.screen,tuple(new_color_list),self.rect)  
        else:
            pygame.draw.rect(self.screen,self.color,self.rect)         
        self.highlighted = val
        self.draw_text()

    def draw(self):    
        self.set_text(self.text)

    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):                
                self.callback(*self.args)
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(pygame.mouse.get_pos()):  
                if not self.highlighted:
                    self.set_highlighted(True)
            else:
                if self.highlighted:
                    self.set_highlighted(False)
            
class GameOfLife(object): 
    def __init__(self,screen,board_pixel_size,init_square_size): 

        self.max_pixel = board_pixel_size        
        self.square_size = init_square_size
        self.board_size = (int)(self.max_pixel/self.square_size)-1
        self.draw = True
        self.shape = {}
        self.to_kill = set()       
        self.speed = 15
        self.mode = 0  
        self.construct_mode = 0
        self.mouse_clicked = False   
        self.screen = screen   
        self.iteration_num = 0  
        self.dist = 0.85
        self.buttons = []
        self.game_states = {}
        self.is_done = False
        self.construct_direction = 0

        self.init_buttons()
        self.draw_states()
        self.draw_legend()
        
        self.randomize()    
        self.draw_board()
 
    def delete_board(self):
        pygame.draw.rect(self.screen,(0,0,0),(0,0,self.max_pixel,self.max_pixel))         
    
    def init_buttons(self):   
        buttons_location = self.max_pixel + 200  
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,50,150,50)),(200,150,50),"New",self.randomize_board))       
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,100,150,50)),(150,150,150),"Stop/Go",self.stop_resume))        
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,150,80,50)),(150,150,50),"+",self.change_size,1))        
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 100,150,80,50)),(100,150,150),"-",self.change_size,-1))
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,200,80,50)),(150,150,50),"<<",self.change_game_speed,3))      
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 100,200,80,50)),(100,150,150),">>",self.change_game_speed,-3))
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,250,150,50)),(200,150,50),"Clear",self.clear_shape))       
       
        for i in range(4):
            self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + i*30,300,30,50)),(100,200-20*i,50+20*i),str(i),self.setmode,i))

        for i in range(6):
            self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 30*i,350,30,50)),(100+20*i,200-20*i,50),str(i),self.set_construct_mode,i))
       
        for i in range(4):
            self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 30*i,400,30,50)),(100+20*i,200-20*i,50),str(i),self.set_construct_direction,i))
     
        for button in self.buttons:
            button.draw() 

    def draw_states(self):
        states_location = self.max_pixel + 50
        speed_state = Game_state((states_location,215),self.screen,"Speed",self.speed)
        self.game_states["Speed"] = speed_state
        board_size_state = Game_state((states_location,165),self.screen,"Size",self.speed)
        self.game_states["Size"] = board_size_state
        pause_state = Game_state((states_location,115),self.screen,"State","Go")
        self.game_states["State"] = pause_state
        mode_state = Game_state((states_location,300),self.screen,"Mode",self.mode)
        self.game_states["Mode"] = mode_state

        construct_mode_state = Game_state((states_location,350),self.screen,"Shape",0)
        self.game_states["Shape"] = construct_mode_state

        direction_state = Game_state((states_location,400),self.screen,"Direction",0)
        self.game_states["Direction"] = direction_state

        total_cells_state = Game_state((50,self.max_pixel + 20),self.screen,"Total","")
        self.game_states["Total"] = total_cells_state
        active_cells_state = Game_state((50,self.max_pixel + 60),self.screen,"Active","")
        self.game_states["Active"] = active_cells_state
        self.update_shape_data()

    def draw_desc(self,loc,dict,name):
        text = name + ": " + str(dict)        
        font = pygame.font.SysFont(None, 25)        
        img = font.render(text, True, (100,200,100))       
        self.screen.blit(img, loc)

    def draw_legend(self):        

        loc = (300,self.max_pixel + 20)
        legend_text = "Legend:"
        font = pygame.font.SysFont(None, 25)        
        img = font.render(legend_text, True, (200,100,100))       
        self.screen.blit(img, (loc[0],loc[1]))  

        modes = {0:"Game of Life",1:"Game of life++",2:"Chaos-1",3:"War-zone"}
        directions = {0:"0",1:"90",2:"180",3:"270"}
        shapes = {0:"Cell",1:"Box",2:"Glider",3:"Glider Fleet",4:"Spaceship1",5:"Spaceship2"}

        self.draw_desc((loc[0], loc[1] + 40),modes,"Modes of board") 
        self.draw_desc((loc[0], loc[1] + 70),shapes,"Shapes to add") 
        self.draw_desc((loc[0], loc[1] + 100),directions,"Directions of adding shape") 

    def set_construct_direction(self,cm):
        self.construct_direction = cm
        self.game_states["Direction"].update_drawing(cm)

    def set_construct_mode(self,cm):
        self.construct_mode = cm
        self.game_states["Shape"].update_drawing(cm)

    def update_shape_data(self):
        self.game_states["Total"].update_drawing(len(self.shape))         
        active_cells_count = 0
        for value in self.shape.values():
            if not value.sleep:
                active_cells_count += 1
        self.game_states["Active"].update_drawing(active_cells_count)

    def change_game_speed(self,factor):
        new_speed = (int)(self.speed + factor)
        if new_speed > 60 or new_speed < 5:
            return
        else:
            self.speed = new_speed
            self.game_states["Speed"].update_drawing(self.speed)    

    def change_size(self,factor):       
        new_square_size = self.square_size + factor
        if new_square_size > 100 or new_square_size < 1:
            return
        self.square_size = new_square_size        
        self.board_size = (int)(self.max_pixel/self.square_size)-1
        self.to_kill.clear()
        if factor > 0:       
            to_delete = []
            for item in self.shape:
                if item[0] >= self.board_size or item[1] >= self.board_size:
                    to_delete.append(item)
            for item in to_delete:
                self.shape.pop(item)

        for value in self.shape.values():
            value.age = 0

        self.game_states["Size"].update_drawing(self.board_size) 
        self.delete_board()                    
        self.draw_board()

    def clear_shape(self):
        self.shape.clear()
        self.delete_board()
   
    def stop_resume(self):
        self.draw = not self.draw 
        if self.draw:
            self.game_states["State"].update_drawing("Go")
        else:
            self.game_states["State"].update_drawing("Stop")

    def randomize_board(self):
        self.randomize()
        self.delete_board()
        self.draw_board()

    def randomize(self):        
        self.shape.clear()
        self.to_kill.clear()
        for row in range(self.board_size):
            for col in range(self.board_size):
                if random.random() > self.dist:
                    self.shape[(row,col)] = Cell((200,200,200)) 

    def add_cell(self,row,col,cell):
        self.shape[(row,col)] = cell    
        if row<0 or row>self.board_size:
            return
        if col<0 or col>self.board_size:
            return
        if (row,col) in self.shape:
            return            
        pygame.draw.rect(self.screen,self.shape[(row,col)].color,((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))      


    def draw_shape(self,row,col,cells):                   
        for curr_cell in cells:   
            dir = (0,0)       
            if self.construct_direction == 0:
                dir = (curr_cell[0],curr_cell[1])
            if self.construct_direction == 1:
                dir = (curr_cell[1],curr_cell[0])
            if self.construct_direction == 2:
                dir = (-curr_cell[0],curr_cell[1])
            if self.construct_direction == 3:
                dir = (curr_cell[1],-curr_cell[0])   
            self.add_cell(row+dir[0],col+dir[1],Cell((200,100,200)))    

    def get_box_shape(self):
        shape = []
        for i in range(-5,6):
            for j in range(-5,6):                                                                        
                shape.append((i,j))        
        return shape   
                

    def get_glider_shape(self):
        new_shape = [(0,0),(0,1),(0,2),(1,2),(2,1)]
        return new_shape

    def get_gilder_fleet_shape(self):
        glider_shape = self.get_glider_shape()
        shape = [] 
        for i in range(5):
            for j in range(5):
                if random.random() > 0.5:
                    for point in glider_shape:
                        shape.append((point[0]+i*5,point[1]+j*5));
        return shape

    def get_space_ship1_shape(col):
        new_shape = [(0,1),(1,0),(1,1),(1,2),(2,0),(2,2),(2,3),(3,1),(3,2),(3,3),(4,1),(4,2)]
        return new_shape;
 
    def get_space_ship2_shape(col):
        new_shape = [(0,3),(0,4),(1,3),(1,4),(3,2),(3,3),(3,4),(3,5),\
        (4,1),(4,2),(4,5),(4,6),(5,0),(5,7),(7,0),(7,7),(8,0),(8,2),(8,5),(8,7),\
        (9,3),(9,4),(10,3),(10,4),(11,1),(11,2),(11,5),(11,6)]
        return new_shape

    def handle_mouse_click_on_shape(self,pos):
        row = (int)(pos[0]/self.square_size)
        col = (int)(pos[1]/self.square_size)                 
        if row in range(self.board_size) and col in range(self.board_size):
            if not (row,col) in self.shape:
                shape = []
                if self.construct_mode == 0:
                    shape.append((0,0))                   
                if self.construct_mode == 1:
                    shape = self.get_box_shape()                                             
                if self.construct_mode == 2:
                    shape = self.get_glider_shape()
                if self.construct_mode == 3:
                    shape = self.get_gilder_fleet_shape()
                if self.construct_mode == 4:
                    shape = self.get_space_ship1_shape()
                if self.construct_mode == 5:
                    shape = self.get_space_ship2_shape()
                self.draw_shape(row,col,shape)

            elif not self.mouse_clicked:
                self.shape.pop((row,col))
                pygame.draw.rect(self.screen,(0,0,0),((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))      
        
   
    def handle_event(self,event):           
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and self.mouse_clicked):            
              self.mouse_clicked = True
        if event.type == pygame.MOUSEBUTTONUP: 
            self.handle_mouse_click_on_shape(pygame.mouse.get_pos())
            self.mouse_clicked = False
        if event.type == pygame.QUIT:
            self.is_done = True 

    def setmode(self,mode):
        self.mode = mode
        self.game_states["Mode"].update_drawing(mode)
            
    def update_color(self):        
        for item in self.shape:
            change = self.shape[item].age*5
            if change>50:
                change = 50
            self.shape[item].color = (250 - change*3,150 - change*1,change*3)

    def should_kill(self,cell,n):
        if self.mode == 0:        
            return n <= 1 or n > 3
        elif self.mode == 1: 
            return n == 1 or n > 3
        elif self.mode == 2:
            return n == 1 or n == 7
        elif self.mode == 3:
            return n == 2
            
    def should_live(self,cell,n):
        if self.mode == 0:        
            return n == 3
        if self.mode == 1:        
            return n == 3
        if self.mode == 2:        
            return n == 2
        if self.mode == 3:
            return n == 1

    def draw_board(self):
        for (row,col) in self.to_kill:
            pygame.draw.rect(self.screen,(0,0,0),((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))              
        for (row,col) in self.shape: 
            if self.shape[(row,col)].age > 10:
                continue
            pygame.draw.rect(self.screen,self.shape[(row,col)].color,((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))              
        max_board_plus_3 = self.max_pixel + 3
        pygame.draw.line(self.screen,(255,255,255),(0,max_board_plus_3),(max_board_plus_3,max_board_plus_3))      
        pygame.draw.line(self.screen,(255,255,255),(max_board_plus_3,0),(max_board_plus_3,max_board_plus_3)) 
        self.update_shape_data()
  
    def update(self):
        self.update_shape()
        self.update_color()

    def update_shape(self):
        for event in pygame.event.get():    
            self.handle_event(event)
            for button in self.buttons:
                button.handle_event(event)                              
        if(self.draw):           
            to_check = set()
            to_live = set()                      
            self.to_kill.clear()
            maybe_to_wake = set()
            self.iteration_num += 1
            for (x,y) in self.shape:
                if self.shape[(x,y)].sleep:
                    continue
                n = 0
                for i in range(-1,2):
                    for j in range(-1,2):        
                        if (i==0 and j==0):
                            continue             
                        curr = (x+i,y+j)                                      
                        if curr in self.shape: 
                            if self.shape[curr].sleep and self.shape[x,y].age <= 2:                           
                                maybe_to_wake.add(curr)
                            n+=1
                        elif not curr in to_check:
                            to_check.add(curr)
                if self.should_kill((x,y),n):
                    self.to_kill.add((x,y))   

            for (x,y) in to_check:
                if not (x >= 0 and y >= 0 and x <= self.board_size and y <= self.board_size):
                    continue                
                n = 0
                for i in range(-1,2):
                    for j in range(-1,2): 
                        if (i==0 and j==0):
                            pass                                      
                        elif (x+i,y+j) in self.shape:
                            n+=1
                if self.should_live((x,y),n):
                    to_live.add((x,y))
            
            for item in to_live:                                         
                self.shape[item] = Cell((200,200,200)) 

            for item in self.to_kill:                  
                self.shape.pop(item)         

            for item in to_live:   
                if not item in self.shape:                         
                    self.shape[item] = Cell((200,200,200)) 

            for item in self.shape:                
                self.shape[item].age += 1

            for item in maybe_to_wake:                
                self.shape[item].sleep = False

            if  self.iteration_num%15 == 0:
                for item in self.shape:       
                    if self.shape[item].age > 10:
                        self.shape[item].sleep = True

#######
#######

def main():
    pygame.init()
    screen = pygame.display.set_mode([1200, 750])
    pygame.display.set_caption('Board')
    clock = pygame.time.Clock()   
    game = GameOfLife(screen,600,5)
    
    while not game.is_done:
        game.update() 
        game.draw_board()                                        
        pygame.display.flip()
        clock.tick(game.speed)
    
# def resource_path(relative_path):
#     try:
#     # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

if __name__ == "__main__":    
    main()
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
        self.value = new_value;        
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

    def set_text(self,text):
        self.text = text
        pygame.draw.rect(self.screen,self.color,self.rect)       
        self.draw_text()

    def draw_text(self):
        font = pygame.font.SysFont(None, 50)        
        img = font.render(self.text, True, (100,100,100))       
        self.screen.blit(img, self.rect.topleft)

    def highlight(self):        
        new_color_list = list.self.color
        for index, item in enumerate(my_color_list):
            new_color_list[index] = item + 20
        pygame.draw.rect(self.screen,tuple(new_color_list),self.rect)  
        self.draw_text()

    def draw(self):    
        self.set_text(self.text)

    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):                
                self.callback(*self.args)
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(pygame.mouse.get_pos()):                
                self.highlight()             


class GameOfLife(object): 
    def __init__(self,screen): 

        self.max_pixel = 600 

        self.dist = 0.85
        self.square_size = 10
        self.board_size = (int)(self.max_pixel/self.square_size)-1
        self.draw = True
        self.shape = {}
        self.to_kill = set()       
        self.speed = 15
        self.mode = 1   
        self.construct_mode = 1
        self.mouse_clicked = False   
        self.screen = screen   
        self.iteration_num = 0  
        self.buttons = []
        self.game_states = {}
        self.is_done = False

        self.init_buttons()
        self.draw_states()
        
        self.randomize()    
        self.draw_board()
 
    def delete_board(self):
        pygame.draw.rect(self.screen,(0,0,0),(0,0,self.max_pixel,self.max_pixel))         
    
    def init_buttons(self):   
        buttons_location = self.max_pixel + 200  
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,50,150,50)),(200,150,50),"Boom",self.randomize_board))       
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,100,150,50)),(150,150,150),"Stop/Go",self.stop_resume))        
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,150,80,50)),(150,150,50),"+",self.change_size,1))        
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 100,150,80,50)),(100,150,150),"-",self.change_size,-1))
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,200,80,50)),(150,150,50),">>",self.change_game_speed,3))      
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 100,200,80,50)),(100,150,150),"<<",self.change_game_speed,-3))
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,250,150,50)),(200,150,50),"Clear",self.clear_shape))       
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,300,50,50)),(100,200,50),"1",self.setmode,1))
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 50,300,50,50)),(100,150,100),"2",self.setmode,2))
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 100,300,50,50)),(100,200,150),"3",self.setmode,3))
       
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location,400,50,50)),(100,200,50),"1",self.set_construct_mode,1))
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 50,400,50,50)),(100,150,100),"2",self.set_construct_mode,2))
        self.buttons.append(Button(self.screen,pygame.Rect((buttons_location + 100,400,50,50)),(100,200,150),"3",self.set_construct_mode,3))
      
        for button in self.buttons:
            button.draw() 

    def draw_states(self):
        states_location = self.max_pixel + 50
        speed_state = Game_state((states_location,215),self.screen,"Speed",self.speed)
        self.game_states["Speed"] = speed_state
        board_size_state = Game_state((states_location,165),self.screen,"Size",self.speed)
        self.game_states["Size"] = board_size_state
        pause_state = Game_state((states_location,115),self.screen,"State","ON")
        self.game_states["State"] = pause_state
        mode_state = Game_state((states_location,300),self.screen,"Mode",self.mode)
        self.game_states["Mode"] = mode_state

        construct_mode_state = Game_state((states_location,400),self.screen,"Shape",1)
        self.game_states["Shape"] = construct_mode_state

        total_cells_state = Game_state((50,self.max_pixel + 20),self.screen,"Total","")
        self.game_states["Total"] = total_cells_state
        active_cells_state = Game_state((50,self.max_pixel + 60),self.screen,"Active","")
        self.game_states["Active"] = active_cells_state
        self.update_shape_data()

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
            self.speed = new_speed;
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
            self.game_states["State"].update_drawing("ON")
        else:
            self.game_states["State"].update_drawing("Paused")

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
        pygame.draw.rect(self.screen,self.shape[(row,col)].color,((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))      
    


    def handle_mouse_click_on_shape(self,pos):
        row = (int)(pos[0]/self.square_size)
        col = (int)(pos[1]/self.square_size)                 
        if row in range(self.board_size) and col in range(self.board_size):
            if not (row,col) in self.shape:
                if self.construct_mode == 1:
                    self.add_cell(row,col,Cell((200,100,200)))
                if self.construct_mode == 2:
                    for i in range(-5,6):
                        for j in range(-5,6):                                                        
                            curr_cell = (row+i,col+j)                                                        
                            if curr_cell[0]<0 or curr_cell[0]>self.board_size:
                                continue;
                            if curr_cell[1]<0 or curr_cell[1]>self.board_size:
                                continue;
                            if curr_cell in self.shape:
                                continue;
                            self.add_cell(curr_cell[0],curr_cell[1],Cell((200,100,200)))                            

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
        if self.mode == 1:        
            return n <= 1 or n > 3
        elif self.mode == 2: 
            return n == 1 or n > 3
        elif self.mode == 3:
            return n == 1 or n == 7
            
    def should_live(self,cell,n):
        if self.mode == 1:        
            return n == 3
        if self.mode == 2:        
            return n == 3
        if self.mode == 3:        
            return n == 2

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
    screen = pygame.display.set_mode([1000, 750])
    pygame.display.set_caption('Board')
    clock = pygame.time.Clock()   
    game = GameOfLife(screen)
    
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
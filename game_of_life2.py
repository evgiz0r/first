import pygame
import numpy as np
import random
import sys
import os

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
        font = pygame.font.SysFont(None, 50)        
        img = font.render(self.text, True, (100,100,100))       
        self.screen.blit(img, self.rect.topleft)

    def draw(self):    
        self.set_text(self.text)

    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):                
                self.callback(self,*self.args)
               
  

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class GameOfLife(object): 
    def __init__(self,screen):        
        self.dist = 0.85
        self.square_size = 10
        self.board_size = (int)(700/self.square_size)
        self.draw = True
        self.shape = set()
        self.to_kill = set()
        self.to_live = set()
        self.inc_factor = 1.5
        self.speed = 15
        self.mode = 1
        self.curr_color = (100,100,100)
        self.curr_color_dir = [1,5,10]
        self.mouse_clicked = False   
        self.screen = screen     
        self.buttons = []
        self.is_done = False

        self.randomize()    
        self.draw_board()
        self.init_buttons()

    def delete_board(self):
        pygame.draw.rect(self.screen,(0,0,0),(0,0,800,800))

    def inc_speed(self,parent):
        if self.speed > 60:
            return
        self.speed = (int)(self.speed + 3)

    def dec_speed(self,parent):
        if self.speed < 5:
            return
        self.speed = (int)(self.speed - 3)

    def dec_size(self,parent):
        if self.square_size <= 4:
            return        
        self.square_size = (int)(self.square_size / self.inc_factor)
        self.board_size = (int)(700/self.square_size)   
        self.randomize()        
        self.draw_board()
    
    def inc_size(self,parent): 
        if self.square_size > 50:
            return        
        self.square_size = (int)(self.square_size * self.inc_factor)
        self.board_size = (int)(700/self.square_size)  
        self.randomize() 
        self.draw_board()

    def clear_shape(self,parent):
        self.shape.clear()
        self.delete_board()
   
    def stop_resume(self,parent):
        self.draw = not self.draw 
        if self.draw:
            parent.set_text("Pause")
        else:
            parent.set_text("Resume")

    def randomize_board(self,parent):
        self.randomize()
        self.draw_board()

    def randomize(self):        
        self.shape.clear()
        self.to_kill.clear()
        self.to_live.clear()
        for row in range(self.board_size):
            for col in range(self.board_size):
                if random.random() > self.dist:
                    self.shape.add((row,col)) 
   
    def handle_event(self,event):           
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and self.mouse_clicked):            
            row = (int)(pygame.mouse.get_pos()[0]/self.square_size)
            col = (int)(pygame.mouse.get_pos()[1]/self.square_size)                 
            if row in range(self.board_size) and col in range(self.board_size):
                if not (row,col) in self.shape:
                    self.shape.add((row,col))                     
                    pygame.draw.rect(self.screen,self.curr_color,((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))      
                elif not self.mouse_clicked:
                    self.shape.remove((row,col))
                    pygame.draw.rect(self.screen,(0,0,0),((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))      
            self.mouse_clicked = True
        if event.type == pygame.MOUSEBUTTONUP: 
            self.mouse_clicked = False
        if event.type == pygame.QUIT:
                self.is_done = True 

    def setmode(self,parent,mode):
        self.mode = mode
    
    def init_buttons(self):        
        self.buttons.append(Button(self.screen,pygame.Rect((800,100,150,50)),(200,150,50),"Pause",self.stop_resume))        
        self.buttons.append(Button(self.screen,pygame.Rect((800,200,150,50)),(200,150,50),"New",self.randomize_board))       
        self.buttons.append(Button(self.screen,pygame.Rect((800,300,80,50)),(150,150,50),"+",self.inc_size))        
        self.buttons.append(Button(self.screen,pygame.Rect((900,300,80,50)),(100,150,150),"-",self.dec_size))
        self.buttons.append(Button(self.screen,pygame.Rect((800,400,80,50)),(150,150,50),">>",self.inc_speed))        
        self.buttons.append(Button(self.screen,pygame.Rect((900,400,80,50)),(100,150,150),"<<",self.dec_speed))
        self.buttons.append(Button(self.screen,pygame.Rect((800,500,150,50)),(200,150,50),"Clear",self.clear_shape))       
        self.buttons.append(Button(self.screen,pygame.Rect((800,600,150,50)),(100,200,50),"Regular",self.setmode,1))
        self.buttons.append(Button(self.screen,pygame.Rect((800,650,150,50)),(100,200,100),"Special",self.setmode,2))
        self.buttons.append(Button(self.screen,pygame.Rect((800,700,150,50)),(100,200,150),"Random",self.setmode,3))
        for button in self.buttons:
            button.draw()         

    def update_color(self):        
        new_color = list(self.curr_color)
        for index, c in enumerate(new_color):
            if c <= 80 or c >= 200:
                self.curr_color_dir[index] = - self.curr_color_dir[index]
            new_color[index] = c + self.curr_color_dir[index]
        self.curr_color = tuple(new_color)

    def should_kill(self,cell,n):
        if self.mode == 1:        
            return n <= 1 or n > 3
        elif self.mode == 2: 
            return n == 1 or n > 3
        elif self.mode == 3:
            return n < 2 or n > 4 
            
    def should_live(self,cell,n):
        if self.mode == 1:        
            return n == 3
        if self.mode == 2:        
            return n == 3
        if self.mode == 3:        
            return n == 2

    def draw_board(self):
        self.delete_board()
        for (row,col) in self.shape:                        
            pygame.draw.rect(self.screen,self.curr_color,((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))              
 
    def my_draw(self):
        self.delete_board()
        self.draw_board()    
        #for (row,col) in self.to_kill:   
        #    if (row >= 0 and col >= 0 and row <= self.board_size and col <= self.board_size):                                                                      
        #        pygame.draw.rect(self.screen,(0,0,0),((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))              
        #for (row,col) in self.to_live:                        
        #    pygame.draw.rect(self.screen,self.curr_color,((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))              
 
    def update(self):
        for event in pygame.event.get():    
            self.handle_event(event)
            for button in self.buttons:
                button.handle_event(event)           
        if(self.draw):           
            to_check = set()
            to_live = set()
            to_kill = set()
            
            for (x,y) in self.shape:
                n = 0
                for i in range(-1,2):
                    for j in range(-1,2):        
                        if (i==0 and j==0):
                            pass                                                       
                        elif (x+i,y+j) in self.shape:                            
                            n+=1
                        elif not (x+i,y+j) in to_check:
                                to_check.add((x+i,y+j))
                if self.should_kill((x,y),n):
                    to_kill.add((x,y))               
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
            self.update_color()

            for item in to_kill:                  
                self.shape.remove(item)         

            for item in to_live:   
                if not item in self.shape:                         
                    self.shape.add(item)    
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
        game.my_draw()                                 
        pygame.display.flip()
        clock.tick(game.speed)
    

if __name__ == "__main__":
    main()
import pygame
import numpy as np
import random
import sys
import os
import cProfile



class Cell(object):
    def __init__(self,color):         
        self.age = 0
        self.color = color
        self.sleep = False

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
                self.callback(*self.args)

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
        self.board_size = (int)(700/self.square_size)-1
        self.draw = True
        self.shape = {}
        self.to_kill = set()
        self.inc_factor = 1.5
        self.speed = 15
        self.mode = 1   
        self.mouse_clicked = False   
        self.screen = screen   
        self.iteration_num = 0  
        self.buttons = []
        self.is_done = False

        self.randomize()    
        self.draw_board()
        self.init_buttons()

        pygame.draw.line(self.screen,(255,255,255),(0,701),(701,701))      
        pygame.draw.line(self.screen,(255,255,255),(701,0),(701,701))   

    def delete_board(self):
        pygame.draw.rect(self.screen,(0,0,0),(0,0,800,800))
        pygame.draw.line(self.screen,(255,255,255),(0,700),(700,700))      
        pygame.draw.line(self.screen,(255,255,255),(700,0),(700,700))   


    def inc_speed(self):
        if self.speed > 60:
            return
        self.speed = (int)(self.speed + 3)

    def dec_speed(self):
        if self.speed < 5:
            return
        self.speed = (int)(self.speed - 3)

    def dec_size(self):
        if self.square_size <= 2:
            return        
        self.square_size = (int)(self.square_size / self.inc_factor)
        self.board_size = (int)(700/self.square_size)-1   
        self.randomize()        
        self.delete_board()
        self.draw_board()
    
    def inc_size(self): 
        if self.square_size > 50:
            return        
        self.square_size = (int)(self.square_size * self.inc_factor)
        self.board_size = (int)(700/self.square_size)  
        self.delete_board()
        self.randomize() 
        self.draw_board()

    def clear_shape(self):
        self.shape.clear()
        self.delete_board()
   
    def stop_resume(self):
        self.draw = not self.draw 

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
   
    def handle_event(self,event):           
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and self.mouse_clicked):            
            row = (int)(pygame.mouse.get_pos()[0]/self.square_size)
            col = (int)(pygame.mouse.get_pos()[1]/self.square_size)                 
            if row in range(self.board_size) and col in range(self.board_size):
                if not (row,col) in self.shape:
                    self.shape[(row,col)] = Cell((200,100,200))                    
                    pygame.draw.rect(self.screen,self.shape[(row,col)].color,((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))      
                elif not self.mouse_clicked:
                    self.shape.pop((row,col))
                    pygame.draw.rect(self.screen,(0,0,0),((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))      
            self.mouse_clicked = True
        if event.type == pygame.MOUSEBUTTONUP: 
            self.mouse_clicked = False
        if event.type == pygame.QUIT:
                self.is_done = True 

    def setmode(self,mode):
        self.mode = mode
    
    def init_buttons(self):         
        self.buttons.append(Button(self.screen,pygame.Rect((800,50,150,50)),(150,150,150),"Stop/Go",self.stop_resume))        
        self.buttons.append(Button(self.screen,pygame.Rect((800,100,150,50)),(200,150,50),"New",self.randomize_board))       
        self.buttons.append(Button(self.screen,pygame.Rect((800,150,80,50)),(150,150,50),"+",self.inc_size))        
        self.buttons.append(Button(self.screen,pygame.Rect((900,150,80,50)),(100,150,150),"-",self.dec_size))
        self.buttons.append(Button(self.screen,pygame.Rect((800,250,80,50)),(150,150,50),">>",self.inc_speed))        
        self.buttons.append(Button(self.screen,pygame.Rect((900,250,80,50)),(100,150,150),"<<",self.dec_speed))
        self.buttons.append(Button(self.screen,pygame.Rect((800,300,150,50)),(200,150,50),"Clear",self.clear_shape))       
        self.buttons.append(Button(self.screen,pygame.Rect((800,350,150,50)),(100,200,50),"Regular",self.setmode,1))
        self.buttons.append(Button(self.screen,pygame.Rect((800,400,150,50)),(100,150,100),"Special",self.setmode,2))
        self.buttons.append(Button(self.screen,pygame.Rect((800,450,150,50)),(100,200,150),"Random",self.setmode,3))
        for button in self.buttons:
            button.draw()         

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
    

if __name__ == "__main__":
    cProfile.run('main()')
    #main()
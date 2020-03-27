import pygame
import numpy as np
import random

import sys
import os

class Button(object):
    def __init__(self,rect,color,callback,text):
        self.rect = rect
        self.text = text
        self.color = color
        self.callback = callback      

    def draw(self,screen):        
        pygame.draw.rect(screen,self.color,self.rect)  
        font = pygame.font.SysFont(None, 50)
        img = font.render(self.text, True, (100,100,100))
        screen.blit(img, self.rect.topleft)

    def handle_event(self,event,screen):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.callback(screen)

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class GameOfLife(object): 
    def __init__(self):        
        self.dist = 0.85
        self.square_size = 10
        self.board_size = (int)(700/self.square_size)
        self.draw = True
        self.shape = set()
        self.inc_factor = 1.5
        self.speed = 15
        self.mode = "G1"

    def delete_board(self,screen):
        pygame.draw.rect(screen,(0,0,0),(0,0,800,800))

    def inc_speed(self,screen):
        if self.speed > 60:
            return
        self.speed = (int)(self.speed + 3)

    def dec_speed(self,screen):
        if self.speed < 5:
            return
        self.speed = (int)(self.speed - 3)


    def dec_size(self,screen):
        if self.square_size <= 2:
            return        
        self.square_size = (int)(self.square_size / self.inc_factor)
        self.board_size = (int)(700/self.square_size)
        self.randomize(screen)
    
    def inc_size(self,screen): 
        if self.square_size > 50:
            return        
        self.square_size = (int)(self.square_size * self.inc_factor);
        self.board_size = (int)(700/self.square_size)
        self.randomize(screen)
   
    def stop_resume(self,screen):
        self.draw = not self.draw 

    def randomize(self,screen):
        self.delete_board(screen)
        for row in range(self.board_size):
            for col in range(self.board_size):
                if random.random()>self.dist:
                    self.shape.add((row,col))                

    def init_buttons(self,screen):
        buttons = []
        buttons.append(Button(pygame.Rect((800,100,100,50)),(250,150,50),self.stop_resume,"Stop"))        
        buttons.append(Button(pygame.Rect((800,200,100,50)),(200,150,50),self.randomize,"New"))       
        buttons.append(Button(pygame.Rect((800,300,80,50)),(150,150,50),self.inc_size,"+"))        
        buttons.append(Button(pygame.Rect((900,300,80,50)),(100,150,50),self.dec_size,"-"))
        buttons.append(Button(pygame.Rect((800,400,80,50)),(150,150,50),self.inc_speed,">>"))        
        buttons.append(Button(pygame.Rect((900,400,80,50)),(100,150,50),self.dec_speed,"<<"))
      
        for button in buttons:
            button.draw(screen) 
        return buttons

    def update(self,screen):
        to_kill = set()
        to_live = set()
        to_check = set()

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
            if(n==1 or n>3):
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
            if(n == 3):
                to_live.add((x,y))           

        for item in to_kill:                                                                    
            self.shape.remove(item)
        
        for item in to_live:  
            self.shape.add(item)    

        for (row,col) in to_kill:           
            if (row >= 0 and col >= 0 and row <= self.board_size and col <= self.board_size):                                                                      
                pygame.draw.rect(screen,(0,0,0),((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))
        for (row,col) in to_live:      
            color = (255*(row/self.board_size),255*(col/self.board_size),255)
            pygame.draw.rect(screen,color,((row*self.square_size),(col*self.square_size),self.square_size-1,self.square_size-1))      
                

    def loop(self):    
        pygame.init()
        screen = pygame.display.set_mode([1000, 750])
        pygame.display.set_caption('Board')
        clock = pygame.time.Clock()    
        buttons = self.init_buttons(screen)      
        self.randomize(screen)   

        done = False     
        while not done:
            for event in pygame.event.get():    
                for button in buttons:
                    button.handle_event(event,screen)      
                if event.type == pygame.QUIT:
                    done = True                  

            if(self.draw):
                self.update(screen);                
            pygame.display.flip()
            clock.tick(self.speed)
            #draw = False

def main():
    g = GameOfLife()
    g.loop()

if __name__ == "__main__":
    main()
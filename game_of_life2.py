import pygame
import numpy as np
import random
import sys
import os

class Button(object):
    def __init__(self,screen,rect,color,callback,text):
        self.rect = rect
        self.text = text
        self.color = color
        self.callback = callback   
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
                self.callback(self)
  

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
        self.square_size = 40
        self.board_size = (int)(700/self.square_size)
        self.draw = True
        self.shape = set()
        self.inc_factor = 1.5
        self.speed = 10
        self.mode = "G1"
        self.curr_color = (100,100,100)
        self.curr_color_dir = [1,5,10]
        self.mouse_clicked = False   
        self.screen = screen     
        self.buttons = []
        self.is_done = False

        self.randomize(None)
        self.init_buttons()

    def delete_board(self,parent):
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
        if self.square_size <= 2:
            return        
        self.square_size = (int)(self.square_size / self.inc_factor)
        self.board_size = (int)(700/self.square_size)
        self.randomize(parent)
    
    def inc_size(self,parent): 
        if self.square_size > 50:
            return        
        self.square_size = (int)(self.square_size * self.inc_factor);
        self.board_size = (int)(700/self.square_size)
        self.randomize(parent)

    def clear_shape(self,parent):
        self.shape.clear()
        self.delete_board(parent)
   
    def stop_resume(self,parent):
        self.draw = not self.draw 
        if self.draw:
            parent.set_text("Pause")
        else:
            parent.set_text("Resume")

    def randomize(self,parent):
        self.delete_board(None)
        for row in range(self.board_size):
            for col in range(self.board_size):
                if random.random() > self.dist:
                    self.shape.add((row,col))  

    def handle_event(self,event):           
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and self.mouse_clicked):            
            row = (int)(pygame.mouse.get_pos()[0]/self.square_size);
            col = (int)(pygame.mouse.get_pos()[1]/self.square_size);                   
            if row in range(self.board_size) and col in range(self.board_size):
                if not (row,col) in self.shape:
                    self.bring_cell((row,col))
                elif not self.mouse_clicked:
                    self.kill_cell((row,col))
            self.mouse_clicked = True
        if event.type == pygame.MOUSEBUTTONUP: 
            self.mouse_clicked = False
        if event.type == pygame.QUIT:
                self.is_done = True 

    def setg1(self,parent):
        self.mode = "G1"    
    def setg2(self,parent):    
        self.mode = "G2"  
    def setg3(self,parent):
        self.mode = "G3"  
    
    def init_buttons(self):        
        self.buttons.append(Button(self.screen,pygame.Rect((800,100,150,50)),(200,150,50),self.stop_resume,"Stop"))        
        self.buttons.append(Button(self.screen,pygame.Rect((800,200,150,50)),(200,150,50),self.randomize,"New"))       
        self.buttons.append(Button(self.screen,pygame.Rect((800,300,80,50)),(150,150,50),self.inc_size,"+"))        
        self.buttons.append(Button(self.screen,pygame.Rect((900,300,80,50)),(100,150,150),self.dec_size,"-"))
        self.buttons.append(Button(self.screen,pygame.Rect((800,400,80,50)),(150,150,50),self.inc_speed,">>"))        
        self.buttons.append(Button(self.screen,pygame.Rect((900,400,80,50)),(100,150,150),self.dec_speed,"<<"))
        self.buttons.append(Button(self.screen,pygame.Rect((800,500,150,50)),(200,150,50),self.clear_shape,"Clear"))       
        self.buttons.append(Button(self.screen,pygame.Rect((800,600,50,50)),(100,150,50),self.setg1,"G1"))
        self.buttons.append(Button(self.screen,pygame.Rect((850,600,50,50)),(100,150,100),self.setg2,"G2"))
        self.buttons.append(Button(self.screen,pygame.Rect((900,600,50,50)),(100,150,150),self.setg3,"G3"))
        for button in self.buttons:
            button.draw()         

    def update_color(self):        
        new_color = list(self.curr_color)
        for index, c in enumerate(new_color):
            if c <= 15 or c >= 240:
                self.curr_color_dir[index] = - self.curr_color_dir[index]
            new_color[index] = c + self.curr_color_dir[index]
        self.curr_color = tuple(new_color)

    def kill_cell(self,cell):
        row,col = cell      
        self.shape.remove(cell)    
        if (row >= 0 and col >= 0 and row <= self.board_size and col <= self.board_size):                                                                      
            pygame.draw.rect(self.screen,(0,0,0),((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))
    
    def bring_cell(self,cell):
        row,col = cell
        self.shape.add(cell)    
        pygame.draw.rect(self.screen,self.curr_color,((row*self.square_size),(col*self.square_size),self.square_size-1,self.square_size-1))      
   
    def should_kill(self,cell,n):
        if self.mode == "G1":        
            return n <= 1 or n > 3
        elif self.mode == "G2": 
            return n == 1 or n > 3
        elif self.mode == "G3": 
            return (n * 0.01 + 0.03) > random.random()
            
    def should_live(self,cell,n):
        if self.mode == "G1":        
            return n == 3
        if self.mode == "G2":        
            return n == 3
        if self.mode == "G3":        
            return n > 4

    def update(self):
        for event in pygame.event.get():    
            self.handle_event(event)
            for button in self.buttons:
                button.handle_event(event)   
            if(self.draw):
                self.update();  

        if(self.draw):
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

            for item in to_kill:                  
                self.kill_cell(item)    
            
            for item in to_live:                            
                self.bring_cell(item)
                    
            self.update_color()

def main():
    pygame.init()
    screen = pygame.display.set_mode([1000, 750])
    pygame.display.set_caption('Board')
    clock = pygame.time.Clock()   
    game = GameOfLife(screen)
    
    while not game.is_done:
        game.update();                                  
        pygame.display.flip()
        clock.tick(game.speed)
    

if __name__ == "__main__":
    main()
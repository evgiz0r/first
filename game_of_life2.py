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
        self.img = None   

    def set_text(self,screen,text):
        self.text = text
        pygame.draw.rect(screen,self.color,self.rect)       
        font = pygame.font.SysFont(None, 50)        
        img = font.render(self.text, True, (100,100,100))       
        screen.blit(img, self.rect.topleft)

    def draw(self,screen):    
        self.set_text(screen,self.text)

    def handle_event(self,event,screen):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.callback(screen,self)
  

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
        self.speed = 10
        self.mode = "G1"
        self.curr_color = (100,100,100)
        self.curr_color_dir = [1,5,10]
        self.mouse_clicked = False

    def delete_board(self,screen,parent):
        pygame.draw.rect(screen,(0,0,0),(0,0,800,800))

    def inc_speed(self,screen,parent):
        if self.speed > 60:
            return
        self.speed = (int)(self.speed + 3)

    def dec_speed(self,screen,parent):
        if self.speed < 5:
            return
        self.speed = (int)(self.speed - 3)

    def dec_size(self,screen,parent):
        if self.square_size <= 2:
            return        
        self.square_size = (int)(self.square_size / self.inc_factor)
        self.board_size = (int)(700/self.square_size)
        self.randomize(screen,parent)
    
    def inc_size(self,screen,parent): 
        if self.square_size > 50:
            return        
        self.square_size = (int)(self.square_size * self.inc_factor);
        self.board_size = (int)(700/self.square_size)
        self.randomize(screen,parent)

    def clear_shape(self,screen,parent):
        self.shape.clear()
        self.delete_board(screen,parent)
   
    def stop_resume(self,screen,parent):
        self.draw = not self.draw 
        if self.draw:
            parent.set_text(screen,"Pause")
        else:
            parent.set_text(screen,"Resume")

    def randomize(self,screen,parent):
        self.delete_board(screen,None)
        for row in range(self.board_size):
            for col in range(self.board_size):
                if random.random() > self.dist:
                    self.shape.add((row,col))  

    def handle_event(self,event,screen):           
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and self.mouse_clicked):   
            self.mouse_clicked = True
            row = (int)(pygame.mouse.get_pos()[0]/self.square_size);
            col = (int)(pygame.mouse.get_pos()[1]/self.square_size);                   
            if row in range(self.board_size) and col in range(self.board_size):
                if not (row,col) in self.shape:
                    self.shape.add((row,col))
                    pygame.draw.rect(screen,self.curr_color,((row*self.square_size),(col*self.square_size),self.square_size-1,self.square_size-1))      
        if event.type == pygame.MOUSEBUTTONUP: 
            self.mouse_clicked = False

    def setg1(self,screen,parent):
        self.mode = "G1"    
    def setg2(self,screen,parent):    
        self.mode = "G2"  
    def setg3(self,screen,parent):
        self.mode = "G3"  
    
    def init_buttons(self,screen):
        buttons = []
        buttons.append(Button(pygame.Rect((800,100,150,50)),(200,150,50),self.stop_resume,"Stop"))        
        buttons.append(Button(pygame.Rect((800,200,150,50)),(200,150,50),self.randomize,"New"))       
        buttons.append(Button(pygame.Rect((800,300,80,50)),(150,150,50),self.inc_size,"+"))        
        buttons.append(Button(pygame.Rect((900,300,80,50)),(100,150,150),self.dec_size,"-"))
        buttons.append(Button(pygame.Rect((800,400,80,50)),(150,150,50),self.inc_speed,">>"))        
        buttons.append(Button(pygame.Rect((900,400,80,50)),(100,150,150),self.dec_speed,"<<"))
        buttons.append(Button(pygame.Rect((800,500,150,50)),(200,150,50),self.clear_shape,"Clear"))       
        buttons.append(Button(pygame.Rect((800,600,50,50)),(100,150,50),self.setg1,"G1"))
        buttons.append(Button(pygame.Rect((850,600,50,50)),(100,150,100),self.setg2,"G2"))
        buttons.append(Button(pygame.Rect((900,600,50,50)),(100,150,150),self.setg3,"G3"))
        for button in buttons:
            button.draw(screen) 
        return buttons

    def update_color(self):        
        new_color = list(self.curr_color)
        for index, c in enumerate(new_color):
            if c <= 15 or c >= 240:
                self.curr_color_dir[index] = - self.curr_color_dir[index]
            new_color[index] = c + self.curr_color_dir[index]
        self.curr_color = tuple(new_color)

    def kill_cell(self,screen,cell):
        row,col = cell          
        if (row >= 0 and col >= 0 and row <= self.board_size and col <= self.board_size):                                                                      
            pygame.draw.rect(screen,(0,0,0),((row*self.square_size),(col*self.square_size),self.square_size,self.square_size))
    
    def bring_cell(self,screen,cell):
        row,col = cell
        pygame.draw.rect(screen,self.curr_color,((row*self.square_size),(col*self.square_size),self.square_size-1,self.square_size-1))      
   
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
            self.shape.remove(item)   
            self.kill_cell(screen,item)    
          
        for item in to_live:          
            self.shape.add(item)                 
            self.bring_cell(screen,item)
                   
        self.update_color()


    def loop(self):    
        pygame.init()
        screen = pygame.display.set_mode([1000, 750])
        pygame.display.set_caption('Board')
        clock = pygame.time.Clock()    
        buttons = self.init_buttons(screen)      
        self.randomize(screen,None)   

        done = False     
        while not done:
            for event in pygame.event.get():              
                if event.type == pygame.QUIT:
                    done = True
                self.handle_event(event,screen)
                for button in buttons:
                    button.handle_event(event,screen)   
            if(self.draw):
                self.update(screen);                
            pygame.display.flip()
            clock.tick(self.speed)

def main():
    g = GameOfLife()
    g.loop()

if __name__ == "__main__":
    main()
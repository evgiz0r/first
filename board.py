import pygame
import numpy as np
import random

import sys
import os

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    
    pygame.init()
    screen = pygame.display.set_mode([1300, 700])
    pygame.display.set_caption('Board')
    clock = pygame.time.Clock()
    #font =  pygame.font.Font(None, 80)
    dist = 0.6
    
    rect1 = pygame.Rect(1000,100,400,100)
    pygame.draw.rect(screen,(50,50,50),rect1)

    square_size = 7
    board_size = 100
    draw = True

    shape = set()
    for row in range(board_size):
        for col in range(board_size):
            if random.random()>dist:
                shape.add((row,col))
    
    done = False     
    while not done:           
        for event in pygame.event.get():          
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect1.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen,(0,0,0),(0,0,1000,1000)) 
                    square_size += 1   
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:                
                    draw = not draw;
                if  event.key == pygame.K_UP:
                    pygame.draw.rect(screen,(0,0,0),(0,0,1000,1000)) 
                    square_size += 1     
                if  event.key == pygame.K_DOWN:
                    pygame.draw.rect(screen,(0,0,0),(0,0,1000,1000)) 
                    square_size = square_size - 1        
            if event.type == pygame.KEYDOWN and event.key == 13:
                shape.clear()
                pygame.draw.rect(screen,(0,0,0),(0,0,1000,1000))            
                for row in range(board_size):
                    for col in range(board_size):
                        if random.random()>dist:
                            shape.add((row,col))

        if(draw):
            to_kill = set()
            to_live = set()
            to_check = set()

            for (x,y) in shape:
                n = 0
                for i in range(-1,2):
                    for j in range(-1,2):        
                        if (i==0 and j==0):
                            pass                                                       
                        elif (x+i,y+j) in shape:
                            n+=1
                        else:
                            if not (x+i,y+j) in to_check:
                                to_check.add((x+i,y+j))
                if(n <=1 or n>3):
                    to_kill.add((x,y))
                
            for (x,y) in to_check:
                if(x >= 0 and y >= 0 and x <= board_size and y <= board_size):
                    n = 0
                    for i in range(-1,2):
                        for j in range(-1,2): 
                            if (i==0 and j==0):
                                pass                                      
                            elif (x+i,y+j) in shape:
                                n+=1
                    if(n==3):
                        to_live.add((x,y))           

            for item in to_kill:            
                shape.remove(item)
                pygame.draw.rect(screen,(0,0,0),((item[0]*square_size),(item[1]*square_size),square_size,square_size))

            for item in to_live:            
                shape.add(item)

            #if(draw):        
            for (row,col) in shape:
                color = (255-row*2,255-col*2,100)
                pygame.draw.rect(screen,color,((row*square_size),(col*square_size),square_size-2,square_size-2))

            pygame.display.flip()
        clock.tick(30)
        #draw = False
       

if __name__ == "__main__":
    main()
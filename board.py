import pygame
import numpy as np
import random
#from pygame.locals import *

def main():
    
    screen = pygame.display.set_mode([800, 600])
    pygame.display.set_caption('Board')
    clock = pygame.time.Clock()
    done = False    
    
    square_size = 50
    board_size = 10
    b = np.zeros((board_size,board_size))
    draw = True

    for row in range(0,board_size):
        for col in range(0,board_size):
            b[row][col] = 1
  
    while not done:           
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    done = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    draw = not draw;
                    
        #if(draw):
        for row in range(0,board_size):
            for col in range(0,board_size):
                if(random.random() < 0.2):
                    b[row][col] = -b[row][col]

                  
        screen.fill((0, 0, 0))   
        if draw:
            for row in range(0,board_size):
                for col in range(0,board_size):                    
                    if (b[row][col] == 1):
                        pygame.draw.rect(screen,(255,255,255),((row*square_size),(col*square_size),square_size,square_size))
            
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
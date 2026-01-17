import random  # for generating random pipes
import sys
import pygame
from pygame.locals import *

# Global variables
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = int(SCREENHEIGHT * 0.8)
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallary/sprites/bird.png'
BACKGROUND = 'gallary/sprites/background.jpg'
PIPE = 'gallary/sprites/pipe.png'


def welcomeScreen():
    """Shows welcome image on screen"""
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def mainGame():
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)
    basex = 0

    # create 2 pipes blitting
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelx = -4
    playerVely = -9
    playerMaxVely = 10
    playerMinVely = -8
    playerAccy = 1

    playerFlapAccv = -8  # bird speed while flapping
    playerFlapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVely = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)  # return true if player is crashed

        if crashTest:
            return

        # check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()

        if playerVely < playerMaxVely and not playerFlapped:
            playerVely += playerAccy

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVely, GROUNDY - playery - playerHeight)

        # move pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelx
            lowerPipe['x'] += pipeVelx

        # add new pipe when first crosses the leftmost part of screen
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if pipe out of screen (then remove)
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # lets blit our sprites
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeRect = pygame.Rect(pipe['x'], pipe['y'], GAME_SPRITES['pipe'][0].get_width(),
                               GAME_SPRITES['pipe'][0].get_height())
        playerRect = pygame.Rect(playerx, playery, GAME_SPRITES['player'].get_width(),
                                 GAME_SPRITES['player'].get_height())
        if playerRect.colliderect(pipeRect):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        pipeRect = pygame.Rect(pipe['x'], pipe['y'], GAME_SPRITES['pipe'][1].get_width(),
                               GAME_SPRITES['pipe'][1].get_height())
        playerRect = pygame.Rect(playerx, playery, GAME_SPRITES['player'].get_width(),
                                 GAME_SPRITES['player'].get_height())
        if playerRect.colliderect(pipeRect):
            GAME_SOUNDS['hit'].play()
            return True

    return False


def getRandomPipe():
    """generating pipe positions for two pipes"""
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = int(SCREENHEIGHT / 3)

    # Ensure positive range
    max_range = int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset)
    if max_range < 0:
        max_range = 100  # fallback safe value

    y2 = offset + random.randrange(0, max_range)
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset

    pipe = [
        {'x': pipeX, 'y': -y1},  # upper pipe
        {'x': pipeX, 'y': y2}    # lower pipe
    ]
    return pipe


if __name__ == "__main__":
    # Main function
    pygame.init()  # initializes all modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird by Ayush")
    # Load numbers
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallary/sprites/0.png').convert_alpha(),
        pygame.image.load('gallary/sprites/1.png').convert_alpha(),
        pygame.image.load('gallary/sprites/2.png').convert_alpha(),
        pygame.image.load('gallary/sprites/3.png').convert_alpha(),
        pygame.image.load('gallary/sprites/4.png').convert_alpha(),
        pygame.image.load('gallary/sprites/5.png').convert_alpha(),
        pygame.image.load('gallary/sprites/6.png').convert_alpha(),
        pygame.image.load('gallary/sprites/7.png').convert_alpha(),
        pygame.image.load('gallary/sprites/8.png').convert_alpha(),
        pygame.image.load('gallary/sprites/9.png').convert_alpha()
    )
    GAME_SPRITES['message'] = pygame.image.load('gallary/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallary/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallary/audio/die.mp3')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallary/audio/hit.mp3')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallary/audio/point.mp3')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallary/audio/swoosh.mp3')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallary/audio/wing.mp3')

    # Background and player
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert_alpha()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    # Main game loop
    while True:
        welcomeScreen()
        mainGame()
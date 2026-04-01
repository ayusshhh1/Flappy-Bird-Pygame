import sys
import pygame
from pygame.locals import *


def gameOverScreen(screen, fpsclock, game_sprites, game_sounds, score):
    """
    Displays a Game Over panel with the player's score.
    Buttons: 'Play Again' (returns True) | 'Exit' (quits).

    Parameters
    ----------
    screen       : pygame.Surface  – the main display surface
    fpsclock     : pygame.time.Clock
    game_sprites : dict            – must contain 'background' key
    game_sounds  : dict            – must contain 'die' key
    score        : int             – final score to display
    """

    SCREENWIDTH  = screen.get_width()
    SCREENHEIGHT = screen.get_height()
    FPS          = 32

    # ── Fonts ──────────────────────────────────────────────────────────────
    font_big   = pygame.font.SysFont('Arial', 42, bold=True)
    font_small = pygame.font.SysFont('Arial', 20)

    # ── Colours ────────────────────────────────────────────────────────────
    WHITE           = (255, 255, 255)
    GOLD            = (255, 215,   0)
    DARK_RED        = (180,  20,  20)
    BTN_GREEN       = ( 50, 180,  50)
    BTN_RED         = (200,  50,  50)
    BTN_HOVER_GREEN = ( 30, 140,  30)
    BTN_HOVER_RED   = (160,  30,  30)

    # ── Semi-transparent overlay ────────────────────────────────────────────
    overlay = pygame.Surface((SCREENWIDTH, SCREENHEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))

    # ── Panel ──────────────────────────────────────────────────────────────
    panel_w, panel_h = 230, 260
    panel_x = (SCREENWIDTH  - panel_w) // 2
    panel_y = (SCREENHEIGHT - panel_h) // 2 - 20

    # ── Buttons ────────────────────────────────────────────────────────────
    btn_w, btn_h = 95, 38
    btn_gap      = 16
    total_btn_w  = btn_w * 2 + btn_gap
    btn_y        = panel_y + panel_h - btn_h - 20
    play_btn_x   = panel_x + (panel_w - total_btn_w) // 2
    exit_btn_x   = play_btn_x + btn_w + btn_gap

    play_btn_rect = pygame.Rect(play_btn_x, btn_y, btn_w, btn_h)
    exit_btn_rect = pygame.Rect(exit_btn_x, btn_y, btn_w, btn_h)

    def draw_screen(mouse_pos):
        # Frozen game background + dark overlay
        screen.blit(game_sprites['background'], (0, 0))
        screen.blit(overlay, (0, 0))

        # Panel shadow
        shadow = pygame.Surface((panel_w + 6, panel_h + 6), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        screen.blit(shadow, (panel_x - 3, panel_y + 5))

        # Panel body (parchment)
        pygame.draw.rect(screen, (245, 245, 230),
                         pygame.Rect(panel_x, panel_y, panel_w, panel_h),
                         border_radius=14)
        # Golden border
        pygame.draw.rect(screen, (180, 140, 60),
                         pygame.Rect(panel_x, panel_y, panel_w, panel_h),
                         width=3, border_radius=14)

        # "GAME OVER" title
        title_surf = font_big.render("GAME OVER", True, DARK_RED)
        screen.blit(title_surf,
                    (panel_x + (panel_w - title_surf.get_width()) // 2, panel_y + 18))

        # Top divider
        div_y = panel_y + 70
        pygame.draw.line(screen, (180, 140, 60),
                         (panel_x + 16, div_y), (panel_x + panel_w - 16, div_y), 2)

        # "YOUR SCORE" label
        label_surf = font_small.render("YOUR SCORE", True, (100, 80, 40))
        screen.blit(label_surf,
                    (panel_x + (panel_w - label_surf.get_width()) // 2, div_y + 14))

        # Score (gold + drop shadow)
        score_surf   = font_big.render(str(score), True, GOLD)
        score_shadow = font_big.render(str(score), True, (100, 70, 0))
        score_x = panel_x + (panel_w - score_surf.get_width()) // 2
        score_y = div_y + 44
        screen.blit(score_shadow, (score_x + 2, score_y + 2))
        screen.blit(score_surf,   (score_x,     score_y))

        # Bottom divider
        div2_y = score_y + score_surf.get_height() + 10
        pygame.draw.line(screen, (180, 140, 60),
                         (panel_x + 16, div2_y), (panel_x + panel_w - 16, div2_y), 2)

        # Buttons with hover
        play_color = BTN_HOVER_GREEN if play_btn_rect.collidepoint(mouse_pos) else BTN_GREEN
        exit_color = BTN_HOVER_RED   if exit_btn_rect.collidepoint(mouse_pos) else BTN_RED

        pygame.draw.rect(screen, play_color, play_btn_rect, border_radius=8)
        pygame.draw.rect(screen, exit_color, exit_btn_rect, border_radius=8)

        play_text = font_small.render("Play Again", True, WHITE)
        exit_text = font_small.render("Exit",       True, WHITE)

        screen.blit(play_text,
                    (play_btn_rect.x + (btn_w - play_text.get_width()) // 2,
                     play_btn_rect.y + (btn_h - play_text.get_height()) // 2))
        screen.blit(exit_text,
                    (exit_btn_rect.x + (btn_w - exit_text.get_width()) // 2,
                     exit_btn_rect.y + (btn_h - exit_text.get_height()) // 2))

        pygame.display.update()

    # Play die sound once
    game_sounds['die'].play()

    # ── Event loop ─────────────────────────────────────────────────────────
    while True:
        mouse_pos = pygame.mouse.get_pos()
        draw_screen(mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if play_btn_rect.collidepoint(event.pos):
                    return True   # play again
                if exit_btn_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

            # Space / Enter → play again
            if event.type == KEYDOWN and event.key in (K_SPACE, K_RETURN):
                return True

        fpsclock.tick(FPS)
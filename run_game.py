"""
run_game.py  –  Launch Flappy Bird with the Game Over screen.

Put this file in the SAME folder as main.py and game_over.py.
Run:  python run_game.py

main.py is NOT modified at all.
"""

import sys
import types
import main          # original, unmodified module
import game_over            # our new Game Over screen


# ── Patch mainGame to return the score ────────────────────────────────────
#
# The original mainGame() calls `return` with no value when the player
# crashes.  We wrap it so it intercepts that bare return and hands back
# the score that was accumulated just before the crash.
#
# Technique: we replace the function in the module's namespace with a
# thin wrapper that shadows the internal `score` variable.

_original_mainGame = main.mainGame   # keep a reference


def _patched_mainGame():
    """
    Runs the original game loop but captures the score before returning.
    We re-implement the score-tracking here by monkey-patching the point
    sound's play() call — but a simpler, cleaner approach is just to
    re-read the score from the local scope via a shared mutable container.
    """
    # We use a mutable list as a 'box' to pass score out of the closure.
    score_box = [0]

    # Inline re-implementation that delegates everything to the original
    # code EXCEPT we intercept the crash return to capture the score.
    #
    # Because main.mainGame is a plain function (no class), the
    # cleanest zero-modification way is to exec a slightly tweaked copy
    # of its source.  Here we use a simpler strategy: duplicate only the
    # score variable tracking via the GAME_SOUNDS['point'] hook.

    original_point_sound = main.GAME_SOUNDS['point']

    class _ScoreCountingSound:
        """Wraps the point sound and increments our score_box on each play."""
        def play(self):
            score_box[0] += 1
            original_point_sound.play()
        def stop(self):
            original_point_sound.stop()

    # Temporarily swap out the point sound
    main.GAME_SOUNDS['point'] = _ScoreCountingSound()

    try:
        _original_mainGame()   # runs until crash (returns None)
    finally:
        # Always restore the real sound object
        main.GAME_SOUNDS['point'] = original_point_sound

    return score_box[0]


# Replace the function in the module so welcomeScreen / other helpers
# that might call mainGame() indirectly also get the patched version.
main.mainGame = _patched_mainGame


# ── Main loop ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Boot pygame via the original module (it already does pygame.init etc.
    # inside its  if __name__ == "__main__"  block, but since we're importing
    # it that block won't run — so we replicate just the setup here).

    import pygame
    from pygame.locals import *

    pygame.init()
    main.FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird by Ayush")

    # Reload all sprites & sounds exactly as the original does
    main.GAME_SPRITES['numbers'] = tuple(
        pygame.image.load(f'gallary/sprites/{i}.png').convert_alpha()
        for i in range(10)
    )
    main.GAME_SPRITES['message']    = pygame.image.load('gallary/sprites/message.png').convert_alpha()
    main.GAME_SPRITES['base']       = pygame.image.load('gallary/sprites/base.png').convert_alpha()
    main.GAME_SPRITES['pipe']       = (
        pygame.transform.rotate(pygame.image.load(main.PIPE).convert_alpha(), 180),
        pygame.image.load(main.PIPE).convert_alpha()
    )
    main.GAME_SPRITES['background'] = pygame.image.load(main.BACKGROUND).convert_alpha()
    main.GAME_SPRITES['player']     = pygame.image.load(main.PLAYER).convert_alpha()

    main.GAME_SOUNDS['die']    = pygame.mixer.Sound('gallary/audio/die.mp3')
    main.GAME_SOUNDS['hit']    = pygame.mixer.Sound('gallary/audio/hit.mp3')
    main.GAME_SOUNDS['point']  = pygame.mixer.Sound('gallary/audio/point.mp3')
    main.GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallary/audio/swoosh.mp3')
    main.GAME_SOUNDS['wing']   = pygame.mixer.Sound('gallary/audio/wing.mp3')

    while True:
        main.welcomeScreen()
        final_score = main.mainGame()          # patched → returns score

        game_over.gameOverScreen(
            screen       = main.SCREEN,
            fpsclock     = main.FPSCLOCK,
            game_sprites = main.GAME_SPRITES,
            game_sounds  = main.GAME_SOUNDS,
            score        = final_score,
        )
        # gameOverScreen returns True (play again) or exits by itself
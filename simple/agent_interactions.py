# Goal is to show the agents user and assistant interations by means of a character (agent) going and using python or to the tool box and choosing a tool
# getting the output and using it to give a final answer


import tkinter as tk
import threading
import pygame
import sys


def launch_game():
    # Start the Pygame game in a separate thread so that Tkinter remains responsive.
    game_thread = threading.Thread(target=run_game, daemon=True)
    game_thread.start()


def run_game():
    # Initialize Pygame and create a window.
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Pygame Launched from Tkinter")
    clock = pygame.time.Clock()

    # Starting position for a moving rectangle.
    rect_x = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update the rectangle's position.
        rect_x += 5
        if rect_x > 640:
            rect_x = 0

        # Fill the screen with black and draw a red rectangle.
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 0, 0), (rect_x, 200, 50, 50))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


# Create a basic Tkinter window with a button.
root = tk.Tk()
root.title("Tkinter Launch Pygame")

launch_button = tk.Button(root, text="Launch Pygame Game", command=launch_game)
launch_button.pack(padx=20, pady=20)

root.mainloop()

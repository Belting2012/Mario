import sounddevice as sd
import numpy as np
from pygame import *
from random import randint

# ====== АУДІО ======
sr = 16000
block = 256
mic_level = 0.0


def audio_cb(indata, frames, time, status):
    global mic_level
    if status:
        return
    rms = float(np.sqrt(np.mean(indata ** 2)))
    mic_level = 0.85 * mic_level + 0.15 * rms


init()
window_size = 1200, 800
window = display.set_mode(window_size)
clock = time.Clock()

# ====== ЗАВАНТАЖЕННЯ КАРТИНОК ======
try:
    bg_img = image.load('background.jpg')
    bg_img = transform.scale(bg_img, window_size)
except:
    bg_img = None

try:
    player_img = image.load('bird.png')
    player_img = transform.scale(player_img, (100, 100))
except:
    player_img = None

try:
    pipe_img = image.load('pipe.png')
    pipe_img = transform.scale(pipe_img, (140, 600))
except:
    pipe_img = None

player_rect = Rect(150, window_size[1] // 2 - 100, 100, 100)


def generate_pipes(count, pipe_width=140, gap=280, min_height=50, max_height=440, distance=650):
    pipes = []
    start_x = window_size[0]
    for i in range(count):
        height = randint(min_height, max_height)
        top_pipe = Rect(start_x, 0, pipe_width, height)
        bottom_pipe = Rect(start_x, height + gap, pipe_width, window_size[1] - (height + gap))
        pipes.extend([top_pipe, bottom_pipe])
        start_x += distance
    return pipes


pies = generate_pipes(150)
main_font = font.Font(None, 100)
score = 0
lose = False
wait = 40

y_vel = 0.0
gravity = 0.6
THRESH = 0.001
IMPULSE = -8.0

with sd.InputStream(samplerate=sr, channels=1, blocksize=block, callback=audio_cb):
    while True:
        for e in event.get():
            if e.type == QUIT:
                quit()

        # ЛОГІКА РУХУ
        if mic_level > THRESH:
            y_vel = IMPULSE
        y_vel += gravity
        player_rect.y += int(y_vel)

        # МАЛЮВАННЯ ФОНУ
        if bg_img:
            window.blit(bg_img, (0, 0))
        else:
            window.fill('sky blue')

        # МАЛЮВАННЯ ГРАВЦЯ
        if player_img:
            window.blit(player_img, player_rect)
        else:
            draw.rect(window, 'red', player_rect)

        # МАЛЮВАННЯ ТРУБ
        for i, pie in enumerate(pies[:]):
            if not lose:
                pie.x -= 10

            if pipe_img:
                # Верхня труба (перевернута)
                if i % 2 == 0:
                    rotated = transform.flip(pipe_img, False, True)
                    scaled = transform.scale(rotated, (pie.width, pie.height))
                    window.blit(scaled, pie)
                # Нижня труба (звичайна)
                else:
                    scaled = transform.scale(pipe_img, (pie.width, pie.height))
                    window.blit(scaled, pie)
            else:
                draw.rect(window, 'green', pie)

            if pie.x <= -100:
                pies.remove(pie)
                score += 0.5
            if player_rect.colliderect(pie):
                lose = True

        if len(pies) < 8:
            pies += generate_pipes(150)

        score_text = main_font.render(f'{int(score)}', 1, 'white')
        window.blit(score_text, (window_size[0] // 2 - score_text.get_rect().w // 2, 40))

        display.update()
        clock.tick(60)

        keys = key.get_pressed()
        if keys[K_r] and lose:
            lose = False
            score = 0
            pies = generate_pipes(150)
            player_rect.y = window_size[1] // 2 - 100
            y_vel = 0.0

        if player_rect.bottom > window_size[1]:
            player_rect.bottom = window_size[1]
            y_vel = 0.0
        if player_rect.top < 0:
            player_rect.top = 0
            if y_vel < 0:
                y_vel = 0.0

        if lose and wait > 1:
            for pie in pies:
                pie.x += 8
            wait -= 1
        else:
            lose = False
            wait = 40
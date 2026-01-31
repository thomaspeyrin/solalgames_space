import pygame
import random
from pygame.locals import *
import asyncio 
import sys

class GAME:
    SPACESHIP_SPEED = 300.0 # spaceship speed
    INVICIBILITY_DURATION = 1000  # invincibility duration in milliseconds when hit
    BOOST_DURATION = 500  # boost duration in milliseconds

    SPEED_MISSILE = 600.0 # missile speed
    
    SPEED_NUCLEAR = 200.0 # radius growth per second of the nuclear bomb
    NUCLEAR_MAX_RADIUS = 300 # maximum radius of the nuclear bomb
    
    SPEED_ENEMIES = 100.0 # enemy speed
    ENEMIES_FREQUENCY = 2000  # milliseconds
    
    ENEMY_BULLET_SPEED = 175.0
    ENEMY_BALLS_SPEED = 100.0
    BALLS_DURATION = 5000  # milliseconds
    
    ENEMIES_MISSILES_PROBABILITY = 0.5  # probability per second (≈0.002 per frame at 60 FPS)
    ENEMIES_BALLS_PROBABILITY = 0.2  # probability per second (≈0.001 per frame at 60 FPS) 

    BONUS_DURATION = 5000  # bonus appearance duration in milliseconds
    BONUS_PROBABILITY = 0.1  # probability of bonus per enemy death
    
    MAX_LIVES = 5  # maximum number of lives
    START_CONFIG = (5, 3, 1)  # starting lives, boosts, nuclear bombs

    def __init__(self, screen, img_spaceship_height):
        self.missiles = []
        self.nuclear = []
        self.enemies = []
        self.enemies_missiles = []
        self.bonus = []
        self.spawn_ratio = 1.0
        self.time_last_enemy = 0
        self.score = 0
        self.lives, self.boosts, self.nuclear_bombs = self.START_CONFIG
        self.spaceship_coord_x = screen.get_width()//2
        self.spaceship_coord_y = screen.get_height() - img_spaceship_height//2 - 10
        self.invicibility = None

def display_namebox(screen, font, font_small, screen_width, screen_height, img_background, name_text=""):
    screen.blit(img_background, (0, 0))
    screen.blit(font_small.render("Enter your name:", True, (255, 255, 255)), (screen_width//2 - 60, screen_height//2 + 70))
    rectangle = pygame.Rect(screen_width//2 -60, screen_height//2 + 100, 140, 35)
    pygame.draw.rect(screen, (255, 255, 255), rectangle, 2)
    screen.blit(font_small.render(name_text, True, (255, 255, 255)), (screen_width//2 + -50, screen_height//2 + 110))
    pygame.display.flip()

def display_leaderboard(screen, font, font_small, screen_width, screen_height, leaderboard):
    leaderboard_text = font.render("Leaderboard (Top Scores):", True, (255, 255, 0))
    screen.blit(leaderboard_text, (3*screen_width//4 - leaderboard_text.get_width()//2, screen_height//2 + 90))
    for i, r in enumerate(leaderboard):
        score_text = font_small.render(str(r[0]) + ": " + r[1], True, (255, 255, 255))
        screen.blit(score_text, (3*screen_width//4 - score_text.get_width()//2, screen_height//2 + 100 + (i+1)*30))

def display_commands(screen, font, font_small, screen_width, screen_height):
    command_text = font.render("Controls:", True, (0, 255, 255))
    screen.blit(command_text, (screen_width//4 - command_text.get_width()//2, screen_height//2 + 90))
    controls_text = font_small.render("Arrow keys to move", True, (0, 255, 255))
    screen.blit(controls_text, (screen_width//4 - controls_text.get_width()//2, screen_height//2 + 130))
    controls_text2 = font_small.render("W to shoot", True, (0, 255, 255))
    screen.blit(controls_text2, (screen_width//4 - controls_text2.get_width()//2, screen_height//2 + 170))
    controls_text3 = font_small.render("E for boost", True, (0, 255, 255))
    screen.blit(controls_text3, (screen_width//4 - controls_text3.get_width()//2, screen_height//2 + 210))
    controls_text4 = font_small.render("Q for nuclear bomb", True, (0, 255, 255))
    screen.blit(controls_text4, (screen_width//4 - controls_text4.get_width()//2, screen_height//2 + 250))

def display_menu(screen, font, font_small, screen_width, screen_height, img_background, leaderboard, score=None):
    screen.blit(img_background, (0, 0))
    if score != None:
        game_over_text = font.render("Game Over! Your final score is: " + str(score), True, (255, 0, 0))
        screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, screen_height//4 ))
        if score == int(leaderboard[0][0]):
            screen.blit(font.render("New record !", True, (255, 215, 0)), (screen_width//2 - 80, screen_height//4 + 30))
    display_leaderboard(screen, font, font_small, screen_width, screen_height, leaderboard)
    display_commands(screen, font, font_small, screen_width, screen_height)
    pause_text = font.render("Press ENTER to start/restart or ESC to quit.", True, (255, 255, 255))
    screen.blit(pause_text, (screen_width//2 - pause_text.get_width()//2, screen_height//2 - pause_text.get_height()//2))            
    pygame.display.flip()

def update_leaderboard(score, leaderboard, name="Anonymous"):
    leaderboard.append([str(score), name])
    leaderboard.sort(key=lambda x: int(x[0]), reverse=True)
    if len(leaderboard) > 5: leaderboard.pop()
    with open("record_score.txt", "w") as f:
        for entry in leaderboard:
            f.write(entry[0] + " " + entry[1] + "\n")

async def main():
    print("Hello c'est Solal ! Bienvenue dans mon jeu.")

    await asyncio.sleep(0)

    # Read the record score from file
    try:
        my_file = open("record_score.txt", "r")
        leaderboard = [[l.split()[0], l.split()[1]] for l in my_file.read().splitlines()]
        my_file.close()
    except (FileNotFoundError, ValueError):
        my_file = open("record_score.txt", "w")
        my_file.write("0 Anonymous")
        leaderboard = [[0, "Anonymous"]]
        my_file.close()

    # Initialize Pygame
    pygame.init()

    # Set up the game window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Hello je suis le createur du jeu, Solal!")
    screen_height = screen.get_height()
    screen_width = screen.get_width()   
    clock = pygame.time.Clock()  # use to cap FPS and get time delta (dt)

    
    def load_sound(path, vol=0.7):
        try:
            s = pygame.mixer.Sound(path)
            s.set_volume(vol)
            return s
        except Exception as e:
            print(f"Warning: could not load sound {path}: {e}")
            return None

    def try_load_music(path, vol=0.5, loop=True):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(vol)
            if loop:
                pygame.mixer.music.play(-1)
            return True
        except Exception as e:
            print(f"Warning: could not load music {path}: {e}")
            return False

    # load music file
    try_load_music("sons/musique.wav", 0.5, loop=True)

    # load sound effects safely
    son_explosion = load_sound("sons/explosion.wav", 0.7)
    son_boost = load_sound("sons/boost.wav", 0.7)
    son_nuclear = load_sound("sons/nuclear.wav", 0.7)
    son_blaster = []
    son_blaster.append(load_sound("sons/tir1.wav", 0.3))
    son_blaster.append(load_sound("sons/tir2.wav", 0.3))
    
    # Load fonts
    font = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)

    # Load images
    img_background = pygame.image.load("images/background_1.png").convert()
    img_background = img_background.subsurface((0, 0, screen_width, screen_height))
    
    img_spaceship = pygame.image.load("images/spaceship.png").convert_alpha()
    img_spaceship = pygame.transform.scale(img_spaceship, (50,50))
    img_spaceship_width = img_spaceship.get_width()
    img_spaceship_height = img_spaceship.get_height() 

    img_enemy = [] 
    img_enemy.append(pygame.image.load("images/enemy1.png").convert_alpha())
    img_enemy.append(pygame.image.load("images/enemy2.png").convert_alpha())
    img_enemy.append(pygame.image.load("images/enemy3.png").convert_alpha())
    img_enemy.append(pygame.image.load("images/enemy4.png").convert_alpha())
    for i in range(len(img_enemy)):
        img_enemy[i] = pygame.transform.scale(img_enemy[i], (50,50))
    img_enemy_width = img_enemy[0].get_width()
    img_enemy_height = img_enemy[0].get_height()

    heart_full_image = pygame.image.load("images/heart_full.png").convert_alpha()
    heart_full_image = pygame.transform.scale(heart_full_image, (24, 19))
    heart_empty_image = pygame.image.load("images/heart_empty.png").convert_alpha() 
    heart_empty_image = pygame.transform.scale(heart_empty_image, (24, 19))
    lightning_image = pygame.image.load("images/lightning.png").convert_alpha()
    lightning_image = pygame.transform.scale(lightning_image, (24, 19))
    nuclear_image = pygame.image.load("images/nuclear.png").convert_alpha()
    nuclear_image = pygame.transform.scale(nuclear_image, (24, 19))   
    
    explosion_images = pygame.image.load("images/explosion_spritesheet.png").convert_alpha()
    # 64 images divided in an 8x6 grid, each 100x100 pixels in the original spritesheet
    explosion_frames = []
    for i in range(6):
        for j in range(8):
            frame = explosion_images.subsurface((30+j*100, 30+i*100, 100, 100))
            explosion_frames.append(pygame.transform.scale(frame, (50, 50)))
        
    # Key states and invincibility
    K_DOWN_PRESSED = K_UP_PRESSED = K_LEFT_PRESSED = K_RIGHT_PRESSED = K_w_PRESSED = K_e_PRESSED = K_q_PRESSED = False

    boost = None
    game_stopped = True
    game_over = False
    explosion = []
    name = None
    name_text = ""
    # Fallback for menu Enter handling (useful when browser canvas lacks keyboard focus)
    menu_return_pressed = False

    # Game loop
    running = True
    while running:
        # Cap frame rate and get time delta in seconds (dt)
        dt = clock.tick(60) / 1000.0

        if game_stopped == False:
            # if the user closes the window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # if the user presses a key
                if event.type == KEYDOWN:  
                    if event.key == K_LEFT: K_LEFT_PRESSED = True
                    elif event.key == K_RIGHT: K_RIGHT_PRESSED = True
                    elif event.key == K_UP: K_UP_PRESSED = True
                    elif event.key == K_DOWN: K_DOWN_PRESSED = True
                    elif event.key == K_ESCAPE:  
                        # Request quit and try a safe shutdown of audio/display to avoid hangs
                        running = False
                        try:
                            pygame.mixer.music.stop()
                        except Exception as _:
                            pass
                        try:
                            pygame.mixer.quit()
                        except Exception as _:
                            pass
                        try:
                            pygame.display.quit()
                        except Exception as _:
                            pass
                    elif event.key == K_w:
                        if not K_w_PRESSED:
                            g.missiles.append([g.spaceship_coord_x, g.spaceship_coord_y])
                            if son_blaster:
                                s = son_blaster[random.randint(0, len(son_blaster)-1)]
                                if s:
                                    s.play()
                        K_w_PRESSED = True
                    elif event.key == K_e:
                        if not K_e_PRESSED:
                            if g.boosts > 0:
                                g.boosts -= 1
                                boost = pygame.time.get_ticks()
                                if son_boost:
                                    son_boost.play()
                        K_e_PRESSED = True
                    elif event.key == K_q:
                        if not K_q_PRESSED:
                            if g.nuclear_bombs > 0:
                                g.nuclear_bombs -= 1
                                g.nuclear.append([g.spaceship_coord_x, g.spaceship_coord_y, 0])
                                if son_nuclear:
                                    son_nuclear.play()
                        K_q_PRESSED = True

                # if the user releases a key    
                if event.type == KEYUP: 
                    if event.key == K_w: K_w_PRESSED = False
                    elif event.key == K_e: K_e_PRESSED = False
                    elif event.key == K_q: K_q_PRESSED = False
                    elif event.key == K_LEFT: K_LEFT_PRESSED = False
                    elif event.key == K_RIGHT: K_RIGHT_PRESSED = False 
                    elif event.key == K_UP: K_UP_PRESSED = False
                    elif event.key == K_DOWN: K_DOWN_PRESSED = False

            # Update spaceship position based on key states (time-based)
            if boost != None:
                my_speed = g.SPACESHIP_SPEED * 2
            else:
                my_speed = g.SPACESHIP_SPEED
            if K_LEFT_PRESSED:  
                g.spaceship_coord_x -= my_speed * dt
                g.spaceship_coord_x = max(img_spaceship_width//2, g.spaceship_coord_x)
            if K_RIGHT_PRESSED:  
                g.spaceship_coord_x += my_speed * dt
                g.spaceship_coord_x = min(screen_width - img_spaceship_width//2, g.spaceship_coord_x)
            if K_UP_PRESSED: 
                g.spaceship_coord_y -= my_speed * dt
                g.spaceship_coord_y = max(img_spaceship_height//2, g.spaceship_coord_y)
            if K_DOWN_PRESSED: 
                g.spaceship_coord_y += my_speed * dt
                g.spaceship_coord_y = min(screen_height - img_spaceship_height//2, g.spaceship_coord_y) 

            # Update missile positions (time-based)
            for m in g.missiles:
                m[1] -= g.SPEED_MISSILE * dt
                if m[1] < 0:
                    g.missiles.remove(m)
            
            # Update nuclear bomb positions (time-based radius growth)
            for n in g.nuclear:
                n[2] += g.SPEED_NUCLEAR * dt
                if n[2] > g.NUCLEAR_MAX_RADIUS:
                    g.nuclear.remove(n)

            # Spawn enemies
            current_time = pygame.time.get_ticks()
            if current_time - g.time_last_enemy > g.ENEMIES_FREQUENCY / g.spawn_ratio:
                enemy_x = random.randint(img_enemy_width//2, screen_width - img_enemy_width//2)
                enemy_y = random.randint(img_enemy_height//2, screen_height- img_spaceship_height - img_enemy_height - 10)
                enemy_type = random.randint(0, len(img_enemy) - 1)
                g.enemies.append([enemy_x, enemy_y, enemy_type, []])
                g.time_last_enemy = current_time

            # Update enemy positions (time-based)
            for e in g.enemies:
                e[0] += random.uniform(-g.SPEED_ENEMIES, g.SPEED_ENEMIES) * dt
                e[1] += random.uniform(-g.SPEED_ENEMIES, g.SPEED_ENEMIES) * dt
                e[0] = max(img_enemy_width//2, min(screen_width - img_enemy_width//2, e[0]))
                e[1] = max(img_enemy_height//2, min(screen_height - img_enemy_height//2, e[1]))

            # spawn enemy bullets/balls (probabilities scaled with dt)
            for e in g.enemies:
                if random.random() < g.ENEMIES_MISSILES_PROBABILITY * dt:
                    direction_x = g.spaceship_coord_x - e[0]
                    direction_y = g.spaceship_coord_y - e[1]
                    length = (direction_x**2 + direction_y**2) ** 0.5
                    if length != 0:
                        g.enemies_missiles.append([e[0], e[1] + img_enemy_height//2, 1, [direction_x/length, direction_y/length]])  # bullet
                if random.random() < g.ENEMIES_BALLS_PROBABILITY * dt:
                    g.enemies_missiles.append([e[0], e[1] + img_enemy_height//2, 2, [], pygame.time.get_ticks()])  # ball

            # Update enemy bullet/balls positions (time-based)
            for em in g.enemies_missiles:            
                if em[2] == 1:  # bullet
                    em[0] += em[3][0] * g.ENEMY_BULLET_SPEED * dt
                    em[1] += em[3][1] * g.ENEMY_BULLET_SPEED * dt
                    if em[0] < 0 or em[0] > screen_width or em[1] < 0 or em[1] > screen_height:
                        g.enemies_missiles.remove(em)
                elif em[2] == 2:  # ball
                    if pygame.time.get_ticks() - em[4] > g.BALLS_DURATION:
                        g.enemies_missiles.remove(em)
                    else:
                        direction_x = g.spaceship_coord_x - em[0]
                        direction_y = g.spaceship_coord_y - em[1]
                        length = (direction_x**2 + direction_y**2) ** 0.5
                        if length != 0:
                            direction_x /= length
                            direction_y /= length
                        em[0] += direction_x * g.ENEMY_BALLS_SPEED * dt
                        em[1] += direction_y * g.ENEMY_BALLS_SPEED * dt
                        if em[0] < 0 or em[0] > screen_width or em[1] < 0 or em[1] > screen_height:
                            g.enemies_missiles.remove(em)

            # check for missile-enemy collisions
            for m in g.missiles:
                for e in g.enemies:
                    if (e[0] - img_enemy_width//2 < m[0] < e[0] + img_enemy_width//2) and (e[1] - img_enemy_height//2 < m[1] < e[1] + img_enemy_height//2):
                        g.enemies.remove(e)
                        g.missiles.remove(m)
                        g.score += 1
                        if son_explosion:
                            son_explosion.play()
                        explosion.append([e[0] - 32, e[1] - 32, 0, pygame.time.get_ticks()])  
                        # spawn bonus with certain probability
                        if random.random() < g.BONUS_PROBABILITY:
                            bonus_type = random.choice(["life", "boost", "nuclear"])
                            g.bonus.append([e[0], e[1], bonus_type, pygame.time.get_ticks()])
                        break
            
            # check for nuclear bomb-enemy collisions
            for n in g.nuclear: 
                for e in g.enemies:
                    distance = ((e[0] - n[0])**2 + (e[1] - n[1])**2) ** 0.5
                    if distance < n[2]:
                        g.enemies.remove(e)
                        g.score += 1
                        if son_explosion:
                            son_explosion.play()
                        explosion.append([e[0] - 32, e[1] - 32, 0, pygame.time.get_ticks()])  

            # check for bonus-spaceship collisions
            for b in g.bonus:
                if (g.spaceship_coord_x - img_spaceship_width//2 < b[0] < g.spaceship_coord_x + img_spaceship_width//2) and (g.spaceship_coord_y - img_spaceship_height//2 < b[1] < g.spaceship_coord_y + img_spaceship_height//2):
                    if b[2] == "life":
                        if g.lives < g.MAX_LIVES:
                            g.lives += 1
                    elif b[2] == "boost":
                        g.boosts += 1
                    elif b[2] == "nuclear":
                        g.nuclear_bombs += 1
                    g.bonus.remove(b)
                    break

            # check for bonus expiration
            for b in g.bonus:
                if pygame.time.get_ticks() - b[3] > g.BONUS_DURATION:
                    g.bonus.remove(b)

            if g.invicibility == None:
                # check for enemy-spaceship collisions
                for e in g.enemies:
                    if (g.spaceship_coord_x - img_spaceship_width//2 < e[0] < g.spaceship_coord_x + img_spaceship_width//2) and (g.spaceship_coord_y - img_spaceship_height//2 < e[1] < g.spaceship_coord_y + img_spaceship_height//2):
                        g.enemies.remove(e)
                        g.lives -= 1
                        if son_explosion:
                            son_explosion.play()
                        g.invicibility = pygame.time.get_ticks()
                        break

                # check for enemy bullet/ball - spaceship collisions
                for em in g.enemies_missiles:   
                    if (g.spaceship_coord_x - img_spaceship_width//2 < em[0] < g.spaceship_coord_x + img_spaceship_width//2) and (g.spaceship_coord_y - img_spaceship_height//2 < em[1] < g.spaceship_coord_y + img_spaceship_height//2):
                        g.enemies_missiles.remove(em)
                        g.lives -= 1
                        if son_explosion:
                            son_explosion.play()
                        g.invicibility = pygame.time.get_ticks()
                        break
                if g.lives <= 0:
                    game_over, game_stopped = True, True   
                    update_leaderboard(g.score, leaderboard, name)
            else:
                if pygame.time.get_ticks() - g.invicibility > g.INVICIBILITY_DURATION:
                    g.invicibility = None
            if boost != None:
                if pygame.time.get_ticks() - boost > g.BOOST_DURATION:
                    boost = None

            # increase spawn ratio over time to make game harder
            g.spawn_ratio += 0.01 * dt

            # Draw everything
            screen.blit(img_background, (0, 0))
            
            if g.invicibility == None:
                screen.blit(img_spaceship, (g.spaceship_coord_x - img_spaceship_width//2, g.spaceship_coord_y - img_spaceship_height//2))
            else:
                if (pygame.time.get_ticks() // 200) % 2 == 0:
                    screen.blit(img_spaceship, (g.spaceship_coord_x - img_spaceship_width//2, g.spaceship_coord_y - img_spaceship_height//2))
            
            for e in g.enemies:
                screen.blit(img_enemy[e[2]], (e[0] - img_enemy_width//2, e[1] - img_enemy_height//2))
            
            for em in g.enemies_missiles:  
                if em[2] == 1:  # bullet
                    pygame.draw.line(screen, (0, 255, 0), (em[0], em[1]), (em[0] + em[3][0]*10, em[1] + em[3][1]*10), 3)
                elif em[2] == 2:  # ball
                    pygame.draw.circle(screen, (0, 0, 255), (int(em[0]), int(em[1])), 5)

            for m in g.missiles:
                pygame.draw.line(screen, (255, 127, 80), (m[0], m[1]), (m[0], m[1] + 10), 3)
            
            for n in g.nuclear:
                pygame.draw.circle(screen, (255, 255, 0), (int(n[0]), int(n[1])), int(n[2]), 2)

            # Display bonus
            for b in g.bonus:
                if b[2] == "life":
                    screen.blit(heart_full_image, (b[0] - 12, b[1] - 10))
                elif b[2] == "boost":
                    screen.blit(lightning_image, (b[0] - 12, b[1] - 10))
                elif b[2] == "nuclear":
                    screen.blit(nuclear_image, (b[0] - 12, b[1] - 10))

            # Display score
            score_text = font.render(f"Score: {g.score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))
            record_score_text = font.render(f"Record: {max(int(leaderboard[0][0]), g.score)}", True, (255, 255, 255))
            screen.blit(record_score_text, (10, 50))
            
            # display lives as heart images on the right
            for i in range(g.MAX_LIVES):
                if i < g.lives:
                    screen.blit(heart_full_image, (750 - i*30, 10))
                else:
                    screen.blit(heart_empty_image, (750 - i*30, 10))
            
            # display boosts as lightning on the right
            for i in range(g.boosts):
                screen.blit(lightning_image, (750 - i*30, 40))

            # display nuclear bombs as nuclear sign on the right
            for i in range(g.nuclear_bombs):
                screen.blit(nuclear_image, (750 - i*30, 70))
                
            # display explosions
            for ex in explosion:
                frame_index = (pygame.time.get_ticks() - ex[3]) // 5
                if frame_index < len(explosion_frames):
                    screen.blit(explosion_frames[frame_index], (ex[0], ex[1]))
                else:
                    explosion.remove(ex)

            # Update the display
            pygame.display.flip()
    
        elif name != None:
            # Game is stopped, wait for user input to restart or quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        g = GAME(screen, img_spaceship_height)
                        game_stopped = False
                        game_over = False
                        K_DOWN_PRESSED = K_UP_PRESSED = K_LEFT_PRESSED = K_RIGHT_PRESSED = K_w_PRESSED = K_e_PRESSED = K_q_PRESSED = False
                    elif event.key == K_ESCAPE:
                        # Request quit from menu and attempt safe shutdown
                        running = False
                        try:
                            pygame.mixer.music.stop()
                        except Exception:
                            pass
                        try:
                            pygame.mixer.quit()
                        except Exception:
                            pass
                        try:
                            pygame.display.quit()
                        except Exception:
                            pass

            # Fallback: poll the key state for K_RETURN (and ESC) — helps when the canvas doesn't have focus in the browser
            keys = pygame.key.get_pressed()
            if keys[K_RETURN] and not menu_return_pressed:
                g = GAME(screen, img_spaceship_height)
                game_stopped = False
                game_over = False
                K_DOWN_PRESSED = K_UP_PRESSED = K_LEFT_PRESSED = K_RIGHT_PRESSED = K_w_PRESSED = K_e_PRESSED = K_q_PRESSED = False
                menu_return_pressed = True
            elif not keys[K_RETURN]:
                menu_return_pressed = False

            # Poll ESC as fallback to quit
            if keys[K_ESCAPE]:
                running = False
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                try:
                    pygame.mixer.quit()
                except Exception:
                    pass
                try:
                    pygame.display.quit()
                except Exception:
                    pass

            if game_over == False:
                display_menu(screen, font, font_small, screen_width, screen_height, img_background, leaderboard)
            else:
                display_menu(screen, font, font_small, screen_width, screen_height, img_background, leaderboard, score=g.score)
        else:
            # Game is stopped, wait for user input to type his name
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        if name_text.strip() != "":
                            name = name_text
                        else:
                            name = "Anonymous"
                        name_text = ""
                    elif event.key == K_BACKSPACE:
                        name_text = name_text[:-1]
                    else:
                        name_text += event.unicode

            display_namebox(screen, font, font_small, screen_width, screen_height, img_background, name_text)

        await asyncio.sleep(0)

    # Quit Pygame
    if 'pygbag' not in sys.modules:
        pygame.quit()

asyncio.run(main())
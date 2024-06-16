
import pygame
import math
import time
import asyncio 

class Button:
    def __init__(self, x, y, width, height, color, hover_color, text, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.font = font
        self.is_hovered = False

    def draw(self, window):
        outline_rect = self.rect.inflate(10, 10)
        pygame.draw.rect(window, (0, 0, 0), outline_rect) 
        if self.is_hovered:
            pygame.draw.rect(window, self.hover_color, self.rect)
        else:
            pygame.draw.rect(window, self.color, self.rect)
        
        font_surface = self.font.render(self.text, True, self.text_color)
        font_rect = font_surface.get_rect(center=self.rect.center)
        window.blit(font_surface, font_rect)

    def update(self, pos):
        if self.rect.collidepoint(pos):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, window):
        pygame.draw.rect(window, (255, 0, 0), self.rect)
        
    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)


class Obstacle_rotating:
    def __init__(self, x, y, width, height, color=(255, 0, 0), rotation_speed=0.1, initial_angle=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width * 2, height * 2), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, color, (0, 0, width * 2, height * 2))
        self.surface = pygame.transform.smoothscale(self.surface, (width, height))
        self.angle = initial_angle
        self.rotation_speed = rotation_speed 
        self.mask = pygame.mask.from_surface(self.surface)
        self.rotated_surface = None
        self.rotated_rect = None

    def rotate(self):
        self.angle += self.rotation_speed
        if abs(self.angle) >= 360:
            self.angle = 0
        self.rotated_surface = pygame.transform.rotate(self.surface, self.angle)
        self.mask = pygame.mask.from_surface(self.rotated_surface)
        self.rotated_rect = self.rotated_surface.get_rect(center=self.rect.center)

    def draw(self, window):
        window.blit(self.rotated_surface, self.rotated_rect.topleft)
    
    def check_collision(self, player_mask, player_rect):
        offset = player_rect.topleft[0] - self.rotated_rect.topleft[0], player_rect.topleft[1] - self.rotated_rect.topleft[1]
        overlap = self.mask.overlap(player_mask, offset)
        return overlap is not None

class Obstacle_oscillating:
    def __init__(self, x, y, width, height, amplitude=50, frequency=0.05, direction=0, type=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.start_y = y
        self.start_x = x
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0
        self.direction = direction
        self.type = type
    def update(self):
        self.time += 1
        if self.direction == 0:
            if self.type == 0:
                self.rect.y = self.start_y + self.amplitude * math.sin(self.frequency * self.time)
            else:
                self.rect.y = self.start_y + self.amplitude * math.cos(self.frequency * self.time)
        elif self.direction == 1:
            if self.type == 0:
                self.rect.x = self.start_x + self.amplitude * math.sin(self.frequency * self.time)
            else:
                self.rect.x = self.start_x + self.amplitude * math.cos(self.frequency * self.time)
        else:
            if self.type == 0:
                self.rect.y = self.start_y + self.amplitude * math.sin(self.frequency * self.time)
                self.rect.x = self.start_x + self.amplitude * math.sin(self.frequency * self.time)
            else:
                self.rect.y = self.start_y + self.amplitude * math.cos(self.frequency * self.time)
                self.rect.x = self.start_x + self.amplitude * math.cos(self.frequency * self.time)
    def draw(self, window):
        pygame.draw.rect(window, (255, 0, 0), self.rect)

    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
    
class Speed_boost:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, window):
        pygame.draw.rect(window, (0, 0, 255), self.rect)
        
    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
    
class Speed_hinder:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, window):
        pygame.draw.rect(window, (165, 42, 42), self.rect)
        
    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
    
class Obstacle_circular:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, window):
        pygame.draw.circle(window, (255, 0, 0), (self.x, self.y), self.radius)
        
    def check_collision(self, player_rect):
        player_center_x = player_rect.centerx
        player_center_y = player_rect.centery
        distance = math.sqrt((player_center_x - self.x) ** 2 + (player_center_y - self.y) ** 2)
        return distance < self.radius + max(player_rect.width, player_rect.height) / 2

class Obstacle_oscillating_circular:
    def __init__(self, x, y, radius, amplitude=50, frequency=0.05, direction=0, type=0):
        self.start_y = y
        self.start_x = x
        self.x = x
        self.y = y
        self.radius = radius
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0
        self.direction = direction
        self.type = type
    def update(self):
        self.time += 1
        if self.direction == 0:
            if self.type == 0:
                self.x = self.start_y + self.amplitude * math.sin(self.frequency * self.time)
            else:
                self.y = self.start_y + self.amplitude * math.cos(self.frequency * self.time)
        elif self.direction == 1:
            if self.type == 0:
                self.x = self.start_x + self.amplitude * math.sin(self.frequency * self.time)
            else:
                self.x = self.start_x + self.amplitude * math.cos(self.frequency * self.time)
        else:
            if self.type == 0:
                self.y = self.start_y + self.amplitude * math.sin(self.frequency * self.time)
                self.x = self.start_x + self.amplitude * math.sin(self.frequency * self.time)
            else:
                self.y = self.start_y + self.amplitude * math.cos(self.frequency * self.time)
                self.x = self.start_x + self.amplitude * math.cos(self.frequency * self.time)
    def draw(self, window):
        pygame.draw.circle(window, (255, 0, 0), (self.x, self.y), self.radius)

    def check_collision(self, player_rect):
        player_center_x = player_rect.centerx
        player_center_y = player_rect.centery
        distance = math.sqrt((player_center_x - self.x) ** 2 + (player_center_y - self.y) ** 2)
        return distance < self.radius + max(player_rect.width, player_rect.height) / 2

    
class End:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, window):
        pygame.draw.rect(window, (0, 255, 0), self.rect)
        
    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)

pygame.init()
pygame.mixer.init()

async def main():
    button_click_sound = pygame.mixer.Sound("Audio/Game sounds/button hover2.wav")
    level_end_sound = pygame.mixer.Sound("Audio/Game sounds/Flag2.wav")
    player_death_sound = pygame.mixer.Sound("Audio/Game sounds/Crunch.wav")
    End_song = pygame.mixer.Sound("Audio/Music/A blue bat.wav")

    sound_files = ["Audio/Music/Staring.wav", "Audio/Music/Bloop.wav", "Audio/Music/Bass.wav"]
    sounds = [pygame.mixer.Sound(sound) for sound in sound_files]

    channel = pygame.mixer.Channel(0)
    playing = True
    current_sound = 0

    channel1 = pygame.mixer.Channel(1)

    window = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Bob's Trials")

    font = pygame.font.Font(None, 36)

    level = 1
    deaths = 0

    Title = pygame.image.load("graphics/383947B3-D823-4E3F-A9F7-96648DDE0AA7.jpeg")
    Title_resized = pygame.transform.scale(Title, (800, 130))

    Background = pygame.image.load("graphics/D018A70E-9054-4B72-9188-BD4AEFFBF446.jpeg")

    End_animation1 = pygame.image.load("graphics/End animation/97CAFAF8-65AA-4AFA-94EC-EBA7D0E12409.jpeg")
    End_animation1_resized = pygame.transform.scale(End_animation1, (800, 600))
    End_animation2 = pygame.image.load("graphics/End animation/5E65A2B0-B6EB-4090-B32F-333573299F1F.jpeg")
    End_animation2_resized = pygame.transform.scale(End_animation2, (800, 600))
    End_animation3 = pygame.image.load("graphics/End animation/BB4B0F08-B010-4818-87D3-F2175F845B59.jpeg")
    End_animation3_resized = pygame.transform.scale(End_animation3, (800, 600))

    Player = pygame.image.load("graphics/costume1.svg")
    player_width = Player.get_width()
    player_height = Player.get_height()
    respawnx = 25
    respawny = 600 - player_height
    x = respawnx
    y = respawny
    player_rect = pygame.Rect(x, y, player_width, player_height)
    player_mask = pygame.mask.from_surface(Player)

    obstacles1 = [
        Obstacle(80, 300, 30, 300),
        Obstacle(50, 0, 120, 280),
        Obstacle(130, 0, 60, 580),
        Obstacle(210, 20, 120, 580),
        Obstacle(350, 0, 60, 580)
    ]

    obstacles2 = [
        Obstacle(80, 300, 30, 300),
        Obstacle(80, 0, 30, 280),
        Obstacle(650, 0, 30, 280),
        Obstacle(650, 300, 30, 300)
    ]

    obstacles3 = [
        Obstacle(80, 300, 30, 300),
        Obstacle(50, 0, 600, 280),
        Obstacle(130, 0, 60, 580),
        Obstacle(210, 300, 120, 300),
        Obstacle(350, 0, 60, 580),
        Obstacle(430, 300, 30, 300),
    ]

    obstacles4 = [
        Obstacle(100, 0, 80, 60)
    ]

    obstacles6 = [
        Obstacle(80, 300, 30, 300),
        Obstacle(80, 0, 30, 280),
        Obstacle(650, 0, 30, 280),
        Obstacle(650, 300, 30, 300)
    ]

    obstacles7 = [
        Obstacle(80, 300, 30, 300),
        Obstacle(80, 0, 30, 280),
        Obstacle(650, 0, 30, 280),
        Obstacle(650, 300, 30, 300)
    ]

    obstacles8 = [
        Obstacle(80, 0, 30, 580),
        Obstacle(130, 20, 30, 580),
        Obstacle(180, 0, 30, 580),
        Obstacle(230, 20, 30, 580),
        Obstacle(280, 0, 30, 580),
        Obstacle(330, 20, 30, 580),
        Obstacle(380, 0, 30, 580),
        Obstacle(430, 20, 30, 580),
        Obstacle(480, 0, 30, 580),
        Obstacle(530, 20, 30, 580),
        Obstacle(580, 0, 30, 580),
        Obstacle(630, 20, 30, 580)
    ]

    obstacles9 = [
        Obstacle(100, 0, 160, 60),
        Obstacle(480, 20, 30, 580),
        Obstacle(530, 0, 30, 580),
        Obstacle(580, 20, 30, 580),
        Obstacle(630, 0, 30, 580)
    ]

    obstacles10 = [
        Obstacle(80, 0, 30, 580),
        Obstacle(130, 20, 30, 580),
        Obstacle(180, 0, 420, 140)
    ]

    obstacles11 = [
        Obstacle(400, 20, 200, 580),
        Obstacle(0, 20, 120, 100)
    ]

    obstacles12 = [
        Obstacle(530, 20, 30, 580),
        Obstacle(580, 0, 30, 580),
        Obstacle(630, 20, 30, 580)
    ]

    obstacles_rotating1 = [
        Obstacle_rotating(250, 100, 30, 300, rotation_speed = -0.1),
        Obstacle_rotating(250, 100, 30, 300, rotation_speed = -0.1, initial_angle = 90),
        Obstacle_rotating(600, 150, 60, 300, rotation_speed = -1)
    ]

    obstacles_rotating2 = [
        Obstacle_rotating(350, 20, 60, 560, rotation_speed = 2),
        Obstacle_rotating(350, 20, 60, 560, rotation_speed = -2)
    ]

    obstacles_rotating3 = [
        Obstacle_rotating(600, 280, 60, 320, rotation_speed = -2),
        Obstacle_rotating(600, 280, 60, 320, rotation_speed = -2, initial_angle = 90)
    ]

    obstacles_rotating4 = [
        Obstacle_rotating(250, 50, 60, 250, rotation_speed = 0.1),
        Obstacle_rotating(250, 50, 60, 250, rotation_speed = -0.1),
        Obstacle_rotating(500, 0, 60, 580, rotation_speed = -1),
        Obstacle_rotating(500, 0, 60, 580, rotation_speed = -1, initial_angle = 90)
    ]

    obstacles_rotating5 = [
        Obstacle_rotating(100, 300, 60, 300, rotation_speed = 3),
        Obstacle_rotating(600, 150, 60, 300, rotation_speed = -2),
        Obstacle_rotating(600, 150, 60, 300, rotation_speed = -2, initial_angle = 90)
    ]

    obstacles_rotating6 = [
        Obstacle_rotating(370, 20, 60, 540, rotation_speed = -2),
        Obstacle_rotating(370, 20, 60, 540, rotation_speed = -2, initial_angle=90),
        Obstacle_rotating(800, 280, 60, 320, rotation_speed = 2),
        Obstacle_rotating(800, 280, 60, 320, rotation_speed = 2, initial_angle = 90)
    ]

    obstacles_rotating7 = [
        Obstacle_rotating(340, 200, 60, 580, rotation_speed = -1),
        Obstacle_rotating(340, 200, 60, 580, rotation_speed = -1, initial_angle=90),
        Obstacle_rotating(340, -200, 60, 580, rotation_speed = 1),
        Obstacle_rotating(340, -200, 60, 580, rotation_speed = 1, initial_angle=90),
        Obstacle_rotating(800, 280, 60, 320, rotation_speed = 2),
        Obstacle_rotating(800, 280, 60, 320, rotation_speed = 2, initial_angle = 90)
    ]

    obstacles_rotating9 = [
        Obstacle_rotating(485, 300, 20, 120, rotation_speed = -1),
        Obstacle_rotating(585, 300, 20, 120, rotation_speed = 1),
        Obstacle_rotating(750, 400, 20, 200, rotation_speed = -1),
        Obstacle_rotating(750, 400, 20, 200, rotation_speed = -1, initial_angle=90)
    ]

    obstacles_rotating10 = [
        Obstacle_rotating(400, 200, 10, 120, rotation_speed = 2),
        Obstacle_rotating(220, 370, 30, 180, rotation_speed = 2),
        Obstacle_rotating(220, 370, 30, 180, rotation_speed = 2, initial_angle=90)
    ]

    obstacles_rotating11 = [
        Obstacle_rotating(625, 150, 10, 200, rotation_speed = -3),
        Obstacle_rotating(755, 150, 10, 200, rotation_speed = 3),
        Obstacle_rotating(685, 450, 10, 200, rotation_speed = -2),
        Obstacle_rotating(685, 450, 10, 200, rotation_speed = -2, initial_angle = 90)
    ]

    obstacles_rotating12 = [
        Obstacle_rotating(160, 480, 250, 60, rotation_speed = 0, initial_angle=45),
        Obstacle_rotating(280, 190, 60, 250, rotation_speed = 0, initial_angle=45),
        Obstacle_rotating(400, 190, 10, 120, rotation_speed = -2)
    ]

    obstacles_oscillating4 = [
        Obstacle_oscillating(100, 0, 80, 600, amplitude=50, frequency=0.1),
        Obstacle_oscillating(200, 0, 80, 600, amplitude=50, frequency=0.1),
    ]

    obstacles_oscillating5 = [
        Obstacle_oscillating(240, 300, 60, 300, amplitude=190, frequency=0.05, direction = 1),
        Obstacle_oscillating(240, 0, 60, 300, amplitude=190, frequency=0.05, direction = 1, type = 1),
        Obstacle_oscillating(240, 240, 200, 60, amplitude = 300, frequency=0.02)
    ]

    obstacles_oscillating7 = [
        Obstacle_oscillating(280, 270, 120, 30),
    ]

    obstacles_oscillating9 = [
        Obstacle_oscillating(100, 0, 160, 600, amplitude=50, frequency=0.1),
        Obstacle_oscillating(290, 0, 160, 600, amplitude=50, frequency=0.1, direction = 0, type = 1),
    ]

    obstacles_oscillating10 = [
        Obstacle_oscillating(480, 0, 120, 580, amplitude=50, frequency=0.1)
    ]

    obstacles_oscillating11 = [
        Obstacle_oscillating(0, 20, 400, 100, amplitude=50, frequency=0.1, direction = 1)
    ]

    speed_boosts9 = [
        Speed_boost(100, 570, 160, 30),
        Speed_boost(290, 0, 160, 30),
        Speed_boost(290, 570, 160, 30),
        Speed_boost(660, 350, 200, 300)
    ]

    speed_boosts11 = [
        Speed_boost(300, 20, 100, 100)
    ]

    speed_hinders9 = [
        Speed_hinder(260, 0, 30, 600)
    ]

    speed_hinders11 = [
        Speed_hinder(650, 100, 30, 300),
        Speed_hinder(700, 100, 30, 300),
    ]

    obstacle_circular10 = [
        Obstacle_circular(250, 250, 90),
        Obstacle_circular(400, 100, 90),
        Obstacle_circular(400, 400, 90)
    ]

    obstacle_circular12 = [
        Obstacle_circular(250, 250, 90),
        Obstacle_circular(400, 100, 90),
        Obstacle_circular(400, 400, 90),
        Obstacle_circular(250, 550, 90), 
        Obstacle_circular(100, 400, 90),
        Obstacle_circular(100, 100, 90)
    ]

    obstacle_oscillating_circular11 = [
        Obstacle_oscillating_circular(200, 400, 85, amplitude=150, frequency=0.1, direction = 2),
        Obstacle_oscillating_circular(200, 400, 85, amplitude=150, frequency=0.1, direction = 2, type = 2)
    ]

    button_font = pygame.font.Font(None, 36)
    button_text = "Start Game"
    button = Button(300, 200, 200, 50, (255, 0, 0), (180, 0, 0), button_text, (255, 255, 255), button_font)
    button1 = Button(15, 270, 200, 50, (255, 0, 0), (180, 0, 0), "Level 1", (255, 255, 255), button_font)
    button2 = Button(300, 270, 200, 50, (255, 0, 0), (180, 0, 0), "Level 2", (255, 255, 255), button_font)
    button3 = Button(585, 270, 200, 50, (255, 0, 0), (180, 0, 0), "Level 3", (255, 255, 255), button_font)
    button4 = Button(15, 340, 200, 50, (255, 0, 0), (180, 0, 0), "Level 4", (255, 255, 255), button_font)
    button5 = Button(300, 340, 200, 50, (255, 0, 0), (180, 0, 0), "Level 5", (255, 255, 255), button_font)
    button6 = Button(585, 340, 200, 50, (255, 0, 0), (180, 0, 0), "Level 6", (255, 255, 255), button_font)
    button7 = Button(15, 410, 200, 50, (255, 0, 0), (180, 0, 0), "Level 7", (255, 255, 255), button_font)
    button8 = Button(300, 410, 200, 50, (255, 0, 0), (180, 0, 0), "Level 8", (255, 255, 255), button_font)
    button9 = Button(585, 410, 200, 50, (255, 0, 0), (180, 0, 0), "Level 9", (255, 255, 255), button_font)
    button10 = Button(15, 480, 200, 50, (255, 0, 0), (180, 0, 0), "Level 10", (255, 255, 255), button_font)
    button11 = Button(300, 480, 200, 50, (255, 0, 0), (180, 0, 0), "Level 11", (255, 255, 255), button_font)
    button12 = Button(585, 480, 200, 50, (255, 0, 0), (180, 0, 0), "Level 12", (255, 255, 255), button_font)

    clock = pygame.time.Clock()

    collided = False

    menu = True

    running = True

    win = False

    music_playing = True

    pausing = False
    start_time = 0 
    delay_time = 1000 
    delay1_done = False  
    delay2_done = False
    pause_once = False
    second_pause = False
    play_sound = True

    alpha = 0
    alpha2 = 0

    sound_played = False

    while running:
        if not channel.get_busy() and music_playing:
            channel.play(sounds[current_sound])
            current_sound = (current_sound + 1) % len(sounds)
        if menu:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if button.is_clicked(mouse_pos):
                            menu = False
                            button_click_sound.play()
                        elif button1.is_clicked(mouse_pos):
                            menu = False
                            level = 1
                            button_click_sound.play()
                        elif button2.is_clicked(mouse_pos):
                            menu = False
                            level = 2
                            button_click_sound.play()
                        elif button3.is_clicked(mouse_pos):
                            menu = False
                            level = 3
                            button_click_sound.play()
                        elif button4.is_clicked(mouse_pos):
                            menu = False
                            level = 4
                            button_click_sound.play()
                        elif button5.is_clicked(mouse_pos):
                            menu = False
                            level = 5
                            button_click_sound.play()
                        elif button6.is_clicked(mouse_pos):
                            menu = False
                            level = 6
                            button_click_sound.play()
                        elif button7.is_clicked(mouse_pos):
                            menu = False
                            level = 7
                            button_click_sound.play()
                        elif button8.is_clicked(mouse_pos):
                            menu = False
                            level = 8
                            button_click_sound.play()
                        elif button9.is_clicked(mouse_pos):
                            menu = False
                            level = 9
                            button_click_sound.play()
                        elif button10.is_clicked(mouse_pos):
                            menu = False
                            level = 10
                            button_click_sound.play()
                        elif button11.is_clicked(mouse_pos):
                            menu = False
                            level = 11
                            button_click_sound.play()
                        elif button12.is_clicked(mouse_pos):
                            menu = False
                            level = 12
                            button_click_sound.play()
            button.update(mouse_pos)
            button1.update(mouse_pos)
            button2.update(mouse_pos)
            button3.update(mouse_pos)
            button4.update(mouse_pos)
            button5.update(mouse_pos)
            button6.update(mouse_pos)
            button7.update(mouse_pos)
            button8.update(mouse_pos)
            button9.update(mouse_pos)
            button10.update(mouse_pos)
            button11.update(mouse_pos)
            button12.update(mouse_pos)
            window.fill((255, 255, 255))
            window.blit(Background, (0, 0))
            button.draw(window)
            button1.draw(window)
            button2.draw(window)
            button3.draw(window)
            button4.draw(window)
            button5.draw(window)
            button6.draw(window)
            button7.draw(window)
            button8.draw(window)
            button9.draw(window)
            button10.draw(window)
            button11.draw(window)
            button12.draw(window)
            window.blit(Title_resized, (0, 0))
        elif win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            music_playing = False
            channel.stop()
            if alpha < 255:
                End_animation1_resized.set_alpha(alpha)
                window.blit(End_animation1_resized, (0, 0))
                alpha += 1
            else:
                if alpha2 < 255: 
                    End_animation2_resized.set_alpha(alpha2)
                    window.blit(End_animation2_resized, (0, 0))
                    alpha2 += 1
                elif not second_pause:
                    if not pausing:
                        pausing = True
                        start_time = pygame.time.get_ticks()
                current_time = pygame.time.get_ticks()
                if pausing and current_time - start_time >= 1000:
                    second_pause = True
                    window.blit(End_animation3_resized, (0, 0))
                    if play_sound:
                        play_sound = False
                        player_death_sound.play()
                        window.blit(End_animation3_resized, (0, 0))
                        time.sleep(0.3)
                    if current_time - start_time >= 2000:
                        channel1.play(End_song, loops = -1)
                        pausing = False
                    


        else:
            window.fill((255, 255, 255))
            window.blit(Background, (0, 0))
            LevelText = font.render("Level:" + str(level), True, (0, 0, 0))
            DeathText = font.render("Deaths:" + str(deaths), True, (0, 0, 0))
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            player_rect.x = x
            player_rect.y = y

            if level == 1:
                for obstacle in obstacles1:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating1:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 2:
                for obstacle in obstacles2:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating2:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 3:
                for obstacle in obstacles3:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating3:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 4:
                for obstacle in obstacles4:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating4:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                for obstacle_oscillating in obstacles_oscillating4:
                    obstacle_oscillating.update() 
                    obstacle_oscillating.draw(window)
                    if obstacle_oscillating.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 5:
                for obstacle_oscillating in obstacles_oscillating5:
                    obstacle_oscillating.update() 
                    obstacle_oscillating.draw(window)
                    if obstacle_oscillating.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating5:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 6:
                for obstacle in obstacles6:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating6:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 550, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 7:
                for obstacle in obstacles6:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating7:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                for obstacle_oscillating in obstacles_oscillating7:
                    obstacle_oscillating.update() 
                    obstacle_oscillating.draw(window)
                    if obstacle_oscillating.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 550, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 8:
                for obstacle in obstacles8:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 9:
                for speed_boost in speed_boosts9:
                    speed_boost.draw(window)
                for speed_hinder in speed_hinders9:
                    speed_hinder.draw(window)
                for obstacle in obstacles9:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_oscillating in obstacles_oscillating9:
                    obstacle_oscillating.update() 
                    obstacle_oscillating.draw(window)
                    if obstacle_oscillating.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating9:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 10:
                for obstacle in obstacles10:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating10:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                for obstacle_circular in obstacle_circular10:
                    obstacle_circular.draw(window)
                    if obstacle_circular.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_oscillating in obstacles_oscillating10:
                    obstacle_oscillating.update() 
                    obstacle_oscillating.draw(window)
                    if obstacle_oscillating.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 11:
                for speed_boost in speed_boosts11:
                    speed_boost.draw(window)
                for speed_hinder in speed_hinders11:
                    speed_hinder.draw(window)
                for obstacle in obstacles11:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_oscillating in obstacles_oscillating11:
                    obstacle_oscillating.update() 
                    obstacle_oscillating.draw(window)
                    if obstacle_oscillating.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                for obstacle_oscillating_circular in obstacle_oscillating_circular11:
                    obstacle_oscillating_circular.update()
                    obstacle_oscillating_circular.draw(window)
                    if obstacle_oscillating_circular.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided=True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating11:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 550, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            elif level == 12:
                for obstacle in obstacles12:
                    obstacle.draw(window)
                    if obstacle.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_circular in obstacle_circular12:
                    obstacle_circular.draw(window)
                    if obstacle_circular.check_collision(player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths+=1
                            collided = True
                            player_death_sound.play()
                for obstacle_rotating in obstacles_rotating12:
                    obstacle_rotating.rotate()
                    obstacle_rotating.draw(window)
                    if obstacle_rotating.check_collision(player_mask, player_rect):
                        if not collided:
                            x = respawnx
                            y = respawny
                            deaths += 1
                            collided = True
                            player_death_sound.play()
                End_point = End(750, 270, 30, 30)
                End_point.draw(window)
                if End_point.check_collision(player_rect):
                    if not collided:
                        x = respawnx
                        y = respawny
                        level += 1
                        level_end_sound.play()
            keys = pygame.key.get_pressed()
            if level == 9:
                if keys[pygame.K_LEFT]:
                    if x - 5 >= 0:
                        if any(speed_boost.check_collision(player_rect) for speed_boost in speed_boosts9):
                            x -= 10
                        elif any(speed_hinder.check_collision(player_rect) for speed_hinder in speed_hinders9):
                            x-=2.5
                        else:
                            x -= 5
                if keys[pygame.K_RIGHT]:
                    if x + 5 + player_width <= 800:
                        if any(speed_boost.check_collision(player_rect) for speed_boost in speed_boosts9):
                            x += 10
                        elif any(speed_hinder.check_collision(player_rect) for speed_hinder in speed_hinders9):
                            x+=2.5
                        else:    
                            x += 5
                if keys[pygame.K_UP]:
                    if y - 5 >= 0:
                        if any(speed_boost.check_collision(player_rect) for speed_boost in speed_boosts9):
                            y -= 10
                        elif any(speed_hinder.check_collision(player_rect) for speed_hinder in speed_hinders9):
                            y -=2.5
                        else: 
                            y -= 5
                if keys[pygame.K_DOWN]:
                    if y + 5 + player_height <= 600:
                        if any(speed_boost.check_collision(player_rect) for speed_boost in speed_boosts9):
                            y += 10
                        elif any(speed_hinder.check_collision(player_rect) for speed_hinder in speed_hinders9):
                            y+=2.5
                        else:
                            y+=5
            elif level == 11:
                if keys[pygame.K_LEFT]:
                    if any(speed_boost.check_collision(player_rect) for speed_boost in speed_boosts11):
                        if x - 10 >= 0:
                            x -= 10
                    elif any(speed_hinder.check_collision(player_rect) for speed_hinder in speed_hinders11):
                        if x-2.5 >= 0:
                            x-=2.5
                    else:
                        if x - 5 >= 0:
                            x -= 5
                if keys[pygame.K_RIGHT]:
                    if any(speed_boost.check_collision(player_rect) for speed_boost in speed_boosts11):
                        if x + 10 + player_width <= 800:
                                x += 10
                    elif any(speed_hinder.check_collision(player_rect) for speed_hinder in speed_hinders11):
                        if x + 2.5 + player_width <=800:
                            x+=2.5
                    else:
                        if x + 5 + player_width <= 800:    
                            x += 5
                if keys[pygame.K_UP]:
                    if any(speed_boost.check_collision(player_rect) for speed_boost in speed_boosts11):
                        if y - 10 >= 0:
                            y -= 10
                        else: y -= 5
                    elif any(speed_hinder.check_collision(player_rect) for speed_hinder in speed_hinders11):
                        if y - 2.5 >= 0:
                            y-=2.5
                    else:
                        if y - 5 >= 0:
                            y -= 5
                if keys[pygame.K_DOWN]:
                    if any(speed_boost.check_collision(player_rect) for speed_boost in speed_boosts11):
                        if y + 10 + player_height <= 600:
                            y += 10
                    elif any(speed_hinder.check_collision(player_rect) for speed_hinder in speed_hinders11):
                        if y + 2.5 + player_height <= 600:
                            y+=2.5
                    else:
                        if y + 5 + player_height <= 600:
                            y+=5
            else:
                if keys[pygame.K_LEFT]:
                    if x - 5 >= 0:
                        x -= 5
                if keys[pygame.K_RIGHT]:
                    if x + 5 + player_width <= 800:   
                        x += 5
                if keys[pygame.K_UP]:
                    if y - 5 >= 0:
                        y -= 5
                if keys[pygame.K_DOWN]:
                    if y + 5 + player_height <= 600:
                        y+=5
                
            collided = False

            window.blit(LevelText, (10, 5))
            window.blit(DeathText, (10, 25))

            window.blit(Player, (x, y))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    await asyncio.sleep(0)

asyncio.run(main())
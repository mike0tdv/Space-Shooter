import pygame
from random import randint, uniform
from os.path import join
import json

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha()
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.math.Vector2()
        self.speed = 650

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400 

        # mask
        self.mask = pygame.mask.from_surface(self.image)  

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = (int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])) * 2
        self.direction.y = (int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) * 2
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        if self.rect.left > WINDOW_WIDTH + 100:
            self.rect.left = -100
        if self.rect.right < -100:
            self.rect.right = WINDOW_WIDTH + 100

        if keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

class Stars(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom = pos)
        
        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.centery -= 1000*dt 
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, groups):
        super().__init__(groups)
        self.original = surf
        self.image = self.original
        self.rect = self.image.get_rect(midbottom = (randint(0, WINDOW_WIDTH), randint(-200, 0)))
        self.speed = randint(250, 600)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.rotation = randint(50, 100)

        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
        
        #rotation
        self.rotation += 100 * dt
        self.image = pygame.transform.rotozoom(self.original, self.rotation, 1)
        self.rect = self.image.get_rect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__ (self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_rect(center = pos)
        explosion_sound.play()
    
    def update(self, dt):
        self.frames_index += 20 * dt
        if self.frames_index < len(self.frames):
            self.image = self.frames[int(self.frames_index)]
        else:
            self.kill() 

def healthbar(health):
    rect = pygame.Rect(540, 650, 200, 50)
    border = pygame.draw.rect(display_surface, "black", rect, 10, 8)
    health_rect = pygame.Rect(550, 660, health, 30)
    health_image = pygame.draw.rect(display_surface, "red2", health_rect)
    
    health, collision = player_collision(health)

    if collision:
        health_rect = pygame.Rect(550, 660, health, 30)

    pygame.display.flip()

def load_json(score):
    with open("scores.json", "r") as f:
            json_load = json.load(f)
    high_score = json_load["score"]
    if score > high_score:
        high_score = score
        json_load["score"] = score
        with open("scores.json", "w") as f:
            json.dump(json_load, f)
    
    return high_score

def player_collision(health):
    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        damage_sound.play()
        health -= 20
        return health, True
    else: return health, False
    
def collisions(score):
    if len(laser_sprites) > 0:
        for laser in laser_sprites:
            if pygame.sprite.spritecollide(laser, meteor_sprites, True, pygame.sprite.collide_mask):
                score += 1
                laser.kill()
                AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
                
    return score

def display_score(score):
    text_surf = font.render(f"{score}", True, "white")
    text_rect = text_surf.get_rect(center = (640, 600)) # !
    pygame.draw.rect(display_surface, 'white', text_rect.inflate(20, 10).move(0, -3), 5, 10)
    display_surface.blit(text_surf, text_rect)

# GENERAL SETUP
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space shooter")
running = True
game_active = False
clock = pygame.time.Clock()
space_pressed = 0
score = 0
health = 180

# import
star_surf = pygame.image.load(join("images", "star.png")).convert_alpha()
laser_surf = pygame.image.load(join("images", "laser.png")).convert_alpha()
meteor_surf = pygame.image.load(join("images", "meteor.png")).convert_alpha()
font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 60)
font2 = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 40)
explosion_frames = [pygame.image.load(join("images", "explosion", f"{i}.png")).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join("audio", "laser.wav"))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join("audio", "explosion.wav"))
damage_sound = pygame.mixer.Sound(join("audio", "damage.ogg"))
game_music_sound = pygame.mixer.Sound(join("audio", "game_music.wav"))
game_music_sound.set_volume(0.3)
game_music_sound.play(loops = True)

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Stars(all_sprites, star_surf)
player = Player(all_sprites)


# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick(60) / 1000
    
    if game_active:
        #EVENT LOOP
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == meteor_event:
                Meteor(meteor_surf, (all_sprites, meteor_sprites))
        
        # update
        all_sprites.update(dt)
        score = collisions(score)
        health, _ = player_collision(health)

        if health <= 0:
            game_active = False

        # DRAW THE GAME
        display_surface.fill("#3a2e3f")
        display_score(score)
        all_sprites.draw(display_surface)
        healthbar(health)   
     
    else: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        high_score = load_json(score)

        all_sprites.empty()
        meteor_sprites.empty()
        laser_sprites.empty()
        
        display_surface.fill("#3a2e3f")
        
        game_over = font2.render("Press 'enter' to start the game", True, "Black")
        game_over_rect = game_over.get_rect(center = (640, 600))
        
        last_score = font2.render(f"Last score: {score}", True, "white")
        last_score_rect = last_score.get_rect(center = (200, 100))
        
        high_score_show = font2.render(f"Highest  score: {high_score}", True, "white")
        high_score_rect = high_score_show.get_rect(center = (200, 150))
        
        image = pygame.image.load(join("images", "player.png")).convert_alpha()
        image = pygame.transform.scale_by(image, 3)
        rect = image.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        display_surface.blit(image, rect)  
        display_surface.blit(game_over, game_over_rect)  
        display_surface.blit(last_score, last_score_rect)
        display_surface.blit(high_score_show, high_score_rect)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_active = True
            score = 0
            health = 180

        for i in range(20):
            Stars(all_sprites, star_surf)
        player = Player(all_sprites)

    pygame.display.update()
pygame.quit()
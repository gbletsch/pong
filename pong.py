import pygame, random
from pygame.locals import *
from pygame.math import *

pygame.init()


SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (500, 300)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

BALL_SIZE = 10
INITIAL_SPEED = 3

PADDLE_SIZE = (5, SCREEN_HEIGHT // 5)
PADDLE_SPEED = 5

SCORE_SIZE = min(*SCREEN_SIZE) // 10
GAME_FONT = ('arial', 48)


score_left = score_right = 0

class Ball(pygame.sprite.Sprite):
    def __init__(self, size, color, velocity = Vector2(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.velocity = velocity
        self.size = size
        self.color = color
        self.image = pygame.Surface((size, size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def move(self):
        self.rect.move_ip(self.velocity)

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity.reflect_ip((0, 1))
        elif self.rect.top < 0:
            self.rect.top = 0
            self.velocity.reflect_ip((0, 1))


class Text:
    '''Params: x, y, value, color'''
    def __init__(self, x, y, value, color):
        self.image = pygame.Surface((SCORE_SIZE, SCORE_SIZE))
        self.value = value
        self.color = color
        self.font = pygame.font.SysFont(*GAME_FONT)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Player(pygame.sprite.Sprite):
    '''
    Parameters
    ----------
        side: string. 'left' or 'right'

    '''

    def __init__(self, side, size = PADDLE_SIZE, speed = PADDLE_SPEED, color = WHITE):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        if side == 'left':
            self.rect.left = 0
        elif side == 'right':
            self.rect.right = SCREEN_WIDTH
        else:
            raise ValueError('parameter "side" must be set to "left" or "right".')
        self.rect.centery = SCREEN_HEIGHT // 2
        self.speed = speed
        self.score = 0


def create_new_ball():
    BALL_SPEED_X = random.choice([-1, 1]) * INITIAL_SPEED
    BALL_SPEED_Y = random.choice([-1, 1]) * INITIAL_SPEED

    global ball
    try:
        del ball
    except NameError:
        pass
    return Ball(BALL_SIZE, WHITE, Vector2(BALL_SPEED_X, BALL_SPEED_Y))


def bounce_paddles(ball, paddles):
    '''
    bounce with simple physics to change the y angle, mimic a convex surface
    for paddle in [right_paddle, left_paddle]:
    Params
    ------
        ball: sprite object
        paddles: list containing paddles (sprite objects)
    Returns
    -------
        ball sprite object
    '''
    for paddle in paddles:
        if ball.rect.colliderect(paddle.rect):
            vx, vy = ball.velocity
            offset = (ball.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
            bounced = Vector2(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = Vector2(vel.x, vel.y + offset)
    return ball

def start_new_game():
    start_msg = Text(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3,
                     value='Press any key', color=RED)
    sm = start_msg.font.render(start_msg.value, True, start_msg.color)
    ball = create_new_ball()
    right_paddle = Player('right')
    left_paddle = Player('left')
    left_score = Text(SCREEN_WIDTH // 15 * 2, SCREEN_HEIGHT // 15, 0, BLUE)
    right_score = Text(SCREEN_WIDTH // 15 * 13, SCREEN_HEIGHT // 15, 0, BLUE)

    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 1, 0, 2, SCREEN_HEIGHT))
    screen.blits((
        (ball.image, ball.rect),
        (left_score.image, left_score.rect),
        (right_score.image, right_score.rect),
        (sm, start_msg.rect),
        (right_paddle.image, right_paddle.rect),
        (left_paddle.image, left_paddle.rect)
    ))
    pygame.display.update()
    pygame.event.clear()
    event = pygame.event.wait()
    return ball, left_score, right_score, right_paddle, left_paddle




# instantiate objects
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Pong')
clock = pygame.time.Clock()

# right_paddle: Player
ball, left_score, right_score, right_paddle, left_paddle = start_new_game()


over = False
while not over:
    pygame.event.pump()
    clock.tick(60)
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 1, 0, 2, SCREEN_HEIGHT))

    ls = left_score.font.render('{}'.format(left_score.value), True, left_score.color)
    rs = right_score.font.render('{}'.format(right_score.value), True, right_score.color)
    screen.blits((
        (ball.image, ball.rect),
        (ls, left_score.rect),
        (rs, right_score.rect),
        (right_paddle.image, right_paddle.rect),
        (left_paddle.image, left_paddle.rect)
    ))

    ball.move()

    for event in pygame.event.get():
        if event.type == QUIT:
            over = True
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                over = True
        if event.type == KEYUP:
            if event.key == K_p:
                paused = True
                while paused:
                    for event in pygame.event.get():
                        if event.type == KEYUP:
                            if event.key == K_c:
                                paused = False

    if ball.rect.left <= 0:
        right_score.value += 1
        ball = create_new_ball()

    elif ball.rect.right >= SCREEN_WIDTH:
        left_score.value += 1
        ball = create_new_ball()

    pygame.event.clear()
    key = pygame.key.get_pressed()
    if key[K_DOWN]:
        right_paddle.rect.bottom = min(SCREEN_HEIGHT,
                                       right_paddle.rect.bottom + right_paddle.speed)
    if key[K_UP]:
        right_paddle.rect.top = max(0,
                                    right_paddle.rect.top - right_paddle.speed)

    ball = bounce_paddles(ball, [left_paddle, right_paddle])

    left_paddle.rect.centery = ball.rect.centery
    if left_paddle.rect.top < 0:
        left_paddle.rect.top = 0
    elif left_paddle.rect.bottom > SCREEN_HEIGHT:
        left_paddle.rect.bottom = SCREEN_HEIGHT

    pygame.display.update()

pygame.quit()
quit()
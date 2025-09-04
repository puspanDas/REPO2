import pygame
import random
import numpy as np
import sys

# Initialize Pygame
pygame.init()

# --- Game Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BIRD_X = 50
PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_SPEED = 4
GRAVITY = 0.5
FLAP_STRENGTH = -8

# --- Colors ---
BLUE = (135, 206, 235)
GREEN = (0, 200, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)

# --- Setup Screen & Font ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird - Smart AI")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)

# --- Q-Learning Parameters ---
LEARNING_RATE = 0.3
DISCOUNT_FACTOR = 0.95
# Exploration vs. Exploitation
EPSILON_START = 0.8
EPSILON_END = 0.05
EPSILON_DECAY = 0.998

# State space discretization (bins for y-dist, x-dist, velocity)
STATE_BINS = [15, 15, 15]
# Actions: 0 = do nothing, 1 = flap
NUM_ACTIONS = 2

# Initialize Q-table (add 1 to each dimension to handle np.digitize edge cases)
q_table = np.random.uniform(low=-1, high=1, size=([x+1 for x in STATE_BINS] + [NUM_ACTIONS]))
epsilon = EPSILON_START


def get_discretized_state(bird_y, bird_velocity, pipes):
    """Convert continuous values into a discrete state (tuple) for Q-table."""
    # Find the next pipe ahead of the bird
    next_pipe = None
    for pipe in pipes:
        if pipe['x'] + PIPE_WIDTH > BIRD_X:
            next_pipe = pipe
            break

    if next_pipe is None:
        return (0, 0, 0)

    # y-distance to middle of pipe gap, normalized
    y_dist_to_gap_center = (bird_y - (next_pipe['y'] + PIPE_GAP / 2)) / SCREEN_HEIGHT
    # x-distance to pipe, normalized
    x_dist_to_pipe = (next_pipe['x'] - BIRD_X) / SCREEN_WIDTH

    # Discretize into bins with bounds checking
    y_bin = int(np.clip(np.digitize(y_dist_to_gap_center, np.linspace(-1, 1, STATE_BINS[0])), 0, STATE_BINS[0]))
    x_bin = int(np.clip(np.digitize(x_dist_to_pipe, np.linspace(0, 1, STATE_BINS[1])), 0, STATE_BINS[1]))
    vel_bin = int(np.clip(np.digitize(bird_velocity, np.linspace(-10, 10, STATE_BINS[2])), 0, STATE_BINS[2]))

    return (y_bin, x_bin, vel_bin)


def run_game():
    """Runs one episode of the game and returns the score."""
    global q_table, epsilon

    bird_y = SCREEN_HEIGHT // 2
    bird_velocity = 0
    pipes = [{'x': SCREEN_WIDTH, 'y': random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)}]
    score = 0

    current_state = get_discretized_state(bird_y, bird_velocity, pipes)
    game_over = False

    while not game_over:
        # Event Handling (to allow window close)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Action selection: Epsilon-Greedy
        if random.uniform(0, 1) < epsilon:
            action = random.randint(0, NUM_ACTIONS - 1)  # Explore
        else:
            action = np.argmax(q_table[current_state])  # Exploit best known

        # Perform Action
        if action == 1:  # Flap
            bird_velocity = FLAP_STRENGTH

        # Update Bird Position
        bird_velocity += GRAVITY
        bird_y += bird_velocity

        # Move Pipes
        for pipe in pipes:
            pipe['x'] -= PIPE_SPEED

        # Reward system
        reward = 2  # survive bonus
        
        # Distance-based reward (closer to gap center = better)
        if pipes:
            next_pipe = None
            for pipe in pipes:
                if pipe['x'] + PIPE_WIDTH > BIRD_X:
                    next_pipe = pipe
                    break
            if next_pipe:
                gap_center = next_pipe['y'] + PIPE_GAP / 2
                distance_to_center = abs(bird_y - gap_center)
                reward += max(0, 10 - distance_to_center / 10)  # Bonus for staying near center

        # Collision check (circular bird)
        bird_center = (BIRD_X + 15, int(bird_y) + 10)
        bird_radius = 12
        for pipe in pipes:
            # Check collision with circular bird
            pipe_left = pipe['x']
            pipe_right = pipe['x'] + PIPE_WIDTH
            top_pipe_bottom = pipe['y']
            bottom_pipe_top = pipe['y'] + PIPE_GAP
            
            # Check if bird is within pipe x-range
            if pipe_left <= bird_center[0] + bird_radius and pipe_right >= bird_center[0] - bird_radius:
                # Check collision with top or bottom pipe
                if (bird_center[1] - bird_radius <= top_pipe_bottom or 
                    bird_center[1] + bird_radius >= bottom_pipe_top):
                    reward = -1000
                    game_over = True
                    break

        if bird_center[1] + bird_radius >= SCREEN_HEIGHT or bird_center[1] - bird_radius <= 0:
            reward = -1000
            game_over = True

        # Score increment when passing a pipe (check the correct pipe)
        for pipe in pipes:
            if pipe['x'] + PIPE_WIDTH < BIRD_X and 'passed' not in pipe:
                pipe['passed'] = True
                score += 1
                reward = 200  # Higher reward for passing pipes
                break

        # Spawn new pipes
        if pipes[0]['x'] < -PIPE_WIDTH:
            pipes.pop(0)
            pipes.append({'x': SCREEN_WIDTH, 'y': random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)})

        # State Update
        new_state = get_discretized_state(bird_y, bird_velocity, pipes)
        max_future_q = np.max(q_table[new_state])
        current_q = q_table[current_state + (action,)]
        # Q-learning formula
        q_table[current_state + (action,)] = current_q + LEARNING_RATE * (reward + DISCOUNT_FACTOR * max_future_q - current_q)
        current_state = new_state

        # Drawing
        screen.fill(BLUE)
        for pipe in pipes:
            pygame.draw.rect(screen, GREEN, (pipe['x'], 0, PIPE_WIDTH, pipe['y']))
            pygame.draw.rect(screen, GREEN, (pipe['x'], pipe['y'] + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT))
        # Draw bird with proper structure
        bird_center = (BIRD_X + 15, int(bird_y) + 10)
        # Body (yellow circle)
        pygame.draw.circle(screen, YELLOW, bird_center, 12)
        # Wing (orange oval)
        pygame.draw.ellipse(screen, ORANGE, (BIRD_X + 5, int(bird_y) + 5, 15, 8))
        # Eye (white circle with black pupil)
        pygame.draw.circle(screen, WHITE, (BIRD_X + 20, int(bird_y) + 7), 4)
        pygame.draw.circle(screen, BLACK, (BIRD_X + 21, int(bird_y) + 7), 2)
        # Beak (orange triangle)
        beak_points = [(BIRD_X + 27, int(bird_y) + 10), (BIRD_X + 32, int(bird_y) + 8), (BIRD_X + 32, int(bird_y) + 12)]
        pygame.draw.polygon(screen, ORANGE, beak_points)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        mode_text = font.render("Training" if epsilon > 0.05 else "AI Playing", True, WHITE)
        screen.blit(mode_text, (10, 40))
        eps_text = font.render(f"Epsilon: {epsilon:.3f}", True, WHITE)
        screen.blit(eps_text, (10, 70))

        pygame.display.update()
        clock.tick(60)

    return score


if __name__ == "__main__":
    total_episodes = 1000   # More training episodes
    best_score = 0

    for episode in range(total_episodes):
        score = run_game()
        if score > best_score:
            best_score = score
        
        print(f"Episode: {episode + 1}, Score: {score}, Best: {best_score}, Epsilon: {epsilon:.3f}")

        # Decay epsilon each episode
        if epsilon > EPSILON_END:
            epsilon *= EPSILON_DECAY

    print(f"Training finished. Best score achieved: {best_score}")
    
    # Run trained AI until it scores 4 or more
    print("\nRunning trained AI until it scores 4+...")
    epsilon = 0  # No more exploration, pure exploitation
    
    while True:
        score = run_game()
        print(f"AI Score: {score}")
        if score >= 4:
            print(f"\nSuccess! AI achieved target score of {score}!")
            break
    
    pygame.quit()
    sys.exit()

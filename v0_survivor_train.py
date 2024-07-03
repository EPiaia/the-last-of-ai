import time
import numpy as np
import gymnasium as gym
import v0_survivor_env
import os
import pickle

# Parameters for Q-learning
alpha = 0.2      # Learning rate
gamma = 0.9     # Discount factor
epsilon_min = 0.1 # Minimum exploration rate
epsilon_decay = 0.995 # Exploration decay rate
max_steps = 100

# Function to choose an action using epsilon-greedy policy
def choose_action(state, env, q_table, epsilon):
    if np.random.rand() < epsilon:
        return env.action_space.sample()  # Explore
    else:
        return np.argmax(q_table[state])  # Exploit

def run_q(episodes, env, is_training=True, render=False):

    if (is_training):
        # Initialize Q-table
        observation_space_size = env.observation_space.nvec
        state_shape = tuple(observation_space_size)  # Adjust based on your environment's observation space
        q_table = np.zeros(state_shape + (env.action_space.n,))
    else:
        # If testing, load Q Table from file.
        f = open('v0_the_last_of_us_solution.pkl', 'rb')
        q_table = pickle.load(f)
        f.close()

    if (is_training):
        train_q(episodes, env, q_table)
    else:
        test_q(env, q_table)

    if is_training:
        # Save Q Table
        f = open("v0_the_last_of_us_solution.pkl","wb")
        pickle.dump(q_table, f)
        f.close()

def train_q(num_episodes, env, q_table):
    epsilon = 1.0     # Exploration rate

    for episode in range(num_episodes):
        state, _ = env.reset()
        state = tuple(state)
        total_reward = 0
        
        for step in range(max_steps):
            action = choose_action(state, env, q_table, epsilon)
            next_state, reward, done, truncated, _ = env.step(action)
            next_state = tuple(next_state)
            
            # Update Q-value
            q_value = q_table[state][action]
            best_next_q = np.max(q_table[next_state])
            new_q_value = q_value + alpha * (reward + gamma * best_next_q - q_value)
            q_table[state][action] = new_q_value
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        # Decay epsilon
        if epsilon > epsilon_min:
            epsilon *= epsilon_decay
        
        if episode % 100 == 0:
            print(f"Episode: {episode}, Total Reward: {total_reward}")

def test_q(env, q_table):
    # Test the trained agent
    state, _ = env.reset()
    state = tuple(state)
    total_reward = 0

    env.render()
    for step in range(max_steps):
        action = np.argmax(q_table[state])
        next_state, reward, done, truncated, _ = env.step(action)
        next_state = tuple(next_state)
        env.render()
        
        state = next_state
        total_reward += reward
        
        time.sleep(1)

        if done:
            break

    print(f"Total Reward: {total_reward}")

if __name__ == '__main__':

    # Initialize the environment
    env = gym.make('the-last-of-us-v0')
    # Train/test using Q-Learning
    run_q(1000, env, is_training=True, render=False)
    print("Training finished")
    time.sleep(5)
    #env.change_render_mode()
    run_q(1, env, is_training=False, render=True)
    env.close()

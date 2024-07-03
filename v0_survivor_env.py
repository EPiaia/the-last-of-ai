import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
from gymnasium.utils.env_checker import check_env

import v0_survivor as sv
import numpy as np

# Register this module as a gym environment. Once registered, the id is usable in gym.make().
register(
    id='the-last-of-us-v0',                                # call it whatever you want
    entry_point='v0_survivor_env:SurvivorEnv', # module_name:class_name
)

# Implement our own gym env, must inherit from gym.Env
# https://gymnasium.farama.org/api/env/
class SurvivorEnv(gym.Env):
    # metadata is a required attribute
    # render_modes in our environment is either None or 'human'.
    # render_fps is not used in our env, but we are require to declare a non-zero value.
    metadata = {"render_modes": ["human"], 'render_fps': 5}

    def __init__(self, grid_rows=5, grid_cols=5, render_mode=None, zombies_amount=2, supplies_amount=3, walls_amount=1, rocks_amount=1):

        self.grid_rows=grid_rows
        self.grid_cols=grid_cols
        self.render_mode = render_mode

        # Initialize the WarehouseRobot problem
        self.survivor = sv.Survivor(grid_rows=grid_rows, grid_cols=grid_cols, fps=self.metadata['render_fps'], zombies_amount=zombies_amount, supplies_amount=supplies_amount, walls_amount=walls_amount, rocks_amount=rocks_amount)

        # Gym requires defining the action space. The action space is robot's set of possible actions.
        # Training code can call action_space.sample() to randomly select an action. 
        self.action_space = spaces.Discrete(len(sv.SurvivorAction))

        self.observation_space = spaces.MultiDiscrete([grid_rows * grid_cols, self.survivor.supplies_amount + 1])

    def change_render_mode(self, render_mode=None):
        self.render_mode = render_mode

    # Gym required function (and parameters) to reset the environment
    def reset(self, seed=None, options=None):
        super().reset(seed=seed) # gym requires this call to control randomness and reproduce scenarios.

        # Reset the WarehouseRobot. Optionally, pass in seed control randomness and reproduce scenarios.
        self.survivor.reset(seed=seed)
        
        # Additional info to return. For debugging or whatever.
        info = {}

        # Return observation and info
        return self._get_obs(), info

    # Gym required function (and parameters) to perform an action
    def step(self, action):
        # Perform action
        gridTile = self.survivor.perform_action(sv.SurvivorAction(action))

        # Determine reward and termination
        reward=-1
        terminated=False
        if (gridTile == sv.GridTile.DOOR.value):
            reward+=-10
            if (self.survivor.supplies_collected == self.survivor.supplies_amount):
                reward += 100
            terminated=True
        elif (gridTile == sv.GridTile.ZOMBIE.value):
           reward+=-100
           terminated=True
        elif (gridTile == sv.GridTile.SUPPLY.value):
           reward+=10

        # Return observation, reward, terminated, truncated (not used), info
        return self._get_obs(), reward, terminated, False, {}

    # Gym required function to render environment
    def render(self):
        self.survivor.render()

    def _get_obs(self):
        obs = np.zeros(2, dtype=np.int32)

        y, x = self.survivor.survivor_pos
        pos_val = y * self.grid_rows + x

        obs[0] = pos_val
        obs[1] = self.survivor.supplies_collected

        return obs
    
    def _get_grid_value(self, position):
        if (position == self.survivor.survivor_pos):
            return sv.GridTile.SURVIVOR.value
        if (position == self.survivor.door_pos):
            return sv.GridTile.DOOR.value
        if (position in self.survivor.zombies_pos):
            return sv.GridTile.ZOMBIE.value
        if (position in self.survivor.supplies_pos):
            return sv.GridTile.SUPPLY.value
        if (position in self.survivor.walls_pos):
            return sv.GridTile.WALL.value
        if (position in self.survivor.rocks_pos):
            return sv.GridTile.ROCK.value
        return sv.GridTile._FLOOR.value

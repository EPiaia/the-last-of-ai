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
    metadata = {"render_modes": ["human"], 'render_fps': 4}

    def __init__(self, grid_rows=5, grid_cols=5, render_mode=None):

        self.grid_rows=grid_rows
        self.grid_cols=grid_cols
        self.render_mode = render_mode

        # Initialize the WarehouseRobot problem
        self.survivor = sv.Survivor(grid_rows=grid_rows, grid_cols=grid_cols, fps=self.metadata['render_fps'])

        # Gym requires defining the action space. The action space is robot's set of possible actions.
        # Training code can call action_space.sample() to randomly select an action. 
        self.action_space = spaces.Discrete(len(sv.SurvivorAction))

        self.observation_space = spaces.MultiDiscrete([self.grid_rows, self.grid_cols, len(sv.GridTile), 
                                                       self.survivor.supplies_amount + 1, len(sv.GridTile), len(sv.GridTile), 
                                                       len(sv.GridTile), len(sv.GridTile)])

    # Gym required function (and parameters) to reset the environment
    def reset(self, seed=None, options=None):
        super().reset(seed=seed) # gym requires this call to control randomness and reproduce scenarios.

        # Reset the WarehouseRobot. Optionally, pass in seed control randomness and reproduce scenarios.
        self.survivor.reset(seed=seed)
        
        # Additional info to return. For debugging or whatever.
        info = {}

        # Render environment
        if(self.render_mode=='human'):
            self.render()

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

        # Render environment
        if(self.render_mode=='human'):
            print(sv.SurvivorAction(action))
            self.render()

        # Return observation, reward, terminated, truncated (not used), info
        return self._get_obs(), reward, terminated, False, {}

    # Gym required function to render environment
    def render(self):
        self.survivor.render()

    def _get_obs(self):
        obs = np.zeros(8, dtype=np.int32)

        x, y = self.survivor.survivor_pos

        obs[0] = x
        obs[1] = y
        obs[2] = self._get_grid_value(self.survivor.survivor_pos)
        obs[3] = self.survivor.supplies_collected

        if (x < self.survivor.grid_rows - 1):
            obs[4] = self._get_grid_value([x + 1, y])
        else:
            obs[4] = -1

        if (x > 0):
            obs[5] = self._get_grid_value([x - 1, y])
        else:
            obs[5] = -1

        if (y < self.survivor.grid_cols - 1):
            obs[6] = self._get_grid_value([x, y + 1])
        else:
            obs[6] = -1

        if (y > 0):
            obs[7] = self._get_grid_value([x, y - 1])
        else:
            obs[7] = -1

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
        return sv.GridTile._FLOOR.value

# For unit testing
if __name__=="__main__":
    env = gym.make('the-last-of-us-v0', render_mode='human')

    # Use this to check our custom environment
    # print("Check environment begin")
    # check_env(env.unwrapped)
    # print("Check environment end")

    # Reset environment
    obs = env.reset()[0]

    # Take some random actions
    while(True):
        rand_action = env.action_space.sample()
        obs, reward, terminated, _, _ = env.step(rand_action)

        if(terminated):
            obs = env.reset()[0]

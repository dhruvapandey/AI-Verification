import gymnasium as gym
import numpy as np
from gymnasium import spaces

class RouterEnv(gym.Env):
    def __init__(self, bridge):
        self.bridge = bridge
        
        # ACTION SPACE: 32 (5 bits)
        # Bits [0:3]: Traffic Request (req_i)
        # Bit  [4]  : Backpressure Control (yumi_i)
        self.action_space = spaces.Discrete(32) 
        
        # OBSERVATION SPACE: [Buffer Count (0-64), Busy (0/1)]
        # We set high=65 to be safe for a depth-64 buffer
        self.observation_space = spaces.Box(low=0, high=65, shape=(2,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        return np.array([0, 0], dtype=np.float32), {}

    def step(self, action):
        obs, reward, done, info = self.bridge.ai_send_action(action)
        return obs, reward, done, False, info

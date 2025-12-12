import queue

class SimBridge:
    """
    Acts as the mailbox between the AI Thread (PPO) and the Simulator Thread (Cocotb).
    """
    def __init__(self):
        # FIFO for the AI to send actions to the Simulator
        self.action_queue = queue.Queue(maxsize=1)
        # FIFO for the Simulator to send observations back to the AI
        self.result_queue = queue.Queue(maxsize=1)
        
    def ai_send_action(self, action):
        """Called by AI Thread: Send action and BLOCK until hardware is done."""
        self.action_queue.put(action)
        # This blocks the AI thread here until the simulator returns a result
        return self.result_queue.get()
        
    def sim_get_action(self):
        """Called by Cocotb Thread: Check if AI sent a command."""
        if not self.action_queue.empty():
            return self.action_queue.get()
        return None
        
    def sim_send_result(self, obs, reward, done, info):
        """Called by Cocotb Thread: Return the hardware state to AI."""
        self.result_queue.put((obs, reward, done, info))

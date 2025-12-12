import cocotb
import threading
import random
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from stable_baselines3 import PPO
from router_env import RouterEnv
from bridge import SimBridge

# -------------------------------------------------------
# THREAD 1: The AI Brain
# -------------------------------------------------------
def train_ai_thread(bridge):
    print("🧠 [AI Thread] Starting PPO Training...")
    env = RouterEnv(bridge)
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.001)
    
    # Run for 200,000 steps to ensure it masters the "Hill Climb"
    model.learn(total_timesteps=200000)
    
    print("✅ [AI Thread] Training Complete!")

# -------------------------------------------------------
# THREAD 2: The Hardware Simulator
# -------------------------------------------------------
@cocotb.test()
async def run_ai_verification(dut):
    # 1. Setup Clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    
    # 2. Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    print("🔌 [Main Thread] Reset Complete. Hardware Ready.")
    
    # 3. Initialize Bridge & AI
    bridge = SimBridge()
    ai_thread = threading.Thread(target=train_ai_thread, args=(bridge,))
    ai_thread.daemon = True
    ai_thread.start()
    
    print("⏳ [Main Thread] Waiting for AI commands...")
    
    step_count = 0
    while ai_thread.is_alive():
        
        action = bridge.sim_get_action()
        
        if action is not None:
            # --- GOD MODE DRIVER ---
            
            # 1. DECODE ACTIONS
            req_val = int(action) & 0xF           # Lower 4 bits = Traffic
            yumi_val = (int(action) >> 4) & 1     # 5th bit = Backpressure
            
            # 2. DRIVE HARDWARE
            dut.req_i.value = req_val
            dut.yumi_i.value = yumi_val  # AI controls the drain!
            
            # Random Data
            dut.data_n_i.value = random.randint(0, 0xFFFFFFFF)
            dut.data_s_i.value = random.randint(0, 0xFFFFFFFF)
            dut.data_e_i.value = random.randint(0, 0xFFFFFFFF)
            dut.data_w_i.value = random.randint(0, 0xFFFFFFFF)
            
            # 3. Step Time
            await RisingEdge(dut.clk)
            
            # 4. Read Outputs
            try:
                count = int(dut.count.value)
                busy = int(dut.busy_o.value)
            except ValueError:
                count = 0; busy = 0
            
            obs = np.array([count, busy], dtype=np.float32)
            
            # 5. REWARD LOGIC (The Hill Climber)
            packets_sent = bin(req_val).count('1')
            
            # Base: Pay for sending packets
            reward = packets_sent * 10
            
            # Hill Climb: Pay for keeping buffer full
            reward += (count * 5) 
            
            # Jackpot: Massive bonus for congestion
            if busy == 1:
                reward += 500 
                
            # 6. Send Result
            bridge.sim_send_result(obs, reward, False, {})
            
            # Logging
            if step_count % 100 == 0:
                 print(f"Cycle {step_count}: Action={action} (Req={req_val}, Yumi={yumi_val}) | Reward={reward} | Buffer={count}")
            
            step_count += 1

        else:
            await RisingEdge(dut.clk)
            # Heartbeat (Optional)
            if step_count % 5000 == 0:
                 # print("Waiting...") 
                 pass

    print("🏁 [Main Thread] Simulation Finished.")

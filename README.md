
# 🤖 AI-Driven Network-on-Chip (NoC) Verification

**An autonomous Hardware Verification environment that uses Reinforcement Learning (PPO) to discover congestion bugs in Silicon designs without human-directed tests.**

-----

## 📖 Executive Summary

Traditional hardware verification relies on humans writing thousands of "directed tests" to find bugs. This project proves that an **AI Agent** can autonomously explore a hardware design, learn its physics, and discover edge-case failures on its own.

In this experiment, an AI agent was connected to a **4-Port Network-on-Chip Router**. Within **4,000 simulation cycles** (approx. 2 minutes), the AI independently discovered a "Buffer Overflow" vulnerability by learning to manipulate backpressure signals while simultaneously flooding the network with traffic.

-----

## 🏗️ System Architecture

This project uses a novel **Hardware-in-the-Loop** architecture to bridge the gap between Python-based AI and Verilog-based Hardware Simulation.

  * **Layer 1: The Brain (AI)** - Uses `Stable-Baselines3` (PPO Algorithm) to make decisions.
  * **Layer 2: The Bridge** - A custom threaded Python interface that synchronizes the asynchronous hardware clock with the synchronous AI training loop.
  * **Layer 3: The Hardware (DUT)** - A SystemVerilog NoC Router running on the `Icarus Verilog` simulator via `Cocotb`.

-----

## 📂 Repository Structure

| File | Description |
| :--- | :--- |
| **`router.sv`** | **The Hardware (DUT).** A 4-port router with a depth-64 FIFO buffer. Includes a `yumi_i` (Read Enable) signal for backpressure control. |
| **`verify_noc.py`** | **The Master Testbench.** Orchestrates the simulation, launches the AI thread, and calculates rewards based on buffer congestion. |
| **`router_env.py`** | **The Gym Environment.** Translates hardware states (Buffer Count) into AI observations and AI actions into hardware signals. |
| **`bridge.py`** | **The Connector.** A thread-safe FIFO implementation that prevents the simulator from hanging while the AI "thinks." |
| **`run/Makefile`** | **Build Script.** Configures Cocotb and Icarus Verilog for execution. |

-----

## ⚡ How to Run

### Prerequisites

You need a Linux/Mac environment with the following installed:

  * **Python 3.8+**
  * **Icarus Verilog** (`iverilog`)
  * **GTKWave** (for viewing waveforms)

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/dhruvapandey/AI-Verification.git
    cd AI-Verification
    ```

2.  Create a virtual environment and install dependencies:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install cocotb stable-baselines3 gymnasium numpy
    ```

### Execution

1.  Navigate to the run folder:

    ```bash
    cd run
    ```

2.  Start the AI Training:

    ```bash
    make
    ```

3.  **Watch the Magic:**
    You will see logs indicating the AI is exploring. Around cycle 100-500, the "Reward" will spike to \~850, indicating the AI has cracked the code.

-----

## 📊 Results & Analysis

The AI was given a simple goal: **"Maximize the congestion in the router."**

### Phase 1: Exploration

Initially, the AI acted randomly. The buffer hovered near 0.

  * *Action:* Random inputs.
  * *Result:* Buffer empty. Low Reward (\~20).

### Phase 2: The "God Mode" Discovery

Around **Cycle 100**, the AI discovered a specific combination of inputs:

1.  **Traffic:** Set `req_i = 15` (Send on all ports).
2.  **Backpressure:** Set `yumi_i = 0` (Force receiver to be STUCK).

### Phase 3: Optimization

By **Cycle 400**, the AI realized it didn't need to send more packets once the buffer was full. It switched to a "Lazy Strategy":

  * *Action:* `req_i = 0` (Stop sending).
  * *Action:* `yumi_i = 0` (Keep drain closed).
  * *Result:* **Buffer pinned at 64 (MAX). Reward maximized.**

### Visual Proof

Below is the waveform showing the exact moment the AI learned to clog the router:

*(Note: Run `open -a gtkwave router.vcd` to see this on your machine)*

> The `buffer_count` signal shoots from 0 to 64 and flatlines, proving the AI has total control over the hardware state.

-----

## 🤝 Contributing

This is an open-research project. If you want to test this on different hardware (e.g., AXI Bridge, UART, RISC-V Core), feel free to fork the repo\!

1.  Fork it.
2.  Create your feature branch (`git checkout -b feature/NewHardware`).
3.  Commit your changes.
4.  Push to the branch.
5.  Create a new Pull Request.

-----

**Author:** [Dhruva Pandey](https://www.google.com/search?q=https://github.com/dhruvapandey)
**Date:** December 2025

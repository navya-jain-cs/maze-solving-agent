# Maze-Solving-Agent

This project demonstrates maze-solving algorithms using Q-learning, DynaQ, and DynaQ+ with a PyQt-based graphical user interface. The user can input the grid size, set the target, start, and blocked cells, and choose an algorithm to solve the maze or compare the performance of all three algorithms.

## Features

- **Input Grid Size**: Accepts grid sizes from 3x3 to 10x10.
- **Grid Setup**: Allows users to set the target, start, and blocked cells.
- **Maze Solving Algorithms**:
  1. **Q-learning**: Solves the maze using Q-learning.
  2. **DynaQ**: Solves the maze using DynaQ.
  3. **DynaQ+**: Solves the maze using DynaQ+.
  4. **Compare**: Plots a graph comparing the performance of Q-learning, DynaQ, and DynaQ+.

## Usage

1. Clone the repository and navigate to the project directory.

    ```bash
    git clone https://github.com/navya-jain-cs/maze-solving-agent.git
    cd maze-solving-agent
    ```

2. Install the required libraries.

    ```bash
    pip install -r requirements.txt
    ```

3. Run the `main.py` file to start the application.

    ```bash
    python main.py
    ```

4. Follow the on-screen instructions to:
    - Input the grid size (3 to 10).
    - Set the target cell.
    - Set the start cell.
    - Set the blocked cells.
    - Choose an algorithm to solve the maze or compare all three algorithms.

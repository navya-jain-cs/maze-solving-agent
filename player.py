import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random as r
from matplotlib import style
from PyQt5 import QtCore, QtGui, QtWidgets

# global x_T, y_T

class Player:
    def __init__(self, env, x_T, y_T, start, alpha=0.1, gamma=0.9, epsilon=0.2, planning_steps=5, kappa=0.2):
        self.env = env
        self.x_T = x_T
        self.y_T = y_T
        self.start = start
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration vs exploitation
        self.planning_steps = planning_steps  # Number of planning steps for Dyna-Q
        self.kappa = kappa
        self.Q_steps_per_ep = []
        self.dynaQ_steps_per_ep = []
        self.dynaQPlus_steps_per_ep = []
        self.Qtable = {}
        self.model = {}
        self.time_since_visited = {}
        for x in range(self.env.n):
            for y in range(self.env.n):
                if self.env.grid[x, y] != -1:  # Not blocked
                    self.Qtable[(x, y)] = {act: 0 for act, _ in self.env.get_possible_acts((x, y))}
                    self.model[(x, y)] = {act: None for act, _ in self.env.get_possible_acts((x, y))}
                    self.time_since_visited[(x, y)] = {act: 0 for act, _ in self.env.get_possible_acts((x, y))}

    def getAct(self, state):
        if r.uniform(0, 1) < self.epsilon:
            return r.choice(list(self.Qtable[state].keys()))  # Exploration
        else:
            return max(self.Qtable[state], key=self.Qtable[state].get)  # Exploitation

    def incQ(self, state, action, reward, next_state):
        if next_state not in self.Qtable:
            return
        best_next_action = max(self.Qtable[next_state], key=self.Qtable[next_state].get)  # maxQ'(s', a')
        td_target = reward + self.gamma * self.Qtable[next_state][best_next_action]  # R(s,a) + gamma * Q(s, a)
        td_error = td_target - self.Qtable[state][action]  # R(s,a) + gamma * Q(s, a) - Q(s, a)
        self.Qtable[state][action] += self.alpha * td_error  # Q(s, a) = Q(s, a) + alpha * { R(s,a) + [gamma * Q(s, a)] - Q(s, a) }

    def train_Q(self, episodes=2000):
        global q_learning_episodes, min_Path_Q
        for ep in range(episodes):
            state = (r.randint(0, self.env.n - 1), r.randint(0, self.env.n - 1))
            while not self.env.isValid(state) or state == (self.x_T, self.y_T):
                state = (r.randint(0, self.env.n - 1), r.randint(0, self.env.n - 1))

            while state != (self.x_T, self.y_T):
                action = self.getAct(state)
                next_state = [new_state for act, new_state in self.env.get_possible_acts(state) if act == action][0]
                reward = 1 if next_state == (self.x_T, self.y_T) else -(1/self.env.n)
                self.incQ(state, action, reward, next_state)
                state = next_state

            # Check if the path is optimal
            if ep == 1:
              min_Path_Q = 1000
            if ep > 2 :
              path = self.path(self.start)
              if self.is_optimal_path(path) and ep > 2:
                if len(path) < min_Path_Q:
                  q_learning_episodes = ep + 1
                  min_Path_Q = len(path)
            self.Q_steps_per_ep.append(len(self.path(self.start))-1)

    def train_DynaQ(self, episodes=2000):
        global dyna_q_episodes, min_Path_dynaQ
        for ep in range(episodes):
            while True:
              state = (r.randint(0, self.env.n - 1), r.randint(0, self.env.n - 1))
              if self.env.isValid(state) and state != (self.x_T, self.y_T):
                break

            while state != (self.x_T, self.y_T):
                action = self.getAct(state)
                next_state = [new_state for act, new_state in self.env.get_possible_acts(state) if act == action][0]
                reward = 1 if next_state == (self.x_T, self.y_T) else -(1/self.env.n)
                self.incQ(state, action, reward, next_state)

                # Update the model
                self.model[state][action] = (next_state, reward)

                # Planning steps
                for _ in range(self.planning_steps):
                    sim_state = r.choice(list(self.model.keys()))
                    sim_action = r.choice(list(self.model[sim_state].keys()))
                    sim_next_state, sim_reward = self.model[sim_state][sim_action] if self.model[sim_state][sim_action] else (sim_state, 0)
                    self.incQ(sim_state, sim_action, sim_reward, sim_next_state)

                state = next_state

            # Check if the path is optimal
            if ep == 1 :
              min_Path_dynaQ = 1000
            if ep > 2 :
              path = self.path(self.start)
              if self.is_optimal_path(path) :
                if len(path) < min_Path_dynaQ:
                  dyna_q_episodes = ep + 1
                  min_Path_dynaQ = len(path)
            self.dynaQ_steps_per_ep.append(len(self.path(self.start))-1)
            
    def train_DynaQPlus(self, episodes=2000):
        global dyna_q_plus_episodes, min_Path_dynaQPlus
        for ep in range(episodes):
            while True:
                state = (r.randint(0, self.env.n - 1), r.randint(0, self.env.n - 1))
                if self.env.isValid(state) and state != (self.x_T, self.y_T):
                    break

            while state != (self.x_T, self.y_T):
                action = self.getAct(state)
                next_state = [new_state for act, new_state in self.env.get_possible_acts(state) if act == action][0]
                reward = 1 if next_state == (self.x_T, self.y_T) else -(1/self.env.n)
                self.incQ(state, action, reward, next_state)

                # Update the model and time since visited
                self.model[state][action] = (next_state, reward)
                self.time_since_visited[state][action] = ep

                # Planning steps with bonus reward
                for _ in range(self.planning_steps):
                    # Choose a state-action pair based on the bonus
                    max_bonus = -float('inf')
                    chosen_state = None
                    chosen_action = None

                    for s in self.Qtable:
                        for a in self.Qtable[s]:
                            bonus = self.kappa * np.sqrt(ep - self.time_since_visited[s][a])
                            if self.Qtable[s][a] + bonus > max_bonus:
                                max_bonus = self.Qtable[s][a] + bonus
                                chosen_state = s
                                chosen_action = a

                    sim_next_state, sim_reward = self.model[chosen_state][chosen_action] if self.model[chosen_state][chosen_action] else (chosen_state, 0)
                    self.incQ(chosen_state, chosen_action, sim_reward, sim_next_state)

                state = next_state

            # Check if the path is optimal
            if ep == 1 :
              min_Path_dynaQPlus = 1000
            if ep > 2 :
              path = self.path(self.start)
              if self.is_optimal_path(path) :
                if len(path) < min_Path_dynaQPlus:
                  dyna_q_plus_episodes = ep + 1
                  min_Path_dynaQPlus = len(path)
            self.dynaQPlus_steps_per_ep.append(len(self.path(self.start))-1)
        
    def path(self, start):
        if start not in self.Qtable:
            return []
        path = [start]
        state = start
        while state != (self.x_T, self.y_T):
            if len(path) > self.env.n*self.env.n:
              return path
            if not self.Qtable[state]:  # If current state has no available actions in Q-table, returns the path found so far.
                return path
            action = max(self.Qtable[state], key=self.Qtable[state].get)  # Selects the action with the highest Q-value from the current state
            next_states = [new_state for act, new_state in self.env.get_possible_acts(state) if act == action]  # Find possible next states for selected action from current state
            if not next_states:  # Breaks loop if no valid next states
                break
            if next_states[0] == state:  # Breaks loop if next state = current state
                break

            state = next_states[0]
            path.append(state)
        return path

    def is_optimal_path(self, path):
        return path[-1] == (self.x_T, self.y_T)

    def reset(self):
        self.Qtable.clear()
        self.model.clear()
        self.env.reset()

def find_start_of_optimal_solution(arr):
    if not arr:
        return -1  # Return -1 or handle the case where arr is empty

    min_value = min(arr)
    n = len(arr)

    for i in range(n):
        if arr[i] == min_value:
            if all(x == min_value for x in arr[i:]):
                return i
    return -1
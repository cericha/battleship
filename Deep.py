from PlayerAI_10 import MoveStrategy
import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from Battleship import Ship, Grid
from collections import deque
from random import random

def convert_grid_to_numeric(map):
    numeric_map = []
    for row in map:
        numeric_row = []
        for cell in row:
            if type(cell) == int:
                numeric_row.append(0)
            elif type(cell) == str:
                numeric_row.append(1)
            elif type(cell) == Ship:
                numeric_row.append(cell.size)
            #numeric_row.append(mapping[cell])
        numeric_map.append(numeric_row)
    return np.array(numeric_map)


def flatten_empty_list(arr):
    empty_spaces = []
    for x,y in arr:
       empty_spaces.append(x*10 + y)
    return np.array(empty_spaces)


class DeepAI(MoveStrategy):

    def __init__(self):
        state_dim = 100
        action_dim = 100
        self.batch_size = 100
        self.agent = Agent(state_dim, action_dim, lr=0.001, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, buffer_size=64)
        self.total_reward = 0
        self.done = True
        self.prev_map = convert_grid_to_numeric(Grid().map)
        self.prev_action = 0
        self.epoch = 0
        self.writer = SummaryWriter()

    def get_move(self, board: Grid):
        empty_spaces = board.getEmptySpaces()
        reward = 0
        if not empty_spaces:
            return (0,0)

        empty_space_list = flatten_empty_list(empty_spaces)
        state = np.array([1 if i in empty_space_list else 0 for i in range(100)])
        action = self.agent.act(state, empty_space_list)

        current_map = convert_grid_to_numeric(board.map)
        x,y = self.prev_action//10, self.prev_action%10
        '''
        if board.map[y][x] == 1:
            print("Hit!")
            reward += 10
        else:
            reward += -1

        if type(board.map[y][x]) == Ship:
            print("Sunk!!!")
            reward += 30
        '''

        reward = 10 if board.map[y][x] == 1 else -1
        reward += 30 if type(board.map[y][x]) == Ship else 0

        if board == Grid():
            self.done = True
            self.writer.add_scalar('Reward', self.total_reward, self.epoch)
            self.epoch += 1
            self.total_reward = 0
        else:
            self.done = False
            self.agent.remember(self.prev_map.flatten(), self.prev_action, 
                                self.total_reward, current_map.flatten(), self.done)
            self.total_reward += reward
            self.agent.replay(self.batch_size)
            self.prev_action = action
            self.prev_map = current_map

        print(self.total_reward)
        return divmod(action, 10)

    '''
    def get_move(self, board: Grid):
        empty_spaces = board.getEmptySpaces()
        state = np.array(board.map).flatten()
        action = self.agent.act(state)
        self.prev_move = divmod(action, 10)
        return self.prev_move
    '''


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)

    def forward(self, x):
        x = T.relu(self.fc1(x))
        x = T.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class Agent:
    def __init__(self, state_dim, action_dim, lr, gamma, epsilon, epsilon_decay, buffer_size):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.memory = deque(maxlen=buffer_size)
        self.model = DQN(state_dim, action_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

    def act(self, state, valid_actions):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(valid_actions)
        q_values = self.model(T.tensor(state, dtype=T.float32))
        valid_q_values = q_values[valid_actions]
        return valid_actions[T.argmax(valid_q_values).item()]

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * T.max(self.model(T.tensor(next_state, dtype=T.float32))).item()
            target_f = self.model(T.tensor(state, dtype=T.float32)).detach().numpy()
            target_f[action] = target
            self.optimizer.zero_grad()
            loss = nn.MSELoss()(T.tensor(target_f), self.model(T.tensor(state, dtype=T.float32)))
            loss.backward()
            self.optimizer.step()
        if self.epsilon > 0.01:
            self.epsilon *= self.epsilon_decay




'''
old attempt:

class DeepQNetwork(nn.Module):
    def __init__(self, lr, input_dims, fc1_dims, fc2_dims, n_actions):
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, self.n_actions)
        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)
    
    # Since we inherited from nn.Module, backprop is already defined, we only need forward pass
    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        actions = self.fc3(x)

        return actions # We want the raw estimate
    

class Agent():
    def __init__(self, gamma, epsilon, lr, input_dims, batch_size, n_actions, 
                 max_mem_size=100000, eps_end = 0.01, eps_dec=5e-4):
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_end
        self.eps_dec = eps_dec
        self.lr = lr
        self.action_space = [(x,y) for x in range(math.isqrt(n_actions)) for y in range(math.isqrt(n_actions))]
        self.mem_size = max_mem_size
        self.batch_size = batch_size
        self.mem_center = 0

        self.Q_eval = DeepQNetwork(self.lr, n_actions=n_actions, input_dims=input_dims,
                                   fc1_dims=256, fc2_dims=256)

        # Opting for np arr instead of a Deque for memory
        self.state_memory = np.zeros((self.mem_size, *input_dims), dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, *input_dims),
                                         dtype=np.float32)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=bool)

    def store_transition_state(self, state, action, reward, state_, done):
        index = self.mem_center % self.mem_size 
        # We continue writing to memory until we hit the limit then wrap back and erase the memory

        state = np.array(state, dtype=np.float32)
        state_ = np.array(state_, dtype=np.float32)

        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = index
        self.terminal_memory[index] = done

        self.mem_center += 1

    def choose_action(self, observation):
        if np.random.random() > self.epsilon:
            state = T.tensor([observation]).to(self.Q_eval.device)
            actions = self.Q_eval.forward(state)
            action = T.argmax(actions).item()
        else:
            action = random.choice(self.action_space)

        return action
        
    # How are we going to learn from the exp
    def learn(self):
        if self.mem_center < self.batch_size:
            return
        
        self.Q_eval.optimizer.zero_grad()

        max_mem = min(self.mem_center, self.mem_size)
        batch = np.random.choice(max_mem, self.batch_size, replace=False)
        batch_index = np.arange(self.batch_size, dtype=np.int32)
        state_batch = T.tensor(self.state_memory[batch]).to(self.Q_eval.device)
        new_state_batch = T.tensor(self.new_state_memory[batch]).to(self.Q_eval.device)
        reward_batch = T.tensor(self.reward_memory[batch]).to(self.Q_eval.device)
        terminal_batch = T.tensor(self.terminal_memory[batch]).to(self.Q_eval.device)

        action_batch = self.action_memory[batch]
        q_eval = self.Q_eval.forward(state_batch)[batch_index, action_batch]
        q_next = self.Q_eval.forward(new_state_batch)
        q_next[terminal_batch] = 0.0

        q_target = reward_batch + self.gamma * T.max(q_next, dim=1)[0]

        loss = self.Q_eval.loss(q_target, q_eval).to(self.Q_eval.device)
        loss.backward()
        self.Q_eval.optimizer.step()

        self.epsilon = self.epsilon - self.eps_dec if self.epsilon > self.eps_min else self.eps_min
'''


# Battleship Solvers

Three agents that find a hidden Battleship board in as few shots as possible,
built as a group project for CSCI 76100 Artificial Intelligence, Hunter College, Spring 2024.

| Agent | Approach | Author |
|---|---|---|
| CSP | Constraint satisfaction over ship placements | @orionpal |
| ISMCTS | Single-observer Information Set Monte Carlo Tree Search | @cericha |
| DQN | Deep Q-Network (PyTorch) | @Sacredfuel |

## Running

```
python3 Battleship.py csp_game.json
python3 Battleship.py ISMCTS.json
python3 Battleship.py deep_game.json
```

Running with no argument uses `standard_game.json`; `human_game.json` lets a
person play. Each config controls board display, number of simulated games,
and cores used for parallel simulation. Average metrics print to the console
and three graphs are written per run. DQN requires PyTorch and TensorBoard.

Details and results for each agent: [CSP](CSP/CSP_README.md),
[ISMCTS](ISMCTS_README.md), [DQN](DQN_README.md).

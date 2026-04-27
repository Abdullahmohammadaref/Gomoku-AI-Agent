# ACE - A Gomoku AI Agent

## Overview
ACE is an AI agent that was developed as part of the GISMA University AI Cup tournament during the August 2025 skill sprint week.
## Features
- Minimax algorithm for ensuring accurate results
- Alpha-Beta pruning to enhance speed at the cost of some accuracy to meet the 5-second execution time requirement
- Pattern recognition for immediate response to specific board states.
- Leverages numpy and multithreading to balance between execution speed and result accuracy.
## Requirements
-  Python 3.12    
## How To Use 
1. Clone the repository by running `git clone https://github.com/Abdullahmohammadaref/Gomoku-AI-Agent`.
2. Run `pip install -r requirements.txt`.
3. Run `py app.py` to start the Flask server.
4. Enter the URL to view the two agents compete.
Note: to change the opposing agent, put the file of the agent in the [teams](teams) directory, then in [app.py](app.py) 
Import the agent file and change the `p1` variable in line 14 from `teams.dum_agent` to `teams.YOU_AGENT_NAME`.

## Contributors
- Abdullah Mohammad Aref
- Ahmed Khaled Ebrahim Mohammad

## References
- Teaching/exercises/artificial-intelligence/gomoku at main · m-mahdavi/teaching (no date) GitHub. Available at: https://github.com/m-mahdavi/teaching/tree/main/exercises/artificial-intelligence/gomoku (Accessed: April 23, 2026).

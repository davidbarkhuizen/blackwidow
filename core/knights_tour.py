from datetime import datetime
import random
import logging
  
from state import State
from node import Node
from decider import Decider
from coordinator import Coordinator

def main():
    
  coordinator = Coordinator()
  exit_criteria = coordinator.solve(max)

if __name__ == '__main__':
  main()

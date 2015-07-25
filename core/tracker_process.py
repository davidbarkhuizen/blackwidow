from datetime import datetime
import random
import time

from messages import Message, TerminationMessage
from tracker_agent import TrackerAgent
from decider import Decider
from node import Node

'''
CONNECTION MESSAGE OBJECTS
# TerminationMessage
# StatusMessage
# SolutionMessage
'''

def tracker_process(proc_id, root_node=None, connection=None):
  
  decider = Decider()    
  agent = TrackerAgent(decider=decider, root_node=root_node, connection=connection, proc_id=proc_id)  
  
  exit_condition = False
  start_time = time.time()
  while (exit_condition == False):
    
    exit_criteria = agent.iterate()
      
    '''# HANDLE INCOMING MESSAGES'''
    while (connection.poll() == True):     
      msg = connection.recv()
      assert(isinstance(msg, Message) == True)
      
      if (isinstance(msg, TerminationMessage)):
        exit_condition = True
        
    if (True in exit_criteria.values()):
      exit_condition = True      
    
  '''# SEND TERMINATION MESSAGE'''
  connection.send(TerminationMessage(proc_id=proc_id))
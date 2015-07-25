# log file - run info
# solutions file - solutions and paths

# PSUTIL - process & system utils
# http://code.google.com/p/psutil/

import logging, time
from datetime import datetime
from multiprocessing import Process, Pipe

import psutil

from agent import Agent
from node import Node
from state import State
from decider import Decider

from tracker_process import tracker_process
from messages import Message, TerminationMessage, SolutionMessage

def cls():
    print('\n'*30)

class Coordinator(object):

  def __init__(self):
    logging.info('Coordinator instantiating...')
    self.solution_nodes = []    

  def solve(self, decider=None, initial_state=None, max_child_count=None):

    n = 5
    initial_state = State(n)
    decision_path = []
    
    seed = datetime.now().microsecond
    logging.info('seed for random number generator - %i' % seed)
    
    exit_criteria = {
      'timed_out' : False,
      'request_cancel' : False,
      'is_solved' : False,
      'solution_space_exhausted' : False,
      }
    
    decider = Decider(random_seed=seed) 
    
    zero_node = Node(id=Node.next_id(), parent_id=None, state=initial_state, recursion_depth=0, decider=decider, max_child_count=max_child_count)
    zero_node.upsert()
    zero_node.create_children()
    zero_node.upsert()
    
    first_generation_count = zero_node.child_count
    
    total_processor_count = psutil.cpu_count()
    max_count = total_processor_count - 1 # use all CPUs, with one reserved for us
    #max_count = 1
    
    active_procs = {}
    terminated_proc_ids = []
    remaining_count = first_generation_count
    procs_instructed_to_terminate = []
    
    cancel = False    
    
    start_time = time.time()
    time_limit = None
    timed_limit_exceeded = False
    
    update_period = 0.5 # second
    
    solutions = []
    solution_counts = {}
    
    solution_count_time_evolution = {}
    
    next_proc_id = 1
    while ((cancel == True) and (len(active_procs.keys()) > 0)) or ((cancel == False) and ((remaining_count > 0) or (len(active_procs.keys()) > 0))):      
      
      if (time_limit != None):
        if (time.time() - start_time > time_limit):
          timed_limit_exceeded = True
      
      if (timed_limit_exceeded == True):
        cancel = True
        
      '''# ISSUE TERMINATION INSTRUCTIONS'''
      if (cancel == True):
        for proc_id in active_procs.keys():        
          if (proc_id not in procs_instructed_to_terminate):
            connxn = active_procs[proc_id]
            term_msg = TerminationMessage(proc_id=0)
            connxn.send(term_msg)
            print('proc %i instructed to terminate' % proc_id)
            procs_instructed_to_terminate.append(proc_id)
      
      new_solutions_arrived = False
      
      '''# HANDLE INCOMING MESSAGES'''
      for proc_id in active_procs.keys():        
        connxn = active_procs[proc_id]        
        
        while (connxn.poll() == True):
          msg = connxn.recv()
          
          '''# SOLUTION MSG'''
          if (isinstance(msg, SolutionMessage)):
            new_solutions_arrived = True
            solutions.append(msg.solution)
            if (msg.proc_id in solution_counts.keys()):
              solution_counts[msg.proc_id] = solution_counts[msg.proc_id] + 1
            else:
              solution_counts[msg.proc_id] = 1
          
          '''# STATUS MSG'''          
          
          '''# TERMINATION MSG'''
          if (isinstance(msg, TerminationMessage)):
            print('TerminationNotice received from process %i' % msg.proc_id)
            active_procs.pop(msg.proc_id)
            terminated_proc_ids.append(msg.proc_id)
      
      '''# SPAWN NEW PROCESS IF NOT YET DONE'''
      if ((cancel == False) and (len(active_procs.keys()) < max_count) and (remaining_count > 0)):
        
        print(zero_node.next_child_idx)
        
        '''# GET NEXT UNUSED STATE, IF ANY '''
        if (zero_node.next_child_idx != -1):          
          
          node_idx = zero_node.child_ids[zero_node.next_child_idx]
          node = Node.tree[node_idx]
          
          '''# ADJUST next_child_idx '''
          if (zero_node.next_child_idx < zero_node.child_count - 1):
            zero_node.next_child_idx = zero_node.next_child_idx + 1
          else:
            zero_node.next_child_idx = -1
          
          zero_node.upsert()
                  
          proc_id = next_proc_id
          next_proc_id = next_proc_id + 1
          
          (parent_connxn, child_connxn) = Pipe()
          active_procs[proc_id] = parent_connxn
          
          proc = Process(target=tracker_process, args=(proc_id, node, child_connxn))
          proc.start()          
          
          remaining_count = remaining_count - 1
      
      if (new_solutions_arrived):
        cls()
        counts = [('%i - %i' % (pid, solution_counts[pid])) for pid in solution_counts.keys()]
        print(str(len(solutions)) + ' : ' + (','.join(counts)) )
        print('active - ' + str(active_procs.keys()))
        print('completed' + str(terminated_proc_ids))        
        
        d = {}
        d[0] = [len(solutions)]
        for pid in solution_counts.keys():
          d[pid] = solution_counts[pid]
        solution_count_time_evolution[datetime.now()] = d
  
      time.sleep(update_period)
    
    print('all done')
    
    print('writing solutions to disk')
    f = open('solutions.txt', 'w')    
    for state in solutions:
      f.write('\n')
      f.write(str(state))
    f.close()   
    
    print('writing solution count time-evolution to disk')
    
    sorted_keys = sorted([x for x in solution_counts.keys()])
    f = open('solution_count_time_evolution.csv', 'w')
    for key in sorted_keys:
      f.write(str(key) + ',' + ','.join([str(x) for x in solution_count_time_evolution[key]]) + '\n')
    
      counts = solution_count_time_evolution[key]
      s = ''
      for i in range(first_generation_count):
        n = i + 1        
        if (n not in counts.keys()):
          s = s + '0' + ','
        else:           
          s = s + str(counts[n]) + ','
    
      f.write(s + '\n')
    
    f.close()   
    
    

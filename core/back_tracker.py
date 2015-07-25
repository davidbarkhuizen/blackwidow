# log file - run info
# solutions file - solutions and paths

# PSUTIL - process & system utils
# http://code.google.com/p/psutil/

import logging
from datetime import datetime
import time

import psutil

from node import Node
from state import State

class BackTracker(object):

  def __init__(self, is_prime=True):
    self.solution_nodes = []
    self.is_prime = is_prime

  def solve(self, decider=None, initial_state=None):
    
    start_time = datetime.now()
   
    solved_count = 0
    best_solved_count = 0
    
    dead_end_count = 0
    
    max_child_count = 64
    
    # INIT ROOT/ZERO NODE
    current_node = Node(id=Node.next_id(), parent_id=None, state=initial_state.clone(), recursion_depth=0, decider=decider, max_child_count=max_child_count)
    current_node.upsert()

    # LOG INITITAL STATE
    logging.info(datetime.now())
    logging.info('root node {%i} instantiated.' % current_node.id)
    logging.info('with initial state = ')
    logging.info(str(initial_state))
    
    target_depth = initial_state.target_depth()
    
    # CREATE FIRST GENERATION OF CHILDREN
    logging.info('creating child states...')
    current_node.create_children()
    logging.info('%i created.' % current_node.child_count)
    
    decision_path = []
    
    exit_criteria = {
      'timed_out' : False,
      'request_cancel' : False,
      'is_solved' : False,
      'solution_space_exhausted' : False,
      }
      
    rotator_counter = 0
    rotator_interval = 100000
    
    exhaust_solution_space = True
    
    skip_solution = False
    while (True not in exit_criteria.values()):
      
      current_time = datetime.now()
      total_elapsed_time = current_time - start_time
      total_elapsed_seconds = total_elapsed_time.total_seconds()
      approx_total_elapsed_minutes = total_elapsed_seconds / 60
      approx_total_elapsed_hours = total_elapsed_seconds / (60 * 60)
      approx_total_elapsed_days = total_elapsed_seconds / (60 * 60 * 24)
    
      # INDICATE PROGRESS
      rotator_counter = rotator_counter + 1
      if (rotator_counter % rotator_interval == 0):
        print('=-'*10)
        print('started @ %s, now @ %s]' % (start_time, current_time))
        print('%i seconds ~ %i minutes ~ %i hours ~ %i days' %
              (total_elapsed_seconds, approx_total_elapsed_minutes, approx_total_elapsed_hours, approx_total_elapsed_days))
        print('node %i - current {%i}/{%i} vs. best {%i}/{%i}' % (current_node.id, solved_count, target_depth, best_solved_count, target_depth))
        print('total solution count - %i' % len(self.solution_nodes))
        print('tree node count - %i' % len(Node.tree.keys()))
        print('dead-end count - %i' % dead_end_count)
        phys_usage = psutil.phymem_usage() 
        print('%d %% of physical memory used' % phys_usage.percent)
        virt_usage = psutil.virtmem_usage() 
        print('%d %% of virtual memory used' % virt_usage.percent)
      
      # SOLVED
      if (decider.solution_status(current_node.state) == True) and (skip_solution == False):
        exit_criteria['is_solved'] = True
        current_node.is_solution = True
        self.solution_nodes.append(current_node)
        
        logging.info('node {%i} solves.' % current_node.id)
        logging.info('state:')
        logging.info(str(current_node.state))        
        
        print('solved')
        print(str(current_node.state))
        
        if (exhaust_solution_space == True):
          exit_criteria['is_solved'] = False
          skip_solution = True
      
      # CONTINUE [current_node is not solution]
      else:
        skip_solution = False
        logging.info('solution not yet reached.')
        
        # NEED TO GENERATE CHILDREN FOR NODE
        if (current_node.next_child_idx == None):
          logging.info('need to generate children for node {%i} ...' % current_node.id)
          current_node.create_children()
          if (current_node.child_count == 0):
            dead_end_count = dead_end_count + 1 
          
          logging.info('done.  %i children created.' % current_node.child_count)
        
        # MOVE FORWARD [IF THE CURRENT NODE HAS AN UNEVALUATED CHILD, THEN MOVE TO IT]
        if (current_node.next_child_idx != -1):
          logging.info('current node {%i} has an unevaluated child' % current_node.id)
          
          # get next child
          next_node_id = current_node.child_ids[current_node.next_child_idx]
          next_node = current_node.get(next_node_id)
          logging.info('moved fwd to unevaluated child node {%i} of parent node {%i} [child no. %i of %i]' % (next_node.id, current_node.id, current_node.next_child_idx + 1, current_node.child_count))

          # increment next child idx
          if (current_node.next_child_idx < current_node.child_count - 1):
            current_node.next_child_idx = current_node.next_child_idx + 1
          # ALL CHILDREN EXHAUSTED
          else:
            current_node.next_child_idx = -1 
          
          current_node.upsert()
          
          # NOTE MOVE FWD
          solved_count = solved_count + 1
          if (solved_count > best_solved_count):
            best_solved_count = solved_count
          logging.info("current completeness = {%i}/{%i}" % (solved_count, target_depth))
          logging.info("vs. best completeness = {%i}/{%i}" % (best_solved_count, target_depth))

          change_loc = current_node.state.locate_fwd_change(next_node.state)
          logging.info('change loc %s' % str(change_loc))

          decision_path.append(change_loc)
          logging.info('updated decision path')
          logging.info(decision_path)
          
          logging.info('new state')
          logging.info(next_node.state)
          
          # update completeness
          # current_completeness = solved_count / target_count * 100)
          # best_completeness = best_solved_count / target_count * 100)

          # increment pointer to next unevaluated remaining child (dec ## of remaining uneval children)          

          current_node = next_node

        # current_node.has_available_children() == False
        else:       
          logging.info("no unevaluated children, i.e. dead-end reached.")

          # MOVE BACKWARDS
          # if current node has a parent, and thus it is actually possible to move backwards
          if (current_node.parent_id != None):

            # retrieve parent node
            next_node = Node.tree[current_node.parent_id]
            logging.info('moving back to parent node {%i}' % next_node.id)
            
            # locate change
            change_loc = current_node.state.locate_bwd_change(next_node.state)

            solved_count = solved_count - 1
            decision_path.pop()
            
            logging.info("current completeness = {%i}/{%i}" % (solved_count, target_depth))
            logging.info("vs. best completeness = {%i}/{%i}" % (best_solved_count, target_depth))
            
            node_to_discard = current_node
            current_node = next_node
            Node.purge_node(node_to_discard)

          ## CanMoveBackwards() == False
          else:             
            exit_criteria['solution_space_exhausted'] = True
            
            logging.info('node i% has no parent.' % current_node.id)
            logging.info('solution space exhausted.')
       
    for exit_criterion in exit_criteria.keys():
      logging.info('%s - %s' % (exit_criterion, exit_criteria[exit_criterion]))  
    
    return exit_criteria
from datetime import datetime
import logging
import time

# PSUTIL - process & system utils
# http://code.google.com/p/psutil/
import psutil

from state import State
from node import Node
from messages import SolutionMessage

class TrackerAgent(object):

  def __init__(self, decider=None, root_node=None, connection=None, proc_id=None):
    
    self.connection = connection
    self.proc_id = proc_id
    
    '''# TODO - FIX - move to decider ?'''
    max_child_count = root_node.state.n * root_node.state.n 
    self.target_depth = root_node.state.target_depth()
    
    self.decider = decider
    '''# TODO need to get decision path from node'''
    self.decision_path = []
    self.solution_nodes = []   
        
    root_node.upsert() # TODO - REDUNDANT ?
    root_node.create_children()
    root_node.upsert()
    
    self.root_node = root_node
    self.current_node = root_node
    
    self.exit_criteria = {
      'solution_found' : False,
      'solution_space_exhausted' : False,
      }
      
    self.exhaust_solution_space = True

  def iterate(self):

    if (True not in self.exit_criteria.values()):    
      
      '''# SOLVED '''
      if (self.decider.solution_status(self.current_node.state) == True):
        
        self.current_node.is_solution = True
        self.solution_nodes.append(self.current_node)
        
        '''# SEND SOLUTION MSG TO CO-ORDINATOR '''
        solution_msg = SolutionMessage(proc_id=self.proc_id, solution=self.current_node.state)
        self.connection.send(solution_msg)        
        
        self.exit_criteria['solution_found'] = (self.exhaust_solution_space == False)         
      
      '''# GENERATE CHILDREN '''
      if (self.current_node.is_solution == False):      
      
        if (self.current_node.next_child_idx == None):
          self.current_node.create_children()
      
      '''# MOVE FORWARD [IF THE CURRENT NODE HAS AN UNEVALUATED CHILD, THEN MOVE TO IT]'''
      if ((self.current_node.is_solution == False) and (self.current_node.next_child_idx != -1)):
        
        '''# get next child'''
        self.next_node_id = self.current_node.child_ids[self.current_node.next_child_idx]
        self.next_node = self.current_node.get(self.next_node_id)

        '''# increment next child idx'''
        if (self.current_node.next_child_idx < self.current_node.child_count - 1):
          self.current_node.next_child_idx = self.current_node.next_child_idx + 1
        # ALL CHILDREN EXHAUSTED
        else:
          self.current_node.next_child_idx = -1 
        
        self.current_node.upsert()
        
        '''# NOTE MOVE FWD'''
        change_loc = self.current_node.state.locate_fwd_change(self.next_node.state)
        self.decision_path.append(change_loc)

        '''# increment pointer to next unevaluated remaining child (dec ## of remaining uneval children)'''          

        self.current_node = self.next_node

        '''# current_node.has_available_children() == False => no unevaluated children, i.e. dead-end reached'''
      else:       
        '''# MOVE BACKWARDS - if current node has a parent, and thus it is actually possible to move backwards'''
        if (self.current_node.recursion_depth > 1):

          '''# retrieve parent node'''
          try:
            self.next_node = Node.tree[self.current_node.parent_id]
          except KeyError:
            print('self.current_node.id = %i' % self.current_node.id)
            print('state')
            print(self.current_node.state)
            print('recursion depth %i' % self.current_node.recursion_depth)            
            
            print('self.current_node.parent_id')
            print(self.current_node.parent_id)
            print('tree')
            for id in Node.tree.keys():
              print(id)
              n = Node.tree[id]
              print(n.state)              
            
            raise
                                    
          '''# locate change'''
          self.change_loc = self.current_node.state.locate_bwd_change(self.next_node.state)

          self.decision_path.pop()
          
          node_to_discard = self.current_node
          self.current_node = self.next_node
          Node.purge_node(node_to_discard)

          '''# CanMoveBackwards() == False'''
        else:             
          self.exit_criteria['solution_space_exhausted'] = True
       
    return self.exit_criteria  
  
  def generate_status_message(self):
    
    current_time = datetime.now()
    total_elapsed_time = current_time - start_time
    total_elapsed_seconds = total_elapsed_time.total_seconds()
    approx_total_elapsed_minutes = total_elapsed_seconds / 60
    approx_total_elapsed_hours = total_elapsed_seconds / (60 * 60)
    approx_total_elapsed_days = total_elapsed_seconds / (60 * 60 * 24)
  
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
  
  
  
  
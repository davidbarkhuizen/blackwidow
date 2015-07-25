import random
import logging

from state import State

class Decider:

  def __init__(self, random_seed=0):
    
    # INIT RANDOM NUMBER GEN WITH SEED
    self.random_seed = random_seed
    random.seed(random_seed)
    logging.info('random seed = %i' % random_seed)
    
  def solution_status(self, state):
    return (state.depth() == state.target_depth())

  displacements = [\
      ( 1, 2),
      ( 2, 1),
      ( 2,-1),
      ( 1,-2),
      (-1,-2),
      (-2,-1),
      (-2, 1),
      (-1, 2),
      ]  

  def get_child_states(self, parent_state):
    '''
    returns [State]
    '''
    
    is_first_gen = True
    for column in parent_state.matrix:
      for element in column:
        if (element != 0):
          is_first_gen = False
    
    child_states = []
    
    n = parent_state.n
    
    # INITIAL MOVE
    if (is_first_gen):
      
      options = []
      for x in range(n):
        for y in range(n):
          options.append((x,y))
          
      moves = []
      remaining = range(len(options))
      while (len(remaining) > 0):
        idx = remaining.pop()#random.randint(0, len(remaining) - 1))        
        moves.append(options[idx])
        
      for i in range(len(moves)):
        (x,y) = moves[i]        
        clone = parent_state.clone()
        clone.set_xy(x, y, 1)
        child_states.append(clone)
    
    # ALL SUBSEQUENT MOVES
    else:
      (x1,y1) = parent_state.last_move()
      cur_depth = parent_state.depth()
      
      order = []
      remaining = range(len(Decider.displacements))
      while (len(remaining) > 0):
        idx = remaining.pop()#random.randint(0, len(remaining) - 1))
        order.append(idx)     
      assert(len(order) == len(Decider.displacements))
      for i in range(len(order)):
        (xd,yd) = Decider.displacements[order[i]]
        x2 = x1 + xd
        y2 = y1 + yd
        if ((x2 >= 0) and (x2 < n)) and ((y2 >= 0) and (y2 < n)):
          if (parent_state.matrix[x2][y2] == 0):
            child_state = parent_state.clone()
            child_state.matrix[x2][y2] = cur_depth + 1
            child_states.append(child_state)

    return child_states
      
  # evaluate base-line / pre-decision situation
  # find all useful options by brute-force checking
  # execute each possible option in turn / in isolation, and evaluate situation for new state
  # score new state - i.t.o improvements made, and confirm that it should not be rejected outright
  # no useful child states => dead-end => return empty set of states
  # trim child-states with undesirable characteristics
    
  def filter_useful_states_to_children(self, useful_states, max_children_to_use):    
    
    # null case
    if (len(useful_states) == 0):
      return []    

    # if there are less available child states than the minimum desired
    # then reduce effective number of children

    ret_count = 0
    if (len(useful_states) < max_children_to_use):
        ret_count = len(useful_states)
    else:
        ret_count = max_children_to_use

    return_states = []
    ret_idxs = []

    # FIRST CHILD = MOST ATTRACTIVE (i.t.o PENALTY) OF USEFUL
    # first find all most attractive options
    # select random choice from this set of most attractive (useful) options  
    # LOG ALL USEFUL COVERINGS - SORTED BY .Count.
    # SECOND CHILD = MOST ATTRACTIVE OF MOST USEFUL
    # get from most useful
    # get from second most useful (if exists)
    # sort into ascending penalty (i.e. best to worst)
    # first find all most attractive options
    # select random choice from this set of most attractive (useful) options  
    # add penalties from second and third best cats
    # first determine which pool we are going to pick from
    # make random choice
    # on last day draw both children from set of most attractive of most useful
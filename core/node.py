class Node(object):

  last_id = 0
  @classmethod
  def next_id(cls):
    
    if (len(Node.tree.keys()) > 0) and (Node.last_id == 0):
      Node.last_id = max([id for id in Node.tree.keys()]) 
    
    id = Node.last_id + 1
    Node.last_id = id
    return id

  # tree = { node_id : node }
  tree = {}
  
  @classmethod
  def purge_node(cls, node):
    discarded_node = Node.tree.pop(node.id)  
  
  def __init__(self, id=None, parent_id=None, state=None, recursion_depth=-1, decider=None, max_child_count=0, is_solution=False):

    self.id = id
    self.parent_id = parent_id
    
    assert(state != None) # and (state is State)
    self.state = state

    self.is_solution = is_solution    
    self.recursion_depth = recursion_depth

    assert(decider != None) # and (decider is Decider)
    self.decider = decider
    
    self.max_child_count = max_child_count    
    self.child_count = 0
    self.child_ids = []
    self.next_child_idx = None
    
  def upsert(self):
    Node.tree[self.id] = self

  def get(self, id):
    return Node.tree[id]
      
  def create_children(self):
 
    child_states = []
    child_states = self.decider.get_child_states(self.state)
    
    self.child_count = len(child_states)
    
    for i in range(self.child_count):
      child_id = Node.next_id()
      child_node = Node(decider=self.decider, id=child_id, parent_id=self.id, recursion_depth=self.recursion_depth + 1, max_child_count=self.max_child_count, state=child_states[i])
      self.child_ids.append(child_id)      
      child_node.upsert()

    if (self.child_count > 0):
      self.next_child_idx = 0
    else:
      self.next_child_idx = -1

    self.upsert() 
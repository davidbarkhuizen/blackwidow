class State(object):
  
  def __init__(self, n):
    
    # State.matrix[x][y]
    # [0][0] = bottom left
    # [n][n] = top right
    
    self.n = n
    
    self.matrix = []
    for x in range(n):
      col = []
      for y in range(n):
        col.append(0)
      self.matrix.append(col)

  def set_xy(self, x, y, value):
    self.matrix[x][y] = value
    
  def get_xy(self, x, y):
    return self.matrix[x][y]
  
  def xy_is_solved(self, x, y):
    return (self.matrix[x][y] != 0)
  
  def __str__(self):
    n = self.n
    s = ''
    for sy in range(n):     
      for sx in range(n):
        val = self.get_xy(sx, (n - 1) - sy)
        s = s + str(val).zfill(2) + ','
      s = s + '\n' 
    return s
    
  def clone(self):
    clone = State(self.n)
    for x in range(self.n):
      for y in range(self.n):
        clone.set_xy(x, y, self.get_xy(x, y))
    return clone
    
  def depth(self):
    depth = 0
    for x in range(self.n):
      for y in range(self.n):
        if (self.xy_is_solved(x,y)):
          depth = depth + 1
    return depth
      
  def target_depth(self):
    return self.n * self.n 
    
  def locate_fwd_change(self, next_state):
    for x in range(self.n):
      for y in range(self.n):
        if (self.matrix[x][y] != next_state.matrix[x][y]):
          return (x,y)
    return None  
    
  def locate_bwd_change(self, prev_state):
    for x in range(self.n):
      for y in range(self.n):
        if (self.matrix[x][y] != prev_state.matrix[x][y]):
          return (x,y)
    return None  
    
  def last_move(self):
    co_ords = (-1,-1)
    max = 0
    for x in range(self.n):
      for y in range(self.n):
        if (self.matrix[x][y] > max):
          co_ords = (x,y)
          max = self.matrix[x][y]
    return co_ords
    
    
    
    
    
    
    
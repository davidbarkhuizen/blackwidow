class TerminationStatus(object):
  COMPLETED = 'completed'
  TIMED_OUT = 'timed_out'
  INSTRUCTED_TO_CANCEL = 'instructed_to_cancel'

class Message(object):
  pass

class TerminationMessage(Message):
  
  def __init__(self, proc_id=0, termination_status=None):
    self.proc_id = proc_id
    self.termination_status = termination_status 
  
  def __str__(self):
    return '%i : %s' % (self.proc_id, self.termination_status)
    
class SolutionMessage(Message):
  def __init__(self, proc_id=0, solution=None):
    self.proc_id = proc_id
    self.solution = solution
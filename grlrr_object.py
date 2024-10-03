from grlrr_states import Initializing

class Grlrr(object):

    def __init__(self):
        self.state = Initializing()
    
    def on_event(self, event):
        self.state = self.state.on_event(event)
class State(object):

    def __init__(self):
        print('current state: ', str(self))

    def on_event(self, event):
        print(event)
        for i in range(10):
            print(i)

        # handle events
        pass

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return self.__class__.__name__
    

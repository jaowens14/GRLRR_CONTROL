import os
from grlrr import Grlrr

def main():
    grlrr = Grlrr()
    grlrr.run()

if __name__ == "__main__":
    PID = str(os.getpid())
    with open('.grlrr.pid', 'w') as file:
        file.write(PID)
        file.close()
    main()


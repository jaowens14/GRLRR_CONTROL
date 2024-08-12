import os
import communications

if __name__ == "__main__":
    PID = str(os.getppid())
    with open('grlrr.pid', 'w') as file:
        file.write(PID)
        file.close()
    communications.main()

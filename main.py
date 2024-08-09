import os
import communications
import log_server

if __name__ == "__main__":
    PID = str(os.getppid())
    with open('grlrr.pid', 'w') as file:
        file.write(PID)
        file.close()
    log_server.main()
    communications.main()

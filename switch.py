

mystring = "process --stop"
term = mystring
match term:

    case "process":
        print("process")
    case "process --stop":
        print("stop")

    case _:
        print("y are you?")
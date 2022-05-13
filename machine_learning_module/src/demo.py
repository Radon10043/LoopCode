with open("demo.py", "r") as f:
    for i in range(20):
        print(i)
        content = f.readline()
        print(content)
        if content == "":
            break

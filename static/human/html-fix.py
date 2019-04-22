import os
src=""
with open("template.html", "r") as f:
    src = f.read()

src=src.split("|")

t = os.listdir()

for i in t:
    if i not in ["html-fix.py", "template.html"] and not os.path.isdir(i):
        with open(i, "r") as f:
            x=f.read()
        with open("./fixed/"+i, "w") as f:
            f.write(src[0])
            f.write('\n')
            f.write(x)
            f.write('\n')
            f.write(src[1])

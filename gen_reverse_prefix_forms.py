f = open("wordbank_rpf.txt", "a")

all_rpf = []

with open("CSW24.txt", "r") as csw24:
    for word in csw24:

        word = word[:len(word)-1]

        for i in range(len(word)):
            newword = ""
            for j in range(i, -1, -1):
                newword += word[j]

            if (i != len(word)-1):
                newword += "#"
                for j in range(i+1, len(word)):
                    newword += word[j]

            all_rpf.append(newword)


all_rpf = sorted(all_rpf)
for word in all_rpf:
    f.write(word + "\n")


f.close()

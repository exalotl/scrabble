class Node:
    def __init__(self):
        self.children = {} # letter, id
        self.endflag = False
        self.sig = None

    def signature(self):
        self.sig = (self.endflag, tuple(self.children.items()))

class DAWG:
    def __init__(self):
        self.register = {} # sig, id
        self.root = Node()
        self.section = [] # parent, node, letter of edge from parent to node (section to minimise)

    def insert(self, word):
        cur = self.root
        for i in range(len(word)):
            if cur.children.get(word[i]) == None:
                newnode = Node() ####
                cur.children[word[i]] = newnode

            cur = cur.children[word[i]]
        cur.endflag = True

    def minimise(self): # minimises whatever is in self.section
        while self.section:
            parent,child, letter = self.section.pop()
            child.signature()
            if self.register.get(child.sig) != None:
                parent.children[letter] = self.register[child.sig]
            else:
                self.register[child.sig] = child


    def build(self, file):
        with open(file, "r") as f:
            words = [word.strip() for word in f]

        self.insert(words[0])
        prevword = words[0]
        for word in words[1:]:
            # find section to minimise from prevword
            cur = self.root
            different = False
            for i in range(len(prevword)):
                if i > len(word)-1 or word[i] != prevword[i]:
                    different = True
                if different:
                    self.section.append((cur, cur.children[prevword[i]], prevword[i]))
                cur = cur.children[prevword[i]]
            self.minimise()

            self.insert(word)
            prevword = word

        cur = self.root
        for i in range(len(prevword)):
            self.section.append((cur, cur.children[prevword[i]], prevword[i]))
            cur = cur.children[prevword[i]]
        self.minimise()

    def search(self, word):
        cur = self.root
        for i in range(len(word)):
            if cur.children.get(word[i]) == None:
                return False
            else: 
                cur = cur.children[word[i]]

        if cur.endflag == True:
            return True
        else:
            return False
def search(x,l):
    d = set()
    for i in l:
        s = x-i
        if(s in d):
            return True
        d.add(i)
    
    return False

print(search(3,[1,2,3]))

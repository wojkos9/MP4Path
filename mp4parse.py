import re
from itertools import tee
from functools import reduce
from struct import unpack
import os
q = 0

class Mp4Parser:
    SUCC=1

    def __init__(self, f):
        self.f = f
    
    def search(self, pat, maxs):
        def search_impl(li, maxs, i=0):
            print("MAX", maxs)
            if i < len(li):
                tok = li[i]
                code = tok[0]
                if "=" in code:
                    l, r = code.split("=")
                    l=int(l)
                    r = r.encode("ascii")
                    n = len(r)
                    f.seek(l, 1)
                    val = f.read(n)
                    ret = 2*int(val == r), None
                    f.seek(-l-n, 1)
                    print(l, "=", r, "?:", ret[0], val)
                    return ret

                code = code.encode('ascii')
                opt = tok[1] if len(tok)>1 else None

                print("SEARCH", code, opt, sep=", ")
                trav = 0
                while 1:
                    n, code2 = unpack(">I4s", f.read(8))
                    nr = 8
                    print("DISC", n, code2, hex(n))
                    if n == 1:
                        n = unpack(">Q", f.read(8))[0]
                        nr = 16
                    elif n < 8:
                        raise Exception()
                    trav += nr
                    
                    if code2 == code:
                        cont=True
                        if opt:
                            print(">>", trav)
                            checkp = f.tell()
                            rc, dat = search_impl(opt, n, 0)
                            f.seek(checkp, 0)
                            print("<<")
                            if rc != 0:
                                print("OPT RC 1")
                                if dat:
                                    return 2, dat
                                else:
                                    # f.seek(-nr, 1)
                                    return 2, n
                            else:
                                cont = False
                        if cont:
                            print(">")
                            rc, dat = search_impl(li, n, i+1)
                            if rc == 1:
                                if dat:
                                    return rc, dat
                                else:
                                    return rc, n
                            elif rc == 2:
                                rc, dat = search_impl(li, n, i+2)
                                if rc == 1:
                                    if dat:
                                        return rc, dat
                                    else:
                                        return rc, n
                            
                    ofs = n-nr
                    trav += ofs
                    if trav >= maxs:
                        print("<", code2)
                        break
                    print("Seek", ofs, "===>", code)
                    f.seek(ofs, 1)
                return 0, None
            else:
                return 1, None
        def parse_path(p: str):
            tok0 = p.split()
            tok = []
            nopen = 0
            newtok = ""
            for t in tok0:
                nopen += t.count("[") - t.count("]")
                if nopen > 0:
                    newtok += t+" "
                elif nopen == 0:
                    newtok += t
                    if (a := newtok.find("[")+1):
                        b = newtok.rfind("]")
                        rest = parse_path(newtok[a:b])
                        tok.append((newtok[:a-1], rest))
                    else:
                        tok.append((newtok,))
                    newtok=""
            if newtok:
                tok.append((newtok,))
            return tok

        pp = parse_path(pat)
                
        # mit = re.finditer("([a-z]+)(?:\[(.*?)\])?", pat)
        rc, dat = search_impl(pp, maxs)
        if rc != 0:
            print(dat)
            
            print(f.read(16))
        return rc, dat


with open("vid.mp4", "rb") as f:
    par = Mp4Parser(f)
    maxs = os.path.getsize(f.name)
    print("MAX", maxs)
    rc, dat = par.search("moov trak[mdia hdlr[8=soun]] mdia minf stbl stts", maxs)
    print(dat)
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
                    ret = 2 if val==r else 0, None
                    f.seek(maxs-l, 1)
                    print(l, "=", r, "?:", ret[0], val)
                    return ret

                code = code.encode('ascii')
                opt = tok[1] if len(tok)>1 else None

                print("SEARCH", code, opt, sep=", ")
                trav = 0
                while 1:
                    n, code2 = unpack(">I4s", f.read(8))
                    nr = 8
                    # print("DISC----------", n, code2)
                    print("== "+code2.decode("ascii"))
                    if n == 1:
                        n = unpack(">Q", f.read(8))[0]
                        nr = 16
                    elif n < 8:
                        raise Exception()
                    # trav += nr

                    ofs = n-nr
                    trav += n
                    
                    if code2 == code:
                        cont=True
                        if opt:
                            print(">>", trav)
                            print(">>", opt)
                            checkp = f.tell()
                            rc, dat = search_impl(opt, n-nr, 0)
                            print("<<")
                            if rc != 0:
                                f.seek(checkp, 0)
                                print("OPT RC 1")
                            else:
                                f.seek(checkp + n-nr, 0)
                                cont = False
                        if cont:
                            print(">")
                            print(">", code)
                            rc, dat = search_impl(li, n-nr, i+1)
                            if rc == 1:
                                return rc, dat
                            elif rc == 2:
                                return 1, dat
                    else:
                        f.seek(ofs, 1)
                    
                    if trav == maxs:
                        a = f.read(16)
                        f.seek(-16, 1)
                        print("PEEK", a)
                        print("OVER", trav, "==", maxs)
                        # print("<", code2, "S("+str(code)+")")
                        break
                    elif trav > maxs:
                        raise Exception("SIZE ERROR %d > %d" % (trav, maxs))
                    else:
                        pass
                        # print(trav, "<", maxs)
                    print("Seek", ofs, "--->", code)
                    
                    
                return 0, None
            else:
                print("FOUNDFOUND", li[-1])
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
        rc, dat = search_impl(pp, maxs)
        return rc, dat


with open("vid.mp4", "rb") as f:
    par = Mp4Parser(f)
    maxs = os.path.getsize(f.name)
    print("MAX", maxs)
    rc, dat = par.search("moov trak mdia[hdlr[8=vide]] minf stbl stss", maxs)
    # rc, dat = par.search("moov trak[mdia hdlr[8=vide]] mdia minf stbl stss", maxs)
    if rc:
        samp = f.read(16)
        f.seek(-16, 1)
        print(samp)
    else:
        print("FAIL")
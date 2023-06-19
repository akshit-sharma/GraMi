from collections import defaultdict

class PatternGraph:

    def __init__(self, vertices: list[tuple[int, int]], edges: list[tuple[int, int, int]]):
        self.vertices = vertices
        self.edges = edges
        self.clique = self.isClique()

    def size(self):
        return len(self.vertices)

    def edgeExist(self, s, d):
        for (s1, d1, l) in self.edges:
            if s1 == s and d1 == d:
                return 1, l
        return 0, None

    def edgeArrow(self, s, d):
        bit21, l1 = self.edgeExist(s, d)
        bit22, l2 = self.edgeExist(d, s)
        bit2 = bit21 + bit22*2
        if bit2 == 0:
            return '     '
        if bit2 == 1:
            return '---{}>'.format(l1)
        if bit2 == 2:
            return '<{}---'.format(l2)

        assert bit2 == 3
        return '<{}-{}>'.format(l2, l1)

    def label(self, v):
        for (vid, vlabel) in self.vertices:
            if vid == v:
                return vlabel
        return None

    def isClique(self):
        for (s, _) in self.vertices:
            for (d, _) in self.vertices:
                if s == d:
                    continue
                if self.edgeExist(s, d) == 0:
                    return False
        return True


    def reorder(self, v0, v1, v2):
        # if v0 is not connected to v1, swap v1 and v2
        if self.edgeExist(v0, v1) == 0 and self.edgeExist(v1, v0) == 0:
            return v0, v2, v1
        # if v1 is not connected to v2, swap v0 and v1
        if self.edgeExist(v1, v2)[0] == 0 and self.edgeExist(v2, v1)[0] == 0:
            return v1, v0, v2
        return v0, v1, v2

    def __str__(self):
        assert self.size() >= 2, "size: {}".format(self.size())
        if self.size() == 2:
            return f"[ {self.label(0)} {self.edgeArrow(0, 1)} {self.label(1)} ]"
        def cliqueStr():
            return "clique" if self.clique else "not clique"
        if self.size() == 3:
            v0, v1, v2 = self.reorder(0, 1, 2)
            return f"[ {self.edgeArrow(v0, v2)} {self.label(v0)} {self.edgeArrow(v0, v1)} {self.label(v1)} {self.edgeArrow(v1, v2)} {self.label(v2)} {self.edgeArrow(v2, v0)} ]"
        if self.size() == 4:
            v0, v1, v2, v3 = 0, 1, 2, 3
            labelsList = f"[ {self.label(v0)} {self.label(v1)} {self.label(v2)} {self.label(v3)} ]"
            edgeMap = defaultdict(list)
            for (src, dst, label) in self.edges:
                edgeMap[src].append((dst, label))
            edgeString = "{ "
            for src, value in edgeMap.items():
                if len(value) == 0:
                    continue
                edgeString += f"{src}:[ "
                for dst, label in value:
                    edgeString += f"{dst}({label}) "
                edgeString += f"] "
            edgeString += "}"
            return f" {labelsList} {edgeString} "

        return f"pattern: {self.size()} {cliqueStr()}"


    @staticmethod
    def getVertex(line):
        v, vid, vlabel = line.split()[-3:]
        assert v == 'v'
        return int(vid), int(vlabel)

    @staticmethod
    def getEdge(line):
        e, s, d, elabel = line.split()[-4:]
        assert e == 'e'
        return int(s), int(d), int(elabel)

def parsePatternGraph(fileCoro, line):
    vertices = []
    edges = []
    vertices.append(PatternGraph.getVertex(line))
    for line in fileCoro:
        if len(line) == 1:
            break
        if line[0] == 'v':
            vertices.append(PatternGraph.getVertex(line))
        elif line[0] == 'e':
            edges.append(PatternGraph.getEdge(line))

#    for (v, l) in vertices:
#        print("v {} {}".format(v, l))
#    for (s, d, l) in edges:
#        print("e {} {} {}".format(s, d, l))

    return PatternGraph(vertices, edges)


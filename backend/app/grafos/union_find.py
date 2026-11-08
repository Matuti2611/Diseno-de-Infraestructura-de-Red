class UnionFind:
    def __init__(self, nodos):
        self.padre = {n: n for n in nodos}
        self.rango = {n: 0 for n in nodos}

    def find(self, u):
        if self.padre[u] != u:
            self.padre[u] = self.find(self.padre[u])
        return self.padre[u]

    def union(self, u, v):
        raiz_u = self.find(u)
        raiz_v = self.find(v)

        if raiz_u != raiz_v:
            if self.rango[raiz_u] > self.rango[raiz_v]:
                self.padre[raiz_v] = raiz_u
            elif self.rango[raiz_u] < self.rango[raiz_v]:
                self.padre[raiz_u] = raiz_v
            else:
                self.padre[raiz_v] = raiz_u
                self.rango[raiz_u] += 1
            return True
        return False
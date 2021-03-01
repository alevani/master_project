class PSITaskHandler:
    # ? do all the function have to lay in the class?
    def __init__(self):
        self.Xmin = 0
        self.Xmax = 1024
        self.delta = 1
        self.phi_base = 0.3
        self.lower_margin, self.upper_margin = 0

    def D(self):
        pass

    def eq1(self, r1, r2):
        th = 0
        return abs(self.D() - r1 + ((r2.w / r1.w) * (r2.x - th)))

    def eq3(self, r1, r2):
        d_effective = self.eq1(r2)
        if r2.x < r1 and d_effective < r1.d_lower:
            r1.d_lower = d_effective

    def eq4(self, r1, r2):
        d_effective = self.eq1(r2)
        if r2.x > r1 and d_effective < r1.d_upper:
            r1.d_upper = d_effective

    def eq5(self, r):
        r.d_lower += self.phi_base
        r.d_upper += self.phi_base

    def eq6(self, r):
        if r.d_lower < r.d_upper:
            r.x += self.delta
        elif r.d_lower > r.d_upper:
            r.x -= self.delta
        else:
            pass  # ???

    def eq7(self, r):
        th = 0

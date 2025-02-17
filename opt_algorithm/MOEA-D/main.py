import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


class TestFunc:
    type_zdt1 = "zdt1"
    type_zdt2 = "zdt2"
    type_zdt3 = "zdt3"
    type_zdt4 = "zdt4"


class Individual:

    def __init__(self, x, test_func):
        self.n_x = len(x)
        self.x = x
        # 测试函数：https://blog.csdn.net/miscclp/article/details/38102831
        if test_func == TestFunc.type_zdt1:
            f1 = self.x[0]
            g = 1 + 9 * np.sum(self.x[1:]) / (self.n_x - 1)
            h = 1 - np.sqrt(f1 / g)
            f2 = g * h
        if test_func == TestFunc.type_zdt2:
            f1 = self.x[0]
            g = 1 + 9 * np.sum(self.x[1:]) / (self.n_x - 1)
            h = 1 - (f1 / g) ** 2
            f2 = g * h
        if test_func == TestFunc.type_zdt3:
            f1 = self.x[0]
            g = 1 + 9 * np.sum(self.x[1:]) / (self.n_x - 1)
            h = 1 - np.sqrt(f1 / g) - (f1 / g) * np.sin(10 * np.pi * f1)
            f2 = g * h
        if test_func == TestFunc.type_zdt4:
            f1 = self.x[0]
            g = 91 + np.sum([x[i] ** 2 - 10 * np.cos(4 * np.pi * x[i]) for i in range(1, 10)])
            h = 1 - np.sqrt(f1 / g)
            f2 = g * h
        self.f = [f1, f2]


# 染色体
class Chromosome:
    # 编码成二进制字符串
    @staticmethod
    def encode(xs):
        res = []
        max_len = len(str(bin(10 ** 4)).replace("0b", ""))
        for x in xs:
            s = str(bin(int(x * (10 ** 4)))).replace("0b", "").zfill(max_len)
            res.append(s)
        return res

    # 解码成浮点数
    @staticmethod
    def decode(chromosomes):
        res = []
        for chromosome in chromosomes:
            res.append(int(chromosome, 2) / (10 ** 4))
        return res


class MOEAD:
    def __init__(self, n_pop, n_neighbor, episode, test_func):
        self.n_pop = n_pop
        self.n_neighbor = n_neighbor
        self.episode = episode
        self.test_func = test_func

    # 交叉
    def crossover(self, pa, pb):
        chromosomes_a = Chromosome.encode(pa.x)
        chromosomes_b = Chromosome.encode(pb.x)
        chromosomes_c = []
        for i in range(len(chromosomes_a)):
            chromosome_a = chromosomes_a[i]
            chromosome_b = chromosomes_b[i]
            R = np.random.randint(0, len(chromosome_a))
            chromosome_c = chromosome_a[:R] + chromosome_b[R:]
            chromosomes_c.append(chromosome_c)
        xs = Chromosome.decode(chromosomes_c)
        xs = self.check_x(xs)
        pc = Individual(xs, self.test_func)
        return pc

    @staticmethod
    def check_x(xs):
        for i in range(len(xs)):
            if xs[i] > 1:
                xs[i] = 1
        return xs

    # 变异
    def mutate(self, pa, pb):
        nx = pa.n_x
        # 选择变异的解
        r = np.random.random()
        # 选择变异的x
        l = np.random.randint(0, nx)
        if r > 0.5:
            mutate_p = pb
        else:
            mutate_p = pa
        chromosomes = Chromosome.encode(mutate_p.x)
        chromosome_mutate = chromosomes[l]
        # 选择变异的染色体位置
        R = np.random.randint(0, len(chromosome_mutate))
        if chromosome_mutate[R] == "0":
            chromosome_new = chromosome_mutate[:R] + "1" + chromosome_mutate[R + 1:]
        else:
            chromosome_new = chromosome_mutate[:R] + "0" + chromosome_mutate[R + 1:]
        chromosomes[l] = chromosome_new
        new_xs = Chromosome.decode(chromosomes)
        new_xs = self.check_x(new_xs)
        pd = Individual(new_xs, self.test_func)
        return pd

    def genetic_operaton(self, pa, pb):
        pc = self.crossover(pa, pb)
        pd = self.mutate(pa, pb)
        return pc, pd

    @staticmethod
    def best_value(pop):
        best = []
        ny = len(pop[0].f)
        ys = np.array([individual.f for individual in pop])
        for i in range(ny):
            best.append(np.min(ys[:, i]))
        return best

    # 计算最近邻的索引
    def neighbor(self, lamb, n_neighbor):
        b = []
        for i in range(len(lamb)):
            distances = []
            for j in range(len(lamb)):
                distance = np.sqrt(np.sum((np.array(lamb[i]) - np.array(lamb[j])) ** 2))
                distances.append(distance)
            neighbor_index = np.argsort(distances)
            b.append(neighbor_index[:n_neighbor])
        return b

    # 计算算法支配
    def dominate(self, pa, pb):
        y_n = len(pa.f)
        for i in range(y_n):
            if pa.f[i] > pb.f[i]:
                return False
        return True

    # 初始化
    def initial(self, n_pop):
        lamb = [[i / n_pop, 1 - i / n_pop] for i in range(n_pop)]
        if self.test_func == TestFunc.type_zdt4:
            pop = [Individual([np.random.random() * 10 - 5 if i >= 1 else np.random.random() for i in range(10)],
                              self.test_func) for _ in range(n_pop)]
        else:
            pop = [Individual([np.random.random() for _ in range(30)], self.test_func) for _ in range(n_pop)]
        return pop, lamb

    def update_z(self, y, z):
        for i in range(len(z)):
            if y.f[i] < z[i]:
                z[i] = y.f[i]
        return z

    @staticmethod
    def tchebycheff(x, lamb, z):
        distances = []
        for i in range(len(x.f)):
            distances.append(np.abs(x.f[i] - z[i]) * lamb[i])
        return np.max(distances)

    # 开始执行进化算法
    def evolve(self):
        pop, lamb = self.initial(n_pop=self.n_pop)
        b = self.neighbor(lamb=lamb, n_neighbor=self.n_neighbor)
        ep = []
        # 参考点先设为种群中每个问题的最优解
        z = self.best_value(pop)
        for i in tqdm(range(self.episode)):
            print('PF number:', len(ep))
            for j in range(self.n_pop):
                m = np.random.randint(0, self.n_neighbor)
                l = np.random.randint(0, self.n_neighbor)
                pa = pop[b[j][m]]
                pb = pop[b[j][l]]
                pc, pd = self.genetic_operaton(pa, pb)
                y = pc if self.dominate(pc, pd) else pd
                # 更新参考点
                z = self.update_z(y, z)
                # 如果解比邻居子问题离基准点z更近那么更新邻居的解
                for k in range(len(b[j])):
                    ta = self.tchebycheff(pop[b[j][k]], lamb[b[j][k]], z)
                    tb = self.tchebycheff(y, lamb[b[j][k]], z)
                    if tb < ta:
                        pop[b[j][k]] = y
                if not ep:
                    ep.append(y)
                else:
                    # 是否支配y
                    dominateY = False
                    rmlist = []
                    for k in range(len(ep)):
                        if self.dominate(y, ep[k]):
                            rmlist.append(ep[k])
                        elif self.dominate(ep[k], y):
                            dominateY = True
                    if not dominateY:
                        ep.append(y)
                        for k in range(len(rmlist)):
                            ep.remove(rmlist[k])
        return ep

    def show_fig(self, ep):
        x = []
        y = []
        for i in range(len(ep)):
            f1 = ep[i].f[0]
            f2 = ep[i].f[1]
            if f1 <= 1 and f2 <= 1 or self.test_func is TestFunc.type_zdt4:
                x.append(f1)
                y.append(f2)
        pareto = np.loadtxt("pareto/{}.txt".format(self.test_func))
        plt.plot(pareto[:, 0], pareto[:, 1], 'r.')
        plt.plot(x, y, '*')
        plt.xlabel('function1')
        plt.ylabel('function2')
        plt.legend(["PF", "MOEA/D"], loc="best")
        plt.title(self.test_func)
        plt.savefig(self.test_func + ".png", dpi=100)
        plt.show()


if __name__ == '__main__':
    N_POP = 100
    N_NEIGHBOR = 20
    EPISODE = 250

    moead = MOEAD(n_pop=N_POP, n_neighbor=N_NEIGHBOR, episode=EPISODE, test_func=TestFunc.type_zdt4)
    ep = moead.evolve()
    moead.show_fig(ep)

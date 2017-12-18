import random


class Chromosome(object):

    def __init__(self, gens_amount, sender_id, receiver_id):
        self.gens = list(range(gens_amount))
        # swap 0 и sender_id
        self.gens[0], self.gens[sender_id - 1] = self.gens[sender_id - 1], self.gens[0]
        # swap receiver_id и последний элемент
        self.gens[-1], self.gens[receiver_id - 1] = self.gens[receiver_id - 1], self.gens[-1]
        # перемешать содержимое
        for i in range(1, gens_amount - 1):
            swap_index = random.randint(1, gens_amount - 3)
            if i != swap_index:
                self.gens[i], self.gens[swap_index] = self.gens[swap_index], self.gens[i]
        # print self.gens

    def mutate(self):
        index = random.randint(1, len(self.gens) - 2)
        value = random.randint(0, len(self.gens))
        self.gens[index] = value

    def value(self, graph):
        value = 100000
        for i in range(len(self.gens) - 1):
            # TODO: понять, почему значение в гене должно соответствовать позиции в матрице
            x = self.gens[i]
            if x >= len(graph):
                x = len(graph) - 1
            y = self.gens[i + 1]
            if y >= len(graph[x]):
                y = len(graph[x]) - 1

            _val = graph[x][y]
            if _val < value:
                value = _val
        return value


class AlgorithmManager(object):
    # Количество компьютеров в сети
    PC_AMOUNT = 11
    # Номер отправителя (от 1 до PC_AMOUNT)
    SENDER_ID = 1
    # Номер получателя (от 1 до PC_AMOUNT)
    RECEIVER_ID = 4
    # Размер популяции
    POPULATION_SIZE = 9
    # Количество итераций
    ITERATIONS_AMOUNT = 1
    # Порог срабатывания для проведения мутации
    MUTATION_LIMIT = 0.3
    # Какая часть от популяции считается лучшей
    POPULATION_BEST = 0.2
    # Отношение оставшихся в живых
    ALIVE_PROPORTION = 0.5

    def __init__(self):
        if self.SENDER_ID == self.RECEIVER_ID:
            raise AssertionError(u'Номер отправителя не может быть равен номеру получателя')
        if self.SENDER_ID > self.PC_AMOUNT:
            raise AssertionError(u'Номер отправителя не может быть больше общего количества компьютеров')
        if self.RECEIVER_ID > self.PC_AMOUNT:
            raise AssertionError(u'Номер получателя не может быть больше общего количества компьютеров')
        print( u'Количество компьютеров в сети: {}'.format(self.PC_AMOUNT))
        print (u'Номер отправителя: {}'.format(self.SENDER_ID))
        print (u'Номер получателя: {}'.format(self.RECEIVER_ID))
        print (u'Размер популяции: {}'.format(self.POPULATION_SIZE))
        print (u'Количество итераций: {}\n'.format(self.ITERATIONS_AMOUNT))

        # Граф путей
        self.graph = [[100000] * self.PC_AMOUNT for _ in range(self.PC_AMOUNT)]
        for i in range(self.PC_AMOUNT):
            for j in range(self.PC_AMOUNT):
                if i != j:
                    self.graph[i][j] = random.randint(1, 100)

        print ('Graph')
        for line in self.graph:
            print (line)

        print (u'\nСоздать популяцию из хромосом:')
        self.population = [Chromosome(
            gens_amount=self.PC_AMOUNT,
            sender_id=self.SENDER_ID,
            receiver_id=self.RECEIVER_ID,
        ) for _ in range(self.POPULATION_SIZE)]

    def print_genes(self):
        for chromosome in self.population:
            print (chromosome.gens)
        print (u'\n')

    def mutate(self):
        print (u'Производим мутацию:')
        for chromosome in self.population:
            if random.randint(0, 100) < self.MUTATION_LIMIT * 100:
                chromosome.mutate()

    def cross(self, first, second):
        new = Chromosome(gens_amount=self.PC_AMOUNT, sender_id=self.SENDER_ID, receiver_id=self.RECEIVER_ID)
        for i in range(len(first.gens)):
            select = random.randint(0, 1)
            if select == 0:
                new.gens[i] = first.gens[i]
            else:
                new.gens[i] = second.gens[i]
        return new

    def reproduction(self, population):
        print (u'Производим репродукцию:')
        new_population = list(population)
        while len(new_population) < self.POPULATION_SIZE:
            new_population.append(self.cross(
                first=random.choice(new_population),
                second=random.choice(new_population),
            ))
        return new_population

    def roulette(self):
        old_population = list(self.population)
        best = int(self.POPULATION_BEST * len(old_population))

        def sort_func(item):
            assert isinstance(item, Chromosome)
            return item.value(graph=self.graph)

        new_population = sorted(old_population, key=sort_func)[:best]

        while len(new_population) < int(self.ALIVE_PROPORTION * len(old_population)):
            fit_sum = 0
            for member in old_population:
                fit_sum += member.value(graph=self.graph)

            roulette_index = random.randint(0, int(fit_sum))
            roulette_index_member = old_population[0].value(graph=self.graph)
            for i in range(len(old_population)):
                if roulette_index < roulette_index_member:
                    new_population.append(old_population[i])
                    del old_population[i]
                    break
                roulette_index_member += old_population[i].value(graph=self.graph)
        return new_population

    def tournament(self):
        print (u'Выжившие:')
        old_population = list(self.population)
        new_population = []
        while len(new_population) < int(self.ALIVE_PROPORTION * len(old_population)):
            first_item = random.choice(old_population)
            second_item = random.choice(old_population)
            if first_item.value(graph=self.graph) > second_item.value(graph=self.graph):
                new_population.append(first_item)
            else:
                new_population.append(second_item)
        return new_population

    def run(self):
        self.print_genes()

        for i in range(self.ITERATIONS_AMOUNT):
            # self.population = self.roulette()
            self.population = self.tournament()

            self.print_genes()

            if not self.population:
                print (u'Популяция умерла')
                break

            self.population = self.reproduction(population=self.population)

            self.print_genes()

            self.mutate()

            self.print_genes()

            self.get_best()
            print ('=' * 50)

    def get_best(self):
        max_value = 0
        for item in self.population:
            value = item.value(graph=self.graph)
            if value > max_value:
                max_value = value
        print (u'Лучшая пропускная способность: {}'.format(max_value))
        return max_value


if __name__ == '__main__':
    manager = AlgorithmManager()
    manager.run()


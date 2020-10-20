from multiprocessing import Pool


def get_fibonacci_value__parallel(n_index, pool=None):
    if pool is None:
        pool = Pool(4)

    if n_index == 0:
        return 0
    if n_index == 1 or n_index == 2:
        return 1
    result1 = pool.apply_async(
        get_fibonacci_value__parallel, (n_index - 1, pool)
    )
    result2 = pool.apply_async(
        get_fibonacci_value__parallel, (n_index - 2, pool)
    )
    return result1.get() + result2.get()


def get_fibonacci_value(n_index):
    if n_index == 0:
        return 0
    if n_index == 1 or n_index == 2:
        return 1
    return get_fibonacci_value(n_index-1) + get_fibonacci_value(n_index-2)


if __name__ == '__main__':
    res = get_fibonacci_value__parallel(9)
    print(res)

'''
F(n + 2) = F(n + 1) + F(n)
F(n + 3) = F(n + 1) + F(n + 2) = F(n + 1) * 2 + F(n)
F(n + 4) = F(n + 2) + F(n + 3) = F(n + 1) * 3 + F(n) * 2
F(n + 5) = F(n + 3) + F(n + 4) = F(n + 1) * 5 + F(n) * 3
F(n + 6) = F(n + 4) + F(n + 5) = F(n + 1) * 8 + F(n) * 5


F(n + k) = F(n + 1) * F(K) + F(n) * F(k - 1)    


also see: http://faculty.cs.tamu.edu/klappi/csce411-f12/csce411-setMultithreaded.pdf
'''
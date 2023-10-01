def benchmark(func):
    import time

    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print(f'[*] Время выполнения: {end - start:.2f} секунд. {func.__name__}')
        return return_value

    return wrapper

@benchmark
def main():
    for _ in range(100000):
        pass

if __name__ == '__main__':
    main()
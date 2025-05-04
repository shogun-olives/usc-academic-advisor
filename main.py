from module.api import Cache
import time


def main() -> None:
    start = time.time()
    cache = Cache()
    end = time.time()

    print(f"Cache instantiation: {end - start} sec")

    start = time.time()
    ret = cache.get_courses("CSCI")
    end = time.time()

    print(f"Course Retrieval: {end - start} sec")

    start = time.time()
    ret = cache.get_sections("CSCI 170")
    end = time.time()

    print(f"Section Retrieval: {end - start} sec")


if __name__ == "__main__":
    main()

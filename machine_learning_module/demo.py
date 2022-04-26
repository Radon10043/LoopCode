import multiprocessing as mp

print(mp.cpu_count())
pool=mp.Pool(mp.cpu_count())
#!/usr/bin/env python3

import os, datetime
import shutil
from numpy import random
import matplotlib.pyplot as plt

def generate_test_set(test_set_folder, size_dist):
    shutil.rmtree(test_set_folder)
    os.makedirs(test_set_folder)
    low = 1024
    high = 64 * 1024 * 1024
    size = 300

    test_file_names = []
    if (size_dist == "uniform"):
        file_sizes = random.randint(low, high + 1, size)
    elif (size_dist == "lognormal"):
        m_log, s_log, w = 3.5, 1.1, 1024
        file_sizes = (w * random.lognormal(m_log, s_log, size)).astype(int)
        file_sizes = [i for i in file_sizes if i >= low and i<=high]
    elif (size_dist == "reversed_lognormal"):
        m_log, s_log, w = 3.5, 1.1, 1024
        file_sizes = (w * random.lognormal(m_log, s_log, size)).astype(int)
        file_sizes = [high - i for i in file_sizes if i >= low and i<=high]

    display_file_histogram(file_sizes, size_dist)
    return
    for idx, size in enumerate(file_sizes):
        print("%d file generate of size %d" % (idx, size))
        test_file_name = get_test_file_name(test_set_folder, size)
        test_file_names.append(test_file_name)
        random_content = os.urandom(size)
        with open(test_file_name, 'wb') as fout:
            fout.write(random_content)


def get_test_file_name(test_set_folder, size):
    return os.path.join(test_set_folder,
        datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))


def display_file_histogram( file_sizes, d):
    fig, ax = plt.subplots()
    kb = [i/1024 for i in file_sizes]
    ax.hist(kb, bins=100)
    ax.set_ylabel('Frequency')
    ax.set_xlabel('File size (KB)')
    ax.set_title('Test files set %s distribution' % d)
    plt.show()

def generate_requests(count, path_to_test_set, p_read, script_file):
    requests = []
    all_files = []
    for key in os.listdir(path_to_test_set):
        if not key.endswith('.csv'):
            all_files.append(key)

    for r in range(count):
        action = 0 if random.uniform() < p_read else 1
        f = all_files[random.randint(len(all_files))]
        requests.append((action, f))

    with open(os.path.join(path_to_test_set, script_file), "w") as o:
        for (action, key) in requests:
            o.write("%d,%s\n" % (action, key))

def main():
    #path_to_test_set = '/media/stefan/Windows/dais/macro_revlognormal'
    #path_to_test_set = generate_test_set(path_to_test_set, "reversed_lognormal")

    path_to_test_set = '/media/stefan/Windows/dais2/tmp'
    path_to_test_set = generate_test_set(path_to_test_set, "reversed_lognormal")


    return
    generate_requests(1000, path_to_test_set, 0.5,  "ycsb_a.csv")
    generate_requests(1000, path_to_test_set, 0.95, "ycsb_b.csv")
    generate_requests(1000, path_to_test_set, 1,    "ycsb_c.csv")
    generate_requests(1000, path_to_test_set, 0.05, "ycsb_w.csv")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from wrap_openssl import *
from inmemtest import InMemTestSet
import os
import sys
from cryptoutil import CryptoUtil
from time import sleep
from timeit import default_timer as timer
import dropbox

class MockCloud:
    in_mem = {}

    @staticmethod
    def clear():
        MockCloud.in_mem.clear()

    @staticmethod
    def put(k, v):
        # add latency based on exponential distribution with mean per ICStore
        sleep(0.01)
        MockCloud.in_mem[k] = v

    @staticmethod
    def get(k):
        # add latency based on exponential distribution with mean per ICStore
        sleep(0.01)
        return MockCloud.in_mem[k]

    @staticmethod
    def footprint():
        s = 0
        for (k,v) in MockCloud.in_mem.items():
            s += sys.getsizeof(v)
        return s


class DropboxCloud:

    token = 'BIHEAThi-nQAAAAAAAAAYSqX7tpWpHvnJ9sLl-rKKTesKkZXm7iwwLbIFHGalf99'
    client = dropbox.client.DropboxClient(token)
    dbx = dropbox.Dropbox(token)

    @staticmethod
    def clear():
        folder_metadata = DropboxCloud.client.metadata('/')
        for f in folder_metadata['contents']:
            print('Deleting ', f['path'])
            DropboxCloud.client.file_delete(f['path'])

    @staticmethod
    def put(k, v):
        # put file with name k and content v
        DropboxCloud.client.put_file(k, v)

    @staticmethod
    def get(k):
        # get file with name k
        f, metadata = DropboxCloud.client.get_file_and_metadata('/' + k)
        return f.read()

    @staticmethod
    def footprint():
        pass


class SyncClient:

    def __init__(self, cipher, signer, cloud):
        self.cipher = cipher
        self.signer = signer
        self.cloud = cloud
        self.key_cache = {}

    def put(self, k, v):
        enc_key = os.urandom(int(CryptoUtil.get_strength_level('aes') / 8))
        iv = os.urandom(16)
        c = self.cipher.encrypt(v, enc_key, iv)
        cs = self.signer.sign(c)
        self.cloud.put(k, cs)
        self.key_cache[k] = enc_key

    def get(self, k):
        enc_key = self.key_cache[k]
        c = self.cloud.get(k)
        v = self.signer.verify(c)
        d = self.cipher.decrypt(v, enc_key)
        return d

def set_up_cloud(client, cloud):
    print("Setting up cloud...")
    cloud.clear()
    for (k,v) in InMemTestSet.test_set.items():
        client.put(k, v)

def execute_workloads(client):
    results = {}
    workloads = InMemTestSet.get_workload_names()
    print("Benchmark workloads : ", workloads)
    for idx, w in enumerate(workloads):
        # execute requests as specified in the workload
        start = timer()
        for i, (action, item) in enumerate(InMemTestSet.workload[w][:10]):
            if action==0:
                s = client.get(item)
                assert s==InMemTestSet.get(item)
            elif action==1:
                client.put(item, InMemTestSet.get(item))
        end = timer()
        e2e_time = end - start
        footprint = None # cloud.footprint()
        #print('E2E for %s : %f' % (w, e2e_time))
        print(e2e_time)
        results[w] = (e2e_time, footprint)
    return results

def test_scheme(cipher, signer, label, cloud):
    print("Benchmarking scheme : ", label)
    client = SyncClient(cipher, signer, cloud)

    start = timer()
    set_up_cloud(client, cloud)
    end = timer()
    print('Time to pre-load everything : ', end - start)

    time_per_workload = execute_workloads(client)
    return time_per_workload

def test_all_schemes(cloud):
    all_results = {}
    for strength in range(3):
        all_results[strength+1] = {}

        # set desired strength level (1 to 3), see CryptoUtil for details
        CryptoUtil.set_strength_level(strength + 1)

        # test all 6 schemes
        # each test will cover 4 workloads`
        r = test_scheme(CBC_CIPHER(), RSA_SIGNER(),     "CBC+RSA",  cloud)
        all_results[strength+1]["cbc+rsa"] = r
        r = test_scheme(CBC_CIPHER(), ECDSA_SIGNER(),   "CBC+ECC",  cloud)
        all_results[strength+1]["cbc+ecc"] = r
        r = test_scheme(CTR_CIPHER(), RSA_SIGNER(),     "CTR+RSA",  cloud)
        all_results[strength+1]["ctr+rsa"] = r
        r = test_scheme(CTR_CIPHER(), ECDSA_SIGNER(),   "CTR+ECC",  cloud)
        all_results[strength+1]["ctr+ecc"] = r
        r = test_scheme(GCM_CIPHER(), RSA_SIGNER(),     "GCM+RSA",  cloud)
        all_results[strength+1]["gcm+rsa"] = r
        r = test_scheme(GCM_CIPHER(), ECDSA_SIGNER(),   "GCM+ECC",  cloud)
        all_results[strength+1]["gcm+ecc"] = r

    return all_results

def print_results(r):
    workloads = ['ycsb_w', 'ycsb_a', 'ycsb_b', 'ycsb_c']
    strengths = [1,2,3]
    schemes = ['cbc+rsa', 'cbc+ecc', 'ctr+rsa', 'ctr+ecc', 'gcm+rsa', 'gcm+ecc']
    for (_iw, w) in enumerate(workloads):
        print('WORKLOAD : ', w)
        print('strength,cbc+rsa,cbc+ecc,ctr+rsa,ctr+ecc,gcm+rsa,gcm+ecc')
        for (_is, s) in enumerate(strengths):
            line = 'level' + str(s)
            for (_sch, sch) in enumerate(schemes):
                line = line + "," + str(r[s][sch][w][0])
            print(line)


#def test_footprint():
#    footprint_results = {}
#    for strength in range(3):
#        footprint_results[strength+1] = []
#        CryptoUtil.set_strength_level(strength + 1)
#        set_up_cloud(SyncClient(CBC_CIPHER(), RSA_SIGNER()))
#        footprint_results[strength+1].append(MockCloud.footprint())
#        set_up_cloud(SyncClient(CBC_CIPHER(), ECDSA_SIGNER()))
#        footprint_results[strength+1].append(MockCloud.footprint())
#        set_up_cloud(SyncClient(CTR_CIPHER(), RSA_SIGNER()))
#        footprint_results[strength+1].append(MockCloud.footprint())
#        set_up_cloud(SyncClient(CTR_CIPHER(), ECDSA_SIGNER()))
#        footprint_results[strength+1].append(MockCloud.footprint())
#        set_up_cloud(SyncClient(GCM_CIPHER(), RSA_SIGNER()))
#        footprint_results[strength+1].append(MockCloud.footprint())
#        set_up_cloud(SyncClient(GCM_CIPHER(), ECDSA_SIGNER()))
#        footprint_results[strength+1].append(MockCloud.footprint())
#        print(','.join(map(str, footprint_results[strength+1])) )


def test_connection_dropbox():
    DropboxCloud.clear()
    #DropboxCloud.put("test.txt", "stefan is the best")
    #s = DropboxCloud.get("test.txt")
    #print(s)

def main():

    print("--- Unleashing MACRO-benchmarks")

    test_set = "/home/stefan/dais/macro/macro_revlognormal"

    print('Loading from disk to RAM : ', test_set)

    InMemTestSet.load_from_disk(test_set)

    print('Loading DONE')


    # one can choose among MockCloud and DropboxCloud
    all_results = test_all_schemes(DropboxCloud) 

    print_results(all_results)

    print("--- Finalized MACRO-benchmarks")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

def plot_workload(workload, ax, ymin, ymax, title, ylabel=False):
        # todo: refactor this into a loop
        ax.plot([item[0] for item in workload], linestyle='--', marker='+', color='black')
        ax.plot([item[1] for item in workload], linestyle='-', marker='x', color='b', markersize=8)
        ax.plot([item[2] for item in workload], linestyle='--', marker='.', color='black')
        ax.plot([item[3] for item in workload], linestyle='-', marker='o', color='b', markersize=8)
        ax.plot([item[4] for item in workload], linestyle='--', marker='v', color='black')
        ax.plot([item[5] for item in workload], linestyle='-', marker='^', color='b', markersize=8)
        ax.set_ylim([ymin, ymax])
        ax.yaxis.grid(True)
        ax.margins(x=0.1)
        ax.set_xticks(range(3))
        ax.set_xticklabels(['L', 'M', 'H'])
        if ylabel:
                ax.set_ylabel('Total Time (s)')
        ax.set_title(title)
        ax.set_xlabel('Security\nStrength')

def plot_four_workloads(bak, wh, rh, ro, ymin, ymax):
        plt.close('all')
        f, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, sharey=True, figsize=(10,4))
        plot_workload(bak, ax1, ymin, ymax, "mostly-write", ylabel=True)
        plot_workload(wh, ax2, ymin, ymax, "write-heavy")
        plot_workload(rh, ax3, ymin, ymax, "read-heavy")
        plot_workload(ro, ax4, ymin, ymax, "read-only")
        f.subplots_adjust(bottom=0.25)
        plt.legend(labels=["CBC-RSA", "CBC-ECC",
                "CTR-RSA", "CTR-ECC",
                "GCM-RSA", "GCM-ECC"],
                #ncol=3, loc=9, bbox_to_anchor=(-1.15,-0.15))
                ncol=1, loc=7, bbox_to_anchor=(3,0.5), frameon=False)
        f.subplots_adjust(wspace=0.4)

        plt.show()

def log_normal():
        bak_log = [
                (3.83, 4.38, 3.04, 2.89, 3.79, 3.62),
                (5.89, 4.15, 4.44, 2.97, 5.21, 3.73),
                (12.65, 4.09, 10.87, 3.15, 12.09, 3.76)]
        wh_log = [
                (3.97,5.21,3.90,3.83,4.43,4.34),
                (6.16,5.55,4.88,3.88,5.38,4.44),
                (10.33, 5.76,9.46,4.02,9.71,4.58)]
        rh_log = [
                (4.37,5.91,4.48,4.53,5.29,5.27),
                (5.86,5.99,4.92,4.54,5.34,5.49),
                (6.18,6.48,5.22,5.03,5.62,5.53)]
        ro_log = [
                (3.78,5.75,4.16,4.16,4.83,4.85),
                (5.40,5.69,4.36,4.31,5.05,4.97),
                (5.36,4.79,4.66,4.51,4.93,4.98)]
        plot_four_workloads(bak_log, wh_log, rh_log, ro_log, 2, 14)


def rev_log_normal():
        bak_rlog = [
                (3.82, 3.76, 2.95, 2.90, 3.15, 3.07),
                (4.63, 3.94, 3.58, 2.95, 3.83, 3.14),
                (7.47, 4.14, 6.52, 3.01, 6.68, 3.20)]
        wh_rlog = [
                (3.45,3.45, 2.97, 2.94, 3.07, 3.04),
                (3.86, 3.55, 3.30, 3.00, 3.39, 3.10),
                (5.18, 3.69, 4.63, 3.09, 4.69, 3.16)]
        rh_rlog = [
                (3.20,3.21, 3.02, 3.00, 3.01, 3.03),
                (3.30, 3.28, 3.07, 3.07, 3.09, 3.06),
                (3.50, 3.38, 3.28, 3.19, 3.28, 3.14)]
        ro_rlog = [
                (3.18,3.21, 3.00, 3.01, 3.01, 3.01),
                (3.24, 3.26, 3.04, 3.07, 3.07, 3.08),
                (3.30, 3.34, 3.11, 3.15, 3.11, 3.14)]
        plot_four_workloads(bak_rlog, wh_rlog, rh_rlog, ro_rlog, 2, 8)


def uniform():
        bak_uni = [
                (12.78,12.58,9.11, 8.64, 10.86,8.99),
                (16.00,13.36,11.16,8.38, 13.71,7.88),
                (28.58,13.05,23.75,7.33, 26.16,9.71)]
        wh_uni = [
                (12.11,12.44,10.41,10.32,10.85,10.72),
                (15.76,12.72,12.07,10.01,13.10,7.24),
                (22.46,12.98,18.65,8.84, 20.40,10.70)]
        rh_uni = [
                (12.79,13.05,11.01,11.06,11.46,11.43),
                (15.28,13.36,11.22,10.81,11.52,9.49),
                (14.14,14.11,11.63,11.29,12.57,12.61)]
        ro_uni = [
                (12.38,12.85,9.72, 9.82, 10.90,10.08),
                (12.82,13.00,10.41,9.97, 11.27,8.31),
                (11.49,13.54,9.76, 10.37,10.42,11.81)]
        plot_four_workloads(bak_uni, wh_uni, rh_uni, ro_uni, 2, 35)


def main():
    #rev_log_normal()
    uniform()
    #log_normal()

if __name__=="__main__":
        main()

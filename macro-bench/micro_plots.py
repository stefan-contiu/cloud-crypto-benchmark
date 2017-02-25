#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

# data collected from TODO : puth excel file path

# AES Results
cbc_enc_cpb_mean = (2.3685862151, 2.7941152963, 3.1697130095)
cbc_enc_cpb_stdev = (0.2448099182, 0.3092048224, 0.2204836467)
ctr_cpb_mean = (0.5838479387, 0.6931198856, 0.7955039347)
ctr_cpb_stdev = (0.0484978139, 0.0789836157, 0.1180309327)
gcm_enc_cpb_mean = (0.6099892252, 0.7089767014, 0.8009293081)
gcm_enc_cpb_stdev = (0.0702988225, 0.0879610644, 0.0928299511)
cbc_dec_cpb_mean = (0.6056169963, 0.7036722533, 0.7818869342)
cbc_dec_cpb_stdev = (0.0614463588, 0.1058349596, 0.0276899868)
gcm_dec_cpb_mean = (0.6296174819, 0.7112930339, 0.8128298198)
gcm_dec_cpb_stdev = (0.1029567728, 0.0579556255, 0.1023129858)

# SHA Results
sha_cpb_mean = (6.4715533278, 4.3574680072, 4.3262215193)
sha_cpb_stdev = (0.3495392566, 0.2725921272, 0.1503878577)

# RSA Results
rsa_sign_cpb_mean = (5.6730520495, 116.3897036042, 614.0089232005)
ecc_sign_cpb_mean = (0.8888893411, 2.0287472943, 4.3417407161)
rsa_sign_cpb_stdev = (0.6725152461, 3.6515501268, 12.714253515)
ecc_sign_cpb_stdev = (0.1100842359, 0.2774615172, 0.6001073186)

rsa_ver_cpb_mean = (0.1144054453, 0.6320163672, 2.562243)
ecc_ver_cpb_mean = (0.992241763, 2.2594288125, 4.5881856771)
rsa_ver_cpb_stdev = (0.0142365226, 0.0295835435, 0.2066347502)
ecc_ver_cpb_stdev = (0.1755392219, 0.2562180472, 0.2894840873)

def plot_aes_operation(ax1,m1,m2,m3,s1,s2,s3,yaxis=True):
    N = 3
    ind = np.arange(N)  # the x locations for the groups
    width = 0.25       # the width of the bars
    buff = width / 3.5
    rects1 = ax1.bar(ind + buff, m1, width,
        color='white', yerr=s1, hatch='..', ecolor='black', edgecolor='dimgray')
    rects2 = ax1.bar(ind + 1.1 * width + buff, m2, width,
        color='silver', yerr=s2, hatch='//', ecolor='black', edgecolor='dimgray')
    rects3 = ax1.bar(ind + 2.2 * width + buff, m3, width,
        color='gray', yerr=s3, hatch='++', ecolor='black', edgecolor='dimgray')
    if (yaxis):
        ax1.set_ylabel('Cycles/Byte')
    ax1.set_xlabel('Security Strength')
    ax1.set_xticks(ind + width * 2)
    ax1.set_ylim([0,3.5])
    ax1.set_xticklabels(('L', 'M', 'H'))
    ax1.yaxis.grid(True)

def singles_plot_aes():
    plt.close('all')
    f, ax = plt.subplots(1,1, figsize=(5,3))
    plot_aes_operation(ax, cbc_enc_cpb_mean, ctr_cpb_mean, gcm_enc_cpb_mean,
        cbc_enc_cpb_stdev, ctr_cpb_stdev, gcm_enc_cpb_stdev)
    #plot_aes_operation(ax, cbc_dec_cpb_mean, ctr_cpb_mean, gcm_dec_cpb_mean,
    #    cbc_dec_cpb_stdev, ctr_cpb_stdev, gcm_dec_cpb_stdev, False)
    plt.show()


def plaot_aes():
    plt.close('all')
    f, (ax1, ax2) = plt.subplots(1,2, sharey = True, figsize=(10,3))

    plot_aes_operation(ax1, cbc_enc_cpb_mean, ctr_cpb_mean, gcm_enc_cpb_mean,
        cbc_enc_cpb_stdev, ctr_cpb_stdev, gcm_enc_cpb_stdev)
    plot_aes_operation(ax2, cbc_dec_cpb_mean, ctr_cpb_mean, gcm_dec_cpb_mean,
        cbc_dec_cpb_stdev, ctr_cpb_stdev, gcm_dec_cpb_stdev, False)

    plt.legend(labels=["CBC", "CTR", "GCM"],
        ncol=1, loc=7, bbox_to_anchor=(1.5,0.5))

    f.subplots_adjust(bottom=0.25,hspace=0.1)
    #f.subplots_adjust(right=5.25)
    #f.tight_layout()
    plt.show()

def plot_sha2(m,s):
    N = 3
    ind = np.arange(N)  # the x locations for the groups
    width = 0.6       # the width of the bars
    buff = 0.175 #width / 1.5
    fig, ax = plt.subplots(figsize=(3,2.5))
    ax.bar(ind + buff, m, width,
        color='silver', yerr=s, ecolor='black', edgecolor='dimgray')

    #ax.set_xticks(ind + width * 2)
    ax.yaxis.grid(True)
    ax.set_ylabel('Cycles/Byte')
    ax.set_xticks(ind + buff + width/2)
    ax.set_xticklabels(('L', 'M', 'H'))
    ax.set_xlabel('Security Strength')
    #ax.legend((rects1[0], rects2[0], rects3[0]), ('SHA-256', 'SHA-384', 'SHA-512'))
    plt.show()


def plot_digi_sig():
    plt.close('all')
    f, (ax1, ax2) = plt.subplots(1,2, sharey = True, figsize=(10,3))

    plot_sig_op(ax1, rsa_sign_cpb_mean, ecc_sign_cpb_mean, rsa_sign_cpb_stdev, ecc_sign_cpb_stdev, True)
    plot_sig_op(ax2, rsa_ver_cpb_mean, ecc_ver_cpb_mean, rsa_ver_cpb_stdev, ecc_ver_cpb_stdev, True)

    plt.legend(labels=["RSA", "ECC"],
        ncol=1, loc=7, bbox_to_anchor=(1.5,0.5))

    f.subplots_adjust(bottom=0.25,hspace=0.1)
    #f.subplots_adjust(right=5.25)
    #f.tight_layout()
    plt.show()

def plot_sig_op(ax,m1,m2,s1,s2,yaxis=True):
    N = 3
    ind = np.arange(N)  # the x locations for the groups
    width = 0.25       # the width of the bars
    buff = width / 3.5
    rects1 = ax.bar(ind*0.675 + buff, m1, width,
        color='white', yerr=s1, hatch='..', ecolor='black', edgecolor='dimgray')
    rects2 = ax.bar(ind*0.675 + 1.1 * width + buff, m2, width,
        color='silver', yerr=s2, hatch='//', ecolor='black', edgecolor='dimgray')
    if (yaxis):
        ax.set_ylabel('Million of Cycles')
    ax.set_xticks(ind*0.675 + width*1.5)
    ax.set_ylim([0,10])
    ax.set_xticklabels(('L', 'M', 'H'))
    ax.yaxis.grid(True)
    ax.set_xlabel('Security Strength')


def plot_sig(m1,m2,s1,s2,yaxis=True,sharedY=True):
    N = 2
    ind = np.arange(N)  # the x locations for the groups
    width = 0.25       # the width of the bars
    buff = width / 3.5

    if sharedY:
        fig, ax = plt.subplots(figsize=(4,3), sharey='row')
    else:
        fig, ax = plt.subplots(figsize=(4,3))

    rects1 = ax.bar(ind*0.675 + buff, m1, width,
        color='white', yerr=s1, hatch='..', ecolor='black', edgecolor='dimgray')
    rects2 = ax.bar(ind*0.675 + 1.1 * width + buff, m2, width,
        color='silver', yerr=s2, hatch='//', ecolor='black', edgecolor='dimgray')

    # add some text for labels, title and axes ticks
    #ax.set_title('AES Encryption Cycles per Byte (lower the better)')
    if (yaxis):
        ax.set_ylabel('Megacycles/Operation')
    ax.set_xticks(ind*0.675 + width*1.5)
    ax.set_ylim([0,10])
    ax.set_xticklabels(('keys-low', 'keys-medium', 'keys-high'))
    ax.yaxis.grid(True)
    #ax.grid(True)
    #ax.legend((rects1[0], rects2[0]), ('RSA', 'ECDSA'))

    return fig

def singles_plot_digi():
    plt.close('all')
    f, ax = plt.subplots(1,1, figsize=(3.5,3))

    #plot_sig_op(ax, rsa_sign_cpb_mean, ecc_sign_cpb_mean, rsa_sign_cpb_stdev, ecc_sign_cpb_stdev, True)
    plot_sig_op(ax, rsa_ver_cpb_mean, ecc_ver_cpb_mean, rsa_ver_cpb_stdev, ecc_ver_cpb_stdev, False)

    #f.subplots_adjust(right=5.25)
    #f.tight_layout()
    plt.show()


def main():
    #singles_plot_aes()
    #plot_sha2(sha_cpb_mean, sha_cpb_stdev)
    singles_plot_digi()





if __name__=="__main__":
    main()

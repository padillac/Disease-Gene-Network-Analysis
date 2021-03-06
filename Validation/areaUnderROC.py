'''
AUROC analysis
'''

import sys
sys.path.insert(1, 'Algorithms/')
sys.path.insert(1, 'Imports/')
sys.path.insert(1, '../Algorithms/')
sys.path.insert(1, '../Imports/')
import RandomWalk as rwr
import DiffusionKernel as dk
import PageRank as pr
import loader
import time
import numpy as np
import matplotlib.pyplot as plt
from CacheUtils import compute_if_not_cached

def roc_curve(result_vec, ground_truth_vec, name):
    TPR = []
    FPR = []
    for threshhold in range(len(result_vec)):
        tp = fp = fn = tn = 0
        for i in range(len(result_vec)):
            item = result_vec[i][0]
      #      print('item', item)
            if i <= threshhold and item in ground_truth_vec:
                tp += 1
            elif i <= threshhold and item not in ground_truth_vec:
                fp += 1
            elif item in ground_truth_vec:
                fn += 1
            else:
                tn += 1

        TPR.append(tp/(tp + fn))
        FPR.append(fp/(fp + tn))
    area = np.trapz(TPR, FPR)
    area = str(round(area, 6))
    file_path = "Results/" + name + '.png'
    c = 'blue'
    label = "rwr: " + area
    if 'pr' in name:
        c = 'red'
        label = "pr: " + area
    elif 'dk' in name:
        c = 'green'
        label = "dk: " + area
    curve, = plt.plot(FPR, TPR, color=c,label=label)
    plt.show()
    return curve

def main():
    print("Starting AUROC..")
    #Get file path choices
    pathToPPINetworkFile = sys.argv[1]
    #pathToPPINetworkFile = 'Data/9606.protein.links.v11.0.txt'

    # Get output vectors from each algorithm

    PPI_Network = compute_if_not_cached(loader.load_graph, pathToPPINetworkFile, fileName=pathToPPINetworkFile)
    ground_truth_files = ['Data/MalaCard-protein-Endometriosis.diseasegenes.tsv', 'Data/MalaCard-protein-ischaemic-stroke.diseasegenes.tsv','Data/MalaCard-protein-lymphoma.diseasegenes.tsv']
    file_paths = ['Data/endometriosis-proteins.diseasegenes.tsv','Data/lymphoma-proteins.diseasegenes.tsv', 'Data/ischaemic-proteins.diseasegenes.tsv']
    prior_paths = ['Data/endometriosis-proteins.priors.tsv','Data/lymphoma-proteins.priors.tsv', 'Data/ischaemic-proteins.priors.tsv']
    names = ['endometriosis', 'lymphoma', 'ischaemic']

    for i in range(1,3):
        # building ground truth
        ground_truth_vec = []
        with open(ground_truth_files[i], 'r') as input_file:
            input_file = input_file.readlines()
            for line in input_file:
                protein = line.rstrip('\n')
                ground_truth_vec.append(protein)
        gene_file = open(file_paths[i], 'r')
        file_contents = list(gene_file.readlines())
        # print(file_contents)
        for line in file_contents:
            protein = line.rstrip('\n')
            if protein not in ground_truth_vec:
                ground_truth_vec.append(protein)
        gene_file.close()
        print(ground_truth_vec)
        # building start and priors vector

        start_vector = loader.load_start_vector(file_paths[i], PPI_Network)
        priors_vector = pr.load_priors(prior_paths[i], PPI_Network)

        #getting output from algorithms
        start_time = time.time()
        output_RWR = rwr.random_walk(PPI_Network, start_vector)
        end_time = time.time()
        print("time for rwr:", end_time - start_time)
        start_time = time.time()
        output_PR = pr.page_rank(PPI_Network, start_vector, priors_vector)
        end_time = time.time()
        print("time for pr:", end_time - start_time)

        start_time = time.time()
        output_DK = dk.diffusion_kernel(PPI_Network, start_vector)
        end_time = time.time()
        print("time for dk:", end_time - start_time)

        #building roc curves

        start_time = time.time()
        name = "rwr-" + names[i]
        rwr_curve = roc_curve(output_RWR, ground_truth_vec, name)
        end_time = time.time()
        print("time for roc curve, rwr:", end_time -start_time)

        start_time = time.time()
        name = "pr-" + names[i]
        pr_curve = roc_curve(output_PR, ground_truth_vec, name)
        end_time = time.time()
        print("time for roc curve, pr:", end_time - start_time)
        start_time = time.time()

        start_time = time.time()
        name = "dk-" + names[i]
        dk_curve = roc_curve(output_DK, ground_truth_vec, name)
        end_time = time.time()
        print("time for roc curve, dk:", end_time - start_time)
        file_path = 'Results/' + names[i] + 'roc_curve.png'
        plt.ylabel('TPR')
        plt.xlabel('FPR')
        plt.title(names[i])
        plt.legend(loc='lower right')
        plt.savefig(file_path) #moved from roc_curve
        plt.clf() #moved from roc_curve
        print("Plots have been saved as png files in the Results folder.")


if __name__ == '__main__':
    main()

import os, shutil, errno, csv
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.metrics import cohen_kappa_score
from backports import csv
import io
from pathlib import Path

def calc_confusion_matrix(labels_true, labels_pred):
    cm = confusion_matrix(labels_true, labels_pred)
    n_classes = cm.shape[0] #number of rows and colums is identical in a N x N confusion matrix
    return cm, n_classes

def overall_accuracy(conf_matrix):
    acc = np.trace(conf_matrix)
    tot = conf_matrix.sum()
    return (acc / tot) * 100

def class_success(conf_matrix):
    rows, cols = conf_matrix.shape
    nclasses = rows
    omit_commit_sum = 0
    for label in range(nclasses):
        row_omit = conf_matrix[label, :][np.arange(cols) != label].sum()    
        col_commit = conf_matrix[:, label][np.arange(rows) != label].sum()
        omit_commit_sum += (row_omit + col_commit)
    csi = (1 - (omit_commit_sum / nclasses)) * 100
    return csi

def kappa_coeff(labels_true, labels_pred):
    k = cohen_kappa_score(labels_true, labels_pred) * 100
    return k

def kappa_w(labels_true, labels_pred):
    k_w = cohen_kappa_score(labels_true, labels_pred, weights='quadratic') * 100
    return k_w

def avg_user_accuracy(label, conf_matrix):
    col_correct = conf_matrix[label, label]
    col_tot = conf_matrix[:, label].sum()
    usr_acc = (col_correct / col_tot) * 100
    return usr_acc

def avg_prod_accuracy(label, conf_matrix):
    row_correct = conf_matrix[label, label]
    row_tot = conf_matrix[label, :].sum()
    prod_acc = (row_correct / row_tot) * 100
    return prod_acc

def omission(label, conf_matrix):
    cols = conf_matrix.shape[1] #number of rows and colums is identical in a N x N confusion matrix
    row_omit = conf_matrix[label, :][np.arange(cols) != label].sum()
    row_tot = conf_matrix[label, :].sum()
    omit = (row_omit / row_tot) * 100
    return omit

def commission(label, conf_matrix):
    rows = conf_matrix.shape[0] #number of rows and colums is identical in a N x N confusion matrix
    col_commit = conf_matrix[:, label][np.arange(rows) != label].sum()
    col_tot = conf_matrix[:, label].sum()
    commit = (col_commit / col_tot) * 100
    return commit

'''
def plot_confusion_matrix(mat, classes, title='Confusion matrix', cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    """
    plt.imshow(mat, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    thresh = mat.max() / 2.
    for i, j in itertools.product(range(mat.shape[0]), range(mat.shape[1])):
        plt.text(j, i, format(cm[i, j], 'd'),
                 horizontalalignment="center",
                 color="white" if mat[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
'''

def write_fbt_fragstats(dir_name, baseline, comparison):
    # Define FRAGSTATS input using mandatory format #
    #baseline = "D:\\\\sample_data\\\\observed.tif"
    #comparison = "D:\\\\sample_data\\\\simulation1.tif"

    base_str_fgst = baseline + ", x, 999, x, x, 1, x, IDF_GeoTIFF\n"
    comp_str_fgst = comparison + ", x, 999, x, x, 1, x, IDF_GeoTIFF\n"

    fbt_file = os.path.join(dir_name, "fragbatchinput.fbt")
    if os.path.exists(fbt_file):
        os.remove(fbt_file)
    # create the output writer
    with open(fbt_file, 'w') as fbt:
        all_rows = [base_str_fgst, comp_str_fgst]
        for row in all_rows:
            fbt.write(row)

    return

def run_fragstats(dir_name, fbt, exe_path, baseline, comparison, nclasses, fout):

    print('Running FRAGSTATS module...')
    # Specify FRAGSTATS model and copy the .fca file to user-defined output folder
    fca_file = "frag_" + str(nclasses) + "class.fca"
    #fca_path = os.path.join(Path(__file__).parents[1], "frag_models", fca_file)
    fca_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frag_models", fca_file)
    shutil.copy(fca_path, dir_name)

    # define the path to the fragstats .exe file and copy the file to the user-defined output folder
    #exe_file_path = os.path.join(os.getcwd(), "frg.exe")
    #shutil.copy(exe_file_path, folder)
    exe_file_path  = os.path.join(exe_path, "frg")
    exe_file_path = f'"{exe_file_path}"'

    #exe_file_path = '"C:\\Program Files (x86)\\Fragstats 4\\frg"'
    #'"C:\\Program Files (x86)\\Fragstats 4\\frg"'

    #Define the results folder to store fragstats model output
    #results_path = os.path.join(folder, "fragout")
    out_folder_name = "fragout"
    out_folder = os.path.join(dir_name, out_folder_name)
    if not os.path.exists(out_folder):
        try:
            os.makedirs(out_folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    results_path = "fragout\\\\fragResult"

    #Full CMD to pass onto terminal via os.system()
    cmd = exe_file_path + ' -m ' + fca_file + ' -b ' + fbt + ' -o ' + results_path
    #Make sure to change dir to current script location
    os.chdir(dir_name)
    os.system(cmd)

    #Calculate FRAG results
    frag_out_file = results_path + ".class"
    result_file = os.path.join(dir_name, frag_out_file.replace('\\\\', '\\')) 

    #Read FRAGSTATS result file into a pandas dataframe
    df = pd.read_csv(result_file)

    #Define empty pandas dataframes
    outro = pd.DataFrame()
    omit = pd.DataFrame()

    print('Computing FRAGSTATS Accuracy Metrics...')
    for label in range(nclasses):
        Omit_count = 0
        try:
            NP = abs((df.iat[(label + nclasses), 2] - df.iat[label, 2])/ df.iat[label, 2])
        except:
            NP = "N/A"
            Omit_count += 1 
            print("Label " + str(label) + " Number of patches omitted from calculation due to geometry.")
        try:
            GYRATE = abs((df.iat[(label + nclasses), 3] - df.iat[label, 3]) / df.iat[label, 3])
        except:
            GYRATE = "N/A"
            Omit_count += 1
            print("Label " + str(label) + " GYRATE_AM omitted from calculation due to geometry.")
        try:
            FRAC = abs((df.iat[(label + nclasses), 4] - df.iat[label, 4]) / df.iat[label, 4])
        except:
            FRAC = "N/A"
            Omit_count += 1
            print("Label " + str(label) + " FRAC_AM omitted from calculation due to geometry.")
        try:
            CORE = abs((df.iat[(label + nclasses), 5] - df.iat[label, 5]) / df.iat[label, 5])
        except:
            CORE = "N/A"
            Omit_count += 1
            print("Label " + str(label) + " CORE_AM omitted from calculation due to geometry.")
        try:
            ENN_AM = abs((df.iat[(label + nclasses), 6] - df.iat[label, 6]) / df.iat[label, 6])
        except:
            ENN_AM = "N/A"
            Omit_count += 1
            print("Label " + str(label) + " ENN_AM omitted from calculation due to geometry.")
        try:
            ENN_CV = abs(df.iat[(label + nclasses), 7] - df.iat[label, 7])
        except:
            ENN_CV = "N/A"
            Omit_count += 1
            print("Label " + str(label) + " ENN_CV omitted from calculation due to geometry.")
        try:
            ECON = abs((df.iat[(label + nclasses), 8] - df.iat[label, 8]) /df.iat[label, 8])
        except:
            ECON = "N/A"
            Omit_count += 1
            print("Label " + str(label) + " ECON_AM omitted from calculation due to geometry.")

        outro.at[label, 0] = label
        outro.at[label, 1] = NP
        outro.at[label, 2] = GYRATE
        outro.at[label, 3] = FRAC
        outro.at[label, 4] = CORE
        outro.at[label, 5] = ENN_AM
        outro.at[label, 6] = ENN_CV
        outro.at[label, 7] = ECON
        omit.at[label, 0] = 7 - Omit_count

    outro['SUM'] = (outro[outro.columns].sum(axis = 1))
    outro = pd.concat([outro, omit], axis = 1)
    outro.columns = ["Label", "NP", "GYRATE", "FRAC", "CORE", "ENN_AM", "ENN_CV", "ECON", "SUM", "Omit"]

    def calculate_Cdif(row):
        return (row['SUM'] / row['Omit']) * 100

    outro['Config Dif'] = outro.apply(calculate_Cdif, axis = 1)
    
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)
    print('\n')
    print(outro.to_string(index = False))

    # Save to output file
    print("\nSaving Validation Metrics Table to File...")

    with io.open(fout, 'a', newline='', encoding='utf-8') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(['\n'])
            writer.writerow(['FRAGSTATS CONFIGURATION METRICS'])
            outro.to_csv(csvFile, index = False)
    csvFile.close()

    # with open(fout, 'a') as csvFile:
    #     writer = csv.writer(csvFile)
    #     writer.writerow('\nFRAGSTATS CONFIGURATION METRICS')
    #     outro.to_csv(csvFile, index = False)
    # csvFile.close()
    
    return
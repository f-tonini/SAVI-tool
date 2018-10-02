import os, shutil, errno
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix

def calc_confusion_matrix(labels_true, labels_pred):
    cm = confusion_matrix(labels_true, labels_pred)
    n_classes = cm.shape[0] #number of rows and colums is identical in a N x N confusion matrix
    return cm, n_classes

def omission(label, conf_matrix):
    rows, cols = conf_matrix.shape #number of rows and colums is identical in a N x N confusion matrix
    row_omit = conf_matrix[label, :][np.arange(cols) != label].sum()
    row_tot = conf_matrix[label, :].sum()
    omit = row_omit.astype('float') / row_tot
    return omit

def commission(label, conf_matrix):
    rows, cols = conf_matrix.shape #number of rows and colums is identical in a N x N confusion matrix
    col_commit = conf_matrix[:, label][np.arange(rows) != label].sum()
    col_tot = conf_matrix[:, label].sum()
    commit = col_commit.astype('float') / col_tot
    return commit

'''def plot_confusion_matrix(mat, classes, title='Confusion matrix', cmap=plt.cm.Blues):
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
    plt.xlabel('Predicted label')'''

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

def run_fragstats(dir_name, fbt, exe_path, baseline, comparison, nclasses):

    # Specify FRAGSTATS model and copy the .fca file to user-defined output folder
    fca_file = "frag_" + str(nclasses) + "class.fca"
    fca_path = os.path.join(os.getcwd(), "frag_models", fca_file)
    shutil.copy(fca_path, dir_name)

    # define the path to the fragstats .exe file and copy the file to the user-defined output folder
    #exe_file_path = os.path.join(os.getcwd(), "frg.exe")
    #shutil.copy(exe_file_path, folder)
    exe_file_path  = os.path.join(exe_path, "frg")
    exe_file_path = f'"{exe_file_path}"'

    #exe_file_path = '"C:\\Program Files (x86)\\Fragstats 4\\frg"'
    #'"C:\\Program Files (x86)\\Fragstats 4\\frg"'

    # define the results folder to store fragstats model output
    #results_path = os.path.join(folder, "fragout")
    out_folder = os.path.join(dir_name, "fragout")
    if not os.path.exists(out_folder):
        try:
            os.makedirs(out_folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    results_path = "fragout\\\\fragResult"

    cmd = exe_file_path + ' -m ' + fca_file + ' -b ' + fbt + ' -o ' + results_path
    
    os.chdir(dir_name)
    os.system(cmd)

    #Calculate FRAG results
    frag_out_file = results_path + ".class"
    result_file = os.path.join(dir_name, frag_out_file.replace('\\\\', '\\')) 

    df = pd.read_csv(result_file)

    outro = pd.DataFrame()
    omit = pd.DataFrame()

    print('\n')
    for i in range(nclasses):
        Omit_count = 0
        Class_count = i + 1
        try:
            NP = abs((df.iat[(i+nclasses),2] - df.iat[i,2])/ df.iat[i,2])
        except:
            NP = "N/A"
            Omit_count += 1 
            print("Class " + str(Class_count) + " Number of Patches omitted from calculation due to geometry.")
        try:
            GYRATE = abs((df.iat[(i+nclasses),3] - df.iat[i,3])/ df.iat[i,3])
        except:
            GYRATE = "N/A"
            Omit_count += 1
            print("Class " + str(Class_count) + " GYRATE_AM omitted from calculation due to geometry.")
        try:
            FRAC = abs((df.iat[(i+nclasses),4] - df.iat[i,4])/ df.iat[i,4])
        except:
            FRAC = "N/A"
            Omit_count += 1
            print("Class " + str(Class_count) + " FRAC_AM omitted from calculation due to geometry.")
        try:
            CORE = abs((df.iat[(i+nclasses),5] - df.iat[i,5])/ df.iat[i,5])
        except:
            CORE = "N/A"
            Omit_count += 1
            print("Class " + str(Class_count) + " CORE_AM omitted from calculation due to geometry.")
        try:
            ENN_AM = abs((df.iat[(i+nclasses),6] - df.iat[i,6])/ df.iat[i,6])
        except:
            ENN_AM = "N/A"
            Omit_count += 1
            print("Class " + str(Class_count) + " ENN_AM omitted from calculation due to geometry.")
        try:
            ENN_CV = abs(df.iat[(i+nclasses),7] - df.iat[i,7])
        except:
            ENN_CV = "N/A"
            Omit_count += 1
            print("Class " + str(Class_count) + " ENN_CV omitted from calculation due to geometry.")
        try:
            ECON = abs((df.iat[(i+nclasses),8] - df.iat[i,8])/ df.iat[i,8])
        except:
            ECON = "N/A"
            Omit_count += 1
            print("Class " + str(Class_count) + " ECON_AM omitted from calculation due to geometry.")

        Class = "Class " + str(Class_count)
        outro.at[i, 0] = Class
        outro.at[i, 1] = NP
        outro.at[i, 2] = GYRATE
        outro.at[i, 3] = FRAC
        outro.at[i, 4] = CORE
        outro.at[i, 5] = ENN_AM
        outro.at[i, 6] = ENN_CV
        outro.at[i, 7] = ECON
        omit.at[i, 0] = 7 - Omit_count

    outro['SUM'] = (outro[outro.columns].sum(axis=1))
    outro = pd.concat([outro, omit], axis=1)
    outro.columns = ["Class", "NP", "GYRATE", "FRAC", "CORE", "ENN_AM", "ENN_CV", "ECON", "SUM", "Omit"]

    def calculate_Cdif(row):
        return row['SUM']/row['Omit']
    outro['Config Dif'] = outro.apply(calculate_Cdif, axis=1)
    
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)
    print('\n')
    print(outro)

    return





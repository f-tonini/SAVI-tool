import os, shutil, csv
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

def write_csv_fragstats(folder, filename, base_input, comp_input):
    # create the output writer
    out_csv_path = os.path.join(folder, filename)
    with open(out_csv_path, 'w') as csvfile:
        outWriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
        all_rows = [[base_input], [comp_input]]
        for row in all_rows:
            outWriter.writerow(row)

    #rename .csv file to .fbt extension for fragstats
    os.rename(out_csv_path, out_csv_path[:-4] + '.fbt')

    return

'''def run_fragstats(baseline, comparison, nclasses):

    # Specify FRAGSTATS model
    sys.argv[0] os.path.dirname(abspath)
    model = "frag_" + str(int(nclasses)) + "class.fca"
    frag_model = dname + '\\frag_models\\' + model
    shutil.copy(frag_model, temppath)
    getEXE = dname + "\\frg.exe"
    shutil.copy(getEXE, temppath)
    results = "Result\\\\fragResult" 
    systemcall = 'frg.exe -m ' + model + ' -b fragbatchinput.fbt -o ' + results
    os.chdir(temppath)
    os.makedirs(temppath + "\\Result")
    os.system(systemcall)

    # Calculate FRAG results
    result = temppath + "\\Result\\fragResult.class"
    bf = pd.read_csv(result)
    outro = pd.DataFrame()
    omit = pd.DataFrame()
    i = 0
    while i < n_classes:
        Omit_count = 0
        Class_count = i + 1
        try:
            NP = abs((bf.iat[(i+n_classes),2] - bf.iat[i,2])/ bf.iat[i,2])
        except:
            NP = "N/A"
            Omit_count = Omit_count + 1 
            print "Class " + str(Class_count) + " Number of Patches omitted from calculation due to geometry."
        try:
            GYRATE = abs((bf.iat[(i+n_classes),3] - bf.iat[i,3])/ bf.iat[i,3])
        except:
            GYRATE = "N/A"
            Omit_count = Omit_count + 1
            print "Class " + str(Class_count) + " GYRATE_AM omitted from calculation due to geometry."
        try:
            FRAC = abs((bf.iat[(i+n_classes),4] - bf.iat[i,4])/ bf.iat[i,4])
        except:
            FRAC = "N/A"
            Omit_count = Omit_count + 1
            print "Class " + str(Class_count) + " FRAC_AM omitted from calculation due to geometry."
        try:
            CORE = abs((bf.iat[(i+n_classes),5] - bf.iat[i,5])/ bf.iat[i,5])
        except:
            CORE = "N/A"
            Omit_count = Omit_count + 1
            print "Class " + str(Class_count) + " CORE_AM omitted from calculation due to geometry."
        try:
            ENN_AM = abs((bf.iat[(i+n_classes),6] - bf.iat[i,6])/ bf.iat[i,6])
        except:
            ENN_AM = "N/A"
            Omit_count = Omit_count + 1
            print "Class " + str(Class_count) + " ENN_AM omitted from calculation due to geometry."
        try:
            ENN_CV = abs(bf.iat[(i+n_classes),7] - bf.iat[i,7])
        except:
            ENN_CV = "N/A"
            Omit_count = Omit_count + 1
            print "Class " + str(Class_count) + " ENN_CV omitted from calculation due to geometry."
        try:
            ECON = abs((bf.iat[(i+n_classes),8] - bf.iat[i,8])/ bf.iat[i,8])
        except:
            ECON = "N/A"
            Omit_count = Omit_count + 1
            print "Class " + str(Class_count) + " ECON_AM omitted from calculation due to geometry."
        Class = "Class " + str(Class_count)
        outro.at[0+i, 0] = Class
        outro.at[0+i, 1] = NP
        outro.at[0+i, 2] = GYRATE
        outro.at[0+i, 3] = FRAC
        outro.at[0+i, 4] = CORE
        outro.at[0+i, 5] = ENN_AM
        outro.at[0+i, 6] = ENN_CV
        outro.at[0+i, 7] = ECON
        omit.at[0+i, 0] = 7 - Omit_count
        i = i + 1
    outro['SUM'] = (outro[outro.columns].sum(axis=1))
    outro = pd.concat([outro, omit], axis=1)
    outro.columns = ["Class", "NP", "GYRATE", "FRAC", "CORE", "ENN_AM", "ENN_CV", "ECON", "SUM", "Omit"]

    def calculate_Cdif(row):
        return row['SUM']/row['Omit']
    outro['Config Dif'] = outro.apply(calculate_Cdif, axis=1)
    print outro
    try:
        temp = temppath + "\\plus_ras"
        arcpy.Delete_management(temp)
    except arcpy.ExecuteError:
        pass
    shutil.rmtree(temppath)'''




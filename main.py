import os, shutil
import pandas as pd
import numpy as np
import rasterio as rio
from sklearn.metrics import confusion_matrix
#import matplotlib.pyplot as plt
from gooey import Gooey, GooeyParser
#from message import display_message

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

@Gooey(dump_build_config=True, program_name="AccuSim")
def main():
    desc = "Write some description of AccuSim here!"
    parser = GooeyParser(description=desc)

    parser.add_argument("Baseline", help="Select a baseline (e.g. observed) raster file from your local drive", widget="FileChooser")
    parser.add_argument("Comparison", help="Select a comparison (e.g. simulated) raster file from your local drive", widget="FileChooser")
    #my_cool_parser.add_argument("FileSaver", help=file_help_msg, widget="FileSaver")
    parser.add_argument("Output", help="Directory to store output", widget='DirChooser')
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite output file (if present)")
    #my_cool_parser.add_argument("-w", "--writelog", default="writelogs", help="Dump output to local file")
    #my_cool_parser.add_argument("-e", "--error", action="store_true", help="Stop process on error (default: No)")
    #verbosity = my_cool_parser.add_mutually_exclusive_group()
    #verbosity.add_argument('-t', '--verbozze', dest='verbose', action="store_true", help="Show more details")
    #verbosity.add_argument('-q', '--quiet', dest='quiet', action="store_true", help="Only output on error")
    fragstats_group = parser.add_argument_group(
        "FRAGSTATS", 
        "Customize here the desired metrics to be returned from the FRAGSTATS software"
    )

    fragstats_group.add_argument(
        '--metrics A', 
        action="store_true",
        help='Check the box to include'
    )
    fragstats_group.add_argument(
        '--metrics B', 
        action="store_true",
        help='Check the box to include'
    )
    fragstats_group.add_argument(
        '--metrics C', 
        action="store_true",
        help='Check the box to include'
    )

    args = parser.parse_args()
    #display_message()

    obs_raster_path = args.Baseline
    sim_raster_path = args.Comparison

    # open raster data
    with rio.open(obs_raster_path) as obs:
        obs_array = obs.read(1)

    with rio.open(sim_raster_path) as sim:
        sim_array = sim.read(1)

    # Compute confusion matrix
    y_true = obs_array.reshape(obs_array.shape[0] * obs_array.shape[1])
    y_pred = sim_array.reshape(sim_array.shape[0] * sim_array.shape[1])    
    cm = confusion_matrix(y_true, y_pred)
    cm_rows, cm_columns = cm.shape #number of rows and colums is identical in a N x N confusion matrix

    print("Label Omission Commission Quantity Allocation")
    for label in range(cm_rows):
        quantity = abs(omission(label, cm) - commission(label, cm))
        allocation = 2 * min(omission(label, cm), commission(label, cm))
        print(f"{label:5d} {omission(label, cm):12.2f} {commission(label, cm):17.2f} {quantity:16.2f} {allocation:13.2f}")


if __name__ == '__main__':
    main()
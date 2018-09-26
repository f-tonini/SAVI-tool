import os, shutil, csv
import pandas as pd
import numpy as np
import rasterio as rio
#import matplotlib.pyplot as plt
from gooey import Gooey, GooeyParser
#from message import display_message
import utils

@Gooey(dump_build_config=True, 
       program_name="AccuSim", 
       image_dir="./img",
       default_size=(610, 710)
       )
def main():
    desc = "Write some description of AccuSim here!"
    parser = GooeyParser(description=desc)

    parser.add_argument("Baseline", help="Select a baseline (e.g. observed) raster file from your local drive", widget="FileChooser")
    parser.add_argument("Comparison", help="Select a comparison (e.g. simulated) raster file from your local drive", widget="FileChooser")
    #my_cool_parser.add_argument("FileSaver", help=file_help_msg, widget="FileSaver")
    parser.add_argument("Output_Directory", help="Main working directory containing all the necessary input files", widget='DirChooser')
    #parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite output file (if present)")
    #my_cool_parser.add_argument("-w", "--writelog", default="writelogs", help="Dump output to local file")
    #my_cool_parser.add_argument("-e", "--error", action="store_true", help="Stop process on error (default: No)")
    #verbosity = my_cool_parser.add_mutually_exclusive_group()
    #verbosity.add_argument('-t', '--verbozze', dest='verbose', action="store_true", help="Show more details")
    #verbosity.add_argument('-q', '--quiet', dest='quiet', action="store_true", help="Only output on error")
    fragstats_group = parser.add_argument_group(
        "FRAGSTATS",
        gooey_options={
            'show_border': False,
            'columns': 1 
        }
    )

    fragstats_group.add_argument(
        "--Calculate metrics", 
        action="store_true",
        help="Check the box to include"
    )
    
    '''fragstats_group.add_argument(
        "-e", "--Executable_File_Location",
        widget="FileChooser",
        help="Select the FRAGSTATS executable (.exe) file"
    )'''

    optArgs_group = parser.add_argument_group(
        "Optional Arguments"
    )

    optArgs_group.add_argument(
        "-o", "--overwrite",  
        action="store_true",
        help="Overwrite output file (if present)"
    )

    args = parser.parse_args()
    #display_message()

    #Read params from the GUI
    base_raster_path = args.Baseline
    comp_raster_path = args.Comparison
    out_dir = args.Output_Directory

    # open raster data
    with rio.open(base_raster_path) as base:
        base_array = base.read(1)
    with rio.open(comp_raster_path) as comp:
        comp_array = comp.read(1)

    # Compute confusion matrix
    y_base = base_array.reshape(base_array.shape[0] * base_array.shape[1])
    y_comp = comp_array.reshape(comp_array.shape[0] * comp_array.shape[1])    
    cm, n_classes = utils.calc_confusion_matrix(labels_true = y_base, labels_pred = y_comp)
    print("Label Omission Commission Quantity Allocation")
    for label in range(n_classes):
        quantity = abs(utils.omission(label, cm) - utils.commission(label, cm))
        allocation = 2 * min(utils.omission(label, cm), utils.commission(label, cm))
        print(f"{label:5d} {utils.omission(label, cm):12.2f} {utils.commission(label, cm):17.2f} {quantity:16.2f} {allocation:13.2f}")

    #FRAGSTATS SECTION
    #-----------------------------------------

    # Write required .fbt batchfile needed by FRAGSTATS 
    utils.write_csv_fragstats(folder = out_dir, baseline = base_raster_path, comparison = comp_raster_path)

    # Run FRAGSTATS
    utils.run_fragstats(folder = out_dir, fbt = "fragbatchinput.fbt",
                        baseline = base_raster_path, comparison = comp_raster_path, 
                        nclasses = n_classes)


if __name__ == '__main__':
    main()




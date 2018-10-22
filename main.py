import os, shutil, time, errno, csv
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
       default_size=(650, 515)
       )
def main():
    desc = "AccuSim is a GUI-based program to help users calculate accuracy metrics for\nland-use/land-change simulation models."
    parser = GooeyParser(description=desc)

    parser.add_argument(
        "Baseline", 
        help="Select a baseline (e.g. observed) raster file", 
        widget="FileChooser",
        gooey_options={
            'validator':{
            'test': 'user_input.split(".")[1] not in [".tif", ".img"]',
            'message': 'The raster file extension must be .tif or .img'
            }
        }
    )
    parser.add_argument(
        "Comparison", 
        help="Select a comparison (e.g. simulated) raster file", 
        widget="FileChooser",
        gooey_options={
            'validator':{
            'test': 'user_input.split(".")[1] not in [".tif", ".img"]',
            'message': 'The raster file extension must be .tif or .img'
            }
        }
    )
    parser.add_argument("Output_Folder", help="Select a folder where you want to save your output metrics files", widget="DirChooser")
    
    fragstats_group = parser.add_argument_group(
        "FRAGSTATS (for Windows users ONLY)",
        gooey_options={
            'show_border': False,
            'columns': 2 
        }
    )

    fragstats_group.add_argument(
        "--Calculate metrics", 
        default=False,
        action="store_true",
        help="Check the box"
    )
    
    fragstats_group.add_argument(
        "--Executable_File_Location",
        widget="DirChooser",
        help="Select the folder of the FRAGSTATS executable (.exe) file"
    )

    args = parser.parse_args()
    #display_message()

    #Read params from the GUI
    base_raster_path = args.Baseline
    comp_raster_path = args.Comparison
    out_dir = args.Output_Folder
    exe_location = args.Executable_File_Location

    # open raster data
    with rio.open(base_raster_path) as base:
        base_array = base.read(1)
    with rio.open(comp_raster_path) as comp:
        comp_array = comp.read(1)

    # Compute confusion matrix
    print('Computing Confusion Matrix from Rasters...')
    y_base = base_array.reshape(base_array.shape[0] * base_array.shape[1])
    y_comp = comp_array.reshape(comp_array.shape[0] * comp_array.shape[1])    
    cm, n_classes = utils.calc_confusion_matrix(labels_true = y_base, labels_pred = y_comp)
    
    # Compute Main Metrics
    #-----------------------------------------
    print('Computing Accuracy Metrics...\n')
    print("Label Omission(%) Commission(%) Quantity Allocation")
    val_lst = []
    for label in range(n_classes):
        quantity_dsgr = abs(utils.omission(label, cm) - utils.commission(label, cm))
        allocation_dsgr = 2 * min(utils.omission(label, cm), utils.commission(label, cm))
        val_lst.append([label, utils.omission(label, cm), utils.commission(label, cm), quantity_dsgr, allocation_dsgr])
        print(f"{label:5d} {utils.omission(label, cm):13.2f} {utils.commission(label, cm):21.2f} {quantity_dsgr:21.2f} {allocation_dsgr:14.2f}")
    
    print('\n')
    print("Accuracy(%)    CSI(%)    Kappa(%)    WKappa(%)")
    ov_acc = utils.overall_accuracy(cm)
    csi = utils.class_success(cm)
    kappa = utils.kappa_coeff(y_base, y_comp)
    kappaW = utils.kappa_w(y_base, y_comp)
    print(f"{ov_acc:9.2f} {csi:17.2f} {kappa:12.2f} {kappaW:16.2f}")

    # Save to output file
    print("Saving Output Table to File...")
    pontius_df = pd.DataFrame(val_lst)
    pontius_df.columns = ["Label", "Omission(%)", "Commission(%)", "Quantity", "Allocation"]
    out_file = os.path.join(out_dir, "AccuSim_metrics.csv")
    pontius_df.to_csv(out_file, index=False)
    with open(out_file, 'a') as csvFile:
        writer = csv.writer(csvFile)
        newdata = [["Accuracy(%)", ov_acc], ["CSI(%)", csi], 
        ["Kappa(%)", kappa], ["W Kappa(%)", kappaW]]
        writer.writerow('\n')
        writer.writerows(newdata)
    csvFile.close()
    print('\n')

    #FRAGSTATS SECTION
    #-----------------------------------------

    #TRY THIS %LocalAppData%
    temp_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'tmpAccuSim')
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # Write required .fbt batchfile needed by FRAGSTATS 
    utils.write_fbt_fragstats(dir_name = temp_dir, baseline = base_raster_path, comparison = comp_raster_path)

    # Run FRAGSTATS
    utils.run_fragstats(dir_name = temp_dir, fbt = "fragbatchinput.fbt", exe_path = exe_location,
                        baseline = base_raster_path, comparison = comp_raster_path, 
                        nclasses = n_classes, fout = out_file)

if __name__ == '__main__':
    main()




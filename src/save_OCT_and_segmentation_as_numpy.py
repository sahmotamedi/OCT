from OCT.formats.OCTVol import OCTVol
from glob import glob
import numpy as np
import os
from copy import deepcopy


def detect_segmented_layers(oct_vol: OCTVol) -> list[str]:
    """ Detect and return the segmented boundaries of an OCT vol file """
    """ Hint: 
        boundary_1 = Internal Limiting Membrane (ILM, aka innermost boundary)
        boundary_2 = Bruch's Membrane (BM, aka outermost boundary)
        boundary_3 = Retinal Nerve Fiber Layer - Ganglion Cell Layer (RNFL-GCL)
        boundary_4 = Ganglion Cell Layer - Inner Plexiform Layer (GCL-IPL)
        boundary_5 = Inner Plexiform Layer - Inner Nuclear Layer (IPL-INL)
        boundary_6 = Inner Nuclear Layer - Outer Plexiform Layer (INL-OPL)
        boundary_7 = Outer Plexiform Layer - Outer Nuclear Layer (OPL-ONL)
        boundary_9 = External Limiting Membrane (ELM)
        boundary_15 = Inner Segments of Photoreceptors - Outer Segments of Photoreceptors (IS-OS, aka PR1 or Ellipsoid Zone)
        boundary_16 = Outer Segments of Photoreceptors - Interdigitation Zone (OS-IZ, aka PR2)
        boundary_17 = Interdigitation Zone - Retinal Pigment Epithelium (IZ-RPE)
        """
    # Define the invalid number which is the largest number for float32
    invalid = np.finfo(np.float32).max

    # Go through boundaries and add the ones that have segmentation data to the list
    segmented_boundaries = []
    for i_boundary in range(oct_vol.b_scan_header['num_seg'][0]):
        if not np.all(oct_vol.b_scan_header['boundary_{}'.format(i_boundary+1)] == invalid):
            segmented_boundaries.append('boundary_{}'.format(i_boundary+1))

    return segmented_boundaries


def extract_segmentation(oct_vol: OCTVol) -> np.ndarray:
    """ One-hot encode segmentation layers and return a numpy array of n+1 boundaries * size_z * size_x * num_b_scans """
    # First the segmented boundaries have be extracted
    segmented_boundaries = detect_segmented_layers(oct_vol)

    # Move boundary_2 to the end of the list if it is segmented because boundary_2 is BM, the outermost layer
    if 'boundary_2' in segmented_boundaries:
        segmented_boundaries.remove('boundary_2')
        segmented_boundaries.append('boundary_2')

    # One-hot encode the layers using the boundaries. If we have n boundaries then we will have a numpy array of n+1
    # layers times size_z * size_x * num_b_scans
    invalid = np.finfo(np.float32).max  # this is written as the segmentation if the boundary is missing
    n_layers = len(segmented_boundaries) + 1
    segmented_layers = np.zeros((n_layers, oct_vol.header['size_z'], oct_vol.header['size_x'], oct_vol.header['num_b_scans']))
    for i_layer in range(n_layers):
        for i_b_scan in range(oct_vol.header['num_b_scans']):
            for i_a_scan in range(oct_vol.header['size_x']):
                if i_layer == 0:
                    if oct_vol.b_scan_header[segmented_boundaries[i_layer]][i_b_scan, i_a_scan] != invalid:
                        segmented_layers[i_layer, :int(np.ceil(oct_vol.b_scan_header[segmented_boundaries[i_layer]][i_b_scan, i_a_scan])), i_a_scan, i_b_scan] = 1
                elif i_layer == n_layers-1:
                    if oct_vol.b_scan_header[segmented_boundaries[i_layer-1]][i_b_scan, i_a_scan] != invalid:
                        segmented_layers[i_layer, int(np.ceil(oct_vol.b_scan_header[segmented_boundaries[i_layer-1]][i_b_scan, i_a_scan])):, i_a_scan, i_b_scan] = 1
                else:
                    if oct_vol.b_scan_header[segmented_boundaries[i_layer-1]][i_b_scan, i_a_scan] != invalid and oct_vol.b_scan_header[segmented_boundaries[i_layer]][i_b_scan, i_a_scan] != invalid:
                        segmented_layers[i_layer, int(np.ceil(oct_vol.b_scan_header[segmented_boundaries[i_layer-1]][i_b_scan, i_a_scan])):int(np.ceil(oct_vol.b_scan_header[segmented_boundaries[i_layer]][i_b_scan, i_a_scan])), i_a_scan, i_b_scan] = 1

    return segmented_layers


def combine_oct_and_segmentation_as_numpy(oct_vol: OCTVol) -> np.ndarray:
    """
    Combine the OCT B-Scans and segmentation of an OCTVol object

    Parameters
    ----------
    oct_vol : OCTVol
        An OCTVol object containing an OCT volumetric scan and its information

    Returns
    --------
    np.ndarray
        An array of ndim=4 with the shape of (1 + number of segmentation) * size_z * size_x * num_b_scans. The first row
        of the array consists of the OCT volumetric image with the rest consisting of the segmented layers from the
        innermost to the outermost

    """
    # Get rid of invalid numbers by replacing them with 0 (black)
    b_scans = deepcopy(oct_vol.b_scans)
    b_scans[b_scans > 1] = 0

    # Transfer the image with the formula provided by HE (pixel intensity is the 4th root of the stored values)
    b_scans = b_scans ** 0.25

    # Extract the segmentation
    segmented_layers = extract_segmentation(oct_vol)

    # combine with segmentation
    b_scans = b_scans[np.newaxis, ...]
    combined_b_scans_seg = np.concatenate((b_scans, segmented_layers), axis=0)

    return combined_b_scans_seg


def save_oct_and_segmentation_as_numpy(data_dir: str) -> None:
    """
    Read OCT vol files and save the OCT and the segmentation as numpy arrays

    Parameters
    ----------
    data_dir : str
        The path to the data directory consisting vol files

    """
    # Find .vol files in the directory
    vol_files_list = glob(os.path.join(data_dir, "*.vol"))

    # Create a new folder to save numpy arrays
    save_dir = os.path.join(data_dir, "numpy_arrays")
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    # Go through each volume and save the BScans of each volumes as a .npy file
    for vol_file_path in vol_files_list:
        try:
            # Read the vol file
            oct_vol = OCTVol(vol_file_path)

            # Combine OCT and the segmentation as numpy
            combined_b_scans_seg = combine_oct_and_segmentation_as_numpy(oct_vol)

            # Save the numpy stack
            np.save(os.path.join(save_dir, os.path.basename(vol_file_path).replace(".vol", ".npy")), combined_b_scans_seg)

        except Exception as error:
            print(vol_file_path + " was NOT processed. This error was raised: {}".format(repr(error)))
            continue

        # Print info
        print("The BScans and segmentation of {} were saved as numpy in {} folder".format(vol_file_path, save_dir))


save_vol_and_segmentation_as_numpy = save_oct_and_segmentation_as_numpy # This is to maintain the compatibility with the previous version of this code


if __name__ == '__main__':
    save_oct_and_segmentation_as_numpy(r"C:\Users\Amir\Downloads")

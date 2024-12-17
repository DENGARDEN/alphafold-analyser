# Import all relevant libraries
import argparse
import os
import pickle
import matplotlib.pyplot as plt
import py3Dmol
import numpy as np
import glob
import pathlib

# Color bands for visualizing plddt => later used for pymol integration
PLDDT_BANDS = [
    (0, 50, "#FF7D45"),
    (50, 70, "#FFDB13"),
    (70, 90, "#65CBF3"),
    (90, 100, "#0053D6"),
]


def plot_plddt_legend():
    """Plots the legend for pLDDT."""
    thresh = [
        "Very low (pLDDT < 50)",
        "Low (70 > pLDDT > 50)",
        "Confident (90 > pLDDT > 70)",
        "Very high (pLDDT > 90)",
    ]

    colors = [x[2] for x in PLDDT_BANDS]

    plt.figure(figsize=(2, 2))
    for c in colors:
        plt.bar(0, 0, color=c)
    plt.legend(thresh, frameon=False, loc="center", fontsize=20)
    plt.xticks([])
    plt.yticks([])
    ax = plt.gca()
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    plt.title("Model Confidence", fontsize=20, pad=20)
    return plt


# Create a PAE plot from the pkl file produced by AlphaFold - N.B code taken from AlphaFold CoLab
# + plddt plot
def pae_plotter(pickle_input: pathlib.Path, output):
    num_plots = 1  # for pLDDT plot only
    pathlib.Path(output).mkdir(parents=True, exist_ok=True)
    try:
        # Load as a dictionary from pickle file
        data = open(pickle_input, "rb")
        prediction_result = pickle.load(data)
        data.close()

        avg_plddt = prediction_result["plddt"].mean()
        #  plddt

        plt.figure(figsize=[8 * num_plots, 6])
        plt.subplot(1, num_plots, 1)
        plt.plot(prediction_result["plddt"])
        plt.title(
            f"{os.path.splitext(pathlib.Path(pickle_input).name)[0]} Predicted LDDT"
        )
        plt.xlabel("Residue")
        plt.ylabel("pLDDT")
        plt.annotate(
            f"Average pLDDT: {avg_plddt:.2f}",
            (0, 0),
            (0, -20),
            xycoords="axes fraction",
            textcoords="offset points",
            va="top",
        )

        plddt_output = (
            f"{output}/{os.path.splitext(pathlib.Path(pickle_input).name)[0]}_plddt.png"
        )
        plt.savefig(
            plddt_output, dpi=300, bbox_inches="tight"
        )  # save plot to output directory

        plt.close()
        # pae
        # plt.subplot(1, 2, 2)
        # pae, max_pae = list(pae_outputs.values())[0]
        # plt.imshow(pae, vmin=0.0, vmax=max_pae, cmap="Greens_r")
        # plt.colorbar(fraction=0.046, pad=0.04)

        # Display lines at chain boundaries.
        # best_unrelaxed_prot = unrelaxed_proteins[best_model_name]
        # total_num_res = best_unrelaxed_prot.residue_index.shape[-1]
        # chain_ids = best_unrelaxed_prot.chain_index
        # for chain_boundary in np.nonzero(chain_ids[:-1] - chain_ids[1:]):
        #     if chain_boundary.size:
        #         plt.plot(
        #             [0, total_num_res], [chain_boundary, chain_boundary], color="red"
        #         )
        #         plt.plot(
        #             [chain_boundary, chain_boundary], [0, total_num_res], color="red"
        #         )

        # plt.title("Predicted Aligned Error")
        # plt.xlabel("Scored residue")
        # plt.ylabel("Aligned residue")

        # Generate dictionary for predicted aligned error results from pkl file
        # pae_outputs = {
        #     "protein": (
        #         prediction_result["predicted_aligned_error"],
        #         prediction_result["max_predicted_aligned_error"],
        #     )
        # }

        # # Output file_path for the plot
        # pae_output = f"{output}/pae.png"

        # # Plot predicted align error results for each aligned residue
        # pae, max_pae = list(pae_outputs.values())[0]
        # fig = plt.figure()  # generate figure
        # fig.set_facecolor("white")  # color background white
        # plt.imshow(pae, vmin=0.0, vmax=max_pae)  # plot pae
        # plt.colorbar(fraction=0.46, pad=0.04)  # create color bar
        # plt.title("Predicted Aligned Error")  # plot title
        # plt.xlabel("Scored residue")  # plot x-axis label
        # plt.ylabel("Aligned residue")  # plot y-axis label

        # plt.savefig(
        #     pae_output, dpi=1000, bbox_inches="tight"
        # )  # save plot to output directory

        # print("\n predicted aligned error plotted\n")

    except EOFError as e:
        print(e)
        print(
            " Error: Data could not be found, predicted aligned error plotting failed\n"
        )

    except FileNotFoundError as e:
        print(e)
        print(
            " Error: File could not be found, predicted aligned error plotting failed\n"
        )


# Create a PAE plot from the pkl file produced by AlphaFold - N.B code taken from AlphaFold CoLab
# + plddt plot
def overlapped_data_parser(
    pickle_input: pathlib.Path, output, data_list: list, plddt_list: list
):
    num_plots = 1  # for pLDDT plot only
    pathlib.Path(output).mkdir(parents=True, exist_ok=True)
    try:
        # Load as a dictionary from pickle file
        data = open(pickle_input, "rb")
        prediction_result = pickle.load(data)
        data.close()

        avg_plddt = prediction_result["plddt"].mean()
        plddt_list.append(avg_plddt)
        #  plddt
        data_list.append(prediction_result["plddt"])

    except EOFError as e:
        print(e)
        print(
            " Error: Data could not be found, predicted aligned error plotting failed\n"
        )

    except FileNotFoundError as e:
        print(e)
        print(
            " Error: File could not be found, predicted aligned error plotting failed\n"
        )


# Create a PyMOL session from the pdb file generated by AlphaFold
def protein_painter(pdb_input, output):
    # File path for the PyMol session
    session_path = f"{output}/pLDDT.pse"

    # Terminal Command to open pdb file, color protein by pLDDT (b-factor) and save the session in the output directory
    pymol_command = f'PyMol -cq {str(pdb_input)} -d "spectrum b, yellow_green_blue; save {session_path}"'

    # Run terminal command
    os.system(pymol_command)

    if os.path.isfile(session_path):
        print("\n pLDDT data visualised\n")

    else:
        print("\n Error: visualisation failed\n")


# Generate CLI and define arguments with Argparse
def cmd_lineparser():
    parser = argparse.ArgumentParser(
        prog="AlphaFold Analyser",
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group_inputs = parser.add_argument_group("Inputs")
    # Get pdb structure path
    group_inputs.add_argument(
        "-p",
        "--pdb",
        metavar="\b",
        type=str,
        action="store",
        help="path to pdb file - generates pLDDT coloured structure",
        default=None,
    )
    # Get pkl file path
    group_inputs.add_argument(
        "-l",
        "--pkl",
        metavar="\b",
        type=str,
        action="store",
        help="path to pkl file - generates predicted aligned error plot",
        default=None,
    )
    # Get file path containing multiple pkls
    group_inputs.add_argument(
        "-d",
        "--pkl_dir",
        metavar="\b",
        type=str,
        action="store",
        help="path to pkl files - generates predicted aligned error plot",
        default="./plddt_analysis_target/",
    )
    group_inputs

    group_output = parser.add_argument_group("Outputs")
    # Get output directory
    group_output.add_argument(
        "-o",
        "--output",
        metavar="\b",
        type=str,
        action="store",
        help="directory to store all generated outputs",
        default=None,
    )

    group_options = parser.add_argument_group("Options")
    # Get Version
    group_options.add_argument(
        "-v", "--version", action="version", version="%(prog)s v1.0"
    )
    # Get help
    group_options.add_argument(
        "-h", "--help", action="help", help="show this help message and exit\n "
    )
    group_options.add_argument(
        "--overlapped", action="store_true", help="overlapped pLDDT plot"
    )

    # Parse arguments
    args = parser.parse_args()
    input_list = [args.pkl, args.pdb, args.output]

    # If all arguments are None display help text by parsing help
    if input_list.count(input_list[0]) == len(input_list):
        parser.parse_args(["-h"])

    # Check arg.pdb input is a pdb file
    if args.pdb is not None:
        if not args.pdb.endswith(".pdb"):
            parser.error("ERROR: --pdb requires pdb file as input")

    # Check arg.pkl input is a pkl file
    if args.pkl is not None:
        if not args.pkl.endswith(".pkl"):
            parser.error("ERROR: --pkl requires pkl file as input")

    # Check output directory exists
    # if not os.path.isdir(args.output):
    #     parser.error("ERROR: Output directory not found")

    return args


# Perform analysis of alphafold results
def main():
    args = cmd_lineparser()

    # if pdb structure provided and generates PyMol session with pLDDT coloured
    # if args.pdb is not None:
    #     print("\n Visualising pLDDT data...\n")
    #     protein_painter(args.pdb, args.output)

    # # if no pdb structure provided skips process
    # elif args.pdb is None:
    #     print("\n no pdb file provided, skipping pLDDT data visualisation...\n")

    # for multiple pkl files, pick best model from each design sample

    paths = sorted(pathlib.Path(args.pkl_dir).rglob("*.pkl"))
    if len(paths) == 0:
        print(
            " no pickle file provided, skipping predicted aligned error visualisation...\n"
        )
        exit(0)

    if not args.overlapped:
        for path in paths:
            print(" plotting predicted aligned error...")
            pae_plotter(path, args.output)
    else:
        data = []
        avg_plddts = []

        for path in paths:
            print(" plotting predicted aligned error...")
            overlapped_data_parser(path, args.output, data, avg_plddts)

        X = [i for i in range(data[0].shape[0])]
        plt.figure(figsize=[8 * 1, 6])
        plt.subplot(1, 1, 1)
        for i in range(len(data)):
            plt.plot(X, data[i], label=f"plddt_{i}")
        plt.title(
            f"{os.path.splitext(pathlib.Path(args.pkl_dir).parent.name)[0]} Predicted LDDT"
        )
        plt.xlabel("Residue")
        plt.ylabel("pLDDT")
        plt.annotate(
            f"Average pLDDT: {np.array(avg_plddts).mean():.2f}",
            (0, 0),
            (0, -20),
            xycoords="axes fraction",
            textcoords="offset points",
            va="top",
        )

        plddt_output = f"{args.output}/{os.path.splitext(pathlib.Path(args.pkl_dir).parent.name)[0]}_plddt+overlapped.png"
        plt.savefig(
            plddt_output, dpi=300, bbox_inches="tight"
        )  # save plot to output directory

        plt.close()

    # Use pkl analysis only
    # if pkl structure provided, generate predicted aligned error plot
    # if args.pkl is not None:
    #     print(" plotting predicted aligned error...")
    #     pae_plotter(args.pdb, args.pkl, args.output)

    # # if no pkl file provided skips process
    # elif args.pkl is None:
    #     print(
    #         " no pickle file provided, skipping predicted aligned error visualisation...\n"
    #     )

    print(" all processes finished, shutting down...\n")


# Run analysis
if __name__ == "__main__":
    main()

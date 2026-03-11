"""SciPy Optimize Simulator."""

# Standard Library Imports
import json
import pathlib
import sys
from functools import cache

# Third-Party Imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import OptimizeResult, differential_evolution

HERE = pathlib.Path(__file__).parent
if str(HERE.parent) not in sys.path:
    sys.path.append(str(HERE.parent))

# Local Imports
import chopper_plot


def generate_samples(datapath: pathlib.Path, iterations: int) -> dict:
    """Generate samples."""
    static_name = next(p.name for p in datapath.glob("*stand_still.csv"))
    samples = {}
    datapoint = []
    empty_error = 0
    with open(datapath / static_name) as f:
        static_data = chopper_plot.calc_static_magnitude(f)

    for p in datapath.glob("*.csv"):
        if not p.is_file() or not p.name.endswith("__.csv"):
            continue

        _curr, tbl, toff, hstrt, hend, _tpfd, _speed, _freq, iteration = (
            p.name.split("__")[1].split("_")
        )
        datapoint_name = (
            # f"current={curr}_"
            f"tbl={tbl}_toff={toff}_hstrt={hstrt}_hend={hend}"
            # f"tpfd={tpfd}_"
            # f"speed={float(speed) / 100:.2f}"
            # f"freq={float(freq) / 1000:.2f}kHz"
        )
        with open(p) as file:
            md_magnitude = chopper_plot.calc_magnitude(file, static_data)
            try:
                md_magnitude = chopper_plot.calc_magnitude(file, static_data)
                datapoint.append(md_magnitude)
                if int(iteration) == iterations:
                    samples[datapoint_name] = np.mean(datapoint, axis=0)
                    datapoint.clear()
            except Exception:
                datapoint.clear()
                empty_error += 1
                samples[datapoint_name] = 0

        samples[datapoint_name] = md_magnitude

    return samples


def cache_samples() -> None:
    """Cache samples to a JSON file."""
    args = chopper_plot.parse_arguments()
    # driver = args.get("driver")
    iterations = args.get("iterations")
    # sense_resistor = round(float(args.get("sense_resistor")), 3)
    # data_folder = pathlib.Path(sys.argv[-1]).expanduser()
    datapath = pathlib.Path(args.get("datapath")).expanduser()

    cache_path = datapath.parent / "cache" / "cached_data.json"

    if not datapath.is_dir():
        raise RuntimeError(f"{datapath} is not a directory!")

    samples = generate_samples(datapath=datapath, iterations=iterations)
    with open(cache_path, "w") as f:
        json.dump(samples, f, indent=4)


@cache
def get_json_data() -> dict:
    """Get JSON data from the cached file."""
    json_data_path = (
        HERE / "../tests/data/sv08_x_axis_20260118_031251/cache/cached_data.json"
    )
    with open(json_data_path) as f:
        return json.load(f)


def sort_json_data() -> None:
    """Sort JSON data and save to a file."""
    data: dict = get_json_data()

    sorted_json_data_path = (
        HERE / "../tests/data/sv08_x_axis_20260118_031251/cache/cached_data_sorted.json"
    )
    with open(sorted_json_data_path, "w") as f:
        json.dump(
            {x: data[x] for x in sorted(data, key=lambda x: data[x])}, f, indent=4
        )


def simulate_measured_vibrations(tbl, toff, hstrt, hend) -> float:
    """Simulate measured vibrations based on parameters.

    Returns:
        float: The simulated measured vibrations.
    """
    json_data = get_json_data()
    key = f"tbl={tbl}_toff={toff}_hstrt={hstrt}_hend={hend}"
    return json_data.get(key, 9999999)


iterations = 0


def objective_function(params) -> float:
    """Objective function for optimization.

    Returns:
        float: The simulated measured vibrations.
    """
    global iterations
    iterations += 1
    _, tbl, toff, hstrt, hend, _ = [round(p) for p in params]
    # tbl, toff, hstrt, hend = [round(p) for p in params]
    return simulate_measured_vibrations(tbl, toff, hstrt, hend)


def run_optimization() -> None:
    """Run optimization using SciPy differential evolution."""
    bounds = [
        (1100, 1100),  # Current
        (0, 3),  # TBL
        (1, 8),  # TOFF
        (0, 7),  # HSTRT
        (2, 15),  # HEND
        (-1, -1),  # TPFD
    ]
    result: OptimizeResult = differential_evolution(
        objective_function,
        bounds,
        init="sobol",
        strategy="best1bin",
        maxiter=10,
        popsize=5,  # Total evaluations = maxiter * popsize * N_params
        tol=0.1,
        mutation=(0.5, 1),
        recombination=0.7,
        polish=False,  # Polish uses local minimize, which we avoid for discrete
    )
    # result : OptimizeResult = dual_annealing(
    #     objective_function,
    #     bounds=bounds,
    #     maxiter=10,
    # )

    print("================================")
    print("Optimization Completed!\n")
    print("Algorithm        : differential_evolution")
    print(f"result.message   : {result.message}")
    print(f"result.nit       : {result.nit}")
    print(f"real num.of.iter : {iterations}")
    best_params = [round(p) for p in result.x]
    print(
        f"Best Score       : {result.fun:0.2f}\n\n"
        "Parameters\n"
        "----------\n"
        f"current = {best_params[0]}\n"
        f"tbl     = {best_params[1]}\n"
        f"toff    = {best_params[2]}\n"
        f"hstrt   = {best_params[3]}\n"
        f"hend    = {best_params[4]}\n"
        f"tpfd    = {best_params[5]}"
        # f"tbl={best_params[0]}, "
        # f"toff={best_params[1]}, "
        # f"hstrt={best_params[2]}, "
        # f"hend={best_params[3]} "
    )
    print("================================")


def plot_noise_heatmap() -> None:
    """Plot heatmap of noise magnitudes."""
    # 1. Load the data
    data = get_json_data()

    # 2. Parse the keys into a structured format
    rows = []
    for key, magnitude in data.items():
        # Parses "tbl=0_toff=2_hstrt=0_hend=5" into a dict
        parts = {p.split("=")[0]: int(p.split("=")[1]) for p in key.split("_")}
        parts["magnitude"] = magnitude
        rows.append(parts)

    df = pd.DataFrame(rows)

    # 3. Aggregate data
    # We group by toff and hend and take the mean magnitude.
    # (You could also use .min() to see the best possible result for each pair)
    for tbl in range(3 + 1):
        for hstrt in range(7 + 1):
            # tbl = 2
            # hstrt = 0
            pivot_df = (
                df[df["tbl"] == tbl][df["hstrt"] == hstrt]
                .groupby(["toff", "hend"])["magnitude"]
                .min()
                .unstack()
            )

            # 4. Create the plot
            plt.figure(figsize=(12, 8))
            sns.heatmap(
                pivot_df,
                annot=True,  # Show the actual noise values
                fmt=".0f",  # Round to nearest integer
                cmap="viridis_r",  # Reverse viridis: purple/blue is quiet, yellow is loud  # noqa: E501
                cbar_kws={"label": "Noise Magnitude"},
            )

            plt.title(
                f"Average Noise Magnitude vs TOFF and HEND (TBL={tbl} HSTRT={hstrt})"
            )
            plt.xlabel("HEND (Hysteresis End)")
            plt.ylabel("TOFF (Time Off)")
            plt.tight_layout()

            # Save the result
            output = f"noise_heatmap_tbl={tbl}_hstart={hstrt}.png"
            plt.savefig(output)
            print(f"Plot saved as {output}")


def plot_acceleration_data() -> None:
    """Plot raw acceleration data."""
    args = chopper_plot.parse_arguments()
    data_folder = pathlib.Path(args.get("datapath")).expanduser()

    for p in data_folder.glob("*.csv"):
        if not p.is_file() or not p.name.endswith("__.csv"):
            continue

        with open(p) as file:
            df = pd.read_csv(file)
            time_data = df.iloc[:, 0].to_numpy()
            accel_data = df.iloc[:, 1].to_numpy()

            plt.figure(figsize=(10, 6))
            plt.plot(time_data, accel_data, label="Acceleration")
            plt.title(f"Acceleration Data from {p.name}")
            plt.xlabel("Time (s)")
            plt.ylabel("Acceleration (m/s²)")
            plt.legend()
            plt.grid()
            plt.tight_layout()
            plt.show()
            break  # Plot only the first valid file for demonstration


if __name__ == "__main__":
    run_optimization()
    # sort_json_data()
    # plot_noise_heatmap()
    # plot_acceleration_data()

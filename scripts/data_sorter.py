import os
import sys
import pathlib


HERE = pathlib.Path(__file__).parent
if str(HERE.parent) not in sys.path:
    sys.path.append(str(HERE.parent))


import chopper_plot


def main():
    DATA_FOLDER = pathlib.Path(sys.argv[-1]).expanduser()
    if not DATA_FOLDER.is_dir():
        raise RuntimeError(f"{DATA_FOLDER} is not a directory!")

    static_name = next(p.name for p in DATA_FOLDER.glob("*stand_still.csv"))
    data = []
    with open(DATA_FOLDER / static_name) as f:
        static_data = chopper_plot.calc_static_magnitude(f)

    for p in DATA_FOLDER.glob("*.csv"):
        if not p.is_file() or not p.name.endswith("__.csv"):
            continue

        curr, tbl, toff, hstrt, hend, tpfd, speed, freq, iteration = p.name.split("__")[
            1
        ].split("_")
        with open(p) as file:
            md_magnitude = chopper_plot.calc_magnitude(file, static_data)

        data.append(
            (md_magnitude, curr, tbl, toff, hstrt, hend, tpfd, speed, freq, iteration)
        )

    data.sort(key=lambda x: x[0])

    print("Lowest 10 values")
    for i in range(10):
        md_magnitude, curr, tbl, toff, hstrt, hend, tpfd, speed, freq, iteration = data[
            i
        ]
        print(
            f"mag={md_magnitude:0.2f} curr={curr} tbl={tbl} toff={toff} "
            f"hstrt={hstrt} hend={hend} tpfd={tpfd} speed={speed} freq={freq} iter={iteration}"
        )

    print("Highest 10 values")
    for i in range(10):
        md_magnitude, curr, tbl, toff, hstrt, hend, tpfd, speed, freq, iteration = data[
            -i - 1
        ]
        print(
            f"mag={md_magnitude:0.2f} curr={curr} tbl={tbl} toff={toff} "
            f"hstrt={hstrt} hend={hend} tpfd={tpfd} speed={speed} freq={freq} iter={iteration}"
        )


if __name__ == "__main__":
    main()

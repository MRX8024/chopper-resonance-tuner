#!/usr/bin/env python3
# TMC drivers registers calibration tool (plotter)
#
# Copyright (C) 2024  Alexander Fedorov <altzbox@gmail.com>
# Copyright (C) 2024  Maksim Bolgov <maksim8024@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import os
#################################################################################################################
RESULTS_FOLDER = os.path.expanduser('~/printer_data/config/adxl_results/chopper_magnitude')
DATA_FOLDER = '/tmp'
#################################################################################################################

import sys
import csv
import numpy as np
from tqdm import tqdm
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

FCLK = 12 # MHz
CUTOFF_RANGE = 5


def cleaner():
    os.system('rm -f /tmp/*.csv')
    sys.exit(0)


def check_export_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            print(f'Error generate path {path}: {e}')


def parse_arguments():
    args = sys.argv[1:]
    parsed_args = {}
    for arg in args:
        name, value = arg.split('=')
        parsed_args[name] = int(value) if value.isdigit() else value
    return parsed_args


def calculate_static_measures(file_path):
    with open(file_path, 'r') as file:
        static = np.array([[float(row["accel_x"]),
                            float(row["accel_y"]),
                            float(row["accel_z"])] for row in csv.DictReader(file)])
        return static.mean(axis=0)


def main():
    print('Magnitude graphs generation...')
    args = parse_arguments()
    accelerometer = args.get('accel_chip')
    driver = args.get('driver')
    iterations = args.get('iterations')
    sense_resistor = round(float(args.get('sense_resistor')), 3)
    current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_files, target_file = [], ''
    for f in os.listdir(DATA_FOLDER):
        if f.endswith('.csv'):
            if f.endswith('-stand_still.csv'):
                target_file = f
            else:
                csv_files.append(f)
    csv_files = sorted(csv_files)
    parameters_list = []

    for current in range(args.get('current_min_ma'), args.get('current_max_ma') + 1, args.get('current_change_step')):
        for tbl in range(args.get('tbl_min'), args.get('tbl_max') + 1):
            for toff in range(args.get('toff_min'), args.get('toff_max') + 1):
                for hstrt in range(args.get('hstrt_min'), args.get('hstrt_max') + 1):
                    for hend in range(args.get('hend_min'), args.get('hend_max') + 1):
                        if hstrt + hend <= args.get('hstrt_hend_max'):
                            for tpfd in range(args.get('tpfd_min'), args.get('tpfd_max') + 1):
                                for speed in range(args.get('min_speed'), args.get('max_speed') + 1,
                                                   args.get('speed_change_step')):
                                    for _ in range(iterations):
                                        freq = float(round(1/(2*(12+32*toff)*1/(1000000*FCLK)+2*1/(1000000*FCLK)*16*(1.5**tbl))/1000, 1))
                                        parameters = (f'current={current}_tbl={tbl}_toff={toff}_hstrt={hstrt}'
                                                      f'_hend={hend}_tpfd={tpfd}_speed={speed/100}_freq={freq}kHz')
                                        parameters_list.append(parameters)

    # Check input count csvs
    if len(csv_files) != len(parameters_list):
        print(f'Warning!!! The number of CSV files ({len(csv_files)}) does not match the expected number '
              f'of combinations based on the provided parameters ({len(parameters_list)})')
        print('Please check your input and try again')
        sys.exit(1)

    # Binding magnitude on registers
    results = []
    static = calculate_static_measures(os.path.join(DATA_FOLDER, target_file))
    datapoint = []
    for csv_file, parameters in tqdm(zip(csv_files, parameters_list), desc='Processing CSV files', total=len(csv_files)):
        file_path = os.path.join(DATA_FOLDER, csv_file)
        with open(file_path, 'r') as file:
            data = np.array([[float(row["accel_x"]),
                              float(row["accel_y"]),
                              float(row["accel_z"])] for row in csv.DictReader(file)]) - static

        trim_size = len(data) // CUTOFF_RANGE
        data = data[trim_size:-trim_size]
        md_magnitude = np.median([np.linalg.norm(row) for row in data])
        datapoint.append(md_magnitude)

        if len(datapoint) == iterations:
            toff = int(parameters.split('_')[2].split('=')[1])
            results.append({'file_name': csv_file, 'median magnitude': np.mean(datapoint),
                            'parameters': parameters, 'color': toff})
            datapoint = []

    # Group result in csv
    # results_csv_path = os.path.join(RESULTS_FOLDER,f'median_magnitudes_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.csv')
    # with open(results_csv_path, 'w', newline='') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=['file_name', 'median magnitude', 'parameters'])
    #     writer.writeheader()
    #     for result in results:
    #         writer.writerow({key: value for key, value in result.items() if key != 'color'})

    # Graphs generation
    colors = ['', '#2F4F4F', '#12B57F', '#9DB512', '#DF8816', '#1297B5', '#5912B5', '#B51284', '#127D0C']
    params = [results, sorted(results, key=lambda x: x['median magnitude'])]
    names = ['', 'sorted_']
    for param, name in zip(params, names):
        fig = go.Figure()
        for entry in param:
            fig.add_trace(go.Bar(x=[entry['median magnitude']], y=[entry['parameters']],
                                 marker_color=colors[entry['color'] if entry['color'] <= 8 else entry['color'] - 8],
                                 orientation='h', showlegend=False))
        fig.update_layout(title='Median Magnitude vs Parameters', xaxis_title='Median Magnitude',
                          yaxis_title='Parameters', coloraxis_showscale=True)
        plot_html_path = os.path.join(RESULTS_FOLDER, f'{name}interactive_plot_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.html')
        pio.write_html(fig, plot_html_path, auto_open=False)
        if parameters_list[0].split('_')[6].split('=')[1] != parameters_list[1].split('_')[6].split('=')[1]:
            break

    # Export Info
    try: print(f'Access to interactive plot at: {"/".join(plot_html_path.split("/")[:-1] + [plot_html_path.split(names[1])[1]])}')
    except IndexError: print(f'Access to interactive plot at: {plot_html_path}')


if __name__ == '__main__':
    if sys.argv[1] == 'cleaner':
        cleaner()
    check_export_path(RESULTS_FOLDER)
    main()

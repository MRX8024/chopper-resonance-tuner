#!/usr/bin/env python3
####################################
###### CHOPPER REGISTERS TUNE ######
####################################
# Written by @altzbox @mrx8024
# @version: 1.2

# CHANGELOG:
#   v1.0: first version of the script, data sort, collection, graph generation
#   v1.1: add support any accelerometers, find vibr mode, smart work area, auto-install,
#   auto-import export, out nametags(acc+drv+sr+date), cleaner data
#   v1.2: rethinking motion calculation & measurements

# These changes describe the operation of the entire system, not a specific file.

import os
#################################################################################################################
# RESULTS_FOLDER = 'Z:/chopper-resonance-tuner/pythonProject/adxl_results/chopper_magnitude'
# DATA_FOLDER = 'Z:/chopper-resonance-tuner/pythonProject'
RESULTS_FOLDER = os.path.expanduser('~/printer_data/config/adxl_results/chopper_magnitude')
DATA_FOLDER = '/tmp'
#################################################################################################################

import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
import plotly.express as px
import plotly.offline as pyo
from natsort import natsorted
from datetime import datetime

def cleaner():
    os.system('rm -f /tmp/*.csv')
    sys.exit(0)

if __name__ == "__main__":
    if sys.argv[1] == 'cleaner':
        cleaner()

print('Magnitude graphs generation...')

def check_export_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            print(f"Error generate path {path}: {e}")

if __name__ == "__main__":
    check_export_path(RESULTS_FOLDER)

def parse_arguments():
    args = sys.argv[1:]
    parsed_args = {}
    for arg in args:
        name, value = arg.split('=')
        parsed_args[name] = int(value) if value.isdigit() else value
    return parsed_args

def calculate_static_measures(file_path, trim_percentage=0.2):
    data = pd.read_csv(file_path, delimiter=',')
    trim_size = int(trim_percentage * len(data))
    trimmed_data = data.iloc[trim_size:-trim_size]
    static_median_x = trimmed_data['accel_x'].median()
    static_median_y = trimmed_data['accel_y'].median()
    static_median_z = trimmed_data['accel_z'].median()
    return static_median_x, static_median_y, static_median_z

def main():
    args = parse_arguments()
    accelerometer = args.get('accel_chip')
    driver = args.get('driver')
    sense_resistor = round(float(args.get('sense_resistor')), 3)
    current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_files, target_file = [], ""
    for f in os.listdir(DATA_FOLDER):
        if f.endswith(".csv"):
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
                                for speed in range(args.get('min_speed'), args.get('max_speed') + 1):
                                    for _ in range(args.get('iterations')):
                                        parameters = f"current={current}_tbl={tbl}_toff={toff}_hstrt={hstrt}_hend={hend}_tpfd={tpfd}_speed={speed}"
                                        parameters_list.append(parameters)

    if len(csv_files) != len(parameters_list):
        print(f"Warning: The number of CSV files ({len(csv_files)}) does not match the expected number of combinations based on the provided parameters ({len(parameters_list)}).")
        print("Please check your input and try again.")
        return

    results = []
    static_median_x, static_median_y, static_median_z = calculate_static_measures(os.path.join(DATA_FOLDER, target_file))

    for csv_file, parameters in tqdm(zip(csv_files, parameters_list), desc='Processing CSV files', total=len(csv_files)):
        file_path = os.path.join(DATA_FOLDER, csv_file)
        data = pd.read_csv(file_path, delimiter=',')
        data['accel_x'] -= static_median_x
        data['accel_y'] -= static_median_y
        data['accel_z'] -= static_median_z
        trim_size = int(0.2 * len(data))
        data = data.iloc[trim_size:-trim_size]
        data['magnitude'] = np.sqrt(data['accel_x']**2 + data['accel_y']**2 + data['accel_z']**2)
        median_magnitude = data['magnitude'].median()
        current_toff = int(parameters.split('_')[2].split('=')[1])
        results.append({'file_name': csv_file, 'median_magnitude': median_magnitude, 'parameters': parameters, 'toff': current_toff})

    results_df = pd.DataFrame(results)
    # results_csv_path = os.path.join(RESULTS_FOLDER,f'median_magnitudes_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.csv')
    # results_df.to_csv(results_csv_path, index=False)

    grouped_results = results_df.groupby('parameters')['median_magnitude'].mean().reset_index()
    sorted_indices = natsorted(range(len(grouped_results)), key=lambda i: grouped_results['parameters'].iloc[i])
    grouped_results = grouped_results.iloc[sorted_indices]

    # Add a 'toff' column based on the 'parameters' column
    grouped_results['toff'] = grouped_results['parameters'].apply(lambda x: int(x.split('_')[2].split('=')[1]))

    # grouped_results_csv_path = os.path.join(RESULTS_FOLDER,f'grouped_median_magnitudes_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.csv')
    # grouped_results.to_csv(grouped_results_csv_path, index=False)
    # print(f'Saved grouped results to: {grouped_results_csv_path}')

    toff_colors = ['#12B57F', '#9DB512', '#DF8816', '#1297B5', '#5912B5', '#B51284', '#127D0C', '#DC143C', '#2F4F4F']

    fig = px.bar(grouped_results, x='median_magnitude', y='parameters', color='toff', title='Median Magnitude vs. Parameters',
                 color_discrete_map={str(i): toff_colors[i] for i in range(9)},
                 color_continuous_scale=toff_colors)
    fig.update_layout(xaxis_title='Median Magnitude', yaxis_title='Parameters')
    fig.update_layout(coloraxis_showscale=False)
    plot_html_path = os.path.join(RESULTS_FOLDER,f'interactive_plot_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.html')
    pyo.plot(fig, filename=plot_html_path, auto_open=False)

    print(f'Access the interactive plot at: {plot_html_path}')



if __name__ == "__main__":
    main()

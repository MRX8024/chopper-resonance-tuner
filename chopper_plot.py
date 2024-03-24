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
# RESULTS_FOLDER = 'Z:/chopper-resonance-tuner/chopper-resonance-tuner/adxl_results/chopper_magnitude'
# DATA_FOLDER = 'Z:/chopper-resonance-tuner/chopper-resonance-tuner/tmp/fields'
RESULTS_FOLDER = os.path.expanduser('~/printer_data/config/adxl_results/chopper_magnitude')
DATA_FOLDER = '/tmp'
#################################################################################################################

import sys
import csv
import numpy as np
import plotly.express as px
import plotly.io as pio
from datetime import datetime

fclk = 12 # MHz

def cleaner():
    os.system('rm -f /tmp/*.csv')
    sys.exit(0)

if __name__ == '__main__':
    if sys.argv[1] == 'cleaner':
        cleaner()

print('Magnitude graphs generation...')

def check_export_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            print(f'Error generate path {path}: {e}')

if __name__ == '__main__':
    check_export_path(RESULTS_FOLDER)

def parse_arguments():
    args = sys.argv[1:]
    parsed_args = {}
    for arg in args:
        name, value = arg.split('=')
        parsed_args[name] = int(value) if value.isdigit() else value
    return parsed_args

def calculate_static_measures(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        static = [0, 0, 0, 0]
        for row in reader:
            static[0] += float(row['accel_x'])
            static[1] += float(row['accel_y'])
            static[2] += float(row['accel_z'])
            static[3] += 1
        for i in range(3):
            static[i] /= static[3]
        return static

def main():
    args = parse_arguments()
    accelerometer = args.get('accel_chip')
    driver = args.get('driver')
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

    # Create a list of parameters
    for current in range(args.get('current_min_ma'), args.get('current_max_ma') + 1, args.get('current_change_step')):
        for tbl in range(args.get('tbl_min'), args.get('tbl_max') + 1):
            for toff in range(args.get('toff_min'), args.get('toff_max') + 1):
                for hstrt in range(args.get('hstrt_min'), args.get('hstrt_max') + 1):
                    for hend in range(args.get('hend_min'), args.get('hend_max') + 1):
                        if hstrt + hend <= args.get('hstrt_hend_max'):
                            for tpfd in range(args.get('tpfd_min'), args.get('tpfd_max') + 1):
                                for speed in range(args.get('min_speed'), args.get('max_speed') + 1):
                                    for _ in range(args.get('iterations')):
                                        freq = float(round(1/(2*(12+32*toff)*1/(1000000*fclk)+2*1/(1000000*fclk)*16*(1.5**tbl))/1000, 1))
                                        parameters = f'current={current}_tbl={tbl}_toff={toff}_hstrt={hstrt}_hend={hend}_tpfd={tpfd}_speed={speed}_freq={freq}kHz'
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
    for csv_file, parameters in zip(csv_files, parameters_list):
        file_path = os.path.join(DATA_FOLDER, csv_file)
        with open(file_path, 'r') as file:
            data = list(csv.DictReader(file))
        for row in data:
            row['accel_x'] = float(row['accel_x']) - static[0]
            row['accel_y'] = float(row['accel_y']) - static[1]
            row['accel_z'] = float(row['accel_z']) - static[2]
        data_length = len(data)
        trim_size = int(0.2 * data_length)
        data = data[trim_size:-trim_size]
        magnitudes = [np.sqrt(float(row['accel_x']) ** 2 + float(row['accel_y']) ** 2 + float(row['accel_z']) ** 2) for row in data]
        md_magnitude = np.median(magnitudes)
        toff = int(parameters.split('_')[2].split('=')[1])
        results.append({'file_name': csv_file, 'median magnitude': md_magnitude, 'parameters': parameters, 'color': toff})

    # Group result in csv
    results_csv_path = os.path.join(RESULTS_FOLDER,f'median_magnitudes_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.csv')
    with open(results_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['file_name', 'median magnitude', 'parameters', 'color'])
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    # Graphs generation
    params = [results, sorted(results, key=lambda x: x['median magnitude'])]
    names = ['', 'sorted_']
    for param, name in zip(params, names):
        colors = ['#12B57F', '#9DB512', '#DF8816', '#1297B5', '#5912B5', '#B51284', '#127D0C', '#DC143C', '#2F4F4F']
        fig = px.bar(param, x='median magnitude', y='parameters', title='Median Magnitude vs Parameters',
         color='color', color_continuous_scale=colors, color_continuous_midpoint=None, orientation='h')
        fig.update_layout(xaxis_title='Median Magnitude', yaxis_title='Parameters', coloraxis_showscale=False)
        fig.update_traces(textposition='outside')
        plot_html_path = os.path.join(RESULTS_FOLDER, f'{name}interactive_plot_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.html')
        pio.write_html(fig, plot_html_path, auto_open=False)
    print(f'Access to interactive plot at: {"/".join(plot_html_path.split("/")[:-1] + [plot_html_path.split(names[1])[1]])}')

if __name__ == '__main__':
    main()
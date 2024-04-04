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
RESULTS_FOLDER = os.path.expanduser('~/printer_data/config/adxl_results/chopper_magnitude')
DATA_FOLDER = '/tmp'
#################################################################################################################

import sys
import csv
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import time
from datetime import datetime
import serial

FCLK = 12                   # System clock frequency MHz
CUTOFF_RANGE = 5            # Data trim size
DELAY = 1.00                # Delay between checks csv in tmp in sec
OPEN_DELAY = 0.25           # Delay between open csv in sec
TIMER = 10.0                # Exit program time in sec
SAVE_RESULT_IN_CSV = False


def cleaner():
    os.system('rm -f /tmp/*.csv')


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
    print('Start tracking')
    args = parse_arguments()
    accelerometer = args.get('accel_chip')
    driver = args.get('driver')
    iterations = args.get('iterations')
    sense_resistor = round(float(args.get('sense_resistor')), 3)
    current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    params = []
    for current in range(args.get('current_min_ma'), args.get('current_max_ma') + 1, args.get('current_change_step')):
        for tbl in range(args.get('tbl_min'), args.get('tbl_max') + 1):
            for toff in range(args.get('toff_min'), args.get('toff_max') + 1):
                for hstrt in range(args.get('hstrt_min'), args.get('hstrt_max') + 1):
                    for hend in range(args.get('hend_min'), args.get('hend_max') + 1):
                        if hstrt + hend <= args.get('hstrt_hend_max'):
                            for tpfd in range(args.get('tpfd_min'), args.get('tpfd_max') + 1):
                                for speed in range(args.get('min_speed') * 100, args.get('max_speed') * 100 + 1,
                                                   args.get('speed_change_step')):
                                    for _ in range(iterations):
                                        freq = float(round(1/(2*(12+32*toff)*1/(1000000*FCLK)+2*1/(1000000*FCLK)*16*(1.5**tbl))/1000, 1))
                                        parameters = (f'current={current}_tbl={tbl}_toff={toff}_hstrt={hstrt}'
                                                      f'_hend={hend}_tpfd={tpfd}_speed={speed / 100}_freq={freq}kHz')
                                        params.append(parameters)

    klippy = serial.Serial(os.path.expanduser('~/printer_data/comms/klippy.serial'), 115200)
    running = True
    datapoint = []
    results = []
    params_line = 0
    timer = 0
    while running:
        time.sleep(DELAY)
        if timer / DELAY > 2:
            print(f'Wait new file {round(timer * DELAY)} sec')
        timer += 1
        for f in os.listdir(DATA_FOLDER):
            if f.endswith('stand_still.csv'):
                timer = 0
                time.sleep(OPEN_DELAY)
                static = calculate_static_measures(os.path.join(DATA_FOLDER, f))
                print('Calculated static measures')
            elif f.endswith('.csv'):
                timer = 0
                time.sleep(OPEN_DELAY)
                print('Receiving csv')
                file_path = os.path.join(DATA_FOLDER, f)
                with open(file_path, 'r') as csv_file:
                    data = np.array([[float(row["accel_x"]),
                                        float(row["accel_y"]),
                                        float(row["accel_z"])] for row in csv.DictReader(csv_file)]) - static

                    trim_size = len(data) // CUTOFF_RANGE
                    data = data[trim_size:-trim_size]
                    md_magnitude = np.median([np.linalg.norm(row) for row in data])
                    datapoint.append(md_magnitude)
                    if len(datapoint) == iterations:
                        toff = int(params[params_line].split('_')[2].split('=')[1])
                        results.append({'parameters': params[params_line], 'median magnitude': np.mean(datapoint), 'color': toff})
                        datapoint = []
                        params_line += iterations
                        if params_line == len(params):
                            print('Last csv received, launching plotter')
                            running = False
            elif timer >= TIMER / DELAY:
                print('TIMER OUT')
                klippy.write(f'RESPOND TYPE=error MSG="WARNING!!! TIMER OUT" \n'.encode('utf-8'))
                raise
            else:
                continue
            cleaner()
            break

    # Group result in csv
    if SAVE_RESULT_IN_CSV:
        results_csv_path = os.path.join(RESULTS_FOLDER,f'median_magnitudes_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.csv')
        with open(results_csv_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['median magnitude', 'parameters'])
            writer.writeheader()
            for result in results:
                writer.writerow({key: value for key, value in result.items() if key != 'color'})

    # Graphs generation
    print('Magnitude graphs generation...')
    klippy.write(f'M118 Magnitude graphs generation... \r\n'.encode('utf-8'))
    colors = ['', '#2F4F4F', '#12B57F', '#9DB512', '#DF8816', '#1297B5', '#5912B5', '#B51284', '#127D0C']
    lists = [results, sorted(results, key=lambda x: x['median magnitude'])]
    names = ['', 'sorted_']
    for param, name in zip(lists, names):
        fig = go.Figure()
        for entry in param:
            fig.add_trace(go.Bar(x=[entry['median magnitude']], y=[entry['parameters']],
                                 marker_color=colors[entry['color'] if entry['color'] <= 8 else entry['color'] - 8],
                                 orientation='h', showlegend=False))
        fig.update_layout(title='Median Magnitude vs Parameters', xaxis_title='Median Magnitude',
                          yaxis_title='Parameters', coloraxis_showscale=True)
        plot_html_path = os.path.join(RESULTS_FOLDER, f'{name}interactive_plot_{accelerometer}_tmc{driver}_{sense_resistor}_{current_date}.html')
        pio.write_html(fig, plot_html_path, auto_open=False)
        if params[0].split('_')[6].split('=')[1] != params[1].split('_')[6].split('=')[1]:
            break

    # Export Info
    try:
        print(f'Access to interactive plot at: {"/".join(plot_html_path.split("/")[:-1] + [plot_html_path.split(names[1])[1]])}')
        klippy.write(f'M118 Access to interactive plot at: {"/".join(plot_html_path.split("/")[:-1] + [plot_html_path.split(names[1])[1]])} \r\n'.encode('utf-8'))
    except IndexError:
        print(f'Access to interactive plot at: {plot_html_path}')
        klippy.write(f'M118 Access to interactive plot at: {plot_html_path} \r\n'.encode('utf-8'))


if __name__ == '__main__':
        if sys.argv[1] == 'cleaner':
            cleaner()
        else:
            try:
                check_export_path(RESULTS_FOLDER)
                main()
            except:
                klippy = serial.Serial(os.path.expanduser('~/printer_data/comms/klippy.serial'), 115200)
                klippy.write('RESPOND TYPE=error MSG="WARNING!!! FATAL ERROR IN PLOTTER" \n'.encode('utf-8'))
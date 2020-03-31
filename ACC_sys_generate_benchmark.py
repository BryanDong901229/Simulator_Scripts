import argparse


def write_files_general_case(metrics_name, operations, metrics_value, file_name, scenario_file_directory, out_file_directory):
    out_file = open(out_file_directory + 'benchmark_' + file_name + '.prototxt', 'w')
    out_file.write('scenario_file : "' + scenario_file_directory + file_name + '.prototxt"\n\n')
    out_file.write('car_model {\n\
        type : TRUCK_SIM\n}\n')

    if len(operations) != len(metrics_value):
        raise Exception('invalid metrics in line:' + file_name)

    out_file.write('expectations {\n\
        description : "ACC system E2E metrics"\n\
        timeline {\n\
            start {\n\
                type : SIMULATION_START\n\
            }\n\
            end  {\n\
                type : SIMULATION_END\n\
            }\n\
        }\n\n')
    for k in range(len(metrics_value)):
        if metrics_value[k] == 'nan':
            continue
        # print(metrics_name[k], operations[k], metrics_value[k])
        metric_type = 'double_value'
        #print('op is : ' + metrics_name[k])
        if metrics_name[k] == 'NUM_COLLISION':
            metric_type = 'int_value'
        out_file.write('metrics {\n\
            metric : ' + metrics_name[k] + '\n\
            op : ' + operations[k] + '\n' +
            '            ' + metric_type + ': ' + metrics_value[k] + '\n\
        }\n\
    \n\
    ')
    out_file.write('}')
    out_file.close()
    print('written: ' + out_file_directory + 'benchmark_' + file_name + '.prototxt')
    return


def write_files_lane_change(metrics_name, operations, metrics_value, file_name, scenario_file_directory, out_file_directory):
    dict_of_metrics = dict(zip(metrics_name, metrics_value))
    dict_of_metrics_op = dict(zip(metrics_name, operations))
    left_indicator = dict_of_metrics['NUM_LEFT_LANE_CHANGE']
    right_indicator = dict_of_metrics['NUM_RIGHT_LANE_CHANGE']
    # print(left_indicator, right_indicator)

    if left_indicator != 'nan' and right_indicator == 'nan':
        direction_flag = 'left'
    else:
        if right_indicator != 'nan' and left_indicator == 'nan':
            direction_flag = 'right'
        else:
            raise Exception('no lane change metrics or wrongly defined')

    # open a file and begin to write
    out_file = open(out_file_directory + 'benchmark_' + file_name + '.prototxt', 'w')
    out_file.write('scenario_file : "' + scenario_file_directory + file_name + '.prototxt"\n\n')
    out_file.write('car_model {\n\
    type : RNN_MODEL\n\
    config_file : "/opt/plusai/var/control/mpc/conf/rnn_car_model.prototxt"\n}\n\n')

    if len(operations) != len(metrics_value):
        raise Exception('invalid metrics in line:' + file_name)

    # write general expectations
    out_file.write('expectations {\n\
    description : "need to make a ' + direction_flag + ' lane change"\n\
    timeline {\n\
        start {\n\
            type : SIMULATION_START\n\
        }\n\
        end  {\n\
            type : SIMULATION_END\n\
        }\n\
    }\n\n')

    # add the lane change requirement
    if direction_flag == 'left':
        lane_change_metric = 'NUM_LEFT_LANE_CHANGE'
    else:
        if direction_flag == 'right':
            lane_change_metric = 'NUM_RIGHT_LANE_CHANGE'
        else:
            raise Exception('not indicate lane change direction')

    lane_change_operation = dict_of_metrics_op[lane_change_metric]
    lane_change_value = dict_of_metrics[lane_change_metric]

    # add collision requirement
    collision_metric = 'NUM_COLLISION'
    collision_operation = dict_of_metrics_op[collision_metric]
    if dict_of_metrics[collision_metric] != 'nan':
        collision_value = dict_of_metrics[collision_metric]

    out_file.write('    #made exactly one ' + direction_flag + ' lane change\n')
    out_file.write('    metrics {\n\
        metric : ' + lane_change_metric + '\n\
        op : ' + lane_change_operation + '\n\
        value : ' + lane_change_value + '\n\
    }\n\n')

    out_file.write('    #other general metrics\n')
    for k in range(len(metrics_value)):
        if metrics_value[k] == 'nan' or metrics_name[k] == 'NUM_COLLISION' or\
                metrics_name[k] == 'NUM_LEFT_LANE_CHANGE' or metrics_name[k] == 'NUM_RIGHT_LANE_CHANGE':
            continue
        # print(metrics_name[k], operations[k], metrics_value[k])
        out_file.write('    metrics {\n\
        metric : ' + metrics_name[k] + '\n\
        op : ' + operations[k] + '\n\
        value : ' + metrics_value[k] + '\n\
        }\n\n')
    out_file.write('}\n\n')

    # write lane change timeline expectations
    out_file.write('expectations {\n\
    description : "collision free before the lane change is finised. After the lane change is finished, other cars may hit from behind, that is fine."\n\
    timeline {\n\
        start {\n\
            type : SIMULATION_START\n\
        }\n\
        end {\n\
            type : LEFT_LANE_CHANGE_END  #this is the lane change attempt, i.e. the first sequence of lane change trajectories\n\
            index : 1  # the lane change should be made in this first attempt.\n\
        }\n\
    }\n\n\
    #confirm the lane change is made in the first attempt\n\
    metrics {\n\
        metric : ' + lane_change_metric + '\n\
        op : ' + lane_change_operation + '\n\
        value : ' + lane_change_value + '\n\
    }\n\n\
    #no collision during this period\n\
    metrics {\n\
        metric : ' + collision_metric + '\n\
        op : ' + collision_operation + '\n\
        value : ' + collision_value + '\n\
    }\n\n\
}\n')

    out_file.close()
    print('written: ' + out_file_directory + 'benchmark_' + file_name + '.prototxt'+'\t' + direction_flag + ' lane chane')
    return


def generate_benchmark(benchmark_csv):
    with open(benchmark_csv) as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        lines = [x.split(',') for x in lines]
        n = len(lines)

        if n > 2:
            # read metrics from 1st line
            if lines[0][0]== 'metrics':
                metrics_name = lines[0][1:]
                print('metrics_name:', metrics_name)

            # read operations from 2nd line
            if lines[1][0] == 'operations':
                operations = lines[1][1:]
                print('operations:', operations)
            if len(metrics_name) != len(operations):
                raise Exception ('invalid metrics definition!')

            # read metrics from left lines, then create test benchmark files
            for i in range(2,n):
                # print(lines[i])
                file_name = lines[i][0]
                metrics_value = lines[i][1:]

                if 'acc' in file_name:
                    scenario_file_directory = "../../../../data/L4E/ACC/SYS/"
                    out_file_directory = "L4E/ACC/SYS/"
                    write_files_general_case(metrics_name, operations, metrics_value, file_name, scenario_file_directory,out_file_directory)

                else:
                    print('unknown file name')
                    continue

    return


def main():
    parser = argparse.ArgumentParser('Generate evaluation metrics from csv file')
    parser.add_argument('benchmark_csv', default="test_benchmark_metrics.csv", type=str, help='path to CSV file')
    args = parser.parse_args()
    generate_benchmark(args.benchmark_csv)


if __name__ == '__main__':
    main()

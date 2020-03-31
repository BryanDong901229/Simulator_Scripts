#!/usr/bin/python
import shutil
file_name_list = []
def objFileName():
    object_name_list = "/home/bryan/Workspace/simulator/scenario/test/data/L4E/ACC/scenario_list.txt"
    for i in open(object_name_list, 'r'):
        file_name_list.append(i.replace('\n', ''))
    return file_name_list
 
def copy_img():
    srs_file = "/home/bryan/Workspace/simulator/scenario/test/data/L4E/ACC/SYS/new/acc_left_cut_in_001_80kph_60m_80kph_to_80kph_5s_80kph_to_80kph_5s.prototxt"
    path = "/home/bryan/Workspace/simulator/scenario/test/data/L4E/ACC/SYS/new"
    for i in objFileName():
        new_file_name = i
        shutil.copy(srs_file, path + '/' + new_file_name + '.prototxt')
 
if __name__ == '__main__':
    copy_img()

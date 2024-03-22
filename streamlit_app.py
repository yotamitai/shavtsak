from collections import defaultdict
from pathlib import Path
from io import StringIO
import streamlit as st
import altair as alt
import pandas as pd
import random


class Mission:
    def __init__(self, name, duration, req_workers):
        self.name = name
        self.duration = duration
        self.req_workers = req_workers
        self.workers = []

    def clear(self):
      self.workers = []

def get_base_shifts_and_missions():
    shifts = defaultdict(list)
    shifts[8] = [
            Mission("Siur 51", 8, ['M', 'W', 'W', 'W']),
            Mission("Machsom", 8, ['M', 'W', 'W', 'W']),
            Mission("ShinGimel 8", 4, ['W']),]
    shifts[16] = [
            Mission("Siur 51", 8, ['M', 'W', 'W', 'W']),
            Mission("Machsom", 8, ['M', 'W', 'W', 'W']),
            Mission("ShinGimel 16", 4, ['W'])]
    shifts[24] = [
            Mission("Siur 51", 8, ['M', 'W', 'W', 'W']),
            Mission("Machsom", 8, ['M', 'W', 'W', 'W']),
            Mission("ShinGimel 0", 4, ['W'])]
    shifts[12] = [Mission("ShinGimel 12", 4, ['W'])]
    shifts[20] = [Mission("ShinGimel 20", 4, ['W'])]
    shifts[28] = [Mission("ShinGimel 4", 4, ['W'])]
    shifts[23] = [Mission("Carmel", 24, ['M', 'W', 'W', 'W'])]
    return shifts

def print_shavtsak(shavtsak):
  shift_set = set(shavtsak['shift'])
  for s in shift_set:
      st.write(f'{s%24:2}:00:')
      shift_df = shavtsak.loc[shavtsak['shift']==s]
      mission_set = set(shift_df['mission'])
      for m in mission_set:
          mission_df = shift_df.loc[shift_df['mission'] == m]
          st.write(f'\t{m}: {", ".join(mission_df.name.tolist())}')

def get_relevant_workers(df, mission, shift, role):
    df_relevant = df.query("available == 1 and hours_since_last_shift >= 8")
    df_relevant = added_preferences(df_relevant, mission, shift)
    df_relevant_role = df_relevant[df_relevant['roles'].str.contains(role)]
    sorted_df = df_relevant_role.sort_values(by='hours_since_last_shift', ascending=False)    
    return sorted_df.name.tolist()

def added_preferences(df, mission, shift):
    """add any mission preferences here"""
    if shift < 16:
        df = df.query("last_mission != 'Home'")

    # if mission == 'Machsom':
    #     df = df.query("last_mission != 'Machsom' or hours_since_last_shift >= 16")
    return df  




# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Shavtsak',
    page_icon='📊', # This is an emoji shortcode. Could be a URL too.
)

# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
'''
# 📊 Shavtsak

**Welcome to the Shavtsak Generator!**
'''

st.info('Upload the worker spreadsheet:')

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file)
    df.to_csv("temp.csv", index=False, encoding='utf-8-sig')
    shifts = get_base_shifts_and_missions()

if st.button("Reset Shifts & Missions"):
    shifts = get_base_shifts_and_missions()
    df = pd.read_csv('temp.csv')
    st.write('Shifts and Missions have been reset to the basics (עוגן)')

st.info("Optional - add a mission")
name = st.text_input('Mission Name')
start_time = st.number_input('Start time',min_value=8,max_value=31, value=None, placeholder="Type a number...")
duration = st.number_input('Duration', min_value=0,value=None, placeholder="Type a number...")
mefakdim = st.number_input('Number of Mefakdim', min_value=0, value=0, placeholder="Type a number...")
haialim = st.number_input('Number of Haialim', min_value=0, value=0, placeholder="Type a number...")


if st.button("Add Mission"):
    if not name or not start_time or not duration or not (mefakdim or haialim):
        st.info('***** Missing mission info - mission not added *****')
        # st.write('Missing mission info - mission not added')
    else:
        req_workers = ['M']*mefakdim + ['W']*haialim
        same_shift_and_name = [i for i,x in enumerate(shifts[start_time]) if x.name == name]
        if same_shift_and_name:
            shifts[start_time].pop(same_shift_and_name[0])
        shifts[start_time].append(Mission(name, duration, req_workers))
        st.info('***** Mission added successfully *****')


if st.button("Show Shifts and Missions"):
    shifts = dict(sorted(shifts.items()))
    st.write(shifts)
    st.write('Missions:')
    for time,shift in shifts.items():
        st.write(f'{time%24}:00:')
        for mission in shift:
            st.write(f'\t{mission.name}')

if st.button("Generate Shavtsak"):
    df = pd.read_csv('temp.csv')
    shifts = dict(sorted(shifts.items()))
    shavtsak = pd.DataFrame(columns=['shift', 'mission', 'duration', 'name', 'roles'])
    current_time = list(shifts.keys())[0]

    for shift, missions in shifts.items():
        df['hours_since_last_shift'] += shift - current_time
        _ = [mission.clear() for mission in missions]
        random.shuffle(missions)
        for role in ['M', 'W']:  # adds priority to first assign mefakdim
            for mission in missions:
                worker_list = get_relevant_workers(df, mission.name, shift, role)
                for i in range(mission.req_workers.count(role)):
                    if not worker_list:
                        st.info(f"{50*'-'}\n\t******* SHAVTSAK FAILED *******\n"\
                                f'{shift%24:2}:00 {mission.name:12} --> {role}: No available assignment\n' \
                                f"{50*'-'}")
                        break
                    else:
                        worker_name = worker_list.pop(0)
                        mission.workers.append(worker_name)
                        df.loc[df['name'] == worker_name, 'hours_since_last_shift'] = -mission.duration
                        shavtsak.loc[len(shavtsak.index)] = [shift, mission.name, mission.duration, worker_name, role]
                        # print(f'{shift%24:2}:00 {mission.name:12} --> {role}: {worker_name}')  # for debugging            
        current_time = shift
    df['hours_since_last_shift'] += 32-current_time
    shavtsak.sort_values(by=['shift', 'mission', 'roles'], inplace=True)
    shavtsak.to_csv("shavtsak_temp.csv", index=False, encoding='utf-8-sig')
    print_shavtsak(shavtsak)
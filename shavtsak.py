from collections import defaultdict
from pathlib import Path

import streamlit as st
import altair as alt
import pandas as pd


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Shavtsak',
    page_icon=':shopping_bags:', # This is an emoji shortcode. Could be a URL too.
)

# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
'''
# :shopping_bags: Inventory tracker

**Welcome to Alice's Corner Store's intentory tracker!**
This page reads and writes directly from/to our inventory database.
'''

st.info('''
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    ''')

df = pd.read_csv(Path(__file__).parent/'workers.csv')
df
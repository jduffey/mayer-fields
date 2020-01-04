import csv
import numpy as np
import pandas as pd
from config import mayer_ranges

def generate_mayer_values(source_file, output_file):
    print("Generating Mayer values...")
    df = pd.read_csv(source_file, skiprows=0)

    df = df.reset_index(drop=True)

    mayer_labels = []
    for mayer_range in mayer_ranges:
        mayer_label = 'Mayer_' + str(mayer_range)
        mayer_labels.append(mayer_label)
        df[mayer_label] = df['Spot']/df['Spot'].rolling(window=(mayer_range)).mean()

    df = df.round(4)
    df.to_csv(output_file, index=False)
    print(f'Created "{output_file}".')
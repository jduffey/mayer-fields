import csv
import numpy as np
import pandas as pd

from config import dma_ranges

# dma_ranges = []
# [dma_ranges.append(i) for i in range(600, 1501, 50)]
# [dma_ranges.append(i) for i in range(300, 601, 10)]
# [dma_ranges.append(i) for i in range(10, 301, 5)]
# dma_ranges.sort(reverse=True)

def generate_mayer_values(source_file, output_file):
    df = pd.read_csv(source_file, skiprows=0)

    df = df.reset_index(drop=True)

    ratio_labels = []
    for dma_range in dma_ranges:
        ratio_label = 'Mayer_' + str(dma_range)
        ratio_labels.append(ratio_label)
        df[ratio_label] = df['Spot']/df['Spot'].rolling(window=(dma_range)).mean()

    df = df.round(4)
    df.to_csv(output_file, index=False)
    print(f'File "{output_file}" has been created.')
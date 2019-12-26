dma_ranges = []
[dma_ranges.append(i) for i in range(600, 1501, 50)]
[dma_ranges.append(i) for i in range(300, 601, 10)]
[dma_ranges.append(i) for i in range(10, 301, 5)]
dma_ranges.sort(reverse=True)

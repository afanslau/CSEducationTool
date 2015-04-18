import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
df=pd.DataFrame.from_csv('survey.csv')
fulldata = np.array(df)
labels = list(df.columns[5:-1])
nandata = fulldata[:,5:-1]
data = [d[np.isfinite(d)] for d in nandata.T]

bpd = plt.boxplot(data[::-1], labels=labels[::-1], showmeans=True)
for line in bpd['medians']:
	line.set_linewidth(4)
locs, labels = plt.xticks()
for label in labels:
	label.set_fontsize(20)
plt.setp(labels, rotation=90)
plt.ylabel('Likelihood', size=20)
plt.title('Knowd Survey Results - How likely are you to...',size=20)

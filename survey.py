import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
df=pd.DataFrame.from_csv('survey.csv')
fulldata = np.array(df)
labels = list(df.columns[:4])
nandata = fulldata[:,:4]
data = [d[np.isfinite(d)] for d in nandata.T]

bpd = plt.boxplot(data, labels=labels, showmeans=True)
for line in bpd['medians']:
	line.set_linewidth(4)
locs, labels = plt.xticks()
for label in labels:
	label.set_fontsize(20)
plt.setp(labels, rotation=90)
plt.ylabel('Likert Scale', size=20)
plt.title('Knowd Ease of Use Survey Results',size=20)

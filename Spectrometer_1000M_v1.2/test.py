import numpy as np
import pandas as pd

i=1
a=[1,1,1]
b=[0,2,3]
c=np.transpose([a,b])
print(c)
# np.savetxt('test_'+str(i)+'.csv',c,delimiter=',')
save = pd.DataFrame(c)
save.to_csv('test.csv',index=False,header=False)  #index=False,header=False表示不保存行索引和列标题
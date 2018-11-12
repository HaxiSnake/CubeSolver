import numpy as np
condition='cube2_light'
label_name='./labels/'+condition+'_label.npy'

label_dic = np.load(label_name)
label_dic = label_dic[()]

this_group=25
target_group=0
for i in range(3):
    this_key=str(this_group)+"_"+str(i)+".jpg"
    target_key=str(target_group)+"_"+str(i)+".jpg"
    points=label_dic[this_key]
    label_dic[target_key]=points
np.save(label_name,label_dic)
print("success")
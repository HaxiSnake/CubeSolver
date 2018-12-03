condition="cube1_dark"
feature="hsv"
feature_file='./labels/'+condition+'_'+feature+'_feature.csv'
color_file = open(feature_file,'r')
line=color_file.readline()
while len(line)>1:
    print(line)
    line=color_file.readline()
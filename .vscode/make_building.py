# 创建Building.config文件
# 建筑rect范围初始化
building_rects=[None]*32
building_rects[0]=[0,0,200,200]
building_rects[5]=[0,700,200,200]
building_rects[16]=[1400,700,200,200]
building_rects[21]=[1400,0,200,200]
for i in range(4):
    building_rects[i+1]=[0,i*125+200,200,125]
for i in range(10):
    building_rects[i+6]=[i*120+200,700,120,200]
for i in range(4):
    building_rects[i+17]=[1400,575-i*125,200,125]
for i in range(10):
    building_rects[i+22]=[1280-i*120,0,120,200]

with open('buildings.config','w') as f:
    for i in range(32):
        print('第{}个建筑：'.format(i))
        name,isbuilding=input('请输入名称 是否为建筑：').split()
        if isbuilding=='1':
            blockprice=input('继续输入地价')
        else:
            blockprice=-1
        data=str(i)+'|'+str(name)+'|'+str(building_rects[i])+'|'+str(isbuilding)+'|'+str(blockprice)+'|'+'\n'
        f.write(data)

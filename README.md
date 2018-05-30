# 旅行商问题(TSP)

使用蚁群算法(ACO)、遗传算法(GA)、霍普菲尔德网络(Hopfield)解决旅行商问题(TSP)

CSDN: http://blog.csdn.net/diamonjoy_zone/article/details/65445704

在研究生《人工智能》课堂上学习了蚁群算法之后，老师提出了可以解决旅行商问题的三种思路，分别通过神经网络计算、进化计算和群智能计算得到最佳途径，如何在此包含50个城市坐标的地图搜索出一条路径，遍历每一座城市且不重复地返回原点？本文选取蚁群算法、遗传算法和霍普菲尔德网络的方法，分别实现其算法的Python程序，并进行了实验比较。

## 【forked 修改】[TSP-ACO 蚁群优化算法解决旅行社问题](https://github.com/huihut/TSP/tree/master/TPS-ACO)

* 增加城市数据的输入输出，使城市数据集以文件形式读写

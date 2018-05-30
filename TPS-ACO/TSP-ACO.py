# -*- coding: utf-8 -*-
import random
import copy
import sys
import Tkinter
import threading

# 参数：阿尔法、贝塔、信息素衰减率（挥发因子）
(ALPHA, BETA, RHO, Q) = (1.0, 2.0, 0.5, 100.0)

# 城市数，蚁群（城市数不同则需修改这里）
(city_num, ant_num) = (52, 52)

# 窗体大小
max_width = 800
max_height = 600

# 城市的x、y坐标数组
distance_x = []
distance_y = []

# 城市距离和信息素
distance_graph = [[0.0 for col in xrange(city_num)] for raw in xrange(city_num)]
pheromone_graph = [[1.0 for col in xrange(city_num)] for raw in xrange(city_num)]


# ----------- 蚂蚁 -----------
class Ant(object):
    # 初始化
    def __init__(self, ID):

        self.ID = ID  # ID
        self.__clean_data()  # 随机初始化出生点

    # 初始数据
    def __clean_data(self):

        self.path = []  # 当前蚂蚁的路径
        self.total_distance = 0.0  # 当前路径的总距离
        self.move_count = 0  # 移动次数
        self.current_city = -1  # 当前停留的城市
        self.open_table_city = [True for i in xrange(city_num)]  # 探索城市的状态

        city_index = random.randint(0, city_num - 1)  # 随机初始出生点
        self.current_city = city_index
        self.path.append(city_index)
        self.open_table_city[city_index] = False
        self.move_count = 1

    # 选择下一个城市
    def __choice_next_city(self):

        next_city = -1
        select_citys_prob = [0.0 for i in xrange(city_num)]
        total_prob = 0.0

        # 获取去下一个城市的概率
        for i in xrange(city_num):
            if self.open_table_city[i]:
                try:
                    # 计算概率：与信息素浓度成正比，与距离成反比
                    select_citys_prob[i] = pow(pheromone_graph[self.current_city][i], ALPHA) * pow(
                        (1.0 / distance_graph[self.current_city][i]), BETA)
                    total_prob += select_citys_prob[i]
                except ZeroDivisionError, e:
                    print 'Ant ID: {ID}, current city: {current}, target city: {target}'.format(ID=self.ID,
                                                                                                current=self.current_city,
                                                                                                target=i)
                    sys.exit(1)

        # 轮盘选择城市
        if total_prob > 0.0:
            # 产生一个随机概率
            temp_prob = random.uniform(0.0, total_prob)
            for i in xrange(city_num):
                if self.open_table_city[i]:
                    # 轮次相减
                    temp_prob -= select_citys_prob[i]
                    if temp_prob < 0.0:
                        next_city = i
                        break

        # 未从概率产生，顺序选择一个未访问城市
        if next_city == -1:
            for i in xrange(city_num):
                if self.open_table_city[i]:
                    next_city = i
                    break

        # 返回下一个城市序号
        return next_city

    # 计算路径总距离
    def __cal_total_distance(self):

        temp_distance = 0.0

        for i in xrange(1, city_num):
            start, end = self.path[i], self.path[i - 1]
            temp_distance += distance_graph[start][end]

        # 回路
        end = self.path[0]
        temp_distance += distance_graph[start][end]
        self.total_distance = temp_distance

    # 移动操作
    def __move(self, next_city):

        self.path.append(next_city)
        self.open_table_city[next_city] = False
        self.total_distance += distance_graph[self.current_city][next_city]
        self.current_city = next_city
        self.move_count += 1

    # 搜索路径
    def search_path(self):

        # 初始化数据
        self.__clean_data()

        # 搜素路径，遍历完所有城市为止
        while self.move_count < city_num:
            # 移动到下一个城市
            next_city = self.__choice_next_city()
            self.__move(next_city)

        # 计算路径总长度
        self.__cal_total_distance()


# ----------- TSP问题 -----------

class TSP(object):
    def __init__(self, root, width=max_width, height=max_height, n=city_num):

        # 创建IO
        self.io = IO()
        self.io.input()

        # 创建画布
        self.root = root
        self.width = width
        self.height = height
        # 城市数目初始化为city_num
        self.n = n
        # Tkinter.Canvas
        self.canvas = Tkinter.Canvas(
            root,
            width=self.width,
            height=self.height,
            bg="#EBEBEB",  # 背景白色
            xscrollincrement=1,
            yscrollincrement=1
        )
        self.canvas.pack(expand=Tkinter.YES, fill=Tkinter.BOTH)
        self.title("蚁群算法解决TPS旅行商问题(n:初始化 e:开始搜索 s:停止搜索 q:退出程序)")
        self.__r = 5
        self.__lock = threading.RLock()  # 线程锁

        self.__bindEvents()
        self.new()

        # 计算城市之间的距离
        for i in xrange(city_num):
            for j in xrange(city_num):
                temp_distance = pow((distance_x[i] - distance_x[j]), 2) + pow((distance_y[i] - distance_y[j]), 2)
                temp_distance = pow(temp_distance, 0.5)
                distance_graph[i][j] = float(int(temp_distance + 0.5))

    # 按键响应程序
    def __bindEvents(self):

        self.root.bind("q", self.quite)  # 退出程序
        self.root.bind("n", self.new)  # 初始化
        self.root.bind("e", self.search_path)  # 开始搜索
        self.root.bind("s", self.stop)  # 停止搜索

    # 更改标题
    def title(self, s):

        self.root.title(s)

    # 初始化
    def new(self, evt=None):

        # 停止线程
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()

        self.clear()  # 清除信息
        self.nodes = []  # 节点坐标
        self.nodes2 = []  # 节点对象

        # 初始化城市节点
        for i in range(len(distance_x)):
            # 在画布上随机初始坐标
            x = distance_x[i]
            y = distance_y[i]
            self.nodes.append((x, y))
            # 生成节点椭圆，半径为self.__r
            node = self.canvas.create_oval(x - self.__r,
                                           y - self.__r, x + self.__r, y + self.__r,
                                           fill="#ff0000",  # 填充红色
                                           outline="#000000",  # 轮廓白色
                                           tags="node",
                                           )
            self.nodes2.append(node)
            # 显示坐标
            self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text=str(i+1) + ' (' + str(x) + ',' + str(y) + ')',  # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )

        # 顺序连接城市
        # self.line(range(city_num))

        # 初始城市之间的距离和信息素
        for i in xrange(city_num):
            for j in xrange(city_num):
                pheromone_graph[i][j] = 1.0

        self.ants = [Ant(ID) for ID in xrange(ant_num)]     # 初始蚁群
        self.best_ant = Ant(-1)                             # 初始最优解
        self.best_ant.total_distance = 1 << 31              # 初始最大距离
        self.iter = 1                                       # 初始化迭代次数

    # 将节点按order顺序连线
    def line(self, order):
        # 删除原线
        self.canvas.delete("line")

        def line2(i1, i2):
            p1, p2 = self.nodes[i1], self.nodes[i2]
            self.canvas.create_line(p1, p2, fill="#000000", tags="line")
            return i2

        # order[-1]为初始值
        reduce(line2, order, order[-1])

    # 清除画布
    def clear(self):
        for item in self.canvas.find_all():
            self.canvas.delete(item)

    # 退出程序
    def quite(self, evt):
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()
        self.root.destroy()
        print u"\n程序已退出..."
        sys.exit()

    # 停止搜索
    def stop(self, evt):
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()
        self.io.output(self)

    # 开始搜索
    def search_path(self, evt=None):

        # 开启线程
        self.__lock.acquire()
        self.__running = True
        self.__lock.release()

        while self.__running:
            # 遍历每一只蚂蚁
            for ant in self.ants:
                # 搜索一条路径
                ant.search_path()
                # 与当前最优蚂蚁比较
                if ant.total_distance < self.best_ant.total_distance:
                    # 更新最优解
                    self.best_ant = copy.deepcopy(ant)
            # 更新信息素
            self.__update_pheromone_gragh()
            print u"迭代次数：", self.iter, u"； 最佳路径总距离：", int(self.best_ant.total_distance)
            # 连线
            self.line(self.best_ant.path)
            # 设置标题
            self.title("蚁群算法解决TPS旅行商问题(n:随机初始 e:开始搜索 s:停止搜索 q:退出程序) 迭代次数: {0}；最佳路径总距离：{1}".format(self.iter, int(self.best_ant.total_distance)))
            # 更新画布
            self.canvas.update()
            self.iter += 1

    # 更新信息素
    def __update_pheromone_gragh(self):

        # 获取每只蚂蚁在其路径上留下的信息素
        temp_pheromone = [[0.0 for col in xrange(city_num)] for raw in xrange(city_num)]
        for ant in self.ants:
            for i in xrange(1, city_num):
                start, end = ant.path[i - 1], ant.path[i]
                # 在路径上的每两个相邻城市间留下信息素，与路径总距离反比
                temp_pheromone[start][end] += Q / ant.total_distance
                temp_pheromone[end][start] = temp_pheromone[start][end]

        # 更新所有城市之间的信息素，旧信息素衰减加上新迭代信息素
        for i in xrange(city_num):
            for j in xrange(city_num):
                pheromone_graph[i][j] = pheromone_graph[i][j] * RHO + temp_pheromone[i][j]

    # 主循环
    def mainloop(self):
        self.root.mainloop()


# ----------- 城市数据的输入输出 -----------

class IO(object):
    # def __init__(self):

    def input(self):
        self.data_filename = raw_input(u"\n请输入城市数据文件名（直接回车默认为 data.txt 文件）\n")
        if self.data_filename == "":
            self.data_filename = "data.txt"

        self.solution_filename = raw_input(u"\n请输入最优路径解保存的文件名（直接回车默认为 solution.txt 文件）\n")
        if self.solution_filename == "":
            self.solution_filename = "solution.txt"

        try:
            self.fo = open(self.data_filename, "r")
            global max_width
            global max_height

            while True:
                line = self.fo.readline()
                line = line.split(' ')
                city_id = "".join(line[0])
                print u"录入第 " + city_id + u" 个城市：",
                if city_id.isdigit():

                    dx = float(line[1])
                    print "[ " + str(dx),
                    if max_width < dx:
                        max_width = dx
                    distance_x.append(dx)

                    # 移除坐标 y 中的 \n
                    ndy = "".join(line[2])
                    dy = float(ndy[:-1])

                    print ", " + str(dy) + " ]"
                    if max_height < dy:
                        max_height = dy
                    distance_y.append(dy)
                else:
                    break

            print u"\n数据录入完成！\n"

        finally:
            if self.fo:
                self.fo.close()

    def output(self, tsp):
        try:
            self.fo = open(self.solution_filename, "w+")
            for city in tsp.best_ant.path:
                self.fo.write(str(city+1))
                self.fo.write("\n")
            self.fo.write("EOF\n")
            self.fo.write("最优解的总长度" + str(int(tsp.best_ant.total_distance)))

        finally:
            if self.fo:
                self.fo.close()


# ----------- 程序的入口处 -----------

if __name__ == '__main__':
    print u""" 
-------------------------------------------------------- 
    程序：蚁群算法解决TPS问题程序 
    作者：许彬 
    日期：2015-12-10
    语言：Python 2.7 
-------------------------------------------------------- 
    修改：增加城市数据的输入输出，使城市数据集（52个城市）以文件形式读写
    作者：谢孟辉
    日期：2018-5-30
    语言：python 2.7
-------------------------------------------------------- 
    """
    TSP(Tkinter.Tk()).mainloop()
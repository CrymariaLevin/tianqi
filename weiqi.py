#!/usr/bin/python3
# 使用Python内置GUI模块tkinter
from tkinter import *
# ttk覆盖tkinter部分对象，ttk对tkinter进行了优化
from tkinter.ttk import *
# 深拷贝时需要用到copy模块
import copy
import tkinter.messagebox

# 围棋应用对象定义
class Application(Tk):
	# 初始化棋盘,默认九格十路棋盘
	def __init__(self):
		Tk.__init__(self)
		# 窗口尺寸设置，默认：1.8
		self.mode_num = 10
		self.size = 1.8
		# 棋盘每格的边长
		self.dd = 360 * self.size / (self.mode_num - 1)
		# 相对九路棋盘的矫正比例
		self.p = 1 #if self.mode_num == 9 else (2 / 3 if self.mode_num == 13 else 4 / 9)
		# 定义棋盘阵列,超过边界：-1，无子：0，黑棋：1，白棋：2
		self.positions = [[0 for i in range(self.mode_num + 1)] for i in range(self.mode_num + 1)]
		# 初始化棋盘，所有超过边界的值置-1
		for m in range(self.mode_num + 1):
			for n in range(self.mode_num + 1):
				if (m * n == 0 or m == self.mode_num or n == self.mode_num):
					self.positions[m][n] = -1
		# 拷贝三份棋盘“快照”，悔棋和判断“打劫”时需要作参考，即最近的3步棋，这里的好像不太对
		self.last_3_positions = copy.deepcopy(self.positions)
		self.last_2_positions = copy.deepcopy(self.positions)
		self.last_1_positions = copy.deepcopy(self.positions)

		# 记录鼠标经过的地方，用于显示shadow时
		self.cross_last = None
		# 当前轮到的玩家，黑：0，白：1，执黑先行，注意后面的函数里是要+1表示为棋子，而非+1变换棋子
		self.present = 0
		# 初始停止运行，点击“开始游戏”运行游戏
		self.stop = True
		# 悔棋次数，次数大于0才可悔棋，初始置0（初始不能悔棋），悔棋后置0，下棋或弃手时恢复为1，以禁止连续悔棋
		self.regretchance = 0
		# 图片资源，存放在当前目录下的/Pictures/中
		self.photoW = PhotoImage(file="./Pictures/W.png")
		self.photoB = PhotoImage(file="./Pictures/B.png")
		self.photoBD = PhotoImage(file="./Pictures/" + "BD" + "-" + '13' + ".png")
		self.photoWD = PhotoImage(file="./Pictures/" + "WD" + "-" + '13' + ".png")
		self.photoBU = PhotoImage(file="./Pictures/" + "BU" + "-" + '13' + ".png")
		self.photoWU = PhotoImage(file="./Pictures/" + "WU" + "-" + '13' + ".png")
		# 用于黑白棋子图片切换的列表
		self.photoWBU_list = [self.photoBU, self.photoWU] #这是鼠标移动时的棋子切换
		self.photoWBD_list = [self.photoBD, self.photoWD] #这是落子的棋子切换
		# 窗口大小
		self.geometry(str(int(600 * self.size)) + 'x' + str(int(400 * self.size)))
		# 画布控件，作为容器
		self.canvas_bottom = Canvas(self, bg='#A0522D', bd=0, width=600 * self.size, height=400 * self.size)
		self.canvas_bottom.place(x=0, y=0)

		# 几个功能按钮, command命令都要在之后的函数里设置
		self.startButton = Button(self, text='开始游戏', command=self.start)
		self.startButton.place(x=480 * self.size, y=200 * self.size)
		self.passmeButton = Button(self, text='弃手', command=self.passme)
		self.passmeButton.place(x=480 * self.size, y=225 * self.size)
		self.regretButton = Button(self, text='悔棋', command=self.regret)
		self.regretButton.place(x=480 * self.size, y=250 * self.size)
		# 初始悔棋按钮禁用
		self.regretButton['state'] = DISABLED
		self.replayButton = Button(self, text='重新开始', command=self.reload)
		self.replayButton.place(x=480 * self.size, y=275 * self.size)
		self.newGameButton1 = Button(self, text='九格十路棋', command=self.newGame)
		self.newGameButton1.place(x=480 * self.size, y=300 * self.size)		#
		self.quitButton = Button(self, text='退出游戏', command=self.quit)
		self.quitButton.place(x=480 * self.size, y=350 * self.size)

		# 画棋盘，填充颜色
		# 画矩形，棋盘底，原理是给出矩形的左上和右下点的坐标
		self.canvas_bottom.create_rectangle(0 * self.size, 0 * self.size, 400 * self.size, 400 * self.size, fill='#DEB887')
		# 刻画棋盘线及九个点
		# 画棋盘外框粗线
		self.canvas_bottom.create_rectangle(20 * self.size, 20 * self.size, 380 * self.size, 380 * self.size, width=3)
		# 画中间的线条
		for i in range(1, self.mode_num - 1):
			# 画线（横），给出的是各个节点的坐标，两个为一组
			self.canvas_bottom.create_line(20 * self.size, 20 * self.size + i * self.dd,
										   380 * self.size, 20 * self.size + i * self.dd, width=2)
			# 纵线
			self.canvas_bottom.create_line(20 * self.size + i * self.dd, 20 * self.size,
										   20 * self.size + i * self.dd, 380 * self.size, width=2)
		# 棋盘上的九个定位点，以中点为模型，移动位置，以作出其余八个点，这里只画了4个
		for m in [-1, 1]: # 九个的话[-1,0,1],下一行一样
			for n in [-1, 1]:
				#画圆，原理是给出圆外切矩形的左上和右下点的坐标
				self.oringinal = self.canvas_bottom.create_oval(200 * self.size - self.size * 10,
																200 * self.size - self.size * 10,
																200 * self.size + self.size * 10,
																200 * self.size + self.size * 10, fill='#F4A460', outline='#DEB887')
				self.canvas_bottom.move(self.oringinal,
										m * self.dd * 2,
										n * self.dd * 2)

		# 放置右侧初始图片，默认图片坐标是中心坐标，可以通过参数anchor更改
		self.pW = self.canvas_bottom.create_image(500 * self.size + 11, 65 * self.size, image=self.photoW)
		self.pB = self.canvas_bottom.create_image(500 * self.size - 11, 65 * self.size, image=self.photoB)
		# 将太极图片都添加image标签，方便reload函数删除图片，提示该谁落子
		self.canvas_bottom.addtag_withtag('image', self.pW)
		self.canvas_bottom.addtag_withtag('image', self.pB)

		# 鼠标移动时，调用shadow函数，显示随鼠标移动的棋子
		self.canvas_bottom.bind('<Motion>', self.shadow)
		# 鼠标左键单击时，调用getdown函数，放下棋子
		self.canvas_bottom.bind('<Button-1>', self.getDown)
		# 设置退出快捷键<Ctrl>+<D>，快速退出游戏
		self.bind('<Control-KeyPress-d>', self.keyboardQuit)

	# 开始游戏函数，点击“开始游戏”时调用
	def start(self):
		# 删除右侧太极图
		self.canvas_bottom.delete(self.pW)
		self.canvas_bottom.delete(self.pB)
		# 利用右侧图案提示开始时谁先落子
		if self.present == 0:
			self.create_pB()
			self.del_pW()
		else:
			self.create_pW()
			self.del_pB()
		# 开始标志，解除stop
		self.stop = None

	# 放弃一手函数，跳过落子环节
	def passme(self):
		# 悔棋恢复
		if not self.regretchance == 1:
			self.regretchance += 1
		else:
			self.regretButton['state'] = NORMAL
		# 拷贝棋盘状态，记录前三次棋局
		self.last_3_positions = copy.deepcopy(self.last_2_positions)
		self.last_2_positions = copy.deepcopy(self.last_1_positions)
		self.last_1_positions = copy.deepcopy(self.positions)
		self.canvas_bottom.delete('image_added_sign')
		# 轮到下一玩家
		if self.present == 0:
			self.create_pW()
			self.del_pB()
			self.present = 1
		else:
			self.create_pB()
			self.del_pW()
			self.present = 0

	# 悔棋函数，可悔棋一回合，下两回合不可悔棋
	def regret(self):
		# 判定是否可以悔棋，以向前的第三盘棋局复原棋盘
		if self.regretchance == 1:
			self.regretchance = 0
			self.regretButton['state'] = DISABLED
			list_of_b = []
			list_of_w = []
			self.canvas_bottom.delete('image')
			if self.present == 0:
				self.create_pB()
			else:
				self.create_pW()
			for m in range(1, self.mode_num + 1): # 所有可落子位置归零（无子）
				for n in range(1, self.mode_num + 1):
					self.positions[m][n] = 0
			for m in range(len(self.last_3_positions)): # 3步之前的棋子位置记录
				for n in range(len(self.last_3_positions[m])):
					if self.last_3_positions[m][n] == 1:
						list_of_b += [[n, m]] # 这里坐标反过来是因为悔棋之后恢复图片时写坐标方便
					elif self.last_3_positions[m][n] == 2:
						list_of_w += [[n, m]]
			self.recover(list_of_b, 0) # 恢复黑棋位置，下一行是白棋
			self.recover(list_of_w, 1)
			self.last_1_positions = copy.deepcopy(self.last_3_positions) #记录前一步的棋子位置（覆盖为前3步的棋子位置）
			for m in range(1, self.mode_num + 1): # 将前2，前3步的棋盘记为无子
				for n in range(1, self.mode_num + 1):
					self.last_2_positions[m][n] = 0
					self.last_3_positions[m][n] = 0

	# 恢复位置列表list_to_recover为b_or_w指定的棋子
	def recover(self, list_to_recover, b_or_w):
		if len(list_to_recover) > 0:
			for i in range(len(list_to_recover)):
				# self.positions[list_to_recover[i][1]][list_to_recover[i][0]] = b_or_w + 1 #将对应棋子的坐标位置变为棋子的代号
				self.positions[list_to_recover[i][0]][list_to_recover[i][1]] = b_or_w + 1
				# 将棋子位置的对应图片恢复，注意画面坐标和棋子坐标是反的。。。。
				self.image_added = self.canvas_bottom.create_image(
					# 40 * self.size + (list_to_recover[i][0] - 1) * self.dd + 4 * self.p,
					# 40 * self.size + (list_to_recover[i][1] - 1) * self.dd - 5 * self.p,
					40 * self.size + (list_to_recover[i][1] - 1) * self.dd + 4 * self.p,
					40 * self.size + (list_to_recover[i][0] - 1) * self.dd - 5 * self.p,
					image=self.photoWBD_list[b_or_w])
				# self.canvas_bottom.addtag_withtag(
				# 	'position' + str(list_to_recover[i][0]) + str(list_to_recover[i][1]), self.image_added)
				self.canvas_bottom.addtag_withtag(
					'position' + str(list_to_recover[i][1]) + str(list_to_recover[i][0]), self.image_added)

	# 重新加载函数,删除图片，序列归零，设置一些初始参数，点击“重新开始”时调用
	def reload(self):
		if self.stop:
			self.stop = False
		self.canvas_bottom.delete('image') # 清除所有棋子
		self.regretchance = 0
		self.present = 0
		self.create_pB()
		for m in range(1, self.mode_num + 1):
			for n in range(1, self.mode_num + 1):
				self.positions[m][n] = 0
				self.last_3_positions[m][n] = 0
				self.last_2_positions[m][n] = 0
				self.last_1_positions[m][n] = 0

	# 以下四个函数实现了右侧太极图的动态创建与删除，见开始游戏函数，为了提示该谁落子
	def create_pW(self):
		self.pW = self.canvas_bottom.create_image(500 * self.size + 11, 65 * self.size, image=self.photoW)
		self.canvas_bottom.addtag_withtag('image', self.pW)

	def create_pB(self):
		self.pB = self.canvas_bottom.create_image(500 * self.size - 11, 65 * self.size, image=self.photoB)
		self.canvas_bottom.addtag_withtag('image', self.pB)

	def del_pW(self):
		self.canvas_bottom.delete(self.pW)

	def del_pB(self):
		self.canvas_bottom.delete(self.pB)

	# 显示鼠标移动下棋子的移动
	def shadow(self, event): # event好像是当前鼠标位置
		if not self.stop:
			# 找到最近格点，在当前位置靠近的格点出显示棋子图片，并删除上一位置的棋子图片
			# 在指定棋盘区域内才会显示
			if (40 * self.size< event.x < 380 * self.size) and (40 * self.size< event.y < 380 * self.size):
				dx = (event.x - 40 * self.size) % self.dd #取余数部分，为了获得当前位置的“零头”，方便下面整体定位
				dy = (event.y - 40 * self.size) % self.dd
				self.cross = self.canvas_bottom.create_image(
					# 单个节点除以边长后四舍五入后看是靠近哪一侧的边，round(dx/self.dd)*self.dd的结果只有0和1两种
					# 然后用当前位置减去零头（dx或dy），在加上单位格的一半长度定位
					event.x - dx + round(dx / self.dd) * self.dd + 16 * self.p,
					event.y - dy + round(dy / self.dd) * self.dd - 21 * self.p,
					image=self.photoWBU_list[self.present])
				self.canvas_bottom.addtag_withtag('image', self.cross)
				# 删除之前的鼠标影子
				if self.cross_last != None:
					self.canvas_bottom.delete(self.cross_last)
				self.cross_last = self.cross

	# 落子，并驱动玩家的轮流下棋行为
	def getDown(self, event):
		if not self.stop:
			# 先找到最近格点
			if (40 * self.size - self.dd * 0.4 < event.x < self.dd * 0.4 + 380 * self.size) and (
					40 * self.size - self.dd * 0.4 < event.y < self.dd * 0.4 + 380 * self.size):
			# if (40 * self.size < event.x < 380 * self.size) and (40 * self.size < event.y < 380 * self.size):
				dx = (event.x - 40 * self.size) % self.dd
				dy = (event.y - 40 * self.size) % self.dd
				# 获取并记录坐标（索引）, 注意这里是横纵坐标，和棋子图的索引是反的
				x = int((event.x - 40 * self.size - dx) / self.dd + round(dx / self.dd) + 1)
				y = int((event.y - 40 * self.size - dy) / self.dd + round(dy / self.dd) + 1)
				print('画面坐标：',x, y)
				# 判断位置是否已经被占据
				if self.positions[y][x] == 0: # 注意和上面坐标位置的区别
					# 未被占据，则尝试占据，获得占据后能杀死的棋子列表
					self.positions[y][x] = self.present + 1 # 指定位置颜色，self.present为位置代号，+1才是棋子的代号
					self.image_added = self.canvas_bottom.create_image( # 填上当前棋手的棋子图
						# 这里位置和鼠标跟踪不一样是因为之前选区域的时候的比例系数0.4，但是为什么这样写不清楚
						# event.x - dx + round(dx / self.dd) * self.dd + 16 * self.p,
						# event.y - dy + round(dy / self.dd) * self.dd - 21 * self.p,
						event.x - dx + round(dx / self.dd) * self.dd + 4 * self.p,
						event.y - dy + round(dy / self.dd) * self.dd - 5 * self.p,
						image=self.photoWBD_list[self.present])
					self.canvas_bottom.addtag_withtag('image', self.image_added)
					# 棋子与位置标签绑定，方便“杀死”
					self.canvas_bottom.addtag_withtag('position' + str(x) + str(y), self.image_added)
					deadlist = self.get_deadlist([y,x])
					# print(deadlist)
					self.kill(deadlist)
					# 判断是否重复棋局（打劫判断）
					if not self.last_2_positions == self.positions:
						# 可以落子，判断是否属于有气或杀死对方其中之一
						if len(deadlist) > 0 or self.if_self_dead([y,x],[[y,x]],self.present) == False:
							# 当不重复棋局，且属于有气和杀死对方其中之一时，落下棋子有效
							if not self.regretchance == 1:
								self.regretchance += 1
							else:
								self.regretButton['state'] = NORMAL
							self.last_3_positions = copy.deepcopy(self.last_2_positions)
							self.last_2_positions = copy.deepcopy(self.last_1_positions)
							self.last_1_positions = copy.deepcopy(self.positions)
							# 删除上次的标记，重新创建标记
							self.canvas_bottom.delete('image_added_sign')
							# 画标记，用于提示上次落子位置
							self.image_added_sign = self.canvas_bottom.create_oval(
								event.x - dx + round(dx / self.dd) * self.dd + 0.4 * self.dd,
								event.y - dy + round(dy / self.dd) * self.dd + 0.35 * self.dd,
								event.x - dx + round(dx / self.dd) * self.dd - 0.35 * self.dd,
								event.y - dy + round(dy / self.dd) * self.dd - 0.4 * self.dd, width=3,
								outline='#3ae')
							self.canvas_bottom.addtag_withtag('image', self.image_added_sign)
							self.canvas_bottom.addtag_withtag('image_added_sign', self.image_added_sign)
							# 落子
							if self.present == 0:
								self.create_pW()
								self.del_pB()
								self.present = 1
							else:
								self.create_pB()
								self.del_pW()
								self.present = 0
						else:
							# 不属于杀死对方或有气，则判断为无气，警告并弹出警告框
							self.positions[y][x] = 0
							self.canvas_bottom.delete('position' + str(x) + str(y))
							self.bell()
							self.showwarningbox('无气', "你被包围了！")
					else:
						# 重复棋局，警告打劫
						self.positions[y][x] = 0
						self.canvas_bottom.delete('position' + str(x) + str(y))
						self.recover(deadlist, (1 if self.present == 0 else 0))
						self.bell()
						self.showwarningbox("打劫", "此路不通！")
				else:
					# 格子里已经有子覆盖，声音警告
					self.bell()
			else:
				# 超出边界，声音警告
				self.bell()

	# 判断单个子周围有没有气
	def get_status(self, position):
		position_list = [[position[0], position[1] - 1], [position[0], position[1] + 1], [position[0] - 1, position[1]],
						 [position[0] + 1, position[1]]]
		if any([self.positions[p[0]][p[1]] == 0 for p in position_list]):  # 周边有空值即可落子
			return True
		elif all([self.positions[p[0]][p[1]] != 0 for p in position_list]):  # 周边无气
			return False

	# 这个函数是看当前颜色的棋子是否死了（没死返回False），如果周围没气，到周围寻找同色的邻居，将当前棋子加入deadlist，直到周围没气或者有气结束递归
	def if_self_dead(self, position, deadlist, present):
		# next_m = 1 if self.present == 0 else 1
		temp_positions = self.positions.copy()
		# deadlist = self.dead_list.copy()
		# print(next_m)
		position_list = [[position[0], position[1] - 1], [position[0], position[1] + 1], [position[0] - 1, position[1]],
						 [position[0] + 1, position[1]]]
		print('当前检测棋子颜色：', present+1)
		status = self.get_status(position)
		print('当前检测坐标：', position)
		if status: # 周边有空值即可落子
			# print(position,'是活的')
			return False
		else:
			for p in position_list: # 在周边找自己颜色的子
				if temp_positions[p[0]][p[1]] == present+1 and p not in deadlist: # 这里不要忘了+1，而且要排除已经检测过的棋子
					print('当前检测是否有气坐标：',p) #
					deadlist.append(p) # 应先把当前循环的子加入到deadlist中再往下判断，防止死循环
					r = self.if_self_dead(p, deadlist, present)
					if not r: # 如果相邻同色棋子有气，则活（返回False）
						return False
					else: # 否则将当前检验的棋子加入到deal_list继续循环
						self.if_self_dead(p, deadlist, present)  # 不能直接return，会中断循环
				else:
					continue
		print('最终吃子列表：', deadlist)
		return deadlist

	def get_deadlist(self, position): # 获取要删除的棋子列表，只检查对面有没有被吃的
		dead_list = []
		next_m = 1 if self.present == 0 else 0
		position_list = [[position[0], position[1] - 1], [position[0], position[1] + 1], [position[0] - 1, position[1]],
						 [position[0] + 1, position[1]]]
		for p in position_list:
			# 只有周围是对面的子才需要检查对面死没死，如果自己的子下到死气里会在流程里报错，不用检查
			if self.positions[p[0]][p[1]] == next_m+1 and p not in dead_list:
				kill_list = self.if_self_dead(p, [p, ], next_m)
				print('kill_list:',kill_list)
				if not kill_list == False: # 周边无气，加入待删除列表
					dead_list.extend(kill_list)
			else:
				continue
		return dead_list

	# 判断棋子（种类为yourChessman，位置为yourPosition）是否无气（死亡），有气则返回False，无气则返回无气棋子的列表
	# 本函数是游戏规则的关键，初始deadlist只包含了自己的位置，每次执行时，函数尝试寻找yourPosition周围有没有空的位置，有则结束，返回False代表有气；
	# 若找不到，则找自己四周的同类（不在deadlist中的）是否有气，即调用本函数，无气，则把该同类加入到deadlist，然后找下一个邻居，只要有一个有气，返回False代表有气；
	# 若四周没有一个有气的同类，返回deadlist,至此结束递归

	# def if_dead(self, deadList, yourChessman, yourPosition):
	# 	# 第一个循环是看落子位置上下左右有没有气，感觉写的有点复杂，使用any函数和array矩阵处理方便点
	# 	for i in [-1, 1]:
	# 		if [yourPosition[0] + i, yourPosition[1]] not in deadList:
	# 			if self.positions[yourPosition[1]][yourPosition[0] + i] == 0: # 当前位置无子
	# 				return False
	# 		if [yourPosition[0], yourPosition[1] + i] not in deadList:
	# 			if self.positions[yourPosition[1] + i][yourPosition[0]] == 0:
	# 				return False
	# 	# 开始递归，坐标一个个移动，一共四个方向轮流递归
	# 	if ([yourPosition[0] + 1, yourPosition[1]] not in deadList) and (
	# 			self.positions[yourPosition[1]][yourPosition[0] + 1] == yourChessman): # 如果相邻棋子是同颜色的棋子
	# 		# 将移动后的坐标加入dead_list递归
	# 		midvar = self.if_dead(deadList + [[yourPosition[0] + 1, yourPosition[1]]], yourChessman,
	# 							  [yourPosition[0] + 1, yourPosition[1]])
	# 		if not midvar:
	# 			return False
	# 		else:
	# 			deadList += copy.deepcopy(midvar)
	# 	if ([yourPosition[0] - 1, yourPosition[1]] not in deadList) and (
	# 			self.positions[yourPosition[1]][yourPosition[0] - 1] == yourChessman):
	# 		midvar = self.if_dead(deadList + [[yourPosition[0] - 1, yourPosition[1]]], yourChessman,
	# 							  [yourPosition[0] - 1, yourPosition[1]])
	# 		if not midvar:
	# 			return False
	# 		else:
	# 			deadList += copy.deepcopy(midvar)
	# 	if ([yourPosition[0], yourPosition[1] + 1] not in deadList) and (
	# 			self.positions[yourPosition[1] + 1][yourPosition[0]] == yourChessman):
	# 		midvar = self.if_dead(deadList + [[yourPosition[0], yourPosition[1] + 1]], yourChessman,
	# 							  [yourPosition[0], yourPosition[1] + 1])
	# 		if not midvar:
	# 			return False
	# 		else:
	# 			deadList += copy.deepcopy(midvar)
	# 	if ([yourPosition[0], yourPosition[1] - 1] not in deadList) and (
	# 			self.positions[yourPosition[1] - 1][yourPosition[0]] == yourChessman):
	# 		midvar = self.if_dead(deadList + [[yourPosition[0], yourPosition[1] - 1]], yourChessman,
	# 							  [yourPosition[0], yourPosition[1] - 1])
	# 		if not midvar:
	# 			return False
	# 		else:
	# 			deadList += copy.deepcopy(midvar)
	# 	return deadList
    #
	# # 落子后，依次判断四周是否有棋子被杀死，并返回死棋位置列表
	# def get_deadlist(self, x, y):
	# 	deadlist = []
	# 	for i in [-1, 1]:
	# 		if self.positions[y][x + i] == (2 if self.present == 0 else 1) and ([x + i, y] not in deadlist):
	# 			killList = self.if_dead([[x + i, y]], (2 if self.present == 0 else 1), [x + i, y])
	# 			if not killList == False:
	# 				deadlist += copy.deepcopy(killList)
	# 		if self.positions[y + i][x] == (2 if self.present == 0 else 1) and ([x, y + i] not in deadlist):
	# 			killList = self.if_dead([[x, y + i]], (2 if self.present == 0 else 1), [x, y + i])
	# 			if not killList == False:
	# 				deadlist += copy.deepcopy(killList)
	# 	return deadlist

	# 杀死位置列表killList中的棋子，即删除图片，位置值置0
	def kill(self, killList):
		# if not killList:
		# 	return None
		if len(killList) > 0:
			for i in range(len(killList)):
				print('删除的棋子：', self.positions[killList[i][0]][killList[i][1]])
				self.positions[killList[i][0]][killList[i][1]] = 0 # 自己写的吃子函数,坐标反的
				# self.positions[killList[i][1]][killList[i][0]] = 0
				# self.canvas_bottom.delete('position' + str(killList[i][0]) + str(killList[i][1])) # 同上
				self.canvas_bottom.delete('position' + str(killList[i][1]) + str(killList[i][0]))
				print('删除画面位置：',[str(killList[i][1]), str(killList[i][0])])

	# 警告消息框，接受标题和警告信息
	def showwarningbox(self, title, message):
		self.canvas_bottom.delete(self.cross)
		tkinter.messagebox.showwarning(title, message)

	# 键盘快捷键退出游戏
	def keyboardQuit(self, event):
		self.quit()

# 以下函数修改全局变量值，newApp使主函数循环，以建立不同参数的对象
	def newGame(self):
		global mode_num,newApp
		mode_num=10
		newApp=True # 中断了main函数的循环
		self.quit()


# 声明全局变量，用于新建Application对象时切换成不同模式的游戏
global newApp
newApp=False
if __name__=='__main__':
	# 循环，直到不切换游戏模式，循环是为了每次循环相当一步棋，存储了一次棋谱
	while True:
		newApp=False
		app=Application()
		app.title('填棋')
		app.mainloop()
		if newApp:
			app.destroy()
		else:
			break

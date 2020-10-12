"""该模块用于计算文件的hash值,基于支持GUI重新编写"""

import hashlib
import os
import time
import threading


func_dict = {
	"sha1": ("sha1", hashlib.sha1),
	"sha256": ("sha256", hashlib.sha256),
	"md5": ("md5", hashlib.md5),
	"sha224": ("sha224", hashlib.sha224),
	"sha512": ("sha512", hashlib.sha512),
	"sha384": ("sha384", hashlib.sha384)
}

rate_value = 0  # 用来记录当前读取的字节数

def get_md5(file_path, read_bytes=1024):
	"""
	用于计算文件的md5值
	:param file_path: 文件地址
	:param read_bytes: 一次读取的字节数
	:return: 文件md5值
	"""
	func = hashlib.md5()
	with open(file_path, 'rb') as f:
		while True:
			data = f.read(read_bytes)
			if data:
				func.update(data)
			else:
				break
	ret = func.hexdigest()
	return ret


def match(file_path, func_info, frame, read_bytes=10240):
	"""
	用于计算文件的hash值
	:param func_info: ("sha1", hashlib.sha1), 方法信息元组
	:param file_path: 文件地址
	:param read_bytes: 一次读取的字节数
	:return: ret={”算法类型“:func.hexdigest()}
	"""
	# h = hashlib.sha1()
	func = func_info[1]()
	total_size = os.path.getsize(file_path)
	count = 0  # 用以计算读取文件数据段次数
	frame.pb1["maximum"] = total_size
	frame.pb1["value"] = 0
	if total_size == 0:
		print("\r该文件内容为空！", end='')
	with open(file_path, 'rb') as f:
		while True:
			frame.pb1["value"] += read_bytes
			count += 1
			if total_size:
				rate = count * read_bytes / total_size  # 进度
				if rate >= 1:
					print("\r计算 %s 进度: %.2f%%" % (func_info[0], 100), end='')
				else:
					print("\r计算 %s 进度: %.2f%%" % (func_info[0], rate*100), end='')
			data = f.read(read_bytes)
			if data:
				# h.update(data)
				func.update(data)
			else:
				break
	print()  # 换行
	# ret = h.hexdigest()
	ret = {func_info[0]: func.hexdigest()}
	return ret



def match2(file_path, args, frame, read_bytes=8092):
	"""
	用于计算文件的hash值
	:param func_info: ("sha1", hashlib.sha1), 方法信息元组
	:param file_path: 文件地址
	:param read_bytes: 一次读取的字节数
	:return: ret={”算法类型“:func.hexdigest()}
	"""
	# h = hashlib.sha1()
	# func = func_info[1]()
	global rate_value
	rate_value = 0  # 进度值置零还原
	func_list = []
	# print(args)
	for item in args:
		if item in func_dict:
			func_list.append(func_dict[item][1]())
	# print(func_list)
	total_size = os.path.getsize(file_path)
	# count = 0  # 用以计算读取文件数据段次数
	frame.pb1["maximum"] = total_size
	frame.pb1["value"] = 0
	if total_size == 0:
		print("\r该文件内容为空！", end='')
	threading.Thread(target=show_rate, args=(frame, total_size)).start()
	with open(file_path, 'rb') as f:
		while True:
			rate_value += read_bytes
			data = f.read(read_bytes)
			if data:
				# h.update(data)
				for func in func_list:
					func.update(data)
			else:
				rate_value = total_size  # 为防止主线程，子线程还没运行完，导致进度条出现bug的问题
				break
	# ret = h.hexdigest()
	# ret = {func_info[0]: func.hexdigest()}
	ret = {}
	for index, item in enumerate(args):
		# print(index, item)
		ret[item] = func_list[index].hexdigest()
	# frame.pb1["value"] = total_size  # 为防止主线程，子线程还没运行完，导致进度条出现bug的问题
	# print(str(ret))
	return ret


def show_rate(frame, total_size):
	global rate_value
	while True:
		frame.pb1["value"] = rate_value
		# print(rate_value)
		if rate_value >= total_size:
			frame.pb1["value"] = rate_value
			break


def cal_hash_by_path(file_path, args, frame):
	"""
	用于提供外部调用，计算hash值
	:param file_path: 文件路径
	:param args: hash值算法元组('sha1', 'sha256', 'md5')
	:param frame: GUI 窗口，用于输出数据
	:return: {'size':xxx, "mtime":xxx, , 'sha1':xxx,'sha256':xxx,'md5':xxx}
	"""
	if os.path.isfile(file_path):  # 是文件
		file_path = os.path.abspath(file_path)
		size = os.path.getsize(file_path)
		mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.path.getmtime(file_path)))
		ret = {"size": size, "mtime": mtime}  # 用于储存单个文件的hash值信息{'size':xxx, "mtime":xxx, 'sha1':xxx,'sha256':xxx,'md5':xxx}
		print("正在计算: %s" % file_path)
		# for item in args:
		# 	if item in func_dict:
				# ret.update(match(file_path, func_dict[item], frame))
		# result = {file_path: ret}  # 用于储存结果{file:{"sha1":xxx,“sha256”:xxx,},}
		ret.update(match2(file_path, args, frame))
		result = {file_path: ret}
		# print(str(result))
		print_result(result, frame)
		return result
	elif os.path.isdir(file_path):  # 是目录
		# 获取文件路径列表
		path_list = []
		for root, dirs, files in os.walk(file_path):
			for filename in files:
				path_list.append(os.path.join(root, filename))
		result = cal_hash_by_list(path_list, args, frame)  # 格式{file_path:{"sha1":xxx,“sha256”:xxx,},}
		return result
	else:  # 因文件名包含空格导致的双层引号   例如：'"C:\\Users\\pro\\Desktop\\【显示器选购指南】从零开始教你选择「适合」自己的显示器 - YouTube.mkv"'
		try:
			file_path = file_path[1:-1]  # 去除最外层的引号
			# print(file_path)
			if os.path.exists(file_path):
				return cal_hash_by_path(file_path, args, frame)
		except Exception as e:
			print(e)
	

def cal_hash_by_list(file_list, args, frame):
	"""
	用于提供外部调用，批量计算hash值
	:param file_list: 保存文件路径的文件列表
	:param args: hash值算法元组('sha1', 'sha256', 'md5')
	:param frame: GUI 窗口，用于输出数据
	:return:
	"""
	# print(args)  # *args  (('sha1', 'sha256', 'md5'),)
	result = {}  # 记录结果 格式{file_path:{"sha1":xxx,“sha256”:xxx,},}
	for file_path in file_list:
		result.update(cal_hash_by_path(file_path, args, frame))
	return result


def writeHash(hash_path, str):
	"""
	用于将计算的到的hash值写出到文件
	:param hash_path: hash值记录文件路径
	:param str: 字符串内容
	:return:
	"""
	print("正在将计算的hash值记录到文件...")
	with open(hash_path, 'w', encoding='utf-8') as f:
		f.write(str)
	print("记录hash值到%s 完成！" % hash_path)


def print_result(temp_result, frame):
	"""
	获取用于输出到屏幕和写出到文件的result内容
	:param temp_result: hash值结果集
	:param frame: GUI 窗口，用于输出数据
	:return:
	"""
	for file in temp_result:
		frame.scr.insert("end", '%s:\t%s\n' % ("File", file))
		for item in temp_result[file]:
			info_str = "%s:\t%s" % (item, temp_result[file][item])
			if frame.upper.get():
				info_str = info_str.upper()
			frame.scr.insert("end", '%s\n' % info_str)
		frame.scr.insert("end", "\n")


	



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import numpy as np
import cv2
import time
import sys
from IkaUtils import *

class IkaScene_GameStart:

	# 720p サイズでの値
	mapname_width = 430
	mapname_left = 1280 - mapname_width
	mapname_top = 580
	mapname_height = 640 - mapname_top

	rulename_left = 640 - 300
	rulename_right = 640 + 300
	rulename_width = rulename_right - rulename_left
	rulename_top = 250
	rulename_bottom = 310
	rulename_height = rulename_bottom - rulename_top

	def load_mapname_mask(self, frame, map_name):
		if frame is None:
			print("%s のマスクデータが読み込めませんでした。" % map_name)

		img_map = IkaUtils.cropImageGray(frame, self.mapname_left, self.mapname_top, self.mapname_width, self.mapname_height)

		keys = [ 'name', 'mask' ]
		values = [ map_name, img_map ]
		return dict(zip(keys, values))

	def load_rulename_mask(self, frame, rule_name):
		if frame is None:
			print("%s のマスクデータが読み込めませんでした。" % rule_name)

		img_rule = IkaUtils.cropImageGray(frame, self.rulename_left, self.rulename_top, self.rulename_width, self.rulename_height)

		keys = [ 'name', 'mask' ]
		values = [ rule_name, img_rule ]
		return dict(zip(keys, values))

	def __init__(self):
		self.map_list = [
			{ 'name': 'タチウオパーキング', 'file': 'masks/gachi_tachiuo.png' },
			{ 'name': 'モズク農園',         'file': 'masks/nawabari_mozuku.png' },
			{ 'name': 'ネギトロ炭鉱',       'file': 'masks/gachi_negitoro.png'},
			{ 'name': 'アロワナモール',     'file': 'masks/nawabari_arowana.png'},
			{ 'name': 'デカライン高架下',   'file': 'masks/yagura_decaline.png' },
			{ 'name': 'Bバスパーク',        'file': 'masks/gachi_buspark.png' },
			{ 'name': 'ハコフグ倉庫',       'file': 'masks/gachi_hakofugu.png' },
			{ 'name': 'シオノメ油田',       'file': 'masks/gachi_shionome.png' },
			{ 'name': 'モンガラキャンプ場', 'file': 'masks/hoko_mongara.png' },
			{ 'name': 'ホッケふ頭',         'file': 'masks/nawabari_hokke.png' },
			{ 'name': 'ヒラメが丘団地',     'file': 'masks/nawabari_hirame.png' },
		]

		self.rule_list = [
			{ 'name': 'ガチエリア',     'file': 'masks/gachi_tachiuo.png'},
			{ 'name': 'ガチヤグラ',     'file': 'masks/yagura_decaline.png'},
			{ 'name': 'ガチホコバトル', 'file': 'masks/hoko_mongara.png'},
			{ 'name': 'ナワバリバトル', 'file': 'masks/nawabari_mozuku.png'},
		]

		for map in self.map_list:
			map['mask'] = IkaMatcher(
				self.mapname_left, self.mapname_top, self.mapname_width, self.mapname_height,
				img_file = map['file'],
				threshold = 0.98,
				orig_threshold = 0.5,
				pre_threshold_value = 160,
				label = 'map:%s' % map['name'],
			)

		for rule in self.rule_list:
			rule['mask'] = IkaMatcher(
				self.rulename_left, self.rulename_top, self.rulename_width, self.rulename_height,
				img_file = rule['file'],
				threshold = 0.98,
				orig_threshold = 0.5,
				pre_threshold_value = 160,
				label = 'rule:%s' % rule['name'],
			)

	def guess_map(self, frame):
		# マップ名を判断
		for map in self.map_list:
			r = map['mask'].match(frame)
			if r:
				return map

		return None

	def guess_rule(self, frame):
		# モード名を判断
		for rule in self.rule_list:
			r = rule['mask'].match(frame)
			if r:
				return rule
		
		return None

	def match(self, context):
		map = self.guess_map(context['engine']['frame'])
		rule = self.guess_rule(context['engine']['frame'])

		if not map is None:
			context['game']['map'] = map
		if not rule is None:
			context['game']['rule'] = rule

		return (map or rule)

if __name__ == "__main__":
	target = cv2.imread(sys.argv[1])

	context = {
		'engine': { 'frame': target },
		'game': {},
	}

	obj = IkaScene_GameStart()

	r = obj.match(context)

	print(r, context['game'])

	#cv2.imshow('Scene', target)
	#k = cv2.waitKey(3000) # 1msec待つ

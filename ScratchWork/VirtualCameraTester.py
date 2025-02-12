import cv2
import pyvirtualcam
# from PIL import ImageFont, ImageDraw, Image
import numpy as np
# import logger
#from pynput import keyboard


# import sys
from video_filter import Filter
import skeletalTracking


class Control:
	""" main class for this project. Starts webcam capture and sends output to virtual camera"""

	def __init__(self, webcam_source=0, width=640, height=480, fps=30):
		""" sets user preferences for resolution and fps, starts webcam capture

		:param webcam_source: webcam source 0 is the laptop webcam and 1 is the usb webcam
		:type webcam_source: int
		:param width: width of webcam stream
		:type width: int
		:param height: height of webcam stream
		:type height: int
		:param fps: fps of videocam stream
		:type fps: int
		"""
		self.webcam_source = webcam_source

		# initialize webcam capture
		self.cam = cv2.VideoCapture(self.webcam_source)
		self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
		self.cam.set(cv2.CAP_PROP_FPS, fps)

		# Query final capture device values (different from what i set??)
		# save as object variables
		self.width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
		self.fps = self.cam.get(cv2.CAP_PROP_FPS)

		# self.INTERVAL = 75 # how often to refresh skeleton in units of frames

		# print out status
		print('webcam capture started ({}x{} @ {}fps)'.format(self.width,
														self.height, self.fps))


		# filter object
		self.videofilter = Filter(self.width, self.height)

		# self.logger = logger.Logger()


	def run(self):
		""" contains main while loop to constantly capture webcam, process, and output

		:return: None
		"""


		with pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps) as virtual_cam:
			# print status
			print(
				'virtual camera started ({}x{} @ {}fps)'.format(virtual_cam.width, virtual_cam.height, virtual_cam.fps))
			virtual_cam.delay = 0
			frame_count = 0

			print("now printing secconds taken per frame:")
			skeletonPoints = []
			while True:

				# STEP 1: capture video from webcam
				ret, raw_frame = self.cam.read()
				#raw_frame = cv2.flip(raw_frame, 1)

				# draw box
				# for rgb_counter in range(0, 3):
				# 	raw_frame[0:100, 0:100, rgb_counter] = 100

				# STEP 2: process frames
				if raw_frame is None:
					continue

				# if frame_count % self.INTERVAL == 0:
				skeletonPoints = skeletalTracking.identifySkeleton(raw_frame)

				raw_frame = skeletalTracking.drawSkeleton(raw_frame, skeletonPoints)

				# convert frame to RGB
				color_frame = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)

				# add alpha channel
				out_frame_rgba = np.zeros(
					(self.height, self.width, 4), np.uint8)
				out_frame_rgba[:, :, :3] = color_frame
				out_frame_rgba[:, :, 3] = 255


				# STEP 3: send to virtual camera
				# virtual_cam.send(out_frame_rgba)
				virtual_cam.send(out_frame_rgba)
				virtual_cam.sleep_until_next_frame() # we might want to arrange something with scheduelingx

				frame_count += 1

# run program
if __name__ == '__main__':
	try:
		instance = Control()
		# instance.logger.startTimer()
		instance.run()
		# instance.logger.endTimer()
	except Exception as e:
		print("Something went wrong" + str(e))
		print(e)
	except:
		print("general error")

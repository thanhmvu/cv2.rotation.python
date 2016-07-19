import os
import glob
import cv2
import numpy as np
import math as m
from random import randint
import transformations as trans

""" Experimenting planar perspective transformation """

def drawPt(img,pt,color):
	cv2.circle(img, pt, 3, color, -1)

def ptToMat ((x,y)):
	return np.array([[x],[y],[1]])

def matToPt (ptMat):
	return (int(ptMat[0][0]/ptMat[2][0]), int(ptMat[1][0]/ptMat[2][0]))

def transform(pt, mat):
	return matToPt(np.dot(mat, ptToMat(pt)))


# translation matrix
def tl(dx,dy):
	return np.array([[1.0	, 0.0	, float(dx)],
					 [0.0	, 1.0	, float(dy)],
					 [0.0	, 0.0	,    1.0   ]])

# rotation matric
def rt(angle):
	p = m.pi
	a = m.radians(angle)
	return np.array([[  m.cos(a), m.sin(a),  0.0 ],
					 [ -m.sin(a), m.cos(a),  0.0 ],
					 [    0.0   ,   0.0   ,  1.0 ]])

# scale about origin
def sc(W,H):
	return np.array([[ float(W)	, 0.0		, 0.0],
					 [ 0.0		, float(H)	, 0.0],
					 [ 0.0		, 0.0		, 1.0]])


def localCoords(P):
	"""
	Adopted from http://stackoverflow.com/questions/26369618/getting-local-2d-coordinates-of-vertices-of-a-planar-polygon-in-3d-space
	
	Return the local 2D coordinates of each 3D points in set P, given that 
	- these points are on the same plane in the original 3D coordinate system
	- the size of P is greater or equal to 3
	"""

	loc0 = P[0]                      # local origin
	locy = np.subtract(P[len(P)-1],loc0)  	 # local Y axis
	normal = np.cross(locy, np.subtract(P[1],loc0)) # a vector orthogonal to polygon plane
	locx = np.cross(normal, locy)      # local X axis

	# normalize
	locx /= np.linalg.norm(locx)
	locy /= np.linalg.norm(locy)

	local_coords = [(np.dot(np.subtract(p,loc0), locx),  # local X coordinate
	                 np.dot(np.subtract(p,loc0), locy))  # local Y coordinate
	                for p in P]

	return local_coords

def convertMatrix(M1):
	""" Convert 4x4 3D perpsective matrix to 3x3 2D perspective matrix """

	# Apply the matrix to transform points
	srcPts3D = [(0.0,0.0,0.0), (200.0,0.0,0.0), (200.0,100.0,0.0), (0.0,100.0,0.0)]
	dstPts3D = []
	for pt in srcPts3D:
		homoPt = np.array([[pt[0]], [pt[1]], [pt[2]], [1]])
		out = np.dot(M1,homoPt)
		dstPt = [out[0][0]/out[3][0],out[1][0]/out[3][0],out[2][0]/out[3][0]]
		dstPts3D.append(dstPt)

	# Convert 3D coords to 2D coords
	srcPts2D = np.float32(localCoords(srcPts3D))
	dstPts2D = np.float32(localCoords(dstPts3D))

	# get 3x3 pespsective matrix
	M2 = cv2.getPerspectiveTransform(srcPts2D, dstPts2D)

	return M2


blue = (255,0,0)
green = (0,255,0)
red = (0,0,255)
white = (255,255,255)

""" ====================== Main code ====================== """
''' Framework
Strategy 1: 

=> 	(pt, angle, scale, ...) -----(transformations.py)---> (needed matrices)
=> 	(4 src pts) -------------------(M1 *M2 *M3 ...)-----> (4 dst pts)
	use this to transform (image corners) and (title corners)
=> 	original image ----(warpPerspective + 8 pts)---> transformed image


Notes:
- cv2.warpPerspective takes a 3x3 float matrix (not 4x4)
- combine 3x3 matrices, not 4x4 ones
- applying dot product of all matrices with warpPerspective returns different result from applying them one by one
- keep in mind that dot product of matrices is not commutative

'''

# Draw an image
h, w = (400,600)
img = np.zeros((h,w,3), np.uint8) 
img[:,:] = (150,150,150)
offset = 50
cv2.rectangle(img,(offset,offset),(w-offset,h-offset),blue,3)

# =============================== perpespective matrix
# Generate 4x4 perspective matrix
point = (-w/2, h/2, w/2)
normal = (-2, 0, 1)
direction = None
perspective = (-w, h/2, w)
M1 = trans.projection_matrix(point, normal, direction, perspective)
# Convert to 3x3 2D matrix
M1 = convertMatrix(M1)

# =============================== translation
M2 = tl(100,100)

# =============================== rotation
M3 = rt(30)



# Apply 3x3 matrix to transform the image
# =====> one way to do it
img = cv2.warpPerspective(img,M1,(w,h))
img = cv2.warpPerspective(img,M2,(w,h))
img = cv2.warpPerspective(img,M3,(w,h))

# =====> another way to do it. but the result is different
M = np.dot(M1,M2,M3)
# img = cv2.warpPerspective(img,M,(w,h))


# Visualize 
cv2.imshow("image",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
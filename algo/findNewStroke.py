import cv2
import numpy as np
import time
import copy

th = 125
th_area = 400

def Test(image_first_path,image_second_path):
    ROI = parseTwoFrame(cv2.imread(image_first_path),cv2.imread(image_second_path),gray_input=False,visualize=True,filtSmall=True,savePng=True)
    print("ROI:",ROI)

def parseTwoFrame(image_first,image_second,gray_input=False,visualize=True,filtSmall=True,savePng=False):
    if visualize==True and savePng==True:
        image_full = copy.copy(image_second)
    if gray_input==False:
        image_first = np.array(cv2.cvtColor(image_first,cv2.COLOR_RGB2GRAY))
        image_second = np.array(cv2.cvtColor(image_second,cv2.COLOR_RGB2GRAY))
    image_first[image_first<th]=0
    image_first[image_first>=th]=255
    image_second[image_second<th]=0
    image_second[image_second>=th]=255
    image_residual = np.array(cv2.bitwise_xor(image_second,image_first))
    image_residual[image_residual<th]=0
    image_residual[image_residual>=th]=255

    mask = np.zeros((image_residual.shape[0], image_residual.shape[1]), np.uint8)
    image_alignment = copy.copy(image_residual)

    mask_multi = ((image_residual==0) & (image_second==0))
    image_alignment[mask_multi]=255
    mask[mask_multi]=255

    ret, labels, stats, centroid = cv2.connectedComponentsWithStats(image_alignment,connectivity=8)

    if visualize==True:
        output = np.zeros((image_residual.shape[0], image_residual.shape[1], 3), np.uint8)
        for i in range(1, ret):
            mk = labels == i
            output[:, :, 0][mk] = np.random.randint(0, 255)
            output[:, :, 1][mk] = np.random.randint(0, 255)
            output[:, :, 2][mk] = np.random.randint(0, 255)

    for i in range(1, ret):
        mk = labels == i
        d = mask[mk]==255
        if (np.sum(d)/d.shape[0])>0:
            image_residual[mk]=0

    ret, labels, stats, centroid = cv2.connectedComponentsWithStats(image_residual,connectivity=8)
    max_area = sorted(stats, key = lambda s : s[-1], reverse = False)[-2]

    if visualize==True:
        cv2.rectangle(output, (max_area[0], max_area[1]), (max_area[0] + max_area[2], max_area[1] + max_area[3]), (255, 255, 255), 1)
        if savePng==True:
            cv2.imwrite("/Users/user/Downloads/out_color.png",output)

    if savePng==True:
        cv2.imwrite("/Users/user/Downloads/out_residual.png",image_residual)

    if filtSmall:
        ret, labels, stats, centroid = cv2.connectedComponentsWithStats(image_residual,connectivity=8)
        for i in range(1, ret):
            mk = labels == i
            area = np.sum(mk)
            if area<th_area:
                image_residual[mk]=0

    if savePng==True:
        cv2.imwrite("/Users/user/Downloads/out_residual_after_filter.png",image_residual)
    
    if visualize==True and savePng==True:
        cv2.imwrite("/Users/user/Downloads/out_roi.png",image_full[max_area[1]:max_area[1] + max_area[3],max_area[0]:max_area[0] + max_area[2],:])

    return max_area,output

#Test("/Users/user/Downloads/2.png","/Users/user/Downloads/1.png")
#Test("/Users/user/Downloads/a.jpg","/Users/user/Downloads/b.jpg")
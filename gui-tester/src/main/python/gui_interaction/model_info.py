import config as cfg
from yolo import Yolo
from cv2 import imread, resize
import numpy as np
import tensorflow as tf
import sys
import gc
import math
import random
import os
import pickle
import re

tf.logging.set_verbosity(tf.logging.INFO)

totals = []
yolo = None

for i in range(10):
    totals.append(0)

def normalise_point(point, val):
    i = point*val
    return i, math.floor(i)

def normalise_label(label):
    px, cx = normalise_point(max(0, min(1, label[0])), cfg.grid_shape[0])
    py, cy = normalise_point(max(0, min(1, label[1])), cfg.grid_shape[1])
    return [
               px,
               py,
               max(0, min(cfg.grid_shape[0], label[2]*cfg.grid_shape[0])),
               max(0, min(cfg.grid_shape[1], label[3]*cfg.grid_shape[1])),
               label[4]
           ], (cx, cy)

def load_files(raw_files):
    raw_files = [f.replace("/data/acp15tdw", "/home/thomas/experiments") for f in raw_files]
    label_files = [f.replace("/images/", "/labels/") for f in raw_files]
    label_files = [f.replace(".png", ".txt") for f in label_files]

    pickle_files = [f.replace("/images/", "/pickle/") for f in raw_files]
    pickle_files = [f.replace(".png", ".pickle") for f in pickle_files]

    images = []
    labels = []
    object_detection = []

    for i in range(len(raw_files)):
        f = raw_files[i]
        f_l = label_files[i]
        image = np.int16(imread(f, 0))

        image = np.uint8(resize(image, (cfg.width, cfg.height)))
        image = np.reshape(image, [cfg.width, cfg.height, 1])


        image = np.reshape(image, [cfg.width, cfg.height, 1])
        images.append(image)

        # read in format [c, x, y, width, height]
        # store in format [c], [x, y, width, height]
        with open(f_l, "r") as l:
            obj_detect = [[0 for i in
                           range(cfg.grid_shape[0])]for i in
                          range(cfg.grid_shape[1])]
            imglabs = [[[0 for i in
                         range(5)]for i in
                        range(cfg.grid_shape[1])] for i in
                       range(cfg.grid_shape[0])]

            for line in l:
                elements = line.split(" ")
                #print(elements[1:3])
                normalised_label, centre = normalise_label([float(elements[1]), float(elements[2]),
                                                            float(elements[3]), float(elements[4]), 1])
                x = max(0, min(int(centre[0]), cfg.grid_shape[0]-1))
                y = max(0, min(int(centre[1]), cfg.grid_shape[1]-1))
                imglabs[y][x] = normalised_label
                obj_detect[y][x] = int(elements[0])
                totals[int(elements[0])] += 1
                #obj_detect[y][x][int(elements[0])] = 1

            object_detection.append(obj_detect)
            labels.append(imglabs)

    return images, labels, object_detection

def print_info(imgs, labels, classes, dataset):

    density = np.array([[[0 for i in
                          range(11)]for i in
                         range(cfg.grid_shape[1])] for i in
                        range(cfg.grid_shape[0])])

    pixels = np.array([0 for i in
                       range(30)])

    for i in range(imgs.shape[0]):

        class_count = np.array([0 for i in
                                range(10)])



        displacement = 255/30

        for j in range(30):
            quantity = np.sum((np.equal((imgs[0]/displacement).astype(np.int32), j).astype(np.float32)))
            pixels[j] += quantity

        for x in range(13):
            for y in range(13):
                if (labels[i,x,y,4] == 1):
                    c = classes[i,x,y]
                    density[y,x,0] = density[x,y,0] + 1
                    density[y,x,c+1] = density[x,y,c+1] + 1
                    class_count[c] += 1

                    with open("label_dims.csv", "a") as file:
                        file.write(str(i) + "," + yolo.names[c] + ",width," + str(labels[i,x,y,2]/13) + "," + dataset + "\n")
                        file.write(str(i) + "," + yolo.names[c] + ",height," + str(labels[i,x,y,3]/13) + "," + dataset + "\n")
                        file.write(str(i) + "," + yolo.names[c] + ",area," + str(labels[i,x,y,2] * labels[i,x,y,3]/13) + "," + dataset + "\n")

        for c in range(len(class_count)):
            with open("class_count.csv", "a") as file:
                file.write(str(i) + "," + yolo.names[c] + "," + str(class_count[c]/np.sum(class_count)) + "," + dataset + "\n")

    for j in range(30):
        with open("img_hist.csv", "a") as file:
            file.write(str(j) + "," + str(pixels[j]) + "," + dataset + "\n")



    for x in range(13):
        for y in range(13):
            for c in range(11):
                with open("label_heat.csv", "a") as file:
                    dens = density[x, y, c] / np.amax(density[..., c])
                    cl = "total"
                    if (c > 0):
                        cl = yolo.names[c-1]
                    file.write(str(x) + "," + str(y) + "," + str(dens) + "," + cl + "," + dataset + "\n")

if __name__ == '__main__':

    training_file = cfg.data_dir + "/train.txt"

    valid_images = []

    real_images = []

    pattern = re.compile(".*\/([0-9]+).*")

    yolo = Yolo()

    with open("img_hist.csv", "w") as file:
        file.write("pixel_value,quantity,dataset" + "\n")

    with open("label_heat.csv", "w") as file:
        file.write("x,y,density,class,dataset" + "\n")

    with open("class_count.csv", "w") as file:
        file.write("img,class,count,dataset" + "\n")

    with open("label_dims.csv", "w") as file:
        file.write("img,class,dimension,value,dataset" + "\n")

    with open(training_file, "r") as tfile:
        for l in tfile:

            file_num = int(pattern.findall(l)[-1])

            if file_num <= 243:
                real_images.append(l.strip())



    valid_file = cfg.data_dir + "/validate.txt"

    with open(valid_file, "r") as tfile:
        for l in tfile:
            file_num = int(pattern.findall(l)[-1])

            if file_num <= 243:
                real_images.append(l.strip())

    valid_file = cfg.data_dir + "/test.txt"

    with open(valid_file, "r") as tfile:
        for l in tfile:
            file_num = int(pattern.findall(l)[-1])

            if file_num <= 243:
                real_images.append(l.strip())

    valid_file = cfg.data_dir + "/test-balanced.txt"

    with open(valid_file, "r") as tfile:
        for l in tfile:
            file_num = int(pattern.findall(l)[-1])

            if file_num > 243 and file_num > 15256 and file_num < 20000:
                valid_images.append(l.strip())

    #valid_images = random.sample(valid_images, cfg.batch_size)

    #random.shuffle(valid_images)

    valid_images = valid_images[:400]

    with tf.device(cfg.gpu):

        v_imgs, v_labels, v_obj_detection = load_files(
            valid_images)

        v_imgs = np.array(v_imgs)

        v_labels = np.array(v_labels)

        v_obj_detection = np.array(v_obj_detection)

        print("Validation set ---")

        print_info(v_imgs, v_labels, v_obj_detection, "synthetic")


        del(v_imgs, v_labels, v_obj_detection)



        v_imgs, v_labels, v_obj_detection = load_files(
            real_images)

        v_imgs = np.array(v_imgs)

        v_labels = np.array(v_labels)

        v_obj_detection = np.array(v_obj_detection)

        print("Real set ---")

        print_info(v_imgs, v_labels, v_obj_detection, "real")

        del(v_imgs, v_labels, v_obj_detection)



        gc.collect()

sys.exit()
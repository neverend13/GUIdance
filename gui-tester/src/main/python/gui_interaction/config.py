# ------------------------
# User Specific          |
# ------------------------
data_dir = "/home/thomas/work/gui_image_identification/public"
output_dir = "/home/thomas/work/gui_image_identification/output"

# ------------------------
# YOLO variables         |
# ------------------------

# Generated anchors from GUI Image dataset using
# K-Means clustering
anchors = [0.9817857382941845, 9.398278193098788,
           5.52115919597547, 6.985948423888699,
           0.9090057538352261, 1.94398118062752,
           2.4060115242354794, 0.7252024765267888,
           9.922079927099324, 1.5033104111199442]

# resolution of input image
width = 416
height = 416

# Threshold to identify a bounding box as correct
threshold = 0.1

# Use Nvidia CUDA for training?
cudnn_on_gpu = False

# Shape of the grid (subdivisions of image to apply anchors to)
grid_shape = [13, 13]

# ------------------------
# input files            |
# ------------------------

# Relative to [data_dir]

names_file = "data.names"
train_file = "train.txt"
validate_file = "validate.txt"
test_file = "test.txt"

images_dir = "images"
labels_dir = "labels"


# ------------------------
# training variables     |
# ------------------------
learning_rate_start = 0.0001
learning_rate_min = 0.00001
learning_rate_decay = 0.9
momentum = 0.9
object_detection_threshold = 0.9

# maximum training epochs
epochs = 100000

# Amount of images to train on in parallel
batch_size = 16

# standard deviation of variables when initialised
var_sd = 0.1


# ------------------------
# output locations       |
# ------------------------

weights_dir = "weights"
results_dir = "results"
log_file = "loss.csv"

# GPU to use (defaults to CPU)
gpu = "/job:localhost/replica:0/task:0/device:CPU:0"
# gpu = "/gpu:0"


# ------------------------
# training weights       |
# ------------------------

coord_weight = 1.0
obj_weight = 5.0
noobj_weight = 1.0
class_weight = 1.0

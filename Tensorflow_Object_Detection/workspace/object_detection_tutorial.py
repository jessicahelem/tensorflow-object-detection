#!/usr/bin/env python
# coding: utf-8

# # Object Detection Demo
# Welcome to the object detection inference walkthrough!  This notebook will walk you step by step through the process of using a pre-trained model to detect objects in an image. Make sure to follow the [installation instructions](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md) before you start.

# # Imports

# In[1]:

'''import six.moves.urllib as urllib, tarfile
from collections import defaultdict
from io import StringIO
import zipfile
from IPython import get_ipython'''
import imutils
import numpy as np
import os
from os import listdir
from os.path import isfile, join

import sys
import tensorflow as tf
import cv2

from distutils.version import StrictVersion
import matplotlib

matplotlib.use('Qt5Agg')

from matplotlib import pyplot as plt

from PIL import Image

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from object_detection.utils import ops as utils_ops

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
    raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')

# ## Env setup

# In[2]:


# This is needed to display the images.


# get_ipython().run_line_magic('matplotlib', 'inline')
'''try:
    get_ipython().magic('matplotlib inline')
except:
    plt.ion()'''

# ## Object detection imports
# Here are the imports from the object detection module.

# In[3]:


from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# # Model preparation

# ## Variables
# 
# Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `PATH_TO_FROZEN_GRAPH` to point to a new .pb file.  
# 
# By default we use an "SSD with Mobilenet" model here. See the [detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.

# In[4]:


# What model to download.
MODEL_NAME = 'trained-inference-graphs/output_inference_graph_v1'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('annotations', 'label_map.pbtxt')

NUM_CLASSES = 2

# ## Download Model

# In[4]:


# ## Load a (frozen) Tensorflow model into memory.

# In[5]:

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.compat.v2.io.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

# In[6]:


category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


# ## Helper code

# In[7]:


def load_image_into_numpy_array(image):
    last_axis = -1
    dim_to_repeat = 2
    repeats = 3
    grscale_img_3dims = np.expand_dims(image, last_axis)
    training_image = np.repeat(grscale_img_3dims, repeats, dim_to_repeat).astype(np.uint8)
    assert len(training_image.shape) == 3
    assert training_image.shape[-1] == 3
    return training_image
    # (im_width, im_height) = image.size
    # return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


# # Detection

# In[8]:


# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
import os

PATH_TO_TEST_IMAGES_DIR = 'test_images'
TEST_IMAGE_PATHS = [f for f in listdir(PATH_TO_TEST_IMAGES_DIR) if isfile(join(PATH_TO_TEST_IMAGES_DIR, f))]

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)


# In[9]:


def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.compat.v1.Session() as sess:

            # Get handles to input and output tensors
            ops = tf.compat.v1.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.compat.v1.get_default_graph().get_tensor_by_name(
                        tensor_name)

            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image.shape[1], image.shape[2])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)
            image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name('image_tensor:0')

            # Run inference
            output_dict = sess.run(tensor_dict,
                                   feed_dict={image_tensor: image})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                'detection_classes'][0].astype(np.int64)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]
            coordinates = vis_util.return_coordinates(
                image,
                np.squeeze(output_dict['detection_boxes']),
                np.squeeze(output_dict['detection_classes']).astype(np.int32),
                np.squeeze(output_dict['detection_scores']),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=0.2)



        verde = (0, 255, 0)
        # xmax = coordinates[0][2]
        # ymin = coordinates[0][1]
        # xmin = coordinates[1][0]
        # ymax = coordinates[1][3]

        #nucleo
        xmin = coordinates[0][0]
        #delta
        xmax = coordinates[1][2]
        #nucleo
        ymin = coordinates[0][1]
        #delta
        ymax = coordinates[1][3]


 

        try:
            teste= cv2.rectangle(image_np, (xmax,ymin),(xmin,ymax), verde, 2)
            # teste = cv2.rectangle(image_np, (xmax,ymin),(xmin,ymax), verde, 2)
            # teste = cv2.rectangle(image_np, (xmin,xmax),(ymin,ymax), verde, 2)



        except (IndexError, ValueError):
            coordinates = 'null'
            print('N??o foi encontrado coordenadas na imagem')
            pass

    return output_dict, coordinates


# In[10]:


for image_path in range(0, len(TEST_IMAGE_PATHS)):
    image = cv2.imread(join(PATH_TO_TEST_IMAGES_DIR, TEST_IMAGE_PATHS[image_path]), 0)
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    output_dict, t2 = run_inference_for_single_image(image_np_expanded, detection_graph)
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks'),
        use_normalized_coordinates=True,
        line_thickness=8)




    image_path += 1

    cv2.imshow("image %04i" % image_path,image_np)

    cv2.imwrite("resultado/fingerprint%04i.png" % image_path, image_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




def cropped_image(image):
    output_dict, t2 = run_inference_for_single_image(image_np_expanded, detection_graph)

    try:
        y = t2[0][1]
        x = t2[1][0]
        w = t2[0][2] - x
        h = t2[1][3] - y
        left = image[y:y + h, x:x + w]
        right = image[y:y + h, x + w:x + w + w]

    except (IndexError, ValueError):

        y, x, w, h = 'null'
        cv2.imshow("image %04i" % image_path, image_np)

        print('N??o foi encontrado coordenadas na imagem')


    return image
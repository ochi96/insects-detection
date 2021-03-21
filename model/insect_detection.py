import matplotlib.pyplot as plt
import os
from PIL import Image, ImageFont, ImageDraw
import random
import tensorflow as tf
import numpy as np

IMAGE_SIZE = (12, 8)
PATH_TO_FROZEN_GRAPH = "model/frozen_inference_graph_rcnn.pb"
label = "model/label_map.txt"
FONT_NAME = 'arial.ttf'
COLORS = ['Green', 'Red', 'Pink', 'Olive', 'Brown', 'Gray', 'Cyan', 'Orange']
N_CHANNELS = 3
TEXT_COLOR = 'Black'
IMAGE_TENSOR_KEY = 'image_tensor'
DETECTION_BOXES_KEY = 'detection_boxes'
DETECTION_SCORES_KEY = 'detection_scores'
DETECTION_CLASSES_KEY = 'detection_classes'
TENSOR_SUFFIX = ':0'
IMAGE_NP_KEY = 'image_np'
RESULTS_KEY = 'results'


class ObjectResult():
    """
    Represents a detection result, containing the object label,
    score confidence, and bounding box coordinates.
    """
    def __init__(self, label, score, box):
        self.label = label
        self.score = score
        self.box = box
    
    def __repr__(self):
        return '{0} ({1}%)'.format(self.label, int(100 * self.score))


def load_image_into_numpy_array(image):
    """
    Converts a PIL image into a numpy array (height x width x channels).
    :param image: PIL image
    :return: numpy array
    """
    (width, height) = image.size
    return np.array(image.getdata()) \
        .reshape((height, width, N_CHANNELS)).astype(np.uint8)


def process_output(classes, scores, boxes, category_index):
    """
    Processes classes, scores, and boxes, gathering in a list of ObjectResult.
    :param classes: list of class id
    :param scores: list of scores
    :param boxes: list of boxes
    :param category_index: label dictionary
    :return: list of ObjectResult
    """
    results = []
    for clazz, score, box in zip(classes, scores, boxes):
        if score > 0.0:
            label = category_index[clazz]#[NAME_KEY]
            obj_result = ObjectResult(label, score, box)
            results.append(obj_result)
    return results

def draw_labeled_boxes(image_np, results, min_score=.3):
    """
    Draws labeled boxes according to results on the given image.
    :param image_np: numpy array image
    :param results: list of ObjectResult
    :param min_score: optional min score threshold, default is 40%
    :return: numpy array image with labeled boxes drawn
    """
    results.sort(key=lambda x: x.score, reverse=False)
    image_np_copy = image_np.copy()
    for r in results:
        if r.score >= min_score:
            color_idx = random.randint(0, len(COLORS) - 1)
            color = COLORS[color_idx]
            image_pil = Image.fromarray(np.uint8(image_np_copy)).convert('RGB')
            draw_bounding_box_on_image(image_pil, r.box, color, str(r))
            np.copyto(image_np_copy, np.array(image_pil))

    return image_np_copy

def get_suitable_font_for_text(text, img_width, font_name, img_fraction=0.12):
    """
    Calculates a suitable font for the image given the text and fraction.
    :param text: text that will be drawn
    :param img_width: width of the image
    :param font_name: name of the font
    :param img_fraction: optional desired image fraction allowed for the text 
    :return: suitable font
    """
    fontsize = 1
    font = ImageFont.truetype(FONT_NAME, fontsize)
    while font.getsize(text)[0] < img_fraction*img_width:
        fontsize += 1
        font = ImageFont.truetype(font_name, fontsize)
    return font



def draw_bounding_box_on_image(image, box, color, box_label):
    """
    Draws the box and label on the given image.
    :param image: PIL image
    :param box: numpy array containing the bounding box information
                [top, left, bottom, right]
    :param color: bounding box color
    :param box_label: bounding box label
    """
    im_width, im_height = image.size
    top, left, bottom, right = box

    # Normalize coordinates
    left = left * im_width
    right = right * im_width
    top = top * im_height
    bottom = bottom * im_height

    # Draw the detected bounding box
    line_width = int(max(im_width, im_height) * 0.005)
    draw = ImageDraw.Draw(image)
    draw.rectangle(((left, top), (right, bottom)),
                   width=line_width,
                   outline=color)

    # Get a suitable font (in terms of size with respect to the image)
    font = get_suitable_font_for_text(box_label, im_width, FONT_NAME)
    text_width, text_height = font.getsize(box_label)

    # Draw the box label rectangle
    text_bottom = top + text_height
    text_rect = ((left, top),
                 (left + text_width + 2 * line_width,
                  text_bottom + 2 * line_width))
    draw.rectangle(text_rect, fill=color)

    # Draw the box label text 
    # right below the upper-left horizontal line of the bounding box
    text_position = (left + line_width, top + line_width)
    draw.text(text_position, box_label, fill=TEXT_COLOR, font=font)



def show_image(filename, image):
    """
    Shows the given image with its filename as title.
    :param filename: image filename
    :param image: image to show
    """
    plt.figure(figsize=IMAGE_SIZE)
    plt.title(filename)
    plt.axis('off')
    plt.imshow(image)
    plt.show()

def run_inference(graph, image_np):
    """
    Runs the inference on the given image.
    :param graph: tensorflow graph
    :param image_np: numpy image
    :return: dictionary with detected classes 
             and their corresponding scores and boxes
    """
    output_tensor_dict = {
        DETECTION_BOXES_KEY: DETECTION_BOXES_KEY + TENSOR_SUFFIX,
        DETECTION_SCORES_KEY: DETECTION_SCORES_KEY + TENSOR_SUFFIX,
        DETECTION_CLASSES_KEY: DETECTION_CLASSES_KEY + TENSOR_SUFFIX
    }

    with graph.as_default():
        with tf.Session() as sess:
            input_tensor = tf.get_default_graph()\
                .get_tensor_by_name(IMAGE_TENSOR_KEY + TENSOR_SUFFIX)
            image_np_expanded = np.expand_dims(image_np, axis=0)
            input_tensor_dict = {input_tensor: image_np_expanded}
            output_dict = sess.run(output_tensor_dict,
                                   feed_dict=input_tensor_dict)

            return {
                DETECTION_BOXES_KEY: 
                    output_dict[DETECTION_BOXES_KEY][0],
                DETECTION_SCORES_KEY: 
                    output_dict[DETECTION_SCORES_KEY][0],
                DETECTION_CLASSES_KEY: 
                    output_dict[DETECTION_CLASSES_KEY][0].astype(np.int64)
            }


def detect(raw_image):
    with open(label, 'r') as f:
        pairs = (l.strip().split('.') for l in f.readlines())
        category_index = dict((int(k), v) for k, v in pairs)

    graph = tf.Graph()
    with graph.as_default():
        graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
            serialized_graph = fid.read()
            graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(graph_def, name='')

    file_result_dict = {}
    image_np = load_image_into_numpy_array(Image.open(raw_image))
    output_dict = run_inference(graph, image_np)
    results = process_output(output_dict[DETECTION_CLASSES_KEY],
                            output_dict[DETECTION_SCORES_KEY],
                            output_dict[DETECTION_BOXES_KEY],
                            category_index)
    file_result_dict[raw_image] = { IMAGE_NP_KEY: image_np, RESULTS_KEY: results }

    for filename, img_results_dict in file_result_dict.items():
        processed_image = draw_labeled_boxes(img_results_dict[IMAGE_NP_KEY], img_results_dict[RESULTS_KEY])
        #show_image(filename, processed_image)
    return processed_image

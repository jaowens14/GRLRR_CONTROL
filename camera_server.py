import cv2
import asyncio
from logger import grlrr_log
import numpy as np
import base64
from queues import image_queue, offset_queue, angle_queue


import cv2
import numpy as np

red = (0,0,255)
green = (0,255,0)
blue = (255,0,0)
purple = (160, 32, 240)
class Camera:
    def __init__(self, height, width):
        self.height = height
        self.width = width
c0 = Camera(0,0)



def draw_line_with_end_points(image, points, color):
    x1, y1, x2, y2 = points
    cv2.line(image, (x1,y1),(x2, y2), color, 1)
    cv2.circle(image, (x1,y1), radius=3, color=red, thickness=3)
    cv2.circle(image, (x2,y2), radius=3, color=red, thickness=3)

def draw_a_lot_of_points(image, xs, ys, color):
    for i in range(len(xs)):
        cv2.circle(image, (xs[i], ys[i]), radius=3, color=color, thickness=3)


def get_image(vidcap):
    return vidcap.read()

def make_gray_image(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def define_vertices(image):
    offset = 2
    vertices = []
    offset_vertices = []
    h, w = image.shape
    u = w//8 # 128 # section unit width
    sh = 2 ** 6 # section height
    # define vertices
    for y in range(0, h, sh): 
        y1 = y
        y2 = y+sh

        x1 = (3 * u) - y1 // 2
        x2 = (5 * u) + y1 // 2

        x3 = (3 * u) - y2 // 2
        x4 = (5 * u) + y2 // 2

        roi_vertices = [(x1,   y1), (x2,   y1), (x4,   y2), (x3,   y2),]

        offset_roi_vertices = [(x1+offset,   y1+offset), (x2-offset,   y1+1), (x4-offset,   y2-offset), (x3+offset,   y2-offset),]

        vertices.append(roi_vertices)
        offset_vertices.append(offset_roi_vertices)
    return vertices, offset_vertices


def image_to_sections(image, vertices):

    sections = []

    for vertex in vertices:
        mask = np.zeros_like(image) # create a empty matrix

        cv2.fillPoly(mask, np.int32([vertex]), 255) # draw roi on empty

        roi = cv2.bitwise_and(image, mask) # union with input image and mask

        sections.append(roi)

    return sections



def get_edge_closest_to_center(lefts, rights):
    if lefts.any() and rights.any():
        return lefts[np.argsort(get_location(lefts))][0], rights[np.argsort(get_location(rights))][0]
    else: 
        return [[0,0,0,0]], [[0,0,0,0]]


def detect_edges_in_section(section, vertex):
    h, w = section.shape
    offset_mask = np.zeros_like(section) # create a empty matrix
    blurred = cv2.GaussianBlur(section, (5, 5), 0) # blur the section
    edges = cv2.Canny(blurred, 50, 150) # detect edges

    cv2.fillPoly(offset_mask, np.int32([vertex]), 255) # draw offset roi on mask

    roi = cv2.bitwise_and(edges, offset_mask) # union with offset mask
    
    # detect lines in the real roi
    detected_edges = cv2.HoughLinesP(image=roi, rho=1, theta=np.pi / 180, threshold=25, minLineLength= 2 ** 5, maxLineGap=10) # these parameters need to be updated based on the size of the section
    
    if detected_edges is not None:
        #for edge in detected_edges:
        #    draw_line_with_end_points(section, edge[0], blue)
        #cv2.imshow("section", section)
        #cv2.waitKey(0)
        left_edges, right_edges = split_edges_into_left_and_right(detected_edges, section)
        left_edges, right_edges = filter_edges_by_slope(left_edges, right_edges)
        left_edge, right_edge = get_edge_closest_to_center(left_edges, right_edges)
        return left_edge, right_edge # detected_edges # vstack the edges to get them all
    else:
        return [[[0,0,0,0]]]

def gather_all_edges(sections, offsets):
    # this is a vstack of a list of results. 
    # each result is the return from the detect edges function 
    # which was passed the image section and the offsets
    return np.vstack([detect_edges_in_section(section, offsets[i]) for i, section in enumerate(sections)])



def get_slopes(edges):
    # get the vectors    
    x1 = edges[:, :, 0]
    y1 = edges[:, :, 1]
    x2 = edges[:, :, 2]
    y2 = edges[:, :, 3]
    v = np.hstack([x2-x1, y2-y1])
    unit_vectors = (v.T / np.linalg.norm(v, axis=1)).T # had to rework this for vector math
    return unit_vectors[:,1] / unit_vectors[:,0]

def get_location(edges):
    x1 = edges[:, :, 0]
    y1 = edges[:, :, 1]
    x2 = edges[:, :, 2]
    y2 = edges[:, :, 3]
    v = np.hstack([x2+x1, y2+y1]) * 0.5 # vector mid point
    return v[:, 0].astype(int) # return xs and compare to width of image outside

def get_z_score(edges):
    slopes = get_slopes(edges)
    return (slopes - np.mean(slopes)) / np.std(slopes)


def split_edges_into_left_and_right(edges, image):
    h, w = image.shape
    rights = edges[get_location(edges) > w//2] # right edges on the right side of the image
    lefts = edges[get_location(edges) < w//2] # left edges on the left side of the image
    return lefts, rights


def filter_edges_by_slope(left_edges, right_edges):
    # the ROI slope is about 2.0. 
    # this comes from the define_vertices function. 
    # these lines are kind of confusing because when you look at the edges you may think that the slope sign is wrong.
    # this is the sign of the slope in image space. So (0,0) is in the upper left instead of lower right.
    roi_s = 2.0
    tol = 1.5
    right_edges = right_edges[(get_slopes(right_edges) < roi_s+tol) & (get_slopes(right_edges) >= roi_s-tol)] 
    # needs to be less then the roi_slope plus tol and greater than toi_slope minus the tol
    left_edges = left_edges[(get_slopes(left_edges) > -(roi_s+tol)) & (get_slopes(left_edges) <= -(roi_s-tol))] 
    return left_edges, right_edges


def check_fit(xs, ys):
    xs = np.reshape(xs, (xs.shape[0],))
    ys = np.reshape(ys, (ys.shape[0],))
    #print(xs.shape)
    coefficients, err, _, _,_ = np.polyfit(xs, ys, deg=1, full=True) # highest power first
    #print("coef", coefficients)
    y = np.polyval(coefficients, xs)
    return np.abs(y-ys)

def estimate_edge(edges, image):
    edges = edges[~np.all(edges == 0, axis=(1, 2))] # this removes any zero edges

    x1 = edges[:, :, 0]
    y1 = edges[:, :, 1]
    x2 = edges[:, :, 2]
    y2 = edges[:, :, 3]
    x = x2 - x1
    y = y2 - y1
    v = np.hstack([x, y])
    m = np.matmul(v, v.T)
    # this selects all the entries in edges where the multiplcation result m is greater than the mean.
    edges = edges[np.all(m >= m.mean(axis=0), axis=1)]
    return edges

def find_vector_intersect(a1, a2, b1, b2):
    """ 
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """

    #print(a1, a2, b1, b2)
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    #print(int(x//z), int(y//z))
    if z == 0:                          # lines are parallel
        return [c0.width//2, 0, c0.width//2, c0.height]       # return default
    return int(x//z), int(y//z), c0.width//2, c0.height



def filter_edges_by_mean_x(lefts, rights):
    right_x1 = rights[:, :, 0]
    right_edges = rights[np.all(right_x1 <= right_x1.mean(axis=0), axis=1)]

    left_x1 = lefts[:, :, 0]
    left_edges = lefts[np.all(left_x1 >= left_x1.mean(axis=0), axis=1)]
    return left_edges, right_edges

def remove_null_edges(all_edges):
    return all_edges[~np.all(all_edges == 0, axis=(1, 2))] # this removes any zero edges


def estimate_robot_angle(left_edge, right_edge):
    vector = find_vector_intersect(right_edge[ :, 0:2], right_edge[ :, 2:4], left_edge[ :, 0:2], left_edge[ :, 2:4])

    robot_reference_vector = [0, c0.height]
    web_vector = [vector[2] - vector[0], vector[3] - vector[1]]
    # atan2(w2​v1​−w1​v2​,w1​v1​+w2​v2​)
    return round(np.degrees(np.arctan2(robot_reference_vector[0]*web_vector[1] - robot_reference_vector[1]*web_vector[0], np.dot(robot_reference_vector, web_vector))), 2)
    
def estimate_offset(left_edge, right_edge):
    # the intersect between the bottom right edge and the right detected edges
        right_offset = find_vector_intersect(right_edge[ :, 0:2], right_edge[ :, 2:4], [c0.width//2, c0.height], [c0.width, c0.height])
        left_offset = find_vector_intersect(left_edge[:, 0:2], left_edge[ :, 2:4], [c0.width//2, c0.height], [0, c0.height])
        # this returns an error value that is negative on the left and positive on the right.
        # the magnitude is the amount from center. So left of center by 50 pixels is -50
        return (right_offset[0] - c0.width + left_offset[0])/(c0.width) * 100.0 # coverted to percent


def estimate_using_mean_of_last_10(l):
    l = l[-10:]
    return round(np.mean(l), 2)

def setup_camera():
    #vidcap = cv2.VideoCapture(0)
    vidcap = cv2.VideoCapture('vid.mp4')
    if vidcap.isOpened():
        grlrr_log.info("Video Capture Started")
        return vidcap
    else:
        exit()



async def run_camera_server():

    vidcap = setup_camera()
    last_robot_angles = []
    last_robot_offsets = []
    success, initial_image = get_image(vidcap)
    gray_image = make_gray_image(initial_image)

    c0.height, c0.width = gray_image.shape



    print(c0.height, c0.width)
    while vidcap.isOpened():
        try:

            #main processing here
            success, initial_image = get_image(vidcap)

            gray_image = make_gray_image(initial_image)


            vertices, offsets = define_vertices(gray_image)

            sections = image_to_sections(gray_image, vertices)

            all_edges = gather_all_edges(sections, offsets)

            all_edges = remove_null_edges(all_edges)

            left_edges, right_edges = split_edges_into_left_and_right(all_edges, gray_image)
            left_edges, right_edges = filter_edges_by_mean_x(left_edges, right_edges)

            for n, v in enumerate(left_edges):
                draw_line_with_end_points(initial_image, v[0], green)

            for n, v in enumerate(right_edges):
                draw_line_with_end_points(initial_image, v[0], red)


            draw_line_with_end_points(initial_image, [c0.width//2, 0, c0.width//2, c0.height], green )


            for i in range(min(len(left_edges), len(right_edges))):

                robot_angle = estimate_robot_angle(left_edges[i], right_edges[i])
                robot_offset = estimate_offset(left_edges[i], right_edges[i])

                last_robot_angles.append(robot_angle)
                last_robot_offsets.append(robot_offset)

            if len(last_robot_angles) >= 10:
                robot_angle = estimate_using_mean_of_last_10(last_robot_angles)
                robot_offset = estimate_using_mean_of_last_10(last_robot_offsets)
            else:
                robot_angle = 0.0
                robot_offset = 0.0


            cv2.putText(initial_image, str(robot_angle), (40, 40), cv2.FONT_HERSHEY_COMPLEX,  
                           1, blue, 2, cv2.LINE_AA)
            
            cv2.putText(initial_image, str(robot_offset), (40, 80), cv2.FONT_HERSHEY_COMPLEX,  
                           1, blue, 2, cv2.LINE_AA)
            

            cv2.imshow("processed_section", initial_image)
            
            cv2.waitKey(10)
    

            encoded = cv2.imencode('.jpg', initial_image)[1]

            data = str(base64.b64encode(encoded))

            await image_queue.put(data[2:len(data)-1])
            #image_queue.put("test")
            #grlrr_log.info("robot angle: "+str(robot_angle))
            await offset_queue.put(robot_offset)
            await angle_queue.put(robot_angle)
            

            await asyncio.sleep(0.1) # should run about every 1/10 a second

        except Exception as e:
            grlrr_log.info(e)




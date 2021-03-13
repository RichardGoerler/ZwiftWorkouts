import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import bisect

time_allowed = [5, 10, 15, 20, 30, 45, 60, 75, 90, 105, 120, 150, 180, 210, 240, 270, 300,
                360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 1080, 1140, 1200, 1260,
                1320, 1380, 1440, 1500, 1560, 1620, 1680, 1740, 1800, 1860, 1920,
                1980, 2040, 2100, 2160, 2220, 2280, 2340, 2400, 2460, 2520, 2580,
                2640, 2700, 2760, 2820, 2880, 2940, 3000, 3060, 3120, 3180, 3240,
                3300, 3360, 3420, 3480, 3540, 3600]

POWER_MULTIPLE_OF = 1


def mask_biggest(img):
    contours, hierarchy = cv.findContours(img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    mx = (0, 0, 0, 0)  # biggest bounding box so far
    max_cont = None
    mx_area = 0
    for cont in contours:
        x, y, w, h = cv.boundingRect(cont)
        area = w * h
        if area > mx_area:
            mx = x, y, w, h
            mx_area = area
            max_cont = cont

    stencil = np.zeros(img.shape).astype(img.dtype)
    cv.fillPoly(stencil, [max_cont], 255)
    # return stencil
    return mx


def detect_repeating_patterns(values):
    values_pro = []
    start = 0
    end = 2
    while start < len(values):
        length = end-start
        pattern = values[start:end]
        comp = values[end:end+length]
        num = 1
        while (pattern == comp) and (end+length*num <= len(values)):
            num += 1
            comp = values[end+length*(num-1):end+length*num]
        if num > 1:
            values_pro.append([num])
            values_pro[-1].extend(pattern)
            start = end+length*(num-1)
            end = start+2
        else:
            if length < 3:  # maximum pattern length defined as 3
                end += 1
            else:
                values_pro.append(values[start])
                start += 1
                end = start + 2
    return values_pro


def add_intervals_to_string(values, wstring):
    for v in values:
        if len(v) == 2:
            time, power_list = v
            power1, power2 = power_list
            time_minutes = time // 60
            time_seconds = time % 60
            if power1 == power2:
                power_string = f'{power1}%'
            else:
                power_string = f'{power1}% -> {power2}%'
            if time_minutes == 0:
                wstring += f'{time_seconds} sek {power_string}\n'
            elif time_seconds == 0:
                wstring += f'{time_minutes} min {power_string}\n'
            else:
                wstring += f'{time_minutes}:{time_seconds:02} {power_string}\n'
        else:
            reps = v[0]
            repeated_vals = v[1:]
            wstring += f'{reps} x (\n'
            wstring = add_intervals_to_string(repeated_vals, wstring)
            wstring += f')\n'
    return wstring


def contour_top_slope(cont):
    cont = np.append(cont, [cont[0]], axis=0)
    if len(cont.shape) > 2:
        cont = cont.reshape((cont.shape[0], cont.shape[2]))
    minx = np.min(cont, axis=0)[0]
    maxx = np.max(cont, axis=0)[0]
    width = maxx-minx
    startx = int(minx + width/4)
    endx = int(np.ceil(maxx - width/4))
    cont_select = cont[(cont[:, 0] >= startx) & (cont[:, 0] <= endx)]
    if len(cont_select) > 0:
        right = cont_select[np.argmax(cont_select, axis=0)[0]]
        left = cont_select[np.argmin(cont_select, axis=0)[0]]
        xdiff = right[0]-left[0]
        ydiff = right[1]-left[1]
        if abs(xdiff) > 1 and abs(xdiff) > 1:
            slope = - ydiff / xdiff   # minus here because y-coordinate is reversed ([0,0] top left)
            return slope
    return 0


def detect_workout(im, t_max=None, p_max=None, power_multiple_of=POWER_MULTIPLE_OF, time_autocorrect=True, debug=False):
    height, width, channels = im.shape
    im_gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    im_gray2 = cv.bitwise_not(im_gray)
    n_pixels = width * height
    hst, hst_borders = np.histogram(np.reshape(im_gray2, (n_pixels,)))
    # the first big histogram bar is the background.
    # the second is an interval. we want to delete everything in between,
    # so we set the binary threshold to the left border of the second big histogram bar minus a safety margin of 20%
    ind = np.nonzero(hst > n_pixels * 0.05)[0][1]
    threshold = int(hst_borders[ind])*0.8
    if debug:
        print(f'threshold set to {threshold}')
    if debug:
        plt.hist(np.reshape(im_gray2, (n_pixels,)))
        plt.show()
    # hs = cv.calcHist(im_gray2, [0], None, [256], (0, 256))
    ret, im_thresh = cv.threshold(im_gray2, threshold, 255, cv.THRESH_BINARY)
    if debug:
        cv.imshow('im_thresh', im_thresh)
        k = cv.waitKey(0)
    
    horizontal = im_thresh.copy()
    horizontal_size = 7
    horizontalStructure = cv.getStructuringElement(cv.MORPH_RECT, (horizontal_size, 1))
    # horizontal = cv.erode(horizontal, horizontalStructure)
    # horizontal = cv.dilate(horizontal, horizontalStructure)
    # cv.imshow('window title', horizontal)
    # k = cv.waitKey(0)
    
    vertical = im_thresh.copy()
    vertical_size = height // 30
    verticalStructure = cv.getStructuringElement(cv.MORPH_RECT, (1, vertical_size))
    vertical = cv.erode(vertical, verticalStructure)
    vertical = cv.dilate(vertical, verticalStructure)
    if debug:
        cv.imshow('vertical', vertical)
        k = cv.waitKey(0)
    
    # stencil = mask_biggest(cv.dilate(vertical, horizontalStructure))
    # k = cv.waitKey(0)
    # stencil_bgr = cv.cvtColor(stencil, cv.COLOR_GRAY2BGR)
    # k = cv.waitKey(0)
    # masked = cv.bitwise_and(vertical, stencil)
    # masked_color = cv.bitwise_and(im, stencil_bgr)
    x, y, w, h = mask_biggest(cv.dilate(vertical, horizontalStructure))
    roi = vertical[y:y + h, x:x + w]
    roi_color = im[y:y + h, x:x + w]
    # cv.imshow('masked_color', masked_color)
    # k = cv.waitKey(0)
    
    # contours, hierarchy = cv.findContours(masked, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours, hierarchy = cv.findContours(roi, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # cv.drawContours(roi_color, contours, -1, (0,0,255), 1)
    if debug:
        cv.imshow('contours', roi_color)
        k = cv.waitKey(0)
    intervals = []
    slopes = []
    w_max = 0
    h_max = 0
    for c in contours:
        slope = contour_top_slope(c)
        slopes.append(slope)
        x, y, w, h = cv.boundingRect(c)
        if h > h_max:
            h_max = h
        if w > w_max:
            w_max = w
        if w < width / 2:
            intervals.append([x, y, w, h])
            # im_rects = cv.rectangle(roi_color, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # img = cv.rectangle(masked_color, (x, y), (x + w, y + h), (0, 0, 255), 2)
    # cv.drawContours(im, contours, -1, (0,255,0), 1)
    sorted_ind = np.argsort(intervals, axis=0)[:, 0]
    intervals = [intervals[i] for i in sorted_ind]
    slopes = [slopes[i] for i in sorted_ind]
    lowest_points = np.array([x[1] + x[3] for x in intervals])
    lowest_mean, lowest_std = np.mean(lowest_points), np.std(lowest_points)
    # remove outliers (intervals that do not connect to bottom)
    intervals = [intervals[i] for i in np.nonzero(lowest_points >= lowest_mean - lowest_std)[0]]
    w_total = 0
    values = []
    n_intervals = len(intervals)
    # w_vals = np.array([v[2] for v in intervals])
    # w_corrections = 1 * np.sqrt(max(w_vals) / w_vals) - 1
    for it in range(n_intervals):
        el = intervals[it]
        sl = slopes[it]
        x, y, w, h = el
        col = (0, 0, 255)
        wid = 1
        if w >= w_max:
            col = (0, 255, 0)
            wid = 2
        elif h >= h_max:
            col = (255, 255, 0)
            wid = 2
        im_rects = cv.rectangle(roi_color, (x, y), (x + w, y + h), col, wid)
        if debug:
            cv.imshow('detection single', im_rects)
            k = cv.waitKey(0)
        if p_max is not None and t_max is not None:
            power1 = (h / h_max) * p_max
            power = int(power_multiple_of*round(power1/power_multiple_of))
            # w = int(w+w_corrections[it])
            time1 = (w / w_max) * t_max
            if time_autocorrect:
                time = time_allowed[bisect.bisect_left(time_allowed, time1*0.97)]
            else:
                time = int(time1)

            if 0 < it < n_intervals - 1 or sl == 0:
                values.append([time, [power, power]])
            else:
                power_low1 = h - w * abs(sl)
                power_low1 = (power_low1 / h_max) * p_max
                power_low = int(power_multiple_of*round(power_low1/power_multiple_of))
                if sl < 0:
                    values.append([time, [power, power_low]])
                else:
                    values.append([time, [power_low, power]])
    if p_max is None or t_max is None:
        return im_rects

    if debug:
        print(values)
        print('')
    
    # detect repeating patterns
    
    values_rep = detect_repeating_patterns(values)
    while values_rep != values:
        values = values_rep
        values_rep = detect_repeating_patterns(values)
    values = values_rep
    if debug:
        print(values)
        print('')
    
    # make workout string
    workout_string = add_intervals_to_string(values, '')
    if debug:
        print(workout_string)
        cv.imshow('detection', im_rects)
        k = cv.waitKey(0)
    return workout_string


if __name__ == '__main__':
    # im = cv.imread('stuff/zwiftworkout.png')
    im = cv.imread('stuff/trainingpeaks.PNG')
    workout_string = detect_workout(im, t_max=600, p_max=120, power_multiple_of=1, time_autocorrect=False)
    print(workout_string)

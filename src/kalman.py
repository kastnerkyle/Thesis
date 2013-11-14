#!/usr/bin/env python
import numpy as np

def pred_mean(source_scale, prev_mean):
    return source_scale*prev_mean


def pred_sigma(source_scale, prev_sigma, source_sigma):
    return np.sqrt((source_scale**2)*(prev_sigma**2)+source_sigma**2)


def update_mean(pred_mean, pred_sigma, meas_val, meas_sigma):
    pred_mean = float(pred_mean)
    pred_sigma = float(pred_sigma)
    meas_val = float(meas_val)
    meas_sigma = float(meas_sigma)
    numerator = (pred_mean/(pred_sigma**2))+(meas_val/(meas_sigma**2))
    denominator = (1./(pred_sigma**2))+(1./(meas_sigma**2))
    return numerator/denominator


def update_sigma(pred_sigma, meas_sigma):
    r = (1./(pred_sigma**2))+(1./(meas_sigma**2))
    return 1./np.sqrt(r)


def lkfilt(y, source_scale, source_sigma, meas_sigma):
    last_mean = 0
    last_sigma = source_sigma
    k = range(len(y))
    for i in range(len(y)):
        est_mean = pred_mean(source_scale, last_mean)
        est_sigma = pred_sigma(source_scale, last_sigma, source_sigma)
        k[i] = est_mean+st.norm.rvs(scale=est_sigma)
        last_mean = update_mean(est_mean, est_sigma, y[i], meas_sigma)
        last_sigma = update_sigma(est_sigma, meas_sigma)
    return k


def basic_kalman(data):
    source_sigma = .4
    source_scale = np.sqrt(1-source_sigma**2)
    meas_sigma = source_sigma  # measurement error?
    k = lkfilt(data, source_scale, source_sigma, meas_sigma)

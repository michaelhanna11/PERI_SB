import streamlit as st
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import requests
import os
import io
from datetime import datetime

# Set the page title for the browser tab
st.set_page_config(page_title="PERI SB Frames")

# Program metadata
PROGRAM_VERSION = "1.0 - 2025"
PROGRAM = "PERI Brace Frame Load Calculator"
COMPANY_NAME = "tekhne Consulting Engineers"
COMPANY_ADDRESS = "   "  # Update with actual address if needed
LOGO_URL = "https://drive.google.com/uc?export=download&id=1VebdT2loVGX57noP9t2GgQhwCNn8AA3h"
FALLBACK_LOGO_URL = "https://onedrive.live.com/download?cid=A48CC9068E3FACE0&resid=A48CC9068E3FACE0%21s252b6fb7fcd04f53968b2a09114d33ed"

# Comprehensive brace frame data
brace_frame_data = {
    "SB-A+B": {
        "heights": [3.75, 4.00, 4.25, 4.50, 4.75, 5.00, 5.25, 5.50, 5.75, 6.00],
        "pressures": [40, 50, 60],
        "data": {
            3.75: {40: {"e": 2.60, "Z": 167, "V1": 71, "V2": 53, "f": 2},
                   50: {"e": 1.95, "Z": 194, "V1": 96, "V2": 58, "f": 2},
                   60: {"e": 1.75, "Z": 216, "V1": 100, "V2": 61, "f": 2}},
            4.00: {40: {"e": 2.50, "Z": 181, "V1": 72, "V2": 63, "f": 3},
                   50: {"e": 1.90, "Z": 212, "V1": 98, "V2": 63, "f": 3},
                   60: {"e": 1.70, "Z": 238, "V1": 103, "V2": 74, "f": 4}},
            4.25: {40: {"e": 2.40, "Z": 195, "V1": 72, "V2": 73, "f": 4},
                   50: {"e": 1.85, "Z": 229, "V1": 98, "V2": 83, "f": 4},
                   60: {"e": 1.65, "Z": 259, "V1": 104, "V2": 88, "f": 5}},
            4.50: {40: {"e": 2.30, "Z": 209, "V1": 72, "V2": 85, "f": 4},
                   50: {"e": 1.80, "Z": 249, "V1": 98, "V2": 98, "f": 5},
                   60: {"e": 1.60, "Z": 280, "V1": 105, "V2": 103, "f": 6}},
            4.75: {40: {"e": 2.20, "Z": 223, "V1": 72, "V2": 98, "f": 5},
                   50: {"e": 1.75, "Z": 265, "V1": 98, "V2": 108, "f": 6},
                   60: {"e": 1.55, "Z": 301, "V1": 105, "V2": 120, "f": 7}},
            5.00: {40: {"e": 2.10, "Z": 238, "V1": 72, "V2": 111, "f": 5},
                   50: {"e": 1.70, "Z": 283, "V1": 98, "V2": 126, "f": 7},
                   60: {"e": 1.50, "Z": 322, "V1": 105, "V2": 138, "f": 8}},
            5.25: {40: {"e": 2.00, "Z": 252, "V1": 72, "V2": 125, "f": 7},
                   50: {"e": 1.65, "Z": 301, "V1": 98, "V2": 133, "f": 8},
                   60: {"e": 1.45, "Z": 344, "V1": 105, "V2": 157, "f": 9}},
            5.50: {40: {"e": 1.90, "Z": 266, "V1": 72, "V2": 140, "f": 7},
                   50: {"e": 1.59, "Z": 318, "V1": 98, "V2": 161, "f": 9},
                   60: {"e": 1.39, "Z": 365, "V1": 105, "V2": 178, "f": 9}},
            5.75: {40: {"e": 1.71, "Z": 280, "V1": 72, "V2": 156, "f": 9},
                   50: {"e": 1.49, "Z": 336, "V1": 98, "V2": 180, "f": 10},
                   60: {"e": 1.31, "Z": 386, "V1": 105, "V2": 198, "f": 11}},
            6.00: {40: {"e": 1.54, "Z": 294, "V1": 72, "V2": 173, "f": 10},
                   50: {"e": 1.39, "Z": 354, "V1": 98, "V2": 200, "f": 11},
                   60: {"e": 1.20, "Z": 407, "V1": 105, "V2": 223, "f": 12}}
        }
    },
    "SB-A0+A+B+C": {
        "heights": [6.75, 7.00, 7.25, 7.50, 7.75, 8.00, 8.25, 8.50, 8.75],
        "pressures": [30, 40, 50, 60],
        "data": {
            6.75: {30: {"e": 1.91, "Z": 261, "V1": 69, "V2": 135, "f": 10},
                   40: {"e": 1.48, "Z": 337, "V1": 92, "V2": 167, "f": 13},
                   50: {"e": 1.22, "Z": 407, "V1": 114, "V2": 197, "f": 15},
                   60: {"e": 1.06, "Z": 471, "V1": 136, "V2": 221, "f": 17}},
            7.00: {30: {"e": 1.83, "Z": 272, "V1": 69, "V2": 147, "f": 12},
                   40: {"e": 1.42, "Z": 351, "V1": 92, "V2": 184, "f": 13},
                   50: {"e": 1.17, "Z": 425, "V1": 114, "V2": 215, "f": 17},
                   60: {"e": 1.01, "Z": 492, "V1": 136, "V2": 242, "f": 19}},
            7.25: {30: {"e": 1.70, "Z": 283, "V1": 69, "V2": 159, "f": 13},
                   40: {"e": 1.35, "Z": 365, "V1": 92, "V2": 200, "f": 16},
                   50: {"e": 1.13, "Z": 442, "V1": 114, "V2": 234, "f": 19},
                   60: {"e": 0.97, "Z": 514, "V1": 136, "V2": 264, "f": 21}},
            7.50: {30: {"e": 1.56, "Z": 293, "V1": 69, "V2": 172, "f": 14},
                   40: {"e": 1.25, "Z": 379, "V1": 92, "V2": 216, "f": 18},
                   50: {"e": 1.06, "Z": 460, "V1": 114, "V2": 254, "f": 21}},
            7.75: {30: {"e": 1.45, "Z": 304, "V1": 69, "V2": 186, "f": 16},
                   40: {"e": 1.15, "Z": 394, "V1": 92, "V2": 233, "f": 20},
                   50: {"e": 0.98, "Z": 478, "V1": 114, "V2": 274, "f": 23}},
            8.00: {30: {"e": 1.36, "Z": 314, "V1": 69, "V2": 198, "f": 18},
                   40: {"e": 1.08, "Z": 408, "V1": 92, "V2": 250, "f": 22},
                   50: {"e": 0.90, "Z": 495, "V1": 114, "V2": 296, "f": 26}},
            8.25: {30: {"e": 1.25, "Z": 328, "V1": 69, "V2": 216, "f": 20},
                   40: {"e": 1.01, "Z": 422, "V1": 92, "V2": 267, "f": 25}},
            8.50: {30: {"e": 1.18, "Z": 336, "V1": 69, "V2": 227, "f": 22},
                   40: {"e": 0.94, "Z": 436, "V1": 92, "V2": 287, "f": 27}},
            8.75: {30: {"e": 1.12, "Z": 347, "V1": 69, "V2": 241, "f": 24},
                   40: {"e": 0.88, "Z": 450, "V1": 92, "V2": 306, "f": 30}}
        }
    },
    "SB-A+B+C": {
        "heights": [5.50, 5.75, 6.00, 6.25, 6.50, 6.75],
        "pressures": [30, 40, 50, 60],
        "data": {
            5.50: {40: {"e": 1.90, "Z": 266, "V1": 72, "V2": 140, "f": 7},
                   50: {"e": 1.59, "Z": 318, "V1": 80, "V2": 160, "f": 9},
                   60: {"e": 1.39, "Z": 365, "V1": 105, "V2": 177, "f": 9}},
            5.75: {40: {"e": 1.71, "Z": 280, "V1": 72, "V2": 156, "f": 9},
                   50: {"e": 1.49, "Z": 336, "V1": 72, "V2": 180, "f": 10},
                   60: {"e": 1.31, "Z": 386, "V1": 105, "V2": 199, "f": 11}},
            6.00: {40: {"e": 1.54, "Z": 294, "V1": 72, "V2": 172, "f": 10},
                   50: {"e": 1.39, "Z": 354, "V1": 72, "V2": 200, "f": 11},
                   60: {"e": 1.20, "Z": 407, "V1": 105, "V2": 222, "f": 12}},
            6.25: {40: {"e": 1.39, "Z": 308, "V1": 72, "V2": 190, "f": 11},
                   50: {"e": 1.20, "Z": 371, "V1": 72, "V2": 221, "f": 13},
                   60: {"e": 1.08, "Z": 429, "V1": 105, "V2": 246, "f": 14}},
            6.50: {30: {"e": 1.53, "Z": 251, "V1": 50, "V2": 170, "f": 10},
                   40: {"e": 1.26, "Z": 322, "V1": 72, "V2": 208, "f": 13},
                   50: {"e": 1.08, "Z": 389, "V1": 89, "V2": 233, "f": 15},
                   60: {"e": 0.97, "Z": 450, "V1": 105, "V2": 272, "f": 17}},
            6.75: {30: {"e": 1.41, "Z": 261, "V1": 50, "V2": 185, "f": 14},
                   40: {"e": 1.17, "Z": 337, "V1": 72, "V2": 229, "f": 16},
                   50: {"e": 1.00, "Z": 407, "V1": 89, "V2": 267, "f": 18},
                   60: {"e": 0.87, "Z": 471, "V1": 105, "V2": 300, "f": 21}}
        }
    },
    "SB-B+C": {
        "heights": [3.75, 4.00, 4.25, 4.50, 4.75, 5.00],
        "pressures": [40, 50, 60],
        "data": {
            3.75: {40: {"e": 2.42, "Z": 167, "V1": 51, "V2": 82, "f": 3},
                   50: {"e": 2.11, "Z": 195, "V1": 63, "V2": 83, "f": 3},
                   60: {"e": 2.05, "Z": 216, "V1": 73, "V2": 94, "f": 4}},
            4.00: {40: {"e": 2.25, "Z": 181, "V1": 51, "V2": 97, "f": 4},
                   50: {"e": 1.93, "Z": 212, "V1": 63, "V2": 107, "f": 4},
                   60: {"e": 1.75, "Z": 238, "V1": 73, "V2": 114, "f": 5}},
            4.25: {40: {"e": 2.01, "Z": 195, "V1": 51, "V2": 114, "f": 4},
                   50: {"e": 1.77, "Z": 229, "V1": 63, "V2": 114, "f": 5},
                   60: {"e": 1.60, "Z": 259, "V1": 73, "V2": 136, "f": 6}},
            4.50: {40: {"e": 1.77, "Z": 209, "V1": 51, "V2": 131, "f": 6},
                   50: {"e": 1.60, "Z": 249, "V1": 63, "V2": 141, "f": 6},
                   60: {"e": 1.43, "Z": 280, "V1": 73, "V2": 160, "f": 7}},
            4.75: {40: {"e": 1.58, "Z": 223, "V1": 51, "V2": 151, "f": 7},
                   50: {"e": 1.38, "Z": 265, "V1": 63, "V2": 171, "f": 8},
                   60: {"e": 1.26, "Z": 301, "V1": 73, "V2": 185, "f": 8}},
            5.00: {40: {"e": 1.40, "Z": 238, "V1": 51, "V2": 172, "f": 9},
                   50: {"e": 1.20, "Z": 283, "V1": 63, "V2": 195, "f": 9},
                   60: {"e": 1.10, "Z": 322, "V1": 73, "V2": 213, "f": 10}}
        }
    },
    "SB-A+C": {
        "heights": [2.75, 3.00, 3.25, 3.50, 3.75, 4.00],
        "pressures": [40, 50, 60],
        "data": {
            2.75: {40: {"e": 3.00, "Z": 110, "V1": 60, "V2": 22, "f": 1},
                   50: {"e": 2.60, "Z": 124, "V1": 60, "V2": 22, "f": 1},
                   60: {"e": 2.40, "Z": 132, "V1": 75, "V2": 22, "f": 1}},
            3.00: {40: {"e": 2.81, "Z": 125, "V1": 64, "V2": 28, "f": 1},
                   50: {"e": 2.40, "Z": 143, "V1": 75, "V2": 30, "f": 1},
                   60: {"e": 2.17, "Z": 153, "V1": 83, "V2": 30, "f": 1}},
            3.25: {40: {"e": 2.69, "Z": 139, "V1": 67, "V2": 35, "f": 2},
                   50: {"e": 2.09, "Z": 159, "V1": 80, "V2": 38, "f": 2},
                   60: {"e": 2.01, "Z": 174, "V1": 90, "V2": 39, "f": 2}},
            3.50: {40: {"e": 2.62, "Z": 153, "V1": 70, "V2": 43, "f": 3},
                   50: {"e": 2.17, "Z": 177, "V1": 84, "V2": 47, "f": 3},
                   60: {"e": 1.90, "Z": 195, "V1": 95, "V2": 49, "f": 3}},
            3.75: {40: {"e": 2.28, "Z": 167, "V1": 71, "V2": 52, "f": 5},
                   50: {"e": 2.12, "Z": 195, "V1": 86, "V2": 57, "f": 5},
                   60: {"e": 1.83, "Z": 216, "V1": 100, "V2": 60, "f": 5}},
            4.00: {40: {"e": 1.60, "Z": 181, "V1": 72, "V2": 63, "f": 7},
                   50: {"e": 1.60, "Z": 212, "V1": 88, "V2": 69, "f": 7},
                   60: {"e": 1.60, "Z": 238, "V1": 103, "V2": 74, "f": 7}}
        }
    },
    "SB-B": {
        "heights": [2.50, 2.75, 3.00, 3.25, 3.50, 3.75, 4.00],
        "pressures": [40, 50, 60],
        "data": {
            2.50: {40: {"e": 3.00, "Z": 96, "V1": 48, "V2": 26, "f": 1},
                   50: {"e": 2.60, "Z": 100, "V1": 59, "V2": 26, "f": 1},
                   60: {"e": 2.40, "Z": 110, "V1": 59, "V2": 26, "f": 1}},
            2.75: {40: {"e": 3.00, "Z": 110, "V1": 59, "V2": 34, "f": 1},
                   50: {"e": 2.60, "Z": 124, "V1": 59, "V2": 34, "f": 1},
                   60: {"e": 2.40, "Z": 132, "V1": 65, "V2": 36, "f": 1}},
            3.00: {40: {"e": 2.80, "Z": 124, "V1": 51, "V2": 44, "f": 1},
                   50: {"e": 2.60, "Z": 141, "V1": 62, "V2": 44, "f": 1},
                   60: {"e": 2.20, "Z": 153, "V1": 70, "V2": 48, "f": 1}},
            3.25: {40: {"e": 2.60, "Z": 139, "V1": 51, "V2": 56, "f": 1},
                   50: {"e": 2.30, "Z": 159, "V1": 69, "V2": 60, "f": 1},
                   60: {"e": 2.10, "Z": 174, "V1": 72, "V2": 61, "f": 2}},
            3.50: {40: {"e": 2.55, "Z": 153, "V1": 51, "V2": 68, "f": 2},
                   50: {"e": 2.25, "Z": 177, "V1": 69, "V2": 74, "f": 2},
                   60: {"e": 2.05, "Z": 195, "V1": 73, "V2": 77, "f": 3}},
            3.75: {40: {"e": 2.42, "Z": 167, "V1": 51, "V2": 82, "f": 3},
                   50: {"e": 2.11, "Z": 194, "V1": 63, "V2": 90, "f": 3},
                   60: {"e": 1.95, "Z": 216, "V1": 73, "V2": 95, "f": 4}},
            4.00: {40: {"e": 2.25, "Z": 181, "V1": 51, "V2": 97, "f": 4},
                   50: {"e": 1.93, "Z": 212, "V1": 63, "V2": 108, "f": 4},
                   60: {"e": 1.75, "Z": 238, "V1": 73, "V2": 115, "f": 5}}
        }
    },
    "SB-A": {
        "heights": [2.50, 2.75, 3.00],
        "pressures": [40, 50, 60],
        "data": {
            2.50: {40: {"e": 3.00, "Z": 96, "V1": 55, "V2": 16, "f": 1},
                   50: {"e": 2.60, "Z": 100, "V1": 62, "V2": 17, "f": 1},
                   60: {"e": 2.40, "Z": 110, "V1": 65, "V2": 17, "f": 1}},
            2.75: {40: {"e": 3.00, "Z": 110, "V1": 60, "V2": 22, "f": 1},
                   50: {"e": 2.60, "Z": 120, "V1": 65, "V2": 22, "f": 1},
                   60: {"e": 2.40, "Z": 132, "V1": 75, "V2": 22, "f": 1}},
            3.00: {40: {"e": 2.81, "Z": 125, "V1": 64, "V2": 28, "f": 1},
                   50: {"e": 2.40, "Z": 141, "V1": 75, "V2": 30, "f": 1},
                   60: {"e": 2.17, "Z": 153, "V1	element": 83, "V2": 30, "f": 1}}
        }
    },
    "SB-1": {
        "heights": [2.50, 2.75, 3.00, 3.25, 3.50, 3.75],
        "pressures": [30, 40, 50],
        "data": {
            2.50: {30: {"e": 1.25, "Z": 81, "V1": 37, "V2": 21, "f": 2},
                   40: {"e": 1.25, "Z": 86, "V1": 48, "V2": 22, "f": 2},
                   50: {"e": 1.25, "Z": 106, "V1": 53, "V2": 22, "f": 2}},
            2.75: {30: {"e": 1.25, "Z": 91, "V1": 38, "V2": 27, "f": 2},
                   40: {"e": 1.25, "Z": 110, "V1": 49, "V2": 30, "f": 2},
                   50: {"e": 1.25, "Z": 124, "V1": 57, "V2": 31, "f": 2}},
            3.00: {30: {"e": 1.25, "Z": 102, "V1": 38, "V2": 35, "f": 2},
                   40: {"e": 1.25, "Z": 125, "V1": 50, "V2": 40, "f": 3},
                   50: {"e": 1.25, "Z": 142, "V1": 59, "V2": 42, "f": 3}},
            3.25: {30: {"e": 1.25, "Z": 113, "V1": 38, "V2": 44, "f": 2},
                   40: {"e": 1.25, "Z": 138, "V1": 58, "V2": 54, "f": 3},
                   50: {"e": 1.25, "Z": 159, "V1": 59, "V2": 42, "f": 3}},
            3.50: {30: {"e": 1.25, "Z": 123, "V1": 38, "V2": 54, "f": 3},
                   40: {"e": 1.25, "Z": 153, "V1": 63, "V2": 46, "f": 2}},
            3.75: {30: {"e": 1.25, "Z": 134, "V1": 38, "V2": 64, "f": 4}}
        }
    },
    "SB-2": {
        "heights": [3.50, 3.75, 4.00, 4.25, 4.50, 4.75, 5.00, 5.25, 5.50, 5.75, 6.00],
        "pressures": [30, 40, 50],
        "data": {
            3.50: {30: {"e": 1.25, "Z": 123, "V1": 48, "V2": 40, "f": 2},
                   40: {"e": 1.25, "Z": 153, "V1": 63, "V2": 46, "f": 2},
                   50: {"e": 1.25, "Z": 177, "V1": 77, "V2": 50, "f": 2}},
            3.75: {30: {"e": 1.25, "Z": 134, "V1": 48, "V2": 47, "f": 2},
                   40: {"e": 1.25, "Z": 167, "V1": 63, "V2": 55, "f": 2},
                   50: {"e": 1.25, "Z": 194, "V1": 78, "V2": 61, "f": 3}},
            4.00: {30: {"e": 1.25, "Z": 144, "V1": 48, "V2": 56, "f": 2},
                   40: {"e": 1.25, "Z": 181, "V1": 63, "V2": 66, "f": 3},
                   50: {"e": 1.25, "Z": 212, "V1": 78, "V2": 74, "f": 3}},
            4.25: {30: {"e": 1.25, "Z": 155, "V1": 48, "V2": 66, "f": 3},
                   40: {"e": 1.25, "Z": 195, "V1": 63, "V2": 78, "f": 3},
                   50: {"e": 1.25, "Z": 230, "V1": 78, "V2": 87, "f": 4}},
            4.50: {30: {"e": 1.25, "Z": 166, "V1": 48, "V2": 76, "f": 3},
                   40: {"e": 1.25, "Z": 210, "V1": 63, "V2": 91, "f": 4},
                   50: {"e": 1.25, "Z": 247, "V1": 78, "V2": 102, "f": 5}},
            4.75: {30: {"e": 1.25, "Z": 176, "V1": 48, "V2": 87, "f": 4},
                   40: {"e": 1.25, "Z": 223, "V1": 63, "V2": 105, "f": 5},
                   50: {"e": 1.25, "Z": 265, "V1": 78, "V2": 118, "f": 5}},
            5.00: {30: {"e": 1.25, "Z": 186, "V1": 48, "V2": 98, "f": 4},
                   40: {"e": 1.25, "Z": 238, "V1": 63, "V2": 120, "f": 6},
                   50: {"e": 1.25, "Z": 283, "V1": 78, "V2": 135, "f": 6}},
            5.25: {30: {"e": 1.25, "Z": 198, "V1": 48, "V2": 111, "f": 5},
                   40: {"e": 1.25, "Z": 252, "V1": 63, "V2": 135, "f": 6},
                   50: {"e": 1.25, "Z": 301, "V1": 78, "V2": 154, "f": 6}},
            5.50: {30: {"e": 1.25, "Z": 208, "V1": 48, "V2": 124, "f": 6},
                   40: {"e": 1.25, "Z": 266, "V1": 63, "V2": 152, "f": 7},
                   50: {"e": 1.25, "Z": 318, "V1": 78, "V2": 174, "f": 8}},
            5.75: {30: {"e": 1.25, "Z": 218, "V1": 48, "V2": 138, "f": 6},
                   40: {"e": 1.25, "Z": 280, "V1": 63, "V2": 170, "f": 8},
                   50: {"e": 1.25, "Z": 336, "V1": 78, "V2": 195, "f": 9}},
            6.00: {30: {"e": 1.25, "Z": 229, "V1": 48, "V2": 153, "f": 7},
                   40: {"e": 1.25, "Z": 294, "V1": 63, "V2": 188, "f": 9},
                   50: {"e": 1.25, "Z": 354, "V1": 78, "V2": 218, "f": 10}}
        }
    }
}

def interpolate_value(x, x0, x1, y0, y1):
    """Linear interpolation between two points."""
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

def get_loads(brace_type, height, pressure):
    """Retrieve or interpolate loads based on user input."""
    if brace_type not in brace_frame_data:
        return "Brace frame type not supported."
    
    data = brace_frame_data[brace_type]["data"]
    heights = brace_frame_data[brace_type]["heights"]
    pressures = brace_frame_data[brace_type]["pressures"]

    if height < min(heights) or height > max(heights) or pressure < min(pressures) or pressure > max(pressures):
        return f"Input out of range for {brace_type}. Height range: {min(heights)}-{max(heights)} m, Pressure range: {min(pressures)}-{max(pressures)} kN/m²."

    h_low = max([h for h in heights if h <= height])
    h_high = min([h for h in heights if h >= height])
    p_low = max([p for p in pressures if p <= pressure])
    p_high = min([p for p in pressures if p >= pressure])

    if h_high not in data or p_high not in data[h_high]:
        return f"Data not available for {brace_type} at height {h_high} m and pressure {p_high} kN/m²."

    if h_low == h_high and p_low == p_high:
        return data[h_low][p_low]

    if h_low == h_high:
        loads_low = data[h_low][p_low]
        loads_high = data[h_low][p_high]
        result = {}
        for key in ["e", "Z", "V1", "V2", "f"]:
            result[key] = interpolate_value(pressure, p_low, p_high, loads_low[key], loads_high[key])
        return result
    elif p_low == p_high:
        loads_low = data[h_low][p_low]
        loads_high = data[h_high][p_low]
        result = {}
        for key in ["e", "Z", "V1", "V2", "f"]:
            result[key] = interpolate_value(height, h_low, h_high, loads_low[key], loads_high[key])
        return result
    else:
        loads_ll = data[h_low][p_low]
        loads_lh = data[h_low][p_high] if p_high in data[h_low] else data[h_low][p_low]
        loads_hl = data[h_high][p_low]
        loads_hh = data[h_high][p_high] if p_high in data[h_high] else data[h_high][p_low]
        result = {}
        for key in ["e", "Z", "V1", "V2", "f"]:
            low_interp = interpolate_value(pressure, p_low, p_high, loads_ll[key], loads_lh[key]) if p_high in data[h_low] else loads_ll[key]
            high_interp = interpolate_value(pressure, p_low, p_high, loads_hl[key], loads_hh[key]) if p_high in data[h_high] else loads_hl[key]
            result[key] = interpolate_value(height, h_low, h_high, low_interp, high_interp)
        return result

def validate_bracing(brace_type, height, e):
    """Validate diagonal bracing requirements based on document notes."""
    validation_messages = []

    if "SB-" in brace_type and ("A" in brace_type or "B" in brace_type or "C" in brace_type):
        validation_messages.append("Recommendation: Pre-incline the Brace Frame by 2/3 of the calculated deflection.")

    if brace_type == "SB-A+B":
        if e <= 1.35 and height <= 5.25:
            validation_messages.append("Diagonal Bracing B can be omitted during concreting.")
        else:
            validation_messages.append("Required: Diagonal Bracing A and B for concreting.")
        validation_messages.append("Required: Diagonal Bracing for moving and lifting the formwork unit with the crane.")
    elif brace_type == "SB-A0+A+B+C":
        validation_messages.append("Required: Diagonal Bracing A, B, and C for concreting, horizontally moving, and lifting the formwork unit with the crane.")
    elif brace_type == "SB-A+B+C":
        validation_messages.append("Required: Diagonal Bracing A, B, and C for concreting.")
        validation_messages.append("Required: Diagonal Bracing for horizontally moving and lifting the formwork unit with the crane.")
    elif brace_type == "SB-B+C":
        if e <= 1.35 and height <= 4.25:
            validation_messages.append("Diagonal Bracing B can be omitted during concreting.")
        else:
            validation_messages.append("Required: Diagonal Bracing B and C for concreting.")
        validation_messages.append("Required: Diagonal Bracing B or D for lifting with the crane.")
    elif brace_type == "SB-A+C":
        validation_messages.append("No diagonal bracing required for concreting.")
        validation_messages.append("Required: Diagonal Bracing C for moving and lifting the formwork unit with the crane.")
    elif brace_type == "SB-B":
        if e > 1.35 and height >= 3.75:
            validation_messages.append("Required: Diagonal Bracing B for concreting.")
        else:
            validation_messages.append("No diagonal bracing required for concreting until height reaches 3.75 m if e ≤ 1.35 m.")
        validation_messages.append("Required: Diagonal Bracing for moving and lifting the formwork unit with the crane.")
    elif brace_type == "SB-A":
        validation_messages.append("No diagonal bracing required for concreting.")
        validation_messages.append("Required: Diagonal Bracing C for moving and lifting the formwork unit with the crane.")
    elif brace_type == "SB-1":
        validation_messages.append("No diagonal bracing required for concreting.")
        validation_messages.append("Required: Diagonal Bracing for moving and lifting the formwork unit with the crane.")
        if e > 1.25:
            validation_messages.append("Warning: Permissible width of influence exceeds maximum of 1.25 m.")
    elif brace_type == "SB-2":
        if height >= 5.00:
            validation_messages.append("Required: Diagonal Bracing for concreting (height ≥ 5.00 m).")
        else:
            validation_messages.append("No diagonal bracing required for concreting (height < 5.00 m).")
        validation_messages.append("Required: Diagonal Bracing for moving and lifting the formwork unit with the crane.")
        if e > 1.25:
            validation_messages.append("Warning: Permissible width of influence exceeds maximum of 1.25 m.")

    return validation_messages

def build_pdf_elements(brace_type, height, pressure, result, validation_messages, project_number, project_name):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontSize=14, spaceAfter=8, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle(name='SubtitleStyle', parent=styles['Normal'], fontSize=10, spaceAfter=8, alignment=TA_CENTER)
    heading_style = ParagraphStyle(name='HeadingStyle', parent=styles['Heading2'], fontSize=12, spaceAfter=6)
    normal_style = ParagraphStyle(name='NormalStyle', parent=styles['Normal'], fontSize=9, spaceAfter=6)
    table_header_style = ParagraphStyle(name='TableHeaderStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT)
    table_cell_style = ParagraphStyle(name='TableCellStyle', parent=styles['Normal'], fontSize=8, alignment=TA_LEFT, leading=8)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])

    elements = []
    logo_file = "logo.png"
    if not os.path.exists(logo_file):
        for url in [LOGO_URL, FALLBACK_LOGO_URL]:
            try:
                response = requests.get(url, stream=True, allow_redirects=True, timeout=10)
                if 'image' in response.headers.get('Content-Type', '').lower():
                    response.raise_for_status()
                    with open(logo_file, 'wb') as f:
                        f.write(response.content)
                    break
            except Exception:
                continue

    company_text = f"<b>{COMPANY_NAME}</b><br/>{COMPANY_ADDRESS}"
    company_paragraph = Paragraph(company_text, normal_style)
    logo = Image(logo_file, width=50*mm, height=20*mm) if os.path.exists(logo_file) else Paragraph("[Logo Placeholder]", normal_style)
    header_data = [[logo, company_paragraph]]
    header_table = Table(header_data, colWidths=[60*mm, 120*mm])
    header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (1, 0), (1, 0), 'CENTER')]))
    elements.extend([header_table, Spacer(1, 4*mm), Paragraph("PERI Brace Frame Load Calculation Report", title_style)])

    project_details = f"Project Number: {project_number}<br/>Project Name: {project_name}<br/>Date: {datetime.now().strftime('%B %d, %Y')}"
    elements.extend([Paragraph(project_details, subtitle_style), Spacer(1, 2*mm), Paragraph("Input Parameters", heading_style)])

    input_data = [
        ["Parameter", "Value"],
        ["Brace Frame Type", brace_type],
        ["Concreting Height (m)", f"{height:.2f}"],
        ["Fresh Concrete Pressure (kN/m²)", f"{pressure:.2f}"],
    ]
    input_table = Table([[Paragraph(row[0], table_header_style if i == 0 else table_cell_style),
                          Paragraph(row[1], table_header_style if i == 0 else table_cell_style)] for i, row in enumerate(input_data)],
                        colWidths=[100*mm, 80*mm])
    input_table.setStyle(table_style)
    elements.extend([input_table, Spacer(1, 4*mm), Paragraph("Calculated Loads (Per Meter)", heading_style)])

    loads_data = [
        ["Parameter", "Value"],
        ["Permissible Width of Influence (e)", f"{result['e']:.2f} m"],
        ["Anchor Tension Force (Z)", f"{result['Z']:.2f} kN/m"],
        ["Spindle Force V1", f"{result['V1']:.2f} kN/m"],
        ["Spindle Force V2", f"{result['V2']:.2f} kN/m"],
        ["Deflection (f)", f"{result['f']:.2f} mm/m"],
    ]
    loads_table = Table([[Paragraph(row[0], table_header_style if i == 0 else table_cell_style),
                          Paragraph(row[1], table_header_style if i == 0 else table_cell_style)] for i, row in enumerate(loads_data)],
                        colWidths=[100*mm, 80*mm])
    loads_table.setStyle(table_style)
    elements.extend([loads_table, Spacer(1, 4*mm), Paragraph(f"Final Values Based on {result['e']:.2f} m Spacing", heading_style)])

    final_data = [
        ["Parameter", "Value"],
        ["Anchor Tension Force (Z)", f"{result['Z'] * result['e']:.2f} kN"],
        ["Spindle Force V1", f"{result['V1'] * result['e']:.2f} kN"],
        ["Spindle Force V2", f"{result['V2'] * result['e']:.2f} kN"],
        ["Deflection (f)", f"{result['f'] * result['e']:.2f} mm"],
    ]
    final_table = Table([[Paragraph(row[0], table_header_style if i == 0 else table_cell_style),
                          Paragraph(row[1], table_header_style if i == 0 else table_cell_style)] for i, row in enumerate(final_data)],
                        colWidths=[100*mm, 80*mm])
    final_table.setStyle(table_style)
    elements.extend([final_table, Spacer(1, 4*mm), Paragraph("Validation and Notes", heading_style)])

    notes_data = [["Notes"]] + [[Paragraph(msg, table_cell_style)] for msg in validation_messages]
    notes_table = Table(notes_data, colWidths=[180*mm])
    notes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(notes_table)
    return elements

def generate_pdf_report(brace_type, height, pressure, result, validation_messages, project_number, project_name):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = build_pdf_elements(brace_type, height, pressure, result, validation_messages, project_number, project_name)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(doc.pagesize[0] / 2.0, 10 * mm, f"{PROGRAM} {PROGRAM_VERSION} | tekhne © | Page {page_num}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# Streamlit app
st.title("PERI Brace Frame Load Calculator")

# Sidebar for inputs
st.sidebar.header("Input Parameters")
brace_type = st.sidebar.selectbox("Brace Frame Type", list(brace_frame_data.keys()))
height = st.sidebar.number_input("Concreting Height (m)", min_value=2.50, max_value=8.75, step=0.01, value=5.50)
pressure = st.sidebar.number_input("Fresh Concrete Pressure (kN/m²)", min_value=30, max_value=60, step=1, value=60)
project_number = st.sidebar.text_input("Project Number", "PRJ-001")
project_name = st.sidebar.text_input("Project Name", "Sample Project")

# Calculate loads
result = get_loads(brace_type, height, pressure)

# Display results
st.header("Results")
if isinstance(result, str):
    st.error(result)
else:
    st.write(f"**Brace Frame:** {brace_type}")
    st.write(f"**Concreting Height:** {height} m")
    st.write(f"**Fresh Concrete Pressure:** {pressure} kN/m²")
    
    st.subheader("Calculated Loads (Per Meter)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Permissible Width of Influence (e): **{result['e']:.2f} m**")
        st.write(f"Anchor Tension Force (Z): **{result['Z']:.2f} kN/m**")
        st.write(f"Spindle Force V1: **{result['V1']:.2f} kN/m**")
    with col2:
        st.write(f"Spindle Force V2: **{result['V2']:.2f} kN/m**")
        st.write(f"Deflection (f): **{result['f']:.2f} mm/m**")

    st.subheader(f"Final Values Based on {result['e']:.2f} m Spacing")
    final_Z = result['Z'] * result['e']
    final_V1 = result['V1'] * result['e']
    final_V2 = result['V2'] * result['e']
    final_f = result['f'] * result['e']
    col3, col4 = st.columns(2)
    with col3:
        st.write(f"Anchor Tension Force (Z): **{final_Z:.2f} kN**")
        st.write(f"Spindle Force V1: **{final_V1:.2f} kN**")
    with col4:
        st.write(f"Spindle Force V2: **{final_V2:.2f} kN**")
        st.write(f"Deflection (f): **{final_f:.2f} mm**")

    st.subheader("Validation and Notes")
    validation_messages = validate_bracing(brace_type, height, result['e'])
    for message in validation_messages:
        if "Warning" in message:
            st.warning(message)
        elif "Required" in message:
            st.info(message)
        else:
            st.success(message)

    # Generate and offer PDF download
    pdf_data = generate_pdf_report(brace_type, height, pressure, result, validation_messages, project_number, project_name)
    if pdf_data:
        st.download_button(
            label="Download PDF Report",
            data=pdf_data,
            file_name=f"PERI_Brace_Frame_Calculation_Report_{project_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

# Sidebar notes
st.sidebar.markdown("---")
st.sidebar.write("**Notes:**")
st.sidebar.write("- Values are interpolated if not exact matches.")
st.sidebar.write("- Ensure inputs are within the supported ranges for each brace type.")
st.sidebar.write("- All values refer to a width of influence of 1.00 m unless otherwise specified.")
st.sidebar.write("- Final values are calculated by multiplying loads and deflection by the permissible width of influence (e).")

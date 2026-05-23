"""Thompson Sampling avec prior informé par features statiques."""
import numpy as np
import pandas as pd
from .recommender import ThompsonSampler as BaseThompson
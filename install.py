import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import silhouette_score
from sklearn_extra.cluster import KMedoids

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
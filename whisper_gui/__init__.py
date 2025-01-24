"""Init file of whisper_gui package"""
#export PYTHONPATH="${PYTHONPATH}:<path of whisper_gui>"
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
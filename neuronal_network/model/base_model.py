#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 14:48:08 2018

@author: daiberma
"""

import abc


class base_model_class():
    """Base class of a model
    """
    @abc.abstractmethod
    def get_model(self):
        """
        Returns
        ----
            the model
        """
        raise NotImplementedError("Should have implemented function \
                                  get_model()")

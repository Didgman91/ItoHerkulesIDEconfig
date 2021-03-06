"""
python implementation of paper: Deep speckle correlation: a deep learning
approach towards scalable imaging through
scattering media

paper link: https://arxiv.org/abs/1806.04139

Author: Yunzhe li, Yujia Xue, Lei Tian

Computational Imaging System Lab, @ ECE, Boston University

Date: 2018.08.21
"""

from __future__ import print_function

from keras.models import Model
from keras.layers import Input
from keras.layers import MaxPooling2D
from keras.layers import UpSampling2D
from keras.layers import Dropout
from keras.layers import Conv2D
from keras.layers import Concatenate
from keras.layers import Activation
from keras.layers.normalization import BatchNormalization

from keras.regularizers import l2

from .base_model import base_model_class


class model_deep_specle_correlation_class(base_model_class):
    # define conv_factory: batch normalization + ReLU + Conv2D + Dropout
    # (optional)
    def conv_factory(self, x, concat_axis, nb_filter,
                     dropout_rate=None, weight_decay=1E-4):
        x = BatchNormalization(axis=concat_axis,
                               gamma_regularizer=l2(weight_decay),
                               beta_regularizer=l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = Conv2D(nb_filter, (5, 5), dilation_rate=(2, 2),
                   kernel_initializer="he_uniform",
                   padding="same",
                   kernel_regularizer=l2(weight_decay))(x)
        if dropout_rate:
            x = Dropout(dropout_rate)(x)

        return x

    # define dense block

    def denseblock(self, x, concat_axis, nb_layers, growth_rate,
                   dropout_rate=None, weight_decay=1E-4):
        list_feat = [x]
        for i in range(nb_layers):
            x = self.conv_factory(x, concat_axis, growth_rate,
                                  dropout_rate, weight_decay)
            list_feat.append(x)
            x = Concatenate(axis=concat_axis)(list_feat)

        return x

    def get_model(self):
        """define model U-net modified with dense block
        """
        inputs = Input((64, 64, 1))
        print("inputs shape:", inputs.shape)

        # E0
        conv1 = Conv2D(16, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(inputs)
        print("conv1 shape:", conv1.shape)
        db1 = self.denseblock(
            x=conv1,
            concat_axis=3,
            nb_layers=4,
            growth_rate=16,
            dropout_rate=0.5)
        print("db1 shape:", db1.shape)
        pool1 = MaxPooling2D(pool_size=(2, 2))(db1)
        print("pool1 shape:", pool1.shape)

        # E1
        conv2 = Conv2D(32, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(pool1)
        print("conv2 shape:", conv2.shape)
        db2 = self.denseblock(
            x=conv2,
            concat_axis=3,
            nb_layers=4,
            growth_rate=16,
            dropout_rate=0.5)
        print("db2 shape:", db2.shape)
        pool2 = MaxPooling2D(pool_size=(2, 2))(db2)
        print("pool2 shape:", pool2.shape)

        # E2
        conv3 = Conv2D(64, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(pool2)
        print("conv3 shape:", conv3.shape)
        db3 = self.denseblock(
            x=conv3,
            concat_axis=3,
            nb_layers=4,
            growth_rate=16,
            dropout_rate=0.5)
        print("db3 shape:", db3.shape)
        pool3 = MaxPooling2D(pool_size=(2, 2))(db3)
        print("pool3 shape:", pool3.shape)

        # E3
        conv4 = Conv2D(128, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(pool3)
        print("conv4 shape:", conv4.shape)
        db4 = self.denseblock(
            x=conv4,
            concat_axis=3,
            nb_layers=4,
            growth_rate=16,
            dropout_rate=0.5)
        print("db4 shape:", db4.shape)
        pool4 = MaxPooling2D(pool_size=(2, 2))(db4)
        print("pool4 shape:", pool4.shape)

        # --
        conv5 = Conv2D(256, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(pool4)
        print("conv5 shape:", conv5.shape)
        db5 = self.denseblock(
            x=conv5,
            concat_axis=3,
            nb_layers=4,
            growth_rate=16,
            dropout_rate=0.5)
        print("db5 shape:", db5.shape)
        up5 = Conv2D(
            64,
            2,
            activation='relu',
            padding='same',
            kernel_initializer='he_normal')(
            UpSampling2D(
                size=(
                    2,
                    2))(db5))
        print("up5 shape:", up5.shape)
        merge5 = Concatenate(axis=3)([db4, up5])
        print("merge5 shape:", merge5.shape)

        # D1
        conv6 = Conv2D(128, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(merge5)
        print("conv6 shape:", conv6.shape)
        db6 = self.denseblock(
            x=conv6,
            concat_axis=3,
            nb_layers=3,
            growth_rate=16,
            dropout_rate=0.5)
        print("db5 shape:", db6.shape)
        up6 = Conv2D(
            64,
            2,
            activation='relu',
            padding='same',
            kernel_initializer='he_normal')(
            UpSampling2D(
                size=(
                    2,
                    2))(db6))
        print("up6 shape:", up6.shape)
        merge6 = Concatenate(axis=3)([db3, up6])
        print("merge6 shape:", merge6.shape)

        # D2
        conv7 = Conv2D(64, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(merge6)
        print("conv7 shape:", conv7.shape)
        db7 = self.denseblock(
            x=conv7,
            concat_axis=3,
            nb_layers=3,
            growth_rate=16,
            dropout_rate=0.5)
        print("db7 shape:", db7.shape)
        up7 = Conv2D(
            32,
            2,
            activation='relu',
            padding='same',
            kernel_initializer='he_normal')(
            UpSampling2D(
                size=(
                    2,
                    2))(db7))
        print("up7 shape:", up7.shape)
        merge7 = Concatenate(axis=3)([db2, up7])
        print("merge7 shape:", merge7.shape)

        # D3
        conv8 = Conv2D(32, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(merge7)
        print("conv8 shape:", conv8.shape)
        db8 = self.denseblock(
            x=conv8,
            concat_axis=3,
            nb_layers=3,
            growth_rate=16,
            dropout_rate=0.5)
        print("db8 shape:", db8.shape)
        up8 = Conv2D(
            16,
            2,
            activation='relu',
            padding='same',
            kernel_initializer='he_normal')(
            UpSampling2D(
                size=(
                    2,
                    2))(db8))
        print("up8 shape:", up8.shape)
        merge8 = Concatenate(axis=3)([db1, up8])
        print("merge8 shape:", merge8.shape)

        # D4
        conv9 = Conv2D(16, 3, activation='relu', padding='same',
                       kernel_initializer='he_normal')(merge8)
        print("conv9 shape:", conv9.shape)
        db9 = self.denseblock(
            x=conv9,
            concat_axis=3,
            nb_layers=3,
            growth_rate=16,
            dropout_rate=0.5)
        print("db9 shape:", db9.shape)

        # D5
        conv10 = Conv2D(
            8,
            3,
            activation='relu',
            padding='same',
            kernel_initializer='he_normal')(db9)
        print("conv10 shape:", conv10.shape)
        conv11 = Conv2D(2, 1, activation='softmax')(conv10)
        print("conv11 shape:", conv11.shape)

        model = Model(inputs=inputs, outputs=conv11)

        return model

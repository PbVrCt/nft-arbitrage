import tensorflow as tf
from tensorflow import keras as k
from keras_tuner import HyperModel


class NNmodel(HyperModel):
    def __init__(self):
        # self.input_shape = input_shape
        pass

    def build(self, hp):

        # Hyperparameter search space
        learning_rate = hp.Float(
            "learning_rate",
            min_value=1e-8,
            max_value=1e-1,
            default=5e-5,
            sampling="linear",
        )
        optimizer = hp.Choice("optimizer", values=["adam", "adagrad"])
        # activation_i=hp.Choice('hidden_activation_i',values=['relu', 'tanh', 'softmax'],default='relu')
        # clipnorm = hp.Float("clipnorm", min_value=0.5, max_value=10.0, default=1.0)
        # clipvalue = hp.Float("clipvalue", min_value=0.1, max_value=0.3, default=0.2)

        # # Initial hidden layers
        units_i = hp.Int(
            "units_i", min_value=10, max_value=100, default=15, sampling="linear"
        )
        batch_norm = hp.Boolean("bacht_norm")
        # activation_i=hp.Choice('hidden_activation_i',values=['relu', 'tanh', 'softmax'],default='relu')
        # l2regularization_i= hp.Float('l2regularization_i',min_value=0.0001,max_value=0.1,sampling='log')
        # gaussianNoise_i= hp.Float('gaussianNoise_i',min_value=0.001,max_value=2,sampling='log')

        # # Intermediate hidden layers
        units = hp.Int(
            "units", min_value=10, max_value=100, default=40, sampling="linear"
        )
        # max_value_ihl = 2
        # num_ihl = hp.Int(
        #     "num_intermediate_hidden_layers",
        #     min_value=0,
        #     max_value=max_value_ihl,
        #     default=1,
        # )
        activation = hp.Choice(
            "hidden_activation", values=["relu", "tanh"], default="relu"
        )
        # l2regularization= hp.Float('l2regularization',min_value=0.0001,max_value=0.1,sampling='log')
        # gaussianNoise = hp.Float('gaussianNoise',min_value=0.001,max_value=2.0,sampling='log')

        # # Final hidden layers
        units_f = hp.Int(
            "units_f", min_value=10, max_value=100, default=20, sampling="linear"
        )
        dropout_f = hp.Float(
            "dropout_f", min_value=0.1, max_value=0.7, sampling="linear"
        )
        # activation_f=hp.Choice('hidden_activation_f',values=['relu', 'tanh', 'softmax'],default='relu')
        # l2regularization_f= hp.Float('l2regularization_f',min_value=0.0001,max_value=0.1,sampling='log')
        # gaussianNoise_f = hp.Float('gaussianNoise_f',min_value=0.001,max_value=2.0,sampling='log')

        # Model
        model = k.Sequential()

        # Sequential() infers the input layer

        # # Initial hidden layers
        model.add(k.layers.Dense(units_i, activation=activation))
        model.add(k.layers.Dropout(0.1))
        if batch_norm == True:
            model.add(k.layers.BatchNormalization())
        # model.add( k.layers.GaussianNoise( gaussianNoise_i ) )
        # model.add(
        #     k.layers.Dense(
        #         units=units_i,
        #         activation=activation_i,
        #         activity_regularizer= k.regularizers.l2(l2regularization_i)
        #     )
        # )

        # # Intermediate hidden layers
        model.add(k.layers.Dense(units, activation=activation))
        model.add(k.layers.Dropout(0.1))
        if batch_norm == True:
            model.add(k.layers.BatchNormalization())
        # for i in range(num_ihl):
        #     with hp.conditional_scope(
        #         "num_intermediate_hidden_layers", list(range(i + 1, max_value_ihl + 1))
        #     ):
        #         model.add(
        #             k.layers.Dense(
        #                 units=hp.Int(
        #                     "units_" + str(i + 1), min_value=32, max_value=512, step=32
        #                 ),
        #                 activation="relu",
        #                 # activity_regularizer= k.regularizers.l2(l2regularization)
        #             )
        #         )
        #         model.add(k.layers.Dropout(0.1))
        #         model.add(k.layers.BatchNormalization())
        #         model.add(k.layers.GaussianNoise(gaussianNoise))

        # # Final hidden layers
        model.add(k.layers.Dense(units_f, activation=activation))
        model.add(k.layers.Dropout(dropout_f))
        # model.add(tf.keras.layers.Reshape((-1,1)))
        # model.add( k.layers.LSTM(16))
        # # model.add( k.layers.GRU(16))
        # # model.add( k.layers.SimpleRNN(16))

        # model.add(
        #     k.layers.Dense(
        #         units=units_f,
        #         activation=activation_f,
        #         activity_regularizer= k.regularizers.l2(l2regularization_f)
        #     )
        # )
        # model.add( k.layers.Dropout( dropout_f ) )
        # model.add( k.layers.GaussianDropout( 0.5 ) )
        # model.add( k.layers.ActivityRegularization(l1=0.1, l2=0.1 ) )
        # model.add( k.layers.LayerNormalization() )
        # model.add( k.layers.BatchNormalization() )
        # model.add( k.layers.GaussianNoise( gaussianNoise_f ) )

        # Output layer
        model.add(k.layers.Dense(1, activation="relu"))

        # Compile
        loss_fn = k.losses.MeanSquaredError(name="loss")
        if optimizer == "adam":
            with hp.conditional_scope("optimizer", "adam"):
                optimizer = k.optimizers.Adam(
                    learning_rate=learning_rate,  # clipnorm=clipnorm, clipvalue=clipvalue
                )
        elif optimizer == "adagrad":
            with hp.conditional_scope("optimizer", "adagrad"):
                optimizer = k.optimizers.Adagrad(
                    learning_rate=learning_rate,  # clipnorm=clipnorm, clipvalue=clipvalue
                )
        model.compile(
            optimizer=optimizer,
            loss=loss_fn,
            metrics=[rmse],
        )
        return model


# Metrics
rmse = k.metrics.RootMeanSquaredError(name="rmse")

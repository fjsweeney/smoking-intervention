# -*- coding: utf-8 -*-
from functools import partial
from hyperopt import fmin, hp, Trials, rand
from Models.hyperopt_pipeline.RandomForest import RandomForest
from Models.hyperopt_pipeline.miSVM_Classifier import miSVM_Classifier
from Models.hyperopt_pipeline.MISVM_Classifier import MISVM_Classifier
from Models.hyperopt_pipeline.LogisticRegression_Classifier import LogisticRegression_Classifier
from Models.hyperopt_pipeline.GradientBoosted_Classifier import GradientBoosted_Classifier
from Models.hyperopt_pipeline.SVM_Classifier import SVM_Classifier


def SvmExperiment(itrs, data, output_dir):
    # Define hyperparamter space
    hyperparameters = {
        "C": hp.choice("C", [0.001, 0.01, 0.1, 1, 10]),
        "gamma": hp.choice("gamma", [0.001, 0.01, 0.1, 1]),
        "resampling": hp.choice("resampling", ["SMOTE", "RandomOverSampler",
                                               "None"])
    }

    # Creating a higher order function to set all parameters except
    # "hyperparameters". This will be set during the call to 'fmin'.
    svm = partial(SVM_Classifier, data=data, output_dir=output_dir)
    obj = partial(train_and_eval, model_class=svm)

    # NOTE: fmin is the function that finds and returns the optimal set of
    # hyperparameters. It will train 'itrs' different models and search the
    # 'hyperparameters' space for the optimal set of
    # hyperparameters using the search algorithm specified by 'algo'.
    # See: https://github.com/hyperopt/hyperopt/wiki/FMin
    trials = Trials()
    best = fmin(fn=obj, space=hyperparameters, algo=rand.suggest,
                max_evals=itrs, trials=trials)

    return trials, best


def gradient_boosted_experiment(itrs, data, output_dir):
    """
    Set up a training experiment using Gradient Boosted Decision Trees.

    Args:
        itrs (int): Number of hyperparameter configurations to test
        data (list): List of Bag objects
        output_dir (str): Output directory for model files

    Returns:
        (obj): Trails object containing info about each Hyperopt trail
        (best): Best hyperparameter configuration
    """
    # Define hyperparamter space
    hyperparameters = {
        "n_estimators": hp.quniform("n_estimators", 10, 1000, 1),
        "min_samples_split": hp.quniform("min_samples_split", 2, 10, 1),
        "min_samples_leaf": hp.quniform("min_samples_leaf", 1, 40, 1),
        "max_depth": hp.quniform("max_depth", 1, 20, 1),
        "max_features": hp.uniform("max_features", 0.2, 1.0),
        "subsample": hp.uniform("subsample", 0.1, 1.0),
        "learning_rate": hp.uniform("learning_rate", 0.0001, 0.1),
        "resampling": hp.choice("resampling", ["SMOTE", "ADASYN",
                                               "RandomOverSampler"])
    }

    # Creating a higher order function to set all parameters except
    # "hyperparameters". This will be set during the call to 'fmin'.
    gbc = partial(GradientBoosted_Classifier, data=data, output_dir=output_dir)
    obj = partial(train_and_eval, model_class=gbc)

    # NOTE: fmin is the function that finds and returns the optimal set of
    # hyperparameters. It will train 'itrs' different models and search the
    # 'hyperparameters' space for the optimal set of
    # hyperparameters using the search algorithm specified by 'algo'.
    # See: https://github.com/hyperopt/hyperopt/wiki/FMin
    trials = Trials()
    best = fmin(fn=obj, space=hyperparameters, algo=rand.suggest,
                max_evals=itrs, trials=trials)

    return trials, best


def logistic_regression_experiment(itrs, data, output_dir):
    """
    Set up a training experiment using Logistic Regression.

    Args:
        itrs (int): Number of hyperparameter configurations to test
        data (list): List of Bag objects
        output_dir (str): Output directory for model files

    Returns:
        (obj): Trails object containing info about each Hyperopt trail
        (best): Best hyperparameter configuration
    """
    # Define hyperparamter space
    hyperparameters = {
        "penalty": hp.choice("penalty", ["l1", "l2"]),
        "C": hp.choice("C", [0.001, 0.01, 0.1, 1, 10, 100]),
        "resampling": hp.choice("resampling", ["SMOTE", "ADASYN",
                                               "RandomOverSampler"])
    }

    # Creating a higher order function to set all parameters except
    # "hyperparameters". This will be set during the call to 'fmin'.
    lrc = partial(LogisticRegression_Classifier, data=data,
                    output_dir=output_dir)
    obj = partial(train_and_eval, model_class=lrc)

    # NOTE: fmin is the function that finds and returns the optimal set of
    # hyperparameters. It will train 'itrs' different models and search the
    # 'hyperparameters' space for the optimal set of
    # hyperparameters using the search algorithm specified by 'algo'.
    # See: https://github.com/hyperopt/hyperopt/wiki/FMin
    trials = Trials()
    best = fmin(fn=obj, space=hyperparameters, algo=rand.suggest,
                max_evals=itrs, trials=trials)

    return trials, best


def miSVM_experiment(itrs, data, output_dir):
    """
    Set up a training experiment using mi-SVM.

    Args:
        itrs (int): Number of hyperparameter configurations to test
        data (list): List of Bag objects
        output_dir (str): Output directory for model files

    Returns:
        (obj): Trails object containing info about each Hyperopt trail
        (best): Best hyperparameter configuration
    """
    # Define hyperparamter space
    hyperparameters = {
        "C": hp.choice("C", [2**-5, 2**-4, 2**-3, 2**-2, 2**-1, 2**0, 2**1,
                             2**2, 2**3, 2**4, 2**5, 2**6, 2**7, 2**8, 2**9,
                             2**10, 2**11, 2**12, 2**13, 2**14, 2**15]),
        "max_iters": hp.quniform("max_depth", 10, 100, 5),
        "gamma": hp.choice("criterion", [2**-15, 2**-14, 2**-13, 2**-12,
                                         2**-11,
                                         2**-10, 2**-9, 2**-8, 2**-7, 2**-6,
                                         2**-5, 2**-4, 2**-3, 2**-2, 2**-1,
                                         2**0, 2**1, 2**2, 2**3]),
        "kernel": "rbf",
        "resampling": "SMOTE"
    }

    # Creating a higher order function to set all parameters except
    # "hyperparameters". This will be set during the call to 'fmin'.
    misvm = partial(miSVM_Classifier, data=data, output_dir=output_dir)
    obj = partial(train_and_eval, model_class=misvm)

    # NOTE: fmin is the function that finds and returns the optimal set of
    # hyperparameters. It will train 'itrs' different models and search the
    # 'hyperparameters' space for the optimal set of
    # hyperparameters using the search algorithm specified by 'algo'.
    # See: https://github.com/hyperopt/hyperopt/wiki/FMin
    trials = Trials()
    best = fmin(fn=obj, space=hyperparameters, algo=rand.suggest,
                max_evals=itrs, trials=trials)

    return trials, best


def MISVM_experiment(itrs, data, output_dir):
    """
    Set up a training experiment using MI-SVM.

    Args:
        itrs (int): Number of hyperparameter configurations to test
        data (list): List of Bag objects
        output_dir (str): Output directory for model files

    Returns:
        (obj): Trails object containing info about each Hyperopt trail
        (best): Best hyperparameter configuration
    """
    # Define hyperparamter space
    hyperparameters = {
        "C": hp.choice("C", [2**-5, 2**-4, 2**-3, 2**-2, 2**-1, 2**0, 2**1,
                             2**2, 2**3, 2**4, 2**5, 2**6, 2**7, 2**8, 2**9,
                             2**10, 2**11, 2**12, 2**13, 2**14, 2**15]),
        "max_iters": hp.quniform("max_depth", 10, 100, 5),
        "gamma": hp.choice("criterion", [2**-15, 2**-14, 2**-13, 2**-12,
                                         2**-11,
                                         2**-10, 2**-9, 2**-8, 2**-7, 2**-6,
                                         2**-5, 2**-4, 2**-3, 2**-2, 2**-1,
                                         2**0, 2**1, 2**2, 2**3]),
        "kernel": "rbf",
        "resampling": "SMOTE"
    }

    # Creating a higher order function to set all parameters except
    # "hyperparameters". This will be set during the call to 'fmin'.
    misvm = partial(MISVM_Classifier, data=data, output_dir=output_dir)
    obj = partial(train_and_eval, model_class=misvm)

    # NOTE: fmin is the function that finds and returns the optimal set of
    # hyperparameters. It will train 'itrs' different models and search the
    # 'hyperparameters' space for the optimal set of
    # hyperparameters using the search algorithm specified by 'algo'.
    # See: https://github.com/hyperopt/hyperopt/wiki/FMin
    trials = Trials()
    best = fmin(fn=obj, space=hyperparameters, algo=rand.suggest,
                max_evals=itrs, trials=trials)

    return trials, best


def random_forest_experiment(itrs, data, output_dir):
    """
    Set up a training experiment using Random Forest.

    Args:
        itrs (int): Number of hyperparameter configurations to test
        data (list): List of Bag objects
        output_dir (str): Output directory for model files

    Returns:
        (obj): Trails object containing info about each Hyperopt trail
        (best): Best hyperparameter configuration
    """

    # Define hyperparamter space
    hyperparameters = {
        "n_estimators": hp.quniform("n_estimators", 10, 1000, 1),
        "min_samples_split": hp.quniform("min_samples_split", 2, 10, 1),
        "min_samples_leaf": hp.quniform("min_samples_leaf", 1, 20, 1),
        "max_depth": hp.quniform("max_depth", 1, 20, 1),
        "max_features": hp.uniform("max_features", 0.01, 0.8),
        "criterion": hp.choice("criterion", ["mse", "mae"]),
        "resampling": hp.choice("resampling", ["SMOTE", "ADASYN",
                                               "RandomOverSampler"])
    }

    # Creating a higher order function to set all parameters except
    # "hyperparameters". This will be set during the call to 'fmin'.
    rf = partial(RandomForest, data=data, output_dir=output_dir)
    obj = partial(train_and_eval, model_class=rf)

    # NOTE: fmin is the function that finds and returns the optimal set of
    # hyperparameters. It will train 'itrs' different models and search the
    # 'hyperparameters' space for the optimal set of
    # hyperparameters using the search algorithm specified by 'algo'.
    # See: https://github.com/hyperopt/hyperopt/wiki/FMin
    trials = Trials()
    best = fmin(fn=obj, space=hyperparameters, algo=rand.suggest,
                max_evals=itrs, trials=trials)

    return trials, best


def train_and_eval(hyperparameters, model_class):
    # Construct model
    model = model_class(hyperparameters)

    # Train model
    loss = model.fit()

    return loss

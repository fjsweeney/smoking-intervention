# -*- coding: utf-8 -*-
import argparse
import datetime as dt
import json
import os
import pickle
import pprint
from subprocess import call
import numpy as np
import Models.Utils.HyperoptHelper as hh
import Models.RandomForest as rf
import Models.RandomForestExperiment as rfe


def create_output_dir(args):
    model_type = args.model

    if not os.path.isdir("./saved_models"):
        call("mkdir saved_models", shell=True)
    
    if not os.path.isdir("./saved_models/%s" % model_type):
        call("mkdir saved_models/%s" % model_type, shell=True)

    # Create directory storing all files generated by the current run
    now = dt.datetime.now()
    output_dir = "saved_models/%s/%s" % (model_type, 
        now.strftime("%Y-%m-%d_%H:%M:%S"))
    call('mkdir %s' % output_dir, shell=True)

    with open("%s/exp_config" % output_dir, "w") as fp:
        fp.write(args.__str__())

    return output_dir


def run_hyperopt_experiment(train, args):
    if args.model == "RF":
        print("Starting hyperopt experiment for Random Forest model...")
        output_dir = create_output_dir(args)

        trials, best = hh.random_forest_experiment(itrs=args.hyperopt,
                                                   data=train,
                                                   output_dir=output_dir)
        pickle.dump(rf.best_rf, open("%s/model.pkl" % output_dir, "wb"))
        pickle.dump(trials, open("%s/trials.pkl" % output_dir, "wb"))

        with open("%s/feature_importances" % output_dir, "w") as fp:
            fp.write(rf.best_rf.feature_importances_.__str__())

        with open("%s/best_config.json" % output_dir, "w") as fp:
            json.dump(best, fp)

    if args.model == "miSVM":
        print("Starting hyperopt experiment for mi-SVM model...")
        output_dir = create_output_dir(args)

        trials, best = hh.miSVM_experiment(itrs=args.hyperopt, data=train,
                                           output_dir=output_dir)
        pickle.dump(rf.best_svm, open("%s/model.pkl" % output_dir, "wb"))
        pickle.dump(trials, open("%s/trials.pkl" % output_dir, "wb"))

        with open("%s/best_config.json" % output_dir, "w") as fp:
            json.dump(best, fp)

    if args.model == "MISVM":
        print("Starting hyperopt experiment for MI-SVM model...")
        output_dir = create_output_dir(args)

        trials, best = hh.MISVM_experiment(itrs=args.hyperopt, data=train,
                                           output_dir=output_dir)
        pickle.dump(rf.best_svm, open("%s/model.pkl" % output_dir, "wb"))
        pickle.dump(trials, open("%s/trials.pkl" % output_dir, "wb"))

        with open("%s/best_config.json" % output_dir, "w") as fp:
            json.dump(best, fp)


def run_sklearn_experiment(train, args):
    print("Starting sklearn experiment for Random Forest model...")
    if args.model == "RF":
        output_dir = create_output_dir(args)

        rf_exp = rfe.RandomForestExperiment(train, args.sklearn)

        rf_exp.run()

        # Print results of best model
        print("Best F1 Score=%.5f" % rf_exp.best_score)
        pprint.PrettyPrinter(indent=4).pprint(rf_exp.cv_results)

        # Save results to experiment's output directory
        pickle.dump(rf_exp.best_model, open("%s/model.pkl" % output_dir, "wb"))
        pickle.dump(rf_exp.cv_results, open("%s/cv_results.pkl" % output_dir,
                                            "wb"))


def main(args):
    train = pickle.load(open(args.train, "rb"))

    if args.take_mean:
        print("Taking the feature mean of bag instances...")
        for bag in train:
            bag.instances = np.mean(bag.instances, axis=0)

    if args.hyperopt:
        run_hyperopt_experiment(train, args)
    elif args.sklearn:
        run_sklearn_experiment(train, args)

    print('Done')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, required=True,
                        help="File containing training data (a pkl)")
    parser.add_argument("--bag_interval", type=str,
                        help="Number of minutes for each bag.")
    parser.add_argument("--model", type=str, required=True,
                        choices=["RF", "miSVM", "MISVM"],
                        help="Model type")
    parser.add_argument("--hyperopt", type=int,
                        help="Number of hyperparameter iterations for "
                             "hyperopt tuning.")
    parser.add_argument("--sklearn", type=int,
                        help="Number of hyperparameter iterations for sklearn "
                             "tuning.")
    parser.add_argument("--take_mean", action='store_true', default=False,
                        help="Use the feature mean for each bag as one "
                             "instance (as opposed to stacking multiple "
                             "instances as the input to the model).")

    main(parser.parse_args())

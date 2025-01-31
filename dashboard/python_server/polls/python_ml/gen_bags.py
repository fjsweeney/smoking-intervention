import argparse
import os
import pandas as pd
import numpy as np
import pickle

from .Models.Preprocessing.Bag import Bag
from sklearn.preprocessing import MinMaxScaler

feature_set = ["activity_zscore", "cadence_zscore",
               "minute_ventilation_adjusted_zscore",
               "tidal_volume_adjusted_zscore",
               "heart_rate_zscore", "RR_interval_zscore", "hrv_zscore",
               "time_of_day"]


def get_label(start_time, end_time, smoking_df):
    mask = ((smoking_df["datetime"] >= start_time) &
            (smoking_df["datetime"] < end_time))
    subset = smoking_df[mask]

    if subset.empty:
        return -1

    return 1


def generate_bags(sensor_df, smoking_df, bag_interval, pid):
    all_bags = []

    if "time_of_day" in feature_set:
        scalar = MinMaxScaler()
        sensor_df["time_of_day"] = sensor_df["datetime"].dt.hour
        sensor_df["time_of_day"] = scalar.fit_transform(
            np.reshape(sensor_df["time_of_day"].values, newshape=(-1, 1))
        )

    # Iterate over all possible time windows and construct bags
    start_time = sensor_df["datetime"].iloc[0]
    end_time = start_time + np.timedelta64(bag_interval, 'm')
    final_time = sensor_df.iloc[sensor_df.shape[0] - 1]["datetime"]
    while start_time <= final_time:
        # Extract subset between start and end times.
        mask = ((sensor_df["datetime"] >= start_time) &
                (sensor_df["datetime"] < end_time))

        # Filter by time interval
        subset = sensor_df.loc[mask]

        # Construct bag
        instances = subset[feature_set].values

        if not np.isnan(instances).any():
            all_bags.append(Bag(pid, start_time, end_time, instances,
                                get_label(start_time, end_time, smoking_df),
                                feature_set))

        # Shift window by one minute
        start_time += np.timedelta64(1, 'm')
        end_time += np.timedelta64(1, 'm')

    print(" %d non-empty bags generated" % len(all_bags))
    return all_bags


def print_bag_stats(labels):
    print("Number of Data Points: %d" % len(labels))
    unique, counts = np.unique(labels, return_counts=True)
    v_pct = float(counts[1]) / float(len(labels))
    nv_pct = float(counts[0]) / float(len(labels))
    print("Vulnerable: %.2f | Not Vulnerable: %.2f" % (v_pct, nv_pct))


def remove_single_day(all_bags):
    unique_days = np.unique([x.end_time.day for x in all_bags])

    # Find the day with the fewest number of data points.
    shortest_length = np.inf
    shortest_day = None
    for day in unique_days:
        bags = [x for x in all_bags if x.end_time.day == day]

        # Ensure that removed day contains at least one positive label.
        pos_labels = [x for x in bags if x.label == 1]
        num_pos_labels = len(pos_labels)

        if 0 < len(bags) < shortest_length and num_pos_labels > 0:
            shortest_length = len(bags)
            shortest_day = day

    train_bags = [x for x in all_bags if x.end_time.day != shortest_day]
    test_bags = [x for x in all_bags if x.end_time.day == shortest_day]

    print("Left-out date: %s" % test_bags[0].end_time.__str__())

    return train_bags, test_bags


def main(args):
    # Navigate to data directory
    os.chdir(args.base_dir)

    # Get each participant directory
    participants = [filename for filename in os.listdir('./') if
                    filename.startswith('participant')]

    # Construct bags for each participant
    all_train_bags = []
    all_test_bags = []

    # Keep participant with largest validation set, our data set is too small.
    largest_validation_pid = None
    largest_validation_length = 0
    for participant in participants:
        print("Creating bags for %s..." % participant, end="")
        os.chdir(participant)

        pid = participant.split("_")[1]

        # Load in all sensor data
        sensor_df = pd.read_csv("all_features_min-to-min.csv", header=0,
                                index_col=0)
        sensor_df["datetime"] = pd.to_datetime(sensor_df["datetime"])

        # Load in smoking episodes
        smoking_df = pd.read_csv("ema/smoking_reports.csv", header=0,
                                 index_col=0)
        smoking_df["datetime"] = pd.to_datetime(smoking_df["datetime"])

        # Leave-one-day-out approach
        bags = generate_bags(sensor_df, smoking_df, args.bag_interval, pid)
        train_bags, test_bags = remove_single_day(bags)

        print("number of training bags=%d" % len(train_bags))
        print("number of test bags=%d" % len(test_bags))

        if len(test_bags) > largest_validation_length:
            largest_validation_length = len(test_bags)
            largest_validation_pid = pid

        all_train_bags += train_bags
        all_test_bags += test_bags

        os.chdir("../")

    print("Total number of training bags=%d." % len(all_train_bags))
    print("Total number of test bags=%d." % len(all_test_bags))

    # Move some bags to training set to put closer to 15% validation
    # TODO shift a percentage of the bags?
    print("Shifting pid=%s to the training set" % largest_validation_pid)
    # shift_bags = [x for x, i in all_test_bags if (x.pid == largest_validation_pid and i < (args.pct_test * len(all_test_bags)))]
    shift_bags = []
    new_test_bags = []
    for x in all_test_bags:
        if (x.pid == largest_validation_pid and len(shift_bags) < ((1 - args.pct_test) * len(all_test_bags))):

            shift_bags.append(x)
        else:
            new_test_bags.append(x)

    all_train_bags += shift_bags

    all_test_bags = new_test_bags
    # all_test_bags = [x for x in all_test_bags if x.pid !=
    #                  largest_validation_pid]  # Remove shifted bags

    print("Total number of training bags=%d." % len(all_train_bags))
    print("Total number of test bags=%d." % len(all_test_bags))

    print("Train Data Stats:")
    print_bag_stats([x.label for x in all_train_bags])
    print("Test Data Stats:")
    print_bag_stats([x.label for x in all_test_bags])

    pickle.dump(all_train_bags, open("train_intv=%s_min.pkl" %
                                     args.bag_interval, "wb"))
    pickle.dump(all_test_bags, open("test_intv=%s_min.pkl" %
                                    args.bag_interval, "wb"))

    print('Done')
    return "test_intv=" + args.bag_interval + "_min.pkl"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base_dir", type=str,
                        help="Directory containing participant data.")
    parser.add_argument("--bag_interval", type=str,
                        help="Number of minutes for each bag.")
    parser.add_argument("--pct_test", type=float,
                        help="Percent of data used for test set")

    main(parser.parse_args())

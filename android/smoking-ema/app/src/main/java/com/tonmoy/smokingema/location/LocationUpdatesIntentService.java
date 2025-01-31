/**
 * Copyright 2017 Google Inc. All Rights Reserved.
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * http://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.tonmoy.smokingema.location;

import android.app.IntentService;
import android.content.Context;
import android.content.Intent;
import android.location.Location;
import android.util.Log;

import com.google.android.gms.location.LocationResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.tonmoy.smokingema.model.UsersLocation;

import java.util.Calendar;
import java.util.List;

/**
 * Handles incoming location updates and displays a notification with the location data.
 * <p>
 * For apps targeting API level 25 ("Nougat") or lower, location updates may be requested
 * using {@link android.app.PendingIntent#getService(Context, int, Intent, int)} or
 * {@link android.app.PendingIntent#getBroadcast(Context, int, Intent, int)}. For apps targeting
 * API level O, only {@code getBroadcast} should be used.
 * <p>
 * Note: Apps running on "O" devices (regardless of targetSdkVersion) may receive updates
 * less frequently than the interval specified in the
 * {@link com.google.android.gms.location.LocationRequest} when the app is no longer in the
 * foreground.
 */
public class LocationUpdatesIntentService extends IntentService {

    private static final String ACTION_PROCESS_UPDATES =
            "com.google.android.gms.location.sample.locationupdatespendingintent.action" +
                    ".PROCESS_UPDATES";
    private static final String TAG = LocationUpdatesIntentService.class.getSimpleName();


    public LocationUpdatesIntentService() {
        // Name the worker thread.
        super(TAG);
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        if (intent != null) {
            final String action = intent.getAction();
            if (ACTION_PROCESS_UPDATES.equals(action)) {
                LocationResult result = LocationResult.extractResult(intent);
                if (result != null) {
                    Log.d("tonmoy", "Found some locations");
                    List<Location> locations = result.getLocations();
                    Utils.setLocationUpdatesResult(this, locations);
                    Utils.sendNotification(this, Utils.getLocationResultTitle(this, locations));
                    Log.i(TAG, Utils.getLocationUpdatesResult(this));
                    uploadLocationInfo(locations);
                }
            }
        }
    }

    private void uploadLocationInfo(List<Location> locations) {
        Log.d("tonmoy", "uploadLocationInfo get called");
        FirebaseDatabase database = FirebaseDatabase.getInstance();
        String currentUserId = FirebaseAuth.getInstance().getCurrentUser().getUid();
        DatabaseReference refUsersLocation = database.getReference().child("users_data").child(currentUserId).child("location");

        for (Location location : locations) {
            UsersLocation usersLocation = new UsersLocation();
            usersLocation.accuracy = location.hasAccuracy() ? location.getAccuracy() + "" : "n/a";
            usersLocation.altitude = location.hasAltitude() ? location.getAltitude() + "" : "n/a";
            usersLocation.latitude = location.getLatitude() + "";
            usersLocation.longitude = location.getLongitude() + "";
            usersLocation.speed = location.hasSpeed() ? location.getSpeed() + "" : "n/a";
            usersLocation.provider = location.getProvider();
            Calendar calendar = Calendar.getInstance();
            calendar.setTimeInMillis(location.getTime());
            usersLocation.timeUTC = calendar.getTimeInMillis();
            usersLocation.time = calendar.getTime().toString();
            refUsersLocation.child(usersLocation.time).setValue(usersLocation);
        }
    }
}

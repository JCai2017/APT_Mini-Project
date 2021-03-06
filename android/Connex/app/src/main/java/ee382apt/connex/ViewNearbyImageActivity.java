package ee382apt.connex;

import android.content.Intent;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.GridView;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.util.ArrayList;

import pub.devrel.easypermissions.EasyPermissions;

public class ViewNearbyImageActivity extends AppCompatActivity
        implements LocationListener, View.OnClickListener {
    private static final String TAG  = "NearByImageActivity";
    private final static int MIN_TIME = 5000;
    private final static float MIN_DIST = 5;
    LocationManager locationManager;
    // flag for GPS status
    boolean isGPSEnabled = false;

    // flag for network status
    boolean isNetworkEnabled = false;

    boolean canGetLocation = false;
    Location location; // location
    private double latitude;
    private double longitude;

    private static class Resp{
        ArrayList<String> images = new ArrayList<String>();
        ArrayList<String> names = new ArrayList<String>();
    }

    private static final String API_BASE_URL = "https://connex-180814.appspot.com/streamapi?location=";
    //private static final String API_BASE_URL = "https://apt-fall2017.appspot.com/streamapi?location=";
    Resp resp;
    private static final String TAG2 = "MyTAG";
    private RequestQueue requestQueue;

    ArrayList<String> urlsHolder;
    ArrayList<String> namesHolder;

    ImageGridAdapter NearByStreamAdapter;
    GridView gridView;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_nearby_image);

        String[] geocamPermissions = {android.Manifest.permission.ACCESS_COARSE_LOCATION, android.Manifest.permission.ACCESS_FINE_LOCATION, android.Manifest.permission.CAMERA, android.Manifest.permission.WRITE_EXTERNAL_STORAGE};

        if (EasyPermissions.hasPermissions(ViewNearbyImageActivity.this, geocamPermissions)) {
            //decode file
        } else {
            EasyPermissions.requestPermissions(ViewNearbyImageActivity.this, "Access for geo and camera",
                    101, geocamPermissions);
        }

        locationManager = (LocationManager) getSystemService(LOCATION_SERVICE);
        getGeoLocation();

        urlsHolder = new ArrayList<String>();
        namesHolder = new ArrayList<String>();
        resp = new Resp();
        gridView = (GridView)findViewById(R.id.NearByGrid);
        String url = API_BASE_URL + Double.toString(longitude) + "&lat=" +  Double.toString(latitude);
        requestQueue = Volley.newRequestQueue(this);
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>(){
                    @Override
                    public void onResponse(String response) {
                        JsonParser parser = new JsonParser();
                        JsonObject json = (JsonObject)parser.parse(response);
                        Gson gson = new Gson();
                        resp = gson.fromJson(json, Resp.class);
                        populateGridView();
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                    }
                });
        stringRequest.setTag(TAG2);
        requestQueue.add(stringRequest);

        findViewById(R.id.StreamsButton).setOnClickListener(this);

    }


    void populateGridView() {
        namesHolder.clear();
        urlsHolder.clear();
        for (int i = 0; i < resp.images.size(); ++i) {
            urlsHolder.add("https://connex-180814.appspot.com/" +resp.images.get(i));
            //namesHolder.add(resp.names.get(i));
            NearByStreamAdapter = new ImageGridAdapter(this, null, urlsHolder);
            gridView.setAdapter(NearByStreamAdapter);
        }
    }



    public void getGeoLocation() {
        try {
            // getting GPS status
            isGPSEnabled = locationManager
                    .isProviderEnabled(LocationManager.GPS_PROVIDER);

            // getting network status
            isNetworkEnabled = locationManager
                    .isProviderEnabled(LocationManager.NETWORK_PROVIDER);

            if (!isGPSEnabled && !isNetworkEnabled) {
                // no network provider is enabled
            } else {
                this.canGetLocation = true;
                // First get location from Network Provider
                if (isNetworkEnabled) {
                    locationManager.requestLocationUpdates(
                            LocationManager.NETWORK_PROVIDER,
                            MIN_TIME,
                            MIN_DIST, this);
                    Log.d("Network", "Network");
                    if (locationManager != null) {
                        location = locationManager
                                .getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
                        if (location != null) {
                            latitude = location.getLatitude();
                            longitude = location.getLongitude();
                        }
                    }
                }
                // if GPS Enabled get lat/long using GPS Services
                if (isGPSEnabled) {
                    if (location == null) {
                        locationManager.requestLocationUpdates(
                                LocationManager.GPS_PROVIDER,
                                MIN_TIME,
                                MIN_DIST, this);
                        Log.d("GPS Enabled", "GPS Enabled");
                        if (locationManager != null) {
                            location = locationManager
                                    .getLastKnownLocation(LocationManager.GPS_PROVIDER);
                            if (location != null) {
                                latitude = location.getLatitude();
                                longitude = location.getLongitude();
                            }
                        }
                    }
                }
                Log.d(TAG, "Latitude: " + String.valueOf(latitude));
                Log.d(TAG, "Longitude: " + String.valueOf(longitude));
            }
        } catch (SecurityException e) {

        }
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {

    }

    @Override
    public void onProviderEnabled(String provider) {

    }

    @Override
    public void onProviderDisabled(String provider) {

    }
    @Override
    public void onLocationChanged(Location location) {
        latitude = location.getLatitude();
        longitude = location.getLongitude();

//        Log.d(TAG, "LatitudeCHANGED: " + String.valueOf(latitude));
//        Log.d(TAG, "LongitudeCHANGED: " + String.valueOf(longitude));
    }

    @Override
    public void onClick(View v){
        switch (v.getId()) {
            case R.id.StreamsButton:
                Intent intent = new Intent(this, ViewAllStreamsActivity.class);
                intent.putExtra("userEmail", getIntent().getStringExtra("user_email"));
                startActivity(intent);
                break;
        }
    }

}

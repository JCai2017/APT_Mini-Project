package ee382apt.connex;

/**
 * Created by StevenChang on 2017/10/26.
 */
import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;

import cz.msebera.android.httpclient.Header;
import pub.devrel.easypermissions.EasyPermissions;

public class ImageUploadActivity extends AppCompatActivity implements LocationListener {
    private static final String TAG  = "ImageUploadActivity";
    private static final int PICK_IMAGE = 1;
    private static final int CAMERA = 3;
    Context context = this;
    private String streamKey;
    private EditText text;
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
    private TextView txvAlert;
    private String userEmail;
    private String streamName;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_image_upload);
        streamKey = getIntent().getStringExtra("streamKey");
        streamName = getIntent().getStringExtra("streamName");
        userEmail = getIntent().getStringExtra("userEmail");

        locationManager = (LocationManager) getSystemService(LOCATION_SERVICE);
        //txvAlert = (TextView) findViewById(R.id.txv_alert);
        text = (EditText) findViewById(R.id.upload_message);

        TextView txv_streamName = (TextView) findViewById(R.id.txv_stream_name);
        txv_streamName.setText("Upload to: " + streamName);

        String[] geoPermissions = {Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.ACCESS_FINE_LOCATION};

        if (EasyPermissions.hasPermissions(ImageUploadActivity.this, geoPermissions)) {
            //decode file
        } else {
            EasyPermissions.requestPermissions(ImageUploadActivity.this, "Access for geo",
                    101, geoPermissions);
        }
        getGeoLocation();

        // Choose image from library
        Button chooseFromLibraryButton = (Button) findViewById(R.id.choose_from_library);
        chooseFromLibraryButton.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        String[] galleryPermissions = {Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE};

                        if (EasyPermissions.hasPermissions(ImageUploadActivity.this, galleryPermissions)) {
                            //decode file
                        } else {
                            EasyPermissions.requestPermissions(ImageUploadActivity.this, "Access for storage",
                                    101, galleryPermissions);
                        }
                        // To do this, go to AndroidManifest.xml to add permission
                        Intent galleryIntent = new Intent(Intent.ACTION_PICK,
                                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
                        // Start the Intent
                        startActivityForResult(galleryIntent, PICK_IMAGE);
                    }
                }
        );

        Button cameraButton = (Button) findViewById(R.id.btn_camera);
        cameraButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //Utils.gotoCameraActivity(ImageUploadActivity.this, CAMERA, userEmail);
                Intent it = new Intent(ImageUploadActivity.this, CameraActivity.class);
                it.putExtra("userEmail", userEmail);
                startActivityForResult(it, CAMERA);
            }
        });
    }

    @Override
    protected void onResume(){
        super.onResume();

        // find the best provider
        String best = locationManager.getBestProvider(new Criteria(), true);
        if (best != null){
            String[] geoPermissions = {Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.ACCESS_FINE_LOCATION};

            if (EasyPermissions.hasPermissions(ImageUploadActivity.this, geoPermissions)) {
                //decode file
            } else {
                EasyPermissions.requestPermissions(ImageUploadActivity.this, "Access for geo",
                        101, geoPermissions);
            }

            getGeoLocation();
        }
        //else txvAlert.setVisibility(View.VISIBLE);
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
    protected void onPause(){
        super.onPause();
        locationManager.removeUpdates(this);
    }

    @Override
    public void onBackPressed(){
        super.onBackPressed();
        //Utils.gotoViewSingleStreamActivity(ImageUploadActivity.this, streamKey, streamName, userEmail);
    }

    public Bitmap rotateBitmap(Bitmap source, float angle)
    {
        Matrix matrix = new Matrix();
        matrix.postRotate(angle);
        return Bitmap.createBitmap(source, 0, 0, source.getWidth(), source.getHeight(), matrix, true);
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == PICK_IMAGE && data != null && data.getData() != null && resultCode == Activity.RESULT_OK) {
            // User had pick an image.
            Uri selectedImage = data.getData();

            String[] filePathColumn = {MediaStore.Images.ImageColumns.DATA};
            Cursor cursor = getContentResolver().query(selectedImage, filePathColumn, null, null, null);
            cursor.moveToFirst();

            // Link to the image
            int columnIndex = cursor.getColumnIndex(filePathColumn[0]);
            String imageFilePath = cursor.getString(columnIndex);
            cursor.close();

            // Bitmap image created and show thumbnail
            ImageView imgView = (ImageView) findViewById(R.id.thumbnail);
            final Bitmap bitmapImage = BitmapFactory.decodeFile(imageFilePath);
            imgView.setImageBitmap(bitmapImage);

            // Enable the upload button once image has been uploaded
            Button uploadButton = (Button) findViewById(R.id.upload_to_server);
            uploadButton.setClickable(true);
            uploadButton.setOnClickListener(
                    new View.OnClickListener() {
                        @Override
                        public void onClick(View v) {
                            // Get photo caption
                            String photoCaption = text.getText().toString();

                            ByteArrayOutputStream baos = new ByteArrayOutputStream();
                            bitmapImage.compress(Bitmap.CompressFormat.JPEG, 50, baos);
                            byte[] b = baos.toByteArray();
                            postToServer(b, photoCaption); // argument must be b
//                            finish();
                        }
                    }
            );
        }

        else if (requestCode == CAMERA && resultCode == Activity.RESULT_OK) {
            String path = data.getStringExtra("path");
//            Bitmap bmp = BitmapFactory.decodeByteArray(byteArr , 0, byteArr.length);
            Bitmap bmp = BitmapFactory.decodeFile(path);
            final Bitmap bitmapImage = rotateBitmap(bmp, 90);
            ImageView imgView = (ImageView) findViewById(R.id.thumbnail);
            imgView.setImageBitmap(bitmapImage);

            Button uploadButton = (Button) findViewById(R.id.upload_to_server);
            uploadButton.setClickable(true);
            uploadButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    // Get photo caption
                    String photoCaption = text.getText().toString();

                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    bitmapImage.compress(Bitmap.CompressFormat.JPEG, 50, baos);
                    byte[] b = baos.toByteArray();
                    postToServer(b, photoCaption);
//                    finish();
                }
            });

        }
    }

    private void postToServer(byte[] encodedImage, String photoCaption){
        String url = "https://apt-fall2017.appspot.com/Add_Image_mobile?streamKey="+streamKey;
        String imgLocation = String.valueOf(latitude)+", "+String.valueOf(longitude);

        RequestParams params = new RequestParams();
        params.put("file", new ByteArrayInputStream(encodedImage));
        params.put("photoCaption", photoCaption);
        params.put("imgLocation", imgLocation);
        AsyncHttpClient client = new AsyncHttpClient();

//        Log.d(TAG, url);

        client.post(url, params, new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                Log.w("async", "success!!!!");
                Toast.makeText(context, "Upload Successful", Toast.LENGTH_SHORT).show();
//                finish();
               // Utils.gotoViewSingleStreamActivity(ImageUploadActivity.this, streamKey, streamName, userEmail);
                Intent intent = new Intent(ImageUploadActivity.this, SearchResultsActivity.class);
                intent.putExtra("userEmail", userEmail);
                startActivity(intent);
            }
            @Override
            public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                Log.e("Posting_to_blob","There was a problem in retrieving the url : " + e.toString());
            }
        });
    }

    @Override
    public void onLocationChanged(Location location) {
        latitude = location.getLatitude();
        longitude = location.getLongitude();

//        Log.d(TAG, "LatitudeCHANGED: " + String.valueOf(latitude));
//        Log.d(TAG, "LongitudeCHANGED: " + String.valueOf(longitude));
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
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        //getMenuInflater().inflate(R.menu.menu_image_upload, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        /*if (id == R.id.action_settings) {
            return true;
        }*/

        return super.onOptionsItemSelected(item);
    }
}

package ee382apt.connex;

import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

public class CameraActivity extends AppCompatActivity {
    ImageView imageView;
    String streamName;
    String streamKey;
    Bitmap bitmap;
    String userEmail;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.i("In Use Camera", "In Use camera");
        setContentView(R.layout.activity_camera);
        System.out.println("Image vie: " + imageView);
        Intent intent = getIntent();
        streamKey = getIntent().getStringExtra("streamKey");
        streamName = getIntent().getStringExtra("streamName");
        userEmail = getIntent().getStringExtra("userEmail");

        Intent lol = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(lol,0);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if(data != null){
            bitmap = (Bitmap) data.getExtras().get("data");
            setContentView(R.layout.activity_camera);
            System.out.println(bitmap);
            ((ImageView) findViewById(R.id.theImageView)).setImageBitmap(bitmap);

            Button ButtonCamera = (Button)findViewById(R.id.ButtonCamera);
            ButtonCamera.setClickable(true);
            ButtonCamera.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    Intent lol = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                    startActivityForResult(lol,0);
                }
            });

            Button usePictureButton = (Button) findViewById(R.id.usePicture);
            usePictureButton.setClickable(true);
            usePictureButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    Intent returnIntent = new Intent();
                    returnIntent.putExtra("bitmap", bitmap);
                    setResult(RESULT_OK, returnIntent);
                    finish();
                }
            });

            Button viewAllBtn = (Button) findViewById(R.id.viewAll);
            viewAllBtn.setClickable(true);
            viewAllBtn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    Intent it = new Intent(CameraActivity.this, ViewAllStreamsActivity.class);
                    it.putExtra("user_Email", userEmail);
                    startActivity(it);
                }
            });
        }
    }
}
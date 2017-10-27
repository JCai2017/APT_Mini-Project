package ee382apt.connex;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;

public class ViewSubsribedStreamActivity extends AppCompatActivity {

    String email;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_subsribed_stream);
        email = getIntent().getStringExtra("user_email");

    }
}

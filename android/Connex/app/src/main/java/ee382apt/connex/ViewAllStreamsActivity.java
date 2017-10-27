package ee382apt.connex;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.GridView;

public class ViewAllStreamsActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_all_streams);
        GridView gridView = (GridView)findViewById(R.id.AllStreams);
        ImageGridAdapter AllStreamAdapter = new ImageGridAdapter(this, new String[16]);
        gridView.setAdapter(AllStreamAdapter);
    }
}

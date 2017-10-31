package ee382apt.connex;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
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

public class ViewStreamActivity extends AppCompatActivity
        implements View.OnClickListener{

    private static class Resp{
        ArrayList<String> images = new ArrayList<String>();
        ArrayList<String> names = new ArrayList<String>();
        String owner;
        String key;
    }

    private static final String API_BASE_URL = "https://connex-180814.appspot.com/streamapi?target=";
    //private static final String API_BASE_URL = "https://apt-fall2017.appspot.com/streamapi?target=";
    Resp resp;
    private static final String TAG = "MyTAG";
    private RequestQueue requestQueue;
    String ownerEmail;
    String name;
    int start = 0;

    ArrayList<String> imageHolder;

    ImageGridAdapter AllStreamAdapter;
    GridView gridView;
    String email;
    void populateGridView() {
        imageHolder.clear();
        int end = resp.images.size();
        if(end - start >= 16){
            end = start + 16;
        }

        for (int i = start; i < end; ++i) {
            imageHolder.add(resp.images.get(i));
            AllStreamAdapter = new ImageGridAdapter(this, imageHolder);
            gridView.setAdapter(AllStreamAdapter);
        }

        start += 16;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_stream);
        email = getIntent().getStringExtra("user_email");
        name = getIntent().getStringExtra("streamName");
        name = name.replaceAll("\\s+", "%20");

        imageHolder = new ArrayList<String>();
        resp = new Resp();
        gridView = (GridView)findViewById(R.id.AllStreams);
        String url = API_BASE_URL + name;
        requestQueue = Volley.newRequestQueue(this);
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>(){
                    @Override
                    public void onResponse(String response) {
                        JsonParser parser = new JsonParser();
                        JsonObject json = (JsonObject)parser.parse(response);
                        Gson gson = new Gson();
                        resp = gson.fromJson(json, Resp.class);
                        ownerEmail = resp.owner;
                        populateGridView();
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                    }
                });
        stringRequest.setTag(TAG);
        requestQueue.add(stringRequest);

        findViewById(R.id.MoreButton).setOnClickListener(this);
        findViewById(R.id.UploadButton).setOnClickListener(this);
        findViewById(R.id.StreamsButton).setOnClickListener(this);
    }

    public void onClick(View v) {
        Intent intent;
        switch (v.getId()) {
            case R.id.MoreButton:
                populateGridView();
                break;
            case R.id.UploadButton:
                if(email != null) {
                    if (ownerEmail.equals(email)){
                        intent = new Intent(this, ImageUploadActivity.class);
                        intent.putExtra("userEmail", email);
                        intent.putExtra("streamKey", resp.key);
                        name = name.replace("%20", " ");
                        intent.putExtra("streamName", name);
                        startActivity(intent);
                    }
                }
                break;
            case R.id.StreamsButton:
                intent = new Intent(this, ViewAllStreamsActivity.class);
                intent.putExtra("user_email", email);
                startActivity(intent);
                break;
        }
    }


    @Override
    protected void onStop(){
        super.onStop();
        if(requestQueue != null){
            requestQueue.cancelAll(TAG);
        }
    }

}


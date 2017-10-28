package ee382apt.connex;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
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

public class ViewAllStreamsActivity extends AppCompatActivity
        implements View.OnClickListener{

    private static class Resp{
        ArrayList<String> coverImage = new ArrayList<String>();
        ArrayList<String> names = new ArrayList<String>();
    }

    private static final String API_BASE_URL = "https://connex-180814.appspot.com/streamapi?target=";
    Resp resp;
    private static final String TAG = "MyTAG";
    private RequestQueue requestQueue;

    ArrayList<String> coverImageHolder;
    ArrayList<String> namesHolder;

    ImageGridAdapter AllStreamAdapter;
    GridView gridView;
    String email;
    void populateGridView() {
        coverImageHolder.clear();
        namesHolder.clear();
        for (int i = 0; i < resp.coverImage.size(); ++i) {
            coverImageHolder.add(resp.coverImage.get(i));
            namesHolder.add(resp.names.get(i));
            AllStreamAdapter = new ImageGridAdapter(this, namesHolder, coverImageHolder);
            gridView.setAdapter(AllStreamAdapter);
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_all_streams);
        email = getIntent().getStringExtra("user_email");
        coverImageHolder = new ArrayList<String>();
        namesHolder = new ArrayList<String>();
        resp = new Resp();
        gridView = (GridView)findViewById(R.id.AllStreams);
        String url = API_BASE_URL + "all";
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
        stringRequest.setTag(TAG);
        requestQueue.add(stringRequest);
        gridView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                Intent it = new Intent(view.getContext(), ViewStreamActivity.class);
                it.putExtra("streamName", namesHolder.get(i));
                it.putExtra("user_email", email);
                startActivity(it);
            }
        });
        findViewById(R.id.SearchButton).setOnClickListener(this);
        findViewById(R.id.NearbyButton).setOnClickListener(this);
        findViewById(R.id.MySubscribedStreamButton).setOnClickListener(this);
    }

    public void onClick(View v) {
        Intent intent;
        switch (v.getId()) {
            case R.id.SearchButton:
                intent = new Intent(this, SearchResultsActivity.class);
                intent.putExtra("userEmail", email);
                startActivity(intent);
                break;
            case R.id.NearbyButton:
                intent = new Intent(this, ViewNearbyImageActivity.class);
                startActivity(intent);
                break;
            case R.id.MySubscribedStreamButton:
                if(email != null) {
                    intent = new Intent(this, ViewSubsribedStreamActivity.class);
                    intent.putExtra("user_email", email);
                    startActivity(intent);
                }
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

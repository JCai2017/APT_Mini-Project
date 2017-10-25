package ee382apt.connex;

import android.content.Intent;
import android.net.Uri;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.ListViewCompat;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;

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
import java.util.List;

public class SearchResultsActivity extends AppCompatActivity implements
        View.OnClickListener{

    private static class Resp{
        ArrayList<String> resultUrls = new ArrayList<String>();
        ArrayList<String> resultImages = new ArrayList<String>();
        ArrayList<String> titles = new ArrayList<String>();
        ArrayList<String> keys = new ArrayList<String>();
    }

    private static final String API_BASE_URL = "https://connex-180814.appspot.com/api?target=";
    Resp resp;
    private static ListView mListView;
    private static ImageListAdapter mImageListAdapter;
    private static List<String> mList, mTitles;
    private static final String TAG = "MyTag";
    private RequestQueue requestQueue;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search_results);
        mListView = (ListView)findViewById(R.id.list);
        mList = new ArrayList<String>();
        mTitles = new ArrayList<String>();
        resp = new Resp();

        findViewById(R.id.search_button).setOnClickListener(this);

        mListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                //Switch to View Image Activity with stream key
                //TODO: replace LoginActivity with name of View Stream activity class
                Intent intent = new Intent(view.getContext(), LoginActivity.class);
                startActivity(intent);
            }
        });
    }

    public void populateListView(){
        mList.clear();
        for(int i = 0; i < resp.resultImages.size(); i ++){
            mList.add(resp.resultImages.get(i));
            mTitles.add(resp.titles.get(i));

            mImageListAdapter = new ImageListAdapter(this, mList, mTitles);
            mListView.setAdapter(mImageListAdapter);
        }
    }

    public void getResults(){
        EditText editText = (EditText) findViewById(R.id.editText);
        String query = editText.getText().toString();
        if(query.equals("")){
            return;
        }
        query = query.replaceAll("\\s+", "%20");
        String url = API_BASE_URL + query;

        requestQueue = Volley.newRequestQueue(this);

        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>(){
                    @Override
                    public void onResponse(String response) {
                        JsonParser parser = new JsonParser();
                        JsonObject json = (JsonObject)parser.parse(response);
                        Gson gson = new Gson();
                        resp = gson.fromJson(json, Resp.class);

                        populateListView();
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                    }
        });

        stringRequest.setTag(TAG);

        requestQueue.add(stringRequest);


        /*if (android.os.Build.VERSION.SDK_INT >= 11){
            recreate();
        }else{
            Intent intent = getIntent();
            finish();
            startActivity(intent);
        }*/
    }

    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.search_button:
                getResults();
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

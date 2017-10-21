package ee382apt.connex;

import android.content.Intent;
import android.net.Uri;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.ListViewCompat;
import android.view.View;
import android.widget.AdapterView;
import android.widget.EditText;
import android.widget.ListView;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.google.gson.Gson;

import java.util.ArrayList;
import java.util.List;

public class SearchResultsActivity extends AppCompatActivity implements
        View.OnClickListener{

    private static class Resp{
        String[] resultUrls;
        String[] resultImages;
        String[] titles;
        String[] keys;
    }

    private static final String API_BASE_URL = "https://connex-180814.appspot.com/api?target=";
    Resp resp;
    private static ListView mListView;
    private static ImageListAdapter mImageListAdapter;
    private static List<String> mList, mTitles;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search_results);
        mListView = (ListView)findViewById(R.id.list);
        mList = new ArrayList<>();

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

    public void getResults(){
        EditText editText = (EditText) findViewById(R.id.editText);
        String query = editText.getText().toString();
        String url = API_BASE_URL + query;

        RequestQueue queue = Volley.newRequestQueue(this);

        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>(){
                    @Override
                    public void onResponse(String response) {
                        Gson gson = new Gson();
                        resp = gson.fromJson(response, Resp.class);
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                    }
        });


        for(int i = 0; i < resp.resultImages.length; i ++){
            mList.add(resp.resultImages[i]);
            mTitles.add(resp.titles[i]);
        }

        mImageListAdapter = new ImageListAdapter(this, mList, mTitles);
        mListView.setAdapter(mImageListAdapter);


        if (android.os.Build.VERSION.SDK_INT >= 11){
            recreate();
        }else{
            Intent intent = getIntent();
            finish();
            startActivity(intent);
        }
    }

    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.search_button:
                getResults();
                break;
        }
    }
}

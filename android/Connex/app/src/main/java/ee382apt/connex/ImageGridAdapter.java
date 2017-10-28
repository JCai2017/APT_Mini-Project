package ee382apt.connex;

/**
 * Created by shidashen on 10/27/17.
 */

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import com.android.volley.toolbox.ImageLoader;
import com.android.volley.toolbox.NetworkImageView;

import java.util.ArrayList;

public class ImageGridAdapter extends BaseAdapter {

    private final Context mContext;
    private final ArrayList<String> names;
    private final ArrayList<String> urls;
    private ImageLoader mImageLoader;
    private String BASE_URL = "https://connex-180814.appspot.com";
    // 1
    public ImageGridAdapter(Context context, ArrayList<String> names, ArrayList<String> img) {
        this.mContext = context;
        this.names = names;
        this.urls = img;
        this.mImageLoader = CustomVolleyRequestQueue.geInstance(context).getImageLoader();
    }

    public ImageGridAdapter(Context context, ArrayList<String> img){
        this.mContext = context;
        this.names = null;
        this.urls = new ArrayList<String>();
        for(int i = 0; i < img.size(); i ++){
            urls.add(BASE_URL.concat(img.get(i)));
        }

        this.mImageLoader = CustomVolleyRequestQueue.geInstance(context).getImageLoader();
    }

    // 2
    @Override
    public int getCount() {
        return urls.size();
    }

    // 3
    @Override
    public long getItemId(int position) {
        return 0;
    }

    // 4
    @Override
    public Object getItem(int position) {
        return null;
    }

    // 5
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {

        View v = View.inflate(mContext, R.layout.linearlayout_book, null);

        NetworkImageView img = (NetworkImageView)v.findViewById(R.id.grid_item_img);
        if(urls.get(position).equals("None")){
            mImageLoader.get("http://connex-180814.appspot.com/assets/NoCoverAvailable.jpg",
                    ImageLoader.getImageListener(img, R.mipmap.ic_launcher, android.R.drawable.alert_dark_frame));
            img.setImageUrl("http://connex-180814.appspot.com/assets/NoCoverAvailable.jpg", mImageLoader);
        } else {
            mImageLoader.get(urls.get(position), ImageLoader.getImageListener(img, R.mipmap.ic_launcher,
                    android.R.drawable.alert_dark_frame));
            img.setImageUrl(urls.get(position), mImageLoader);
        }
        if(names != null) {
            TextView nameTextView = (TextView)v.findViewById(R.id.grid_item_label);
            nameTextView.setText(names.get(position));
        }
        return v;
    }

    //private
}


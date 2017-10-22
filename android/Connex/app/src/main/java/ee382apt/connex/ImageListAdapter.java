package ee382apt.connex;

/**
 * Created by caiju on 10/20/2017.
 */

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;

import com.android.volley.toolbox.ImageLoader;
import com.android.volley.toolbox.NetworkImageView;

import java.util.List;

public class ImageListAdapter extends BaseAdapter{
    private ImageLoader mImageLoader;
    private Context mContext;
    private List<String> listURL;
    private List<String> titles;
    public ImageListAdapter(Context context, List<String> list, List<String> titles){
        mContext = context;
        listURL = list;
        this.titles = titles;
        mImageLoader = CustomVolleyRequestQueue.geInstance(context).getImageLoader();
    }

    @Override
    public int getCount(){
        return listURL.size();
    }

    @Override
    public Object getItem(int position){
        return listURL.get(position);
    }

    @Override
    public long getItemId(int position){
        return position;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent){
        View v = View.inflate(mContext, R.layout.list_item, null);
        NetworkImageView img = (NetworkImageView)v.findViewById(R.id.network_img_view);
        if(listURL.get(position).equals("None")){
            //TODO: replace listUrl.get(position) below with URL for no cover image url
            mImageLoader.get(listURL.get(position), ImageLoader.getImageListener(img, R.mipmap.ic_launcher, android.R.drawable.alert_dark_frame));
            img.setImageUrl(listURL.get(position), mImageLoader);
        }else {
            mImageLoader.get(listURL.get(position), ImageLoader.getImageListener(img, R.mipmap.ic_launcher, android.R.drawable.alert_dark_frame));
            img.setImageUrl(listURL.get(position), mImageLoader);
        }

        TextView txt = (TextView)v.findViewById(R.id.str_title);
        txt.setText(titles.get(position));

        return v;
    }
}

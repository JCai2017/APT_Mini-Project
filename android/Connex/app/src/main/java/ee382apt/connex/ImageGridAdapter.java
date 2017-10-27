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

public class ImageGridAdapter extends BaseAdapter {

    private final Context mContext;
    private final int[] streamIDs;

    // 1
    public ImageGridAdapter(Context context, int[] sIDs) {
        this.mContext = context;
        this.streamIDs = sIDs;
    }

    // 2
    @Override
    public int getCount() {
        return streamIDs.length;
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

        streamIDs[position];

        if (convertView == null) {
            final LayoutInflater layoutInflater = LayoutInflater.from(mContext);
            convertView = layoutInflater.inflate(R.layout.linearlayout_book, null);
        }

        final ImageView imageView = (ImageView)convertView.findViewById(R.id.grid_item_image);
        final TextView nameTextView = (TextView)convertView.findViewById(R.id.grid_item_label);

        imageView.setImageResource();
        nameTextView.setText();

        return convertView;
    }

    private
}


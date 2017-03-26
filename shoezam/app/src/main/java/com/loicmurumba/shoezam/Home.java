package com.loicmurumba.shoezam;

import android.media.Image;
import android.support.v7.app.ActionBar;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.ImageView;

public class Home extends AppCompatActivity {
    private ImageView shoePic;


    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);
        ActionBar actionBar = getSupportActionBar();
        actionBar.hide();

        shoePic= (ImageView) findViewById(R.id.shoePic);

    }
}

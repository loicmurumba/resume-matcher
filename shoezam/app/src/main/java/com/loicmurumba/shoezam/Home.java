package com.loicmurumba.shoezam;

import android.content.Intent;
import android.graphics.Bitmap;
import android.provider.MediaStore;
import android.support.v4.graphics.BitmapCompat;
import android.support.v7.app.ActionBar;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

public class Home extends AppCompatActivity {
    private ImageView shoePic;
    private Button takePic;

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);
        ActionBar actionBar = getSupportActionBar();
        actionBar.hide();

        shoePic= (ImageView) findViewById(R.id.shoePic);
        takePic= (Button) findViewById(R.id.takePic);

        takePic.setOnClickListener(new View.OnClickListener(){
            public void onClick(View view){
                Intent camera = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                startActivityForResult(camera, 5);

            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 5 && resultCode== RESULT_OK){
            Bitmap image = (Bitmap) data.getExtras().get("data");
            shoePic.setImageBitmap(image);
        }
    }
}

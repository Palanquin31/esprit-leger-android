package com.espritlibre.app;

import android.app.Activity;
import android.content.ClipData;
import android.content.Intent;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import androidx.core.content.FileProvider;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;
import org.json.JSONObject;
import java.io.File;

/** On-device OCR; camera images are private temporary files and are never uploaded. */
public final class PhotoBridge {
    public static final int PICK=8111, CAMERA=8112;
    private final MainActivity activity;
    private final WebView web;
    private final Handler main=new Handler(Looper.getMainLooper());
    private File pendingFile;
    private Uri pendingCamera;
    private boolean busy=false;

    PhotoBridge(MainActivity activity,WebView web){this.activity=activity;this.web=web;}
    @JavascriptInterface public void chooseImage(){main.post(()->start(false));}
    @JavascriptInterface public void takePhoto(){main.post(()->start(true));}

    private void start(boolean camera){
        if(busy)return;
        busy=true;
        try{
            Intent intent;
            if(camera){
                pendingFile=File.createTempFile("esprit-photo-",".jpg",activity.getCacheDir());
                pendingCamera=FileProvider.getUriForFile(activity,activity.getPackageName()+".photo",pendingFile);
                intent=new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                intent.putExtra(MediaStore.EXTRA_OUTPUT,pendingCamera);
                intent.setClipData(ClipData.newUri(activity.getContentResolver(),"Photo",pendingCamera));
                intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION|Intent.FLAG_GRANT_READ_URI_PERMISSION);
                activity.startActivityForResult(intent,CAMERA);
            }else{
                intent=new Intent(Intent.ACTION_GET_CONTENT).setType("image/*");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                activity.startActivityForResult(Intent.createChooser(intent,"Choisir une image"),PICK);
            }
        }catch(Exception e){cleanup();busy=false;emit("error","Impossible d’ouvrir la photo. Vérifie qu’une application photo est disponible.");}
    }

    public void onResult(int request,int result,Intent data){
        if(request!=PICK&&request!=CAMERA)return;
        Uri uri=request==CAMERA?pendingCamera:(data==null?null:data.getData());
        if(result!=Activity.RESULT_OK){cleanup();busy=false;emit("cancel","");return;}
        if(uri==null){cleanup();busy=false;emit("error","Aucune image reçue.");return;}
        emit("processing","");
        final TextRecognizer recognizer=TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
        try{
            InputImage image=InputImage.fromFilePath(activity,uri);
            recognizer.process(image).addOnSuccessListener(text->{
                String value=text.getText().trim();
                emit(value.isEmpty()?"empty":"success",value);
            }).addOnFailureListener(e->emit("error","La reconnaissance a échoué. Réessaie avec une image plus nette."))
              .addOnCompleteListener(task->{recognizer.close();cleanup();busy=false;});
        }catch(Exception e){recognizer.close();cleanup();busy=false;emit("error","Impossible de lire cette image.");}
    }

    private void cleanup(){
        if(pendingCamera!=null){
            try{activity.revokeUriPermission(pendingCamera,Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);}catch(Exception ignored){}
            pendingCamera=null;
        }
        if(pendingFile!=null){try{pendingFile.delete();}catch(Exception ignored){}pendingFile=null;}
    }

    private void emit(String status,String text){
        try{
            JSONObject payload=new JSONObject();payload.put("status",status);payload.put("text",text);
            String js="if(window.espritPhotoResultV811)window.espritPhotoResultV811(JSON.parse("+JSONObject.quote(payload.toString())+"));";
            main.post(()->web.evaluateJavascript(js,null));
        }catch(Exception ignored){}
    }
}

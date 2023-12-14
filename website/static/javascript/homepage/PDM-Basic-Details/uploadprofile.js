$('#fileup').change(function(){
    //here we take the file extension and set an array of valid extensions
        var res=$('#fileup').val();
        var arr = res.split("\\");
        var filename=arr.slice(-1)[0];
        filextension=filename.split(".");
        filext="."+filextension.slice(-1)[0];
        valid=[".jpg",".png",".jpeg",".bmp"];
        var filenameinput= filename.substring(0, 20);

        

    //if file is not valid we show the error icon, the red alert, and hide the submit button
        if (valid.indexOf(filext.toLowerCase())==-1){
            $( ".imgupload" ).hide("slow");
            $( ".imgupload.ok" ).hide("slow");
            $( ".imgupload.stop" ).show("slow");
          
            $('#namefile').css({"color":"red","font-weight":700});
            $('#namefile').html("File "+filenameinput+" is not a valid image!");
            $('#filetype').css({"color":"red","font-weight":700});
            $('#filetype').html("File Type:"+'\xa0'+filext.substring(1, 10).toUpperCase());
            
            $( "#submitbtn" ).hide();
            $( "#fakebtn" ).show();
        }else{
            //if file is valid we show the green alert and show the valid submit
            $( ".imgupload" ).hide("slow");
            $( ".imgupload.stop" ).hide("slow");
            $( ".imgupload.ok" ).show("slow");
          
            $('#namefile').css({"color":"green","font-weight":700});
            $('#namefile').html(filenameinput);
            $('#filetype').css({"color":"green","font-weight":700});
            $('#filetype').html("File Type:"+'\xa0'+filext.substring(1, 10).toUpperCase());
          
            $( "#submitbtn" ).show();
            $( "#fakebtn" ).hide();
            var value 
            const toBase64 = file => new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
          });
            
          async function Main() {
        
          const file = document.querySelector('#fileup').files[0];
          console.log(await toBase64(file));
          value = await toBase64(file);
          document.getElementById("base64").setAttribute('value',value);
          }
        Main();
        }
    });
       

    // BANNER DISPLAY FOR SELECTED IMAGE

    var selDiv = "";
    var storedFiles = [];
    $(document).ready(function () {
      $("#fileup").on("change", handleFileSelect);
      selDiv = $("#selectedBanner");
    });
  
    function handleFileSelect(e) {
      var files = e.target.files;
      var filesArr = Array.prototype.slice.call(files);
      filesArr.forEach(function (f) {
        if (!f.type.match("image.*")) {
            storedFiles.push(f);
  
            var reader1 = new FileReader();
            reader1.onload = function (e) {
              var html =
                '';
              selDiv.html(html);
            };
            reader1.readAsDataURL(f);
        }
        else{
            storedFiles.push(f);
  
            var reader = new FileReader();
            reader.onload = function (e) {
              var html =
                '<img src="' +
                e.target.result +
                "\" data-file='" +
                f.name +
                "' class='' width='200px' height='200px'" + "style=border-radius:50%;border-style:double;>";
              selDiv.html(html);
            };
            reader.readAsDataURL(f);
        }
      });
    }

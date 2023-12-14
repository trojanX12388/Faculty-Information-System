// DRAW SIGNATURE
const wrapper = document.getElementById("signature-pad");
const clearButton = wrapper.querySelector("[data-action=clear]");
const undoButton = wrapper.querySelector("[data-action=undo]");
const submitSignature = wrapper.querySelector("[data-action=submit-signature]");
const savePNGButton = wrapper.querySelector("[data-action=save-png]");
const saveJPGButton = wrapper.querySelector("[data-action=save-jpg]");
const canvas = wrapper.querySelector("canvas");
const signaturePad = new SignaturePad(canvas, {
  // It's Necessary to use an opaque color when saving image as JPEG;
  // this option can be omitted if only saving as PNG or SVG
  backgroundColor: 'rgb(255, 255, 255)'
});

// Adjust canvas coordinate space taking into account pixel ratio,
// to make it look crisp on mobile devices.
// This also causes canvas to be cleared.
function resizeCanvas() {
  // When zoomed out to less than 100%, for some very strange reason,
  // some browsers report devicePixelRatio as less than 1
  // and only part of the canvas is cleared then.
  const ratio =  Math.max(window.devicePixelRatio || 1, 1);

  // This part causes the canvas to be cleared
  canvas.width = canvas.offsetWidth * ratio;
  canvas.height = canvas.offsetHeight * ratio;
  canvas.getContext("2d").scale(ratio, ratio);

  // This library does not listen for canvas changes, so after the canvas is automatically
  // cleared by the browser, SignaturePad#isEmpty might still return false, even though the
  // canvas looks empty, because the internal data of this library wasn't cleared. To make sure
  // that the state of this library is consistent with visual state of the canvas, you
  // have to clear it manually.
  //signaturePad.clear();
  
  // If you want to keep the drawing on resize instead of clearing it you can reset the data.
  signaturePad.fromData(signaturePad.toData());
}

// On mobile devices it might make more sense to listen to orientation change,
// rather than window resize events.
window.onresize = resizeCanvas;
resizeCanvas();

function download(dataURL, filename) {
  const blob = dataURLToBlob(dataURL);
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.style = "display: none";
  a.href = url;
  a.download = filename;

  document.body.appendChild(a);
  a.click();

  window.URL.revokeObjectURL(url);
}

// One could simply use Canvas#toBlob method instead, but it's just to show
// that it can be done using result of SignaturePad#toDataURL.
function dataURLToBlob(dataURL) {
  // Code taken from https://github.com/ebidel/filer.js
  const parts = dataURL.split(';base64,');
  const contentType = parts[0].split(":")[1];
  const raw = window.atob(parts[1]);
  const rawLength = raw.length;
  const uInt8Array = new Uint8Array(rawLength);

  for (let i = 0; i < rawLength; ++i) {
    uInt8Array[i] = raw.charCodeAt(i);
  }

  return new Blob([uInt8Array], { type: contentType });
}

clearButton.addEventListener("click", () => {
  signaturePad.clear();
});

undoButton.addEventListener("click", () => {
  const data = signaturePad.toData();

  if (data) {
    data.pop(); // remove the last dot or line
    signaturePad.fromData(data);
  }
});

submitSignature.addEventListener("click", () => {
  if (signaturePad.isEmpty()) {
    alert("Please provide a signature first.");
  } else {
    const dataURL = signaturePad.toDataURL();
    value = dataURL;
    document.getElementById("base64").setAttribute('value',value);
  }
});

savePNGButton.addEventListener("click", () => {
  if (signaturePad.isEmpty()) {
    alert("Please provide a signature first.");
  } else {
    const dataURL = signaturePad.toDataURL("image/png");
    download(dataURL, "signature.png");
  }
});

saveJPGButton.addEventListener("click", () => {
  if (signaturePad.isEmpty()) {
    alert("Please provide a signature first.");
  } else {
    const dataURL = signaturePad.toDataURL("image/jpeg");
    download(dataURL, "signature.jpg");
  }
});


// VERIFYING FILE INPUT
var file_upload_signature = document.getElementById('file-upload');

/* Attached file size check. */
 var UploadFieldID = "file-upload";
 var MaxSizeInBytes = 102400;
 var fld = document.getElementById(UploadFieldID);

file_upload_signature.onchange = function(e) {
  var ext = this.value.match(/\.([^\.]+)$/)[1];
  switch (ext) {
    case 'jpg':
    case 'jpeg':
    case 'png':
       if( fld.files && fld.files.length == 1 && fld.files[0].size > MaxSizeInBytes )
         {
            // alert("The file size must be no more than " + parseInt(MaxSizeInBytes/1024) + "KB");
            fld.value = '';
            exceed_input()
         }
      else{
         valid_input()
         data_base64()
         return true; 
      }
      break;
    default:
      invalid_input()
      this.value = '';
  }
};

var valid = document.getElementById("is_valid");
var invalid = document.getElementById("is_invalid");
var exceed = document.getElementById("size_exceed");

// SHOW VALID
function valid_input() {
    valid.style.display = "block";
    invalid.style.display = "none";
    exceed.style.display = "none";
}

// SHOW INVALID
function invalid_input() {
    invalid.style.display = "block";
    valid.style.display = "none";
    exceed.style.display = "none";
}


// SHOW EXCEED
function exceed_input() {
    exceed.style.display = "block";
    invalid.style.display = "none";
    valid.style.display = "none";
}

// BASE 64 DATA
const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
});

async function data_base64() {
   const file = document.querySelector('#file-upload').files[0];
   try {
      const result = await toBase64(file);
      document.getElementById("base64_value").value = result;
   } catch(error) {
      console.error(error);
      return;
   }
   //...
}

// DICT CERTIFICATE UPLOAD

// VERIFYING FILE INPUT
var file_upload_dict = document.getElementById('dict_certificate');
file_upload_dict.onchange = function(e) {
  dict_base64()
};

async function dict_base64() {
   const file = document.querySelector('#dict_certificate').files[0];
   try {
      const result = await toBase64(file);
      document.getElementById("base64_dict_value").value = result;
   } catch(error) {
      console.error(error);
      return;
   }
   //...
}

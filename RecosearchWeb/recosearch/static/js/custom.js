function saveTextAsFile(ctx) {  
    console.log(ctx);
        
    var textToWrite;
      if(ctx=='text'){
        textToWrite = document.getElementById("article-text").innerText;
        console.log('denem');
        
      }
      else{
        textToWrite = document.getElementById("article-summary").innerText;
      }
    
    var textFileAsBlob = new Blob([textToWrite], { type: "text/plain" });
    filename = document.getElementById("title").innerText;
    var fileNameToSaveAs = filename + ".txt";

    var downloadLink = document.createElement("a");
    downloadLink.download = fileNameToSaveAs;
    downloadLink.innerHTML = "Download File";
    if (window.webkitURL != null) {
      // Chrome allows the link to be clicked
      // without actually adding it to the DOM.
      downloadLink.href = window.webkitURL.createObjectURL(textFileAsBlob);
    } else {
      // Firefox requires the link to be added to the DOM
      // before it can be clicked.
      downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
      downloadLink.onclick = function () {
        document.body.removeChild(downloadLink);
      };
      downloadLink.style.display = "none";
      document.body.appendChild(downloadLink);
    }

    downloadLink.click();
}

var button = document.getElementById("download");
if(button){
    button.addEventListener("click", function(){
        
        saveTextAsFile('text')});
}

var button2 = document.getElementById("download-sum");
if(button2){
    button2.addEventListener("click", saveTextAsFile);
}

var text = document.getElementById("article-text")
var btn = document.getElementById('analyze');
if(text){
    if(text.innerText)
    btn.classList.add('d-none')
}

//this is the javascript functions for base.html


function Add() {
  var selectCollection = document.getElementById('selectCollection');
  var newCollectionName = document.getElementById('newCollectionName');
  var newCollection = document.getElementById('newCollection');
  var collectionName = document.getElementById('collectionName');
  var videoUrl = document.getElementById('videoUrl');
  var description = document.getElementById('description');
  var inputAlert = document.getElementById('inputAlert');

  //var message = "string length is " + text.length;
  //results_box.innerHTML = message;

  if(selectCollection.value=="") {
    //new collection detect
    newCollection.value = "True";
    collectionName.value = newCollectionName.value;
  }
  else if(selectCollection.value=="Choose an Option") {
    collectionName.value = "";
  }
  else {
    collectionName.value = selectCollection.value;
  }

  if(collectionName.value=="") {
    if(newCollection.value=="True") {
      inputAlert.innerHTML = "Please input a name for your new collection."; console.log("1");
    }
    else {
      inputAlert.innerHTML = "Please choose a collection or create a new collection."; console.log("22");console.log("test");
    }
    event.preventDefault();
  }
  else if(videoUrl.value=="") {
    inputAlert.innerHTML = "Please input a youtube video url to add a video."; console.log("3");
    event.preventDefault();
  }
  else {
    document.forms["AddVideo"].submit();
    document.forms["AddVideo"].reset();
    //reset all the parameters
    newCollection.value = "False";
    var inputNewCollection = document.getElementById('newCollectionBlock');
    inputNewCollection.style.display="none";
    inputAlert.innerHTML = "";
  }
    //alert("new collection: "+selectcollection.value);
  event.preventDefault();
}

// change of drop down list
function OnSelectedIndexChange(){
  var inputNewCollection = document.getElementById('newCollectionBlock');
  if (document.getElementById('selectCollection').value == "") {
    inputNewCollection.style.display="block";
  } 
  else {
    inputNewCollection.style.display="none";
  }
}

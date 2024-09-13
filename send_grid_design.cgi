#!/usr/bin/perl

print "Content-type: text/html\n\n";

use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use DBI;

# require("rm_alert.cgi");
require("rm_config.cgi");
require("rm_dt_now.cgi") ;
# require("ma_reg_email_render.cgi") ;

my $localdb = &DB();
my $usr     = &USR();
my $pw      = &PW();
my $master  = &MASTER();
$shop       = &Shop() ;
$tz         = &TZ() ;

@data = &TimeNow($tz) ;

my $sqlnow = $data[0] ;
my $ymd    = $data[1] ;#yyyy-mm-dd

my $q = new CGI;
my $dfn     = $q->param('dfn');


$dbh = DBI->connect("DBI:mysql:rewardsaero_$localdb:localhost","$usr","$pw") ;

$sql = "SELECT `ID` from `Events` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
$showID = $sth->fetchrow_array();
$sth->finish();

$sql = "SELECT `Banner_Image_Small`, `Name` from `Events` WHERE `ID` = ?";
$sth = $dbh->prepare($sql);
$sth->execute($showID);
@row = $sth->fetchrow_array();
$bannerx    = $row[0];
$eventname  = $row[1];
$sth->finish();



$sql = "SELECT `Name`,`Subject`,`Message`, `Status`, `Purpose` from `Emails` where `ID` = '$dfn'";
$sth = $dbh->prepare($sql);
$sth->execute();
@row       = $sth->fetchrow_array();
$name      = $row[0];
$subjectx  = $row[1];
$htmlcodex = $row[2];
$stat      = $row[3];
$purposex  = $row[4];
$sth->finish();

if ($stat eq "Active"){
  $btnclass = "btn-danger";
  $btntext  = "Delete Email";
}
else{
  $btnclass = "btn-success";
  $btntext  = "Activate Email";
}

$sql = "SELECT `ID`, `Reserved`, `Context`, `Examples`, `The_Example` from `Email_Reserved_Words` WHERE `The_Example` != '' and `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
  $rID      = $row[0];
  $reserve  = $row[1];
  $context  = $row[2];
  $example  = $row[3];
  $theEx    = $row[4];
  $reserveMe{$reserve} = $theEx;
}
$sth->finish();

$sql = "SELECT `ID`, `URL`, `Description`, `Reserved`, `Sort` from `Image_Bin` WHERE `Status` = 'Active' and `Location` = 'email'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
  $iID      = $row[0];
  $iurl     = $row[1];
  $idesc    = $row[2];
  $ires     = $row[3];
  $isort    = $row[4];
  $theEx = qq[<img src="$iurl" alt="$idesc" style="max-height:40px;max-width:100%;" class="text-light">];
  $imageMe{"$isort^$ires"} = $theEx;
}
$sth->finish();

$dbh->disconnect ;

# foreach $ri(sort keys %imageMe){
#   $ex = $reserveMe{$r};
#   print qq[$r becomes $ex<br>];
#   # $htmlcode =~ s/$r/$ex/gi;
#   $subjectx  =~ s//"$ex"/gi;
# }


print qq[
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Design Email | $subjectx</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"></script>

  <!-- Font awesome 5 -->
<link href="fonts/fontawesome/css/all.min.css" type="text/css" rel="stylesheet">

  <!-- include summernote css/js -->
<link href="summernote/summernote.min.css" rel="stylesheet">
<script src="summernote/summernote.min.js"></script>

<!-- Alert Styling -->
<link rel="stylesheet" href="style/jquery.alertable.css">
<script src="script/jquery.alertable.min.js"></script>

<link href="style/style2.css" rel="stylesheet">

<style>
.btn-finish{
  background-color: #5cb85c!important;
  color: #000000!important;
  border-color: #5cb85c!important;
 }

 .btn-finish:hover{
   background-color: #f4f5f6!important;
   color: #f7893c!important;
   border-color: #f7893c;
}
.btn {
	text-transform: none;
}
</style>

<script>
function addText2HTML(str) {
    // var res = str.replace(/\\[username]/gi, "$email");
    // var res1 = res.replace(/\\[password]/gi, "$regnum");
    // var res2 = res1.replace(/\\[greeting]/gi, "Dear $first_name");
    // var res3 = res2.replace(/\\[full]/gi, "$first $last");
    document.getElementById('theRenderedText').innerHTML = str;
}
</script>


<script>
function PreviewMail(){
 var html = document.getElementById("summernote").value;
 var subject = document.getElementById("subject").value;
 console.log(html)
 document.getElementById("html2").value = html;
 document.getElementById("subject2").value = subject;

 var frm = document.getElementById("preview");
 frm.submit();

 
}

function reloadPage(){
	location.reload(false);
}

function popup(url){
 var width  = 1200;
 var height = 1200;
 var left   = (screen.width  - width)/2;
 var top    = (screen.height - height)/2;
 var params = 'width='+width+', height='+height;
 params += ', top='+top+', left='+left;
 params += ', directories=no';
 params += ', location=no';
 params += ', menubar=no';
 params += ', resizable=yes';
 params += ', scrollbars=yes';
 params += ', status=no';
 params += ', toolbar=no';
 newwin=window.open(url,'newwin111', params);
 if (window.focus) {newwin.focus()}
}
function deleteMe(x){
  if (x == "Inactive"){
    var msg = "Are you sure you want to <b>activate</b> this email?";
  }
  else{
    var msg = "Are you sure you want to <b>delete</b> this email?";
  }
  
  jQuery.alertable.confirm(msg,{html:true}).then(function(){
    actuallyDelete(x);
    }, function() {
    return;
    });
}
function actuallyDelete(stat){
  var dfn = "$dfn";
  var strURL = "delete_email_ajax.cgi"
    \$.ajax({
        type: "POST",
        url: strURL, 
        data: "emailID=$dfn&stat=$stat",
        error: function() {
            jQuery.alertable.alert("We had an API connection issue. Please try again.");
        },
        success: function (x){
          if (x == "Inactive"){
            // jQuery.alertable.alert("Email has been deleted.");
            jQuery.alertable.alert("Email has been deleted.",{html:true}).then(function() {
         
              window.location.reload()
            
            });
            
          }
          else if(x == "Active"){
            // jQuery.alertable.alert("Email has been activated");
            // window.location.reload()
            jQuery.alertable.alert("Email has been activated",{html:true}).then(function() {
         
              window.location.reload()
            
            });
          }
          else{
            jQuery.alertable.alert("There was an error in deleting this email.  Contact Joe.");
            return;
          }

        }
      });
}
function uploadNewImage(elementid){
  if (document.getElementById(elementid).value == ""){
    jQuery.alertable.alert("select an image to upload.");
    return;
  } else{
    var formData = new FormData();
    var imageFile = \$('#' + elementid)[0].files[0];
    formData.append('image', imageFile);
    formData.append('dfn', "$dfn");
    formData.append('purpose', "$purposex");
    formData.append('flag', "email");
    //console.log(formData);
    // var imgsrc = "catimg" + catid;
    var strURL = "image_ajax.cgi";

        \$.ajax({
            type: "POST",
            url: strURL,
            processData: false,
            contentType: false,
            data: formData,
            error: function() {
                jQuery.alertable.alert("We had an API connection issue. Please try again.");
                return;
            },
            success: function (x){
                var ex = document.getElementById("newimageshere").innerHTML;
                if (ex == ""){
                  document.getElementById("newimageshere").innerHTML = x;
                } else{
                  document.getElementById("newimageshere").innerHTML = ex + x;
                }
                document.getElementById(elementid).value = "";
                // document.getElementById(imgsrc).src = img;
            }
        });
      }
}
</script>
<script>
\$(document).ready(function() {
  // \$('#summernote').summernote();
  \$('#summernote').summernote({
                toolbar: [
                    // [groupName, [list of button]]
                    ['style', ['style']],
                    ['font', ['bold', 'italic', 'underline', 'clear']],
                    ['fontname', ['fontname']],
                    ['fontsize', ['fontsize']],
                    ['color', ['color']],
                    ['para', ['ul', 'ol', 'paragraph']],
                    ['height', ['height']],
                    ['table', ['table']],
                    ['insert', ['link']],
                    ['view', ['codeview']] // Removed 'fullscreen' and 'undo' buttons
                ]
            });
});
function copyMe(button){
  var buttonId = button.id;

  // Remove 'text-warning' class from all elements with the class 'copy'
  var copyElements = document.querySelectorAll('.copy');
  copyElements.forEach(function(element) {
      element.classList.remove('text-warning');
  });

  // Add 'text-warning' class to the clicked element
  button.classList.add('text-warning');

  // Copy the button ID to the clipboard
  var tempElement = document.createElement('textarea');
  tempElement.value = buttonId;
  document.body.appendChild(tempElement);
  tempElement.select();
  document.execCommand('copy');
  document.body.removeChild(tempElement);
  //alert('Copied to clipboard: ' + buttonId);
}
function toggleArrow(btnid,iID){
  \$('#' + iID).toggleClass('fa-chevron-down');
  \$('#' + iID).toggleClass('fa-chevron-up');
}
function sendGridTest(dfn,purpose,elementid){
  var emails = document.getElementById(elementid).value;
  if (emails == "" || emails.length < 4){
    jQuery.alertable.alert("No email entered.");
    return;
  } else{
    \$('#sendtest').hide();
    \$('#pendtest').show();
    var strURL = "send_grid_test.cgi";
    \$.ajax({
        type: "POST",
        url: strURL, 
        data: "dfn=" + dfn + "&purpose=" + purpose + "&emails=" + encodeURIComponent(emails),
        error: function() {
          \$('#sendtest').show();
          \$('#pendtest').hide();
            jQuery.alertable.alert("We had an API connection issue. Please try again.");
        },
        success: function (x){
          \$('#sendtest').show();
          \$('#pendtest').hide();
          jQuery.alertable.alert(x);
          return;

        }
      });
  }
}
</script>
</head>

<body>  
<div class="card mx-auto mt-3 shadow" style="width:98%;min-height: 100vh;">
<div class="card-header text-center">
<div class="mb-2">
<h4>$subjectx</h4>
</div>
<input type="button" value="Back" class="btn btn-white" onclick="location.href='send_grid_start.cgi'">
<input type="button" name="Preview" class="btn btn-primary" value="Preview" onclick="PreviewMail()">
</div>
<div class="card-body">
  <div class="form-row no-gutters">
<div class="col-3 shadow p-1">
<button id="keywordbutton" data-toggle="collapse" data-target="#keyword" class="btn btn-link text-dark small" onclick="toggleArrow(this.id,'arrowKeyword')"> Keywords <i class="fas fa-chevron-down text-dark ml-2 small" id="arrowKeyword"></i></button>
<div id="keyword" class="collapse">
<h6 class="mb-1 small"><span class="small text-warning">click to copy</span></h6>
];
foreach my $r(sort keys %reserveMe){
  my $ex = $reserveMe{$r};
  print qq[
    <div class="small mb-0"><button id="$r" class="btn btn-sm copy" onclick="copyMe(this)">$r</button> &nbsp;&nbsp; e.g. $ex</div>
  ];
}
print qq[
</div><!--end keyword collapse-->
<hr>
<button id="imagebutton" data-toggle="collapse" data-target="#image" class="btn btn-link text-dark small" onclick="toggleArrow(this.id,'imageKeyword')"> Images <i class="fas fa-chevron-down text-dark ml-2 small" id="imageKeyword"></i></button>
<div id="image" class="collapse">
<h6 class="mb-1 small"><span class="small text-warning">click to copy image</span></h6>
];
foreach my $ix(sort {$a <=> $b} keys %imageMe){
  my ($s,$i) = split(/\^/,$ix);
  my $ex = $imageMe{$ix};
  print qq[
    <div class="small mb-0"><button id="$i" class="btn btn-sm copy" onclick="copyMe(this)">$i</button> &nbsp;&nbsp; $ex</div>
  ];
}
print qq[
<div id="newimageshere"></div>
</div><!--end images-->
<hr>
<button id="newimagebutton" data-toggle="collapse" data-target="#newimage" class="btn btn-link text-dark small" onclick="toggleArrow(this.id,'newimagetag')">+ Add Image <i class="fas fa-chevron-down text-dark ml-2 small" id="newimagetag"></i></button>
<div id="newimage" class="collapse">
  <div class="form-group mt-1 mb-1">
    <label class="label">New Image</label>
    <input id="newimageX" class="form-control form-control-sm" type="file" accept="image/*" id="imageUpload" autocomplete="off">
  </div>
  <div class="text-left">
    <button type="button" class="btn btn-sm btn-primary" onclick="uploadNewImage('newimageX')">Submit</button>
  </div>
</div>
<hr>
<button id="testemailbutton" data-toggle="collapse" data-target="#sendemail" class="btn btn-link text-dark small" onclick="toggleArrow(this.id,'sendemailtag')"> Test Email <i class="fas fa-chevron-down text-dark ml-2 small" id="sendemailtag"></i></button>
<div id="sendemail" class="collapse">
  <div class="form-group mt-1 mb-1">
    <label class="label">Enter Email(s)</label>
    <input class="form-control form-control-sm" type="text" id="testemails" placeholder="separate multiple emails with a comma" autocomplete="off">
  </div>
  <div class="text-left">
    <button id="sendtest" type="button" class="btn btn-sm btn-primary" onclick="sendGridTest('$dfn','$purposex','testemails')">Submit</button>
    <button style="display:none" id="pendtest" type="button" class="btn btn-sm btn-primary" disabled>
      <span class="spinner-grow text-light"></span><span class="spinner-grow text-light"></span><span class="spinner-grow text-light"></span>
    </button>
  </div>
</div>
</div><!--end col-2-->
<div class="col-9">
  <form name="myform" id="myform" method="post" action="send_grid_build.cgi">
    <input type="hidden" name="dfn" value="$dfn">
<div class="form-group w-50">
<label class="label">Subject:</label>
<input type="text" class="form-control" name="subject" id="subject" value="$subjectx">
</div>

<div class="m-3">
<textarea id="summernote" name="code">$htmlcodex</textarea>
</div>

<!-- <div class="container-fluid text-center mt-3">
  <h4>$name</h4>
  <button type="button" class="btn btn-info mb-3" onclick="popup('ma_reg_email_reserved.cgi')">Reserved Words Table</button>
  <button type="button" class="btn $btnclass mb-3" onclick="deleteMe('$stat')">$btntext</button>
</div>

<div class="container-fluid">
  <div class="row">
      <div class="col-md-6 bg-light" style="padding-top:20px;">
        <span style="background: #000000;padding: 15px;color: white;">Subject: $subject_rendered</span>
        <br><hr>
        <span id="theRenderedText">$rendered</span>
      </div>

      <div class="col-md-6">
      Subject: <input type="text" class="form-control mb-2" name="subject" id="subject" value="$subject">
      <label for="code">HTML Code</label>
      <textarea class="form-control" name="code" id="code" rows="30" onkeyup="addText2HTML(this.value)">$htmlcode</textarea>
      </div>
  </div>
</div> -->

<div class="text-center mt-3 mb-4">

<!-- <input type="button" name="Reload" class="btn btn-primary" value="Reload" onclick="reloadPage()"> -->
<input type="submit" name="Submit" class="btn btn-lg btn-finish" value="Submit">
</div>
</form>

</div><!--end col-10-->
</div><!--end big row-->
</div><!--end card body-->
<div class="text-center card-footer">
  <input type="button" value="Back" class="btn btn-white" onclick="location.href='send_grid_start.cgi'">
<input type="button" name="Preview" class="btn btn-primary" value="Preview" onclick="PreviewMail()">
</div>
</div><!--end card-->

<form name="preview" id="preview" method="post" action="send_grid_preview.cgi" target="_blank">
<input type="hidden" name="dfn" value="$dfn">
<input type="hidden" name="html" id="html2" value="">
<input type="hidden" name="subject" id="subject2" value="">
</form>

<br><br>
</body>

</html>

];

exit;

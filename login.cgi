#!/usr/bin/perl


print "Content-type: text/html\n\n";
#print "<body bgcolor=#ffffff text=#000000>\n" ;

use CGI;
use DBI;
use CGI::Carp qw/fatalsToBrowser/;
use DateTime ;
use CGI::Cookie;
use Data::Dumper qw(Dumper) ;
use CGI::Session;
use MIME::Base64;

my $cgi = CGI->new;
my $session_id = $cgi->cookie('CGISESSID');
$session = CGI::Session->load(undef, $session_id, {Directory=>'sessions'});

if ($session){
$session->param("sid", "");
$session->expire("sid", '1s');
$session->expire('1s');
$session->clear();
}

require('rm_config.cgi') ;

$localdb = &DB() ;
$master = &MASTER();
$shop = &Shop();

print qq[
<!DOCTYPE html>
<html>
<head>
<title>$shop - Please sign in</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script><!--needed for boostrap-->
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.bundle.min.js" integrity="sha384-6khuMg9gaYr5AxOqhkVIODVIvm9ynTT5J4V1cfthmT+emCG6yVmEZsRHdxlotUnm" crossorigin="anonymous"></script><!--javascript + popper-->
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous"><!--stylesheet-->

<!-- Alert Styling -->
<link rel="stylesheet" href="style/jquery.alertable.css">
<script src="script/jquery.alertable.min.js"></script>

<link rel="icon" type="image/png" href="favicon.png">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="shortcut icon" href="favicon.ico">

<link rel="stylesheet" href="style/style2.css">
<style>
.label{
	font-weight: 675!important;
}
::placeholder{
	font-weight: 50;
}
.overlay{
display: none;
position: fixed;
width: 100%;
height: 100%;
top: 0;
left: 0;
z-index: 999;
background: rgba(255,255,255,0.8) center no-repeat;
}

/* Turn off scrollbar when body element has the loading class */
body.loading{
overflow: hidden;
}
/* Make spinner image visible when body element has the loading class */
body.loading .overlay{
display: block;
}
.spinner {
display: block;
position: fixed;
z-index: 1031; /* High z-index so it is on top of the page */
top: 20%;
right: 50%; /* or: left: 50%; */
margin-top: -..px; /* half of the elements height */
margin-right: -..px; /* half of the elements widht */
}
</style>
<style>

</style>
<SCRIPT LANGUAGE="JavaScript">

\$(document).on({
    ajaxStart: function(){
        \$("body").addClass("loading");
    },
    ajaxStop: function(){
        \$("body").removeClass("loading");
    }
});
function checkCreds(){
	var un = document.getElementById("username").value;
	var pwd = document.getElementById("password").value;
	if (un == "" || pwd == ""){
		document.getElementById("username").focus();
		jQuery.alertable.alert("Please complete both fields");
		return;
	}
	else{
		var strURL = "check_creds_ajax.cgi";
    \$.ajax({
        type: "POST",
        url: strURL,
        data: "username=" + encodeURIComponent(un) + "&pwd=" + encodeURIComponent(pwd),
        error: function() {
            jQuery.alertable.alert("We had an API connection issue. Please try again.");
        },
        success: function (rec){
			console.log(rec);
			if (rec == "Yes"){
				var frm = document.getElementById("nextform");
				frm.submit();
			}
			else{
				document.getElementById("username").focus();
				document.getElementById("username").value = "";
				document.getElementById("password").value = "";
				jQuery.alertable.alert("Incorrect credentials.");
				return;
			}
			

        }
    });

	 }
}
</script>
<style>
.bg2{
background-color: black; /* Set background color to black */
background-image: url('grey_logo.png'); /* Path to your logo image */
background-repeat: repeat; /* Repeat the image across the background */
background-size: 100px 50px;/*  Adjust the size of the repeated logo */
}
.row.no-gutters {
    display: flex;
    align-items: center; /* Vertically center content */
    background-color: #fff;
}
.left-columnx {
    background-color: white;
    padding: 20px;
    padding-top: 60px;
}
.right-columnx img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.min-vh-100 {
	min-height: calc(100vh - 50px) !important;
}
.w90{
    width: 90%;
}
\@media (max-width: 767.98px) {

    .right-columnx {
        display:none;
    }
    .w90{
        width: 100%;
    }
    /* .min-vh-100 {
	    min-height: calc(60vh - 50px) !important;
    } */
}
.btn-sign{
    background-color: transparent;
    border: 2px solid #e8e8e8;
    color: #e8e8e8;
}
.btn-sign:hover{
    border: 2px solid #ffffff!important;
    color: #ffffff!important;
}
.text-light{
    color: #e8e8e8!important;
}
.bg-light{
    background-color: #e8e8e8!important;
}
body{
    background-image: url("/images/background/Entry_Background_image2x.png");
    background-size: cover;
    background-position: center;
    height: 100vh;
}
.w25{
    width: 30%;
}
\@media (max-width: 1400px) {
.w25{
    width: 50%;
}
}
\@media (max-width: 900px) {
.w25{
    width: 60%;
}
}
\@media (max-width: 800px) {
.w25{
    width: 80%;
}
}
\@media (max-width: 600px) {
.w25{
    width: 100%;
}
}
</style>
</head>

<body>
<div class="overlay"><div class="spinner-border text-primary spinner" role="status"></div></div>

<form id="nextform" action="checknext.cgi" method="post" autocomplete="off">
</form>


<div class="mt-0 text-center mx-auto w25 bg-light shadow p-1" style="height:50px;">
    <img class="brandtop" src="/images/menu/Nav_Aero.png" alt="Logo" style="max-height:100%;max-width:20%;object-fit:cover;">&nbsp;&nbsp;&nbsp;
    <img class="brandtop" src="/images/menu/Nav_Stag.png" alt="Logo" style="max-height:100%;max-width:20%;object-fit:cover;">&nbsp;&nbsp;&nbsp;
    <img class="brandtop" src="/images/menu/Nav_BA.png" alt="Logo" style="max-height:100%;max-width:20%;object-fit:cover;">&nbsp;&nbsp;&nbsp;
    <img class="brandtop" src="/images/menu/Nav_VG6.png" alt="Logo" style="max-height:100%;max-width:20%;object-fit:cover;">
</div>

<div class="d-flex align-items-center justify-content-md-center min-vh-100 flex-column pt-3 pt-md-0" style="">
    <h1 class="mb-1 text-light">WELCOME</h1>
    <p class="mb-3 text-light">Login to enjoy your hard work!</p>
    <div class="card w-50 shadow" style="border: 0px solid transparent!important">
        <div class="row no-gutters align-items-stretch">
            <div class="col-md-6 left-columnx p-4">
                <div class="p-0 p-xl-4">
                <div class="form-group mx-auto w90" ><h4>SIGN IN</h4></div>
                <div class="form-group mx-auto w90" >
                    <label for="username">USERNAME</label>
                    <input type="text" placeholder="username\@domain.com" id="username" class="form-control" autocomplete="off">
                </div>
                <div class="form-group mx-auto w90" >
                    <label for="username">PASSWORD</label>
                    <input type="password" placeholder="Password" id="password" class="form-control" autocomplete="off">
                </div>
                <div class="form-group mx-auto w90" >
                    <button type="button" class="btn btn-primary" onclick="checkCreds()">SIGN IN</button>
                </div>
                </div>
                <div class="text-right mt-3">
                <button type="button" class="btn btn-link btn-sm p-0" style="color:#000000" onclick="location.href='reset.cgi'">FORGOT PASSWORD</button>
                </div>
            </div>
            <div class="col-md-6 right-columnx">
                <img id="columnX" src="/images/login_page/LoginPage_RightImage.png" alt="Placeholder Image">
            </div>
        </div>
    </div>
    <div class="text-center mt-3">
        <p class="smalltext">Don't have an account?</p>
        <button type="button" class="btn btn-sign" onclick="location.href='New-Account.cgi'">SIGN UP</button>
    </div>
</div>


</body>
</html>

];

exit ;

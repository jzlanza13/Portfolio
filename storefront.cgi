#!/usr/bin/perl

print "Content-type: text/html\n\n";

use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use DBI;
use CGI::Session;

my $cgi = CGI->new;
my $session_id = $cgi->cookie('CGISESSID');
$session = CGI::Session->load(undef, $session_id, {Directory=>'sessions'});

require("rm_config.cgi") ;
require("rm_dt_now.cgi") ;
require("ab_nav_bar.cgi");

&Security();

$sid = "";
$sid = $session->param("sid");

if ($loginType ne "Admin"){
	MyAlert("Your session has ended.","login.cgi");
}

my $localdb = &DB();my $usr = &USR();my $pw = &PW();
my $master  = &MASTER();
my $shop    = &Shop() ;
my $tz      = &TZ() ;

my @data    = &TimeNow($tz) ;
my $sqlnow = $data[0] ;
my $ymd    = $data[1] ;

my $q = new CGI;

$displayThis = $q->param("display");

if ($displayThis eq ""){
    $displayThis = "Category_Grid";
}

$dbh = DBI->connect("DBI:mysql:rewardsaero_$localdb:localhost","$usr","$pw") ; ;

$sql = "SELECT `ID`, `Brand`, `Color_Bar`, `Light_Logo`, `Sort`, `bg_class`, `txt_class`, `Dark_Logo` from `Brand_Management` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $brandID  = $row[0];
    my $brand    = $row[1];
    my $color    = $row[2];
    my $white    = $row[3];
    my $sort     = $row[4];
    my $bg       = $row[5];
    my $txt      = $row[6];
    my $darkSlice = $row[7];

    $brandSlice{$brandID} = $darkSlice;

    $brandSquare{$brandID} = $white;
    $brandTxtClass{$brandID} = $txt;
    $brandSquareClass{$brandID} = $bg;
    $brandName{$brandID} = $brand;
}
$sth->finish();

$sql = "SELECT `ID`, `Category` from `Categories` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
  my $catID = $row[0];
  my $cat   = $row[1];
  $catHash{"$cat^$catID"} = 1;
  $catName{$catID} = $cat;
}
$sth->finish();

$sql = "SELECT `ID`, `Category_ID`, `Subcategory` from `Categories_Sub` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
  my $subid = $row[0];
  my $catid = $row[1];
  my $sub   = $row[2];

  $catname = $catName{$catid};
  $subname = $sub.qq[ ($catname)];
  $subHash{$catid}{"$subname^$subid"} = 1;
  $subName{$subid} = $sub;
}
$sth->finish();

#$brandSquare{1} = "images/logos/aero_white.png";
#$brandClass{1}  = "aero";
#$brandSquare{2} = "images/logos/stag_white.png";
#$brandClass{2}  = "stag";
#$brandSquare{3} = "images/logos/ba_white.png";
#$brandClass{3}  = "ba";
#$brandSquare{4} = "images/logos/vg6_white.png";
#$brandClass{4}  = "vg6";



$sql = "SELECT `ID`, `Position`, `Title`, `Description`, `Link_Type`, `DFN`, `Image`, `Button_Text` from `rm1_store_slider` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $slideID = $row[0];
    my $pos     = $row[1];
    my $tit     = $row[2];
    my $desc    = $row[3];
    my $ltype   = $row[4];
    my $ldfn    = $row[5];
    my $img     = $row[6];
    my $btxt    = $row[7];
    $slideHash{"$pos^$slideID"} = "$tit^$desc^$ltype^$dfn^$btxt^$img";
}
$sth->finish();

$sql = "SELECT `ID`, `Position`, `Image`, `BrandID`, `Link_Type`, `DFN` from `rm1_store_catgrid` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $catgridid = $row[0];
    my $catpos    = $row[1];
    my $catimg    = $row[2];
    my $catbrand  = $row[3];
    my $cattype   = $row[4];
    my $catdfn    = $row[5];
    if ($cattype eq "Cat"){
        $catname = $catName{$catdfn};
    }
    if ($cattype eq "Sub"){
        $catname = $subName{$catdfn};
    }
    if ($cattype eq "Brand"){
        $catname = $brandName{$catdfn};
    }
    $catname = uc($catname);
    my $square      = $brandSquare{$catbrand};
    my $squareclass = $brandSquareClass{$catbrand};
    my $txtclass    = $brandTxtClass{$catbrand};
    my $brandname   = $brandName{$catbrand};
    $brandname = uc($brandname);
    $catGridImage{$catpos}       = $catimg;
    $catGridSquareClass{$catpos} = $squareclass;
    $catGridSquare{$catpos}      = $square;
    $catGridTxtClass{$catpos}    = $txtclass;
    $catGridBrand{$catpos}       = $brandname;
    $catGridCat{$catpos}         = $catname;
    $catGridLink{$catpos} = qq[onclick="selectMe('$cattype','$catdfn')"];

    $brandSelectedGrid{"$catpos^$catbrand"} = "selected";
    $catSelectedGrid{"$catpos^$catdfn^$cattype"} = "selected";
}
$sth->finish();

$featureLink = "";
$sql = "SELECT `ID`, `Type`, `ImageURL`, `ActionType`, `DFN`, `PromoTitle` from `Featured_Products` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    $featureID  = $row[0];
    $ftype      = $row[1];
    $fimg       = $row[2];
    $faction    = $row[3];
    $fdfn       = $row[4];
    $ftitle     = $row[5];##promo only
    if ($ftype eq "Promo"){
        $featured{"PromoImg"} = $fimg;
        $featured{"PromoTitle"} = $ftitle;
        $featuredLink = qq[selectMe('$faction','$fdfn')];
        $featuredDFNSelected{"$featureID^$faction^$fdfn"} = "selected";
    } else{
        $featuredX{$featureID} = $fdfn;
        $featuredDFNSelected{"$featureID^$faction^$fdfn"} = "selected";
    }
}
$sth->finish();

$sql = "SELECT `ID`, `Image_Location_Small`, `Item`, `Accrue`, `Redeem`, `SKU` from `rm1_items` WHERE `Status` = 'Active' and `Image_Location_Small` != ''";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $itemID   = $row[0];
    my $iimg     = $row[1];
    my $item     = $row[2];
    my $accrue   = $row[3];
    my $redeem   = $row[4];
    my $sku      = $row[5];
    $itemImage{$itemID} = $iimg;
    $itemName{$itemID}  = $item;
    $itemRedeem{$itemID} = $redeem;
    $itemSku{$itemID} = $sku;
}
$sth->finish();

$dbh->disconnect;

print qq[
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="pragma" content="no-cache" />
<meta http-equiv="cache-control" content="max-age=604800" />
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

<title>Storefront</title>


<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script><!--needed for boostrap-->
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.bundle.min.js" integrity="sha384-6khuMg9gaYr5AxOqhkVIODVIvm9ynTT5J4V1cfthmT+emCG6yVmEZsRHdxlotUnm" crossorigin="anonymous"></script><!--javascript + popper-->
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous"><!--stylesheet-->

<!-- Font awesome 5 -->
<link href="fonts/fontawesome/css/all.min.css" type="text/css" rel="stylesheet">

<!-- Alert Styling -->
<link rel="stylesheet" href="style/jquery.alertable.css">
<script src="script/jquery.alertable.min.js"></script>

<script src="script/sorttable.js"></script>

<link rel="icon" type="image/png" href="favicon.png">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="shortcut icon" href="favicon.ico">

<link rel="stylesheet" href="style/style2.css">


<style>
.carousel-item {
    height: 100%;
    min-height: 300px;
    background-size: cover;
    background-position: center;
}

.carousel-caption {
    bottom: 50%;
    transform: translateY(50%);
    text-align: left;
    left: 15%;
    right: auto;
}
.carousel-caption h5, .carousel-caption p, .carousel-caption h2 {
    color: white!important;
}
.carousel-caption h2{
    font-size: 2.8em;
}
.carousel-caption h2{
    font-size: 2.8em;
}
.carousel-caption h5{
    font-size: 1.1em;
}
\@media (max-width: 450px) {
    .carousel-caption {
        left: 50%;
        transform: translateX(-50%);
        text-align: center;
        right: auto;
        font-size: 1em;
    }
    .carousel-caption h2{
        font-size: 2em;
    }
    .carousel-caption h5{
        font-size: 1em;
    }
}
.carousel-control-prev-icon, .carousel-control-next-icon {
    /* filter: invert(100%); */
    /* background-color: white; */
}

.cards-row {
    margin-top: -50px;
    position: relative;
    z-index: 100;
}
.btn-orange{
    background-color: transparent;
    color: #f15a29!important;
    border-color: #f15a29!important;
    font-family: "Roboto Bold", sans-serif !important;
    border: 2px solid #f15a29!important;
}
.cardx {
position: relative;
padding: 0;
overflow: hidden;
border: none;
max-height: 500px;
}
\@media (max-width: 800px) {
    .cardx{
        max-width: 300px;
    }
}
.nav-link{
    color: black!important;
    font-weight: 550;
}
.nav-item{
    margin-bottom: 0px;
}
.card-img {
    width: 100%;
    height: 100%;
    object-fit:cover;
}
.card-img-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 1rem;
    color: #fff;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.card-title {
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}
.card-title h5{
    color: #fff!important;
}
h5.card-title{
    color: #fff!important;
}
.btn-white {
    background-color: transparent;
    color: #fff!important;
    border-color: #fff!important;
    font-family: "Roboto Bold", sans-serif !important;
    border: 2px solid #fff!important;
}
.color-bar1 {
    height: 10px;
    background-color: #e77852; /* Your desired color */
    width: 100%;
    top: 0;
    left: 0;
    z-index: 1;
}
.color-bar2 {
    height: 10px;
    background-color: #CCAA4F; /* Your desired color */
    width: 100%;
    top: 0;
    left: 0;
    z-index: 1;
}
.color-bar3 {
    height: 10px;
    background-color: #EC1C24; /* Your desired color */
    width: 100%;
    top: 0;
    left: 0;
    z-index: 1;
}
.color-bar4 {
    height: 10px;
    background-color: #21A1DF; /* Your desired color */
    width: 100%;
    top: 0;
    left: 0;
    z-index: 1;
}
.cardy {
    border: none;
    position: relative;
    height: 388px;
    cursor: pointer;
}
.cardy:hover{
    transform: scale(1.02);
    -webkit-transition: transform 0.4s ease-in-out;
}


.card-img-overlay2 {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    padding: 1rem;
    z-index: 1;
}
.logo {
    position: absolute;
    top: 10px;
    left: 10px;
}
p.text-bottom-left {
    margin-bottom: 0;
    font-family: "Roboto Bold", sans-serif !important;
}
h5.text-bottom-left {
    color: white!important;
    font-family: "Roboto Bold", sans-serif !important;
}
.half-width {
    flex: 0 0 50%;
    max-width: 50%;
}
.double-height {
    height: calc(776px + .5rem);
}
.active-page {
  text-decoration:underline;
}
.widget-header {
	display: inline-block;
	vertical-align: middle;
	position: relative;
}
.icon-sm {
	width: 30px;
	height: 30px;
	font-size: 20px;
    display: inline-block;
    text-align: center;
}
.icon i{
    color: #000000!important;
}
.icon i:hover{
    color: #f15a29!important;
}
.widget-header .cartcount {
	position: absolute;
	top: -10px;
	right: 1px;
}
.cartcount{
    color: #f15a29!important;
    font-weight: 900;
}

.dropdown-toggle{
    margin-bottom: 0;
}
.dropdown-menu {
    padding: 0; /* Removes padding, adjust if needed */
    margin: 0; /* Ensures no additional margins */
}
.navbar-nav {
            margin: auto;
        }
.navbar{
    height: auto;
}
\@media (min-width: 992px) {
.navbar {
    height: 60px;
}
}
.second-header {
    position: relative;
    height: 50px;
    background-color: #e8e8e8; /* Light grey background */
    display: flex;
    align-items: center;
    justify-content: flex-end; /* Align items to the right */
    padding: 0 20px; /* Add padding to the sides */
}
.customer-info .btnx {
    background-color: #f15a29;
    color: #fff;
}
.black{
    color: #000000!important;
}
.white{
    color: #fff!important;
}
.cardx{
    max-height:500px;
}
.styled-square {
    position: absolute;
    top: 10px;
    left: 0px;
    width: 60px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index:3;
    clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 0 100%)
}
.styled-square img {
    width: 40px; /* Adjust logo size as needed */
    height: auto;
}
.styled-square.aero{
    background-color: #f15a29; /* Background color */
}
.styled-square.stag{
    background-color: #CCAA4F; /* Background color */
}
.styled-square.ba{
    background-color: #EC1C24; /* Background color */
}
.styled-square.vg6{
    background-color: #21A1DF; /* Background color */
}
.aero-text{
    color: #f15a29!important;
}
.stag-text{
    color: #CCAA4F!important;
}
.ba-text{
    color: #EC1C24!important;
}
.vg6-text{
    color: #21A1DF!important;
}
.product-container{
    display: flex;
    overflow-x: auto;
    padding: 10px 10px;
    height: 500px;
}
.product-cardx{
    background-color: #E8E8EB;
    box-shadow: 0 .5rem 1rem rgba(0,0,0,.15) !important;
    transition: transform 0.5s ease-in-out;
    height: 465px;
    margin-right: 15px;
    max-width: calc(300px - 15px);
    flex: 0 0 calc(300px - 15px);
}
.product-card {
    position: relative;
    margin-bottom: 30px;
    background-color: #E8E8EB;
    box-shadow: 0 .5rem 1rem rgba(0,0,0,.15) !important;
    transition: transform 0.5s ease-in-out;
    height: 450px;
}
.product-card .card-img-top {
    width: 96%;
    height: 225px; /* Set the desired height */
    object-fit: contain;
    margin-right:auto;
    margin-left:auto;
    margin-top:5px;
    padding:5px;
    background-color:#fff;
    box-shadow: 0 .5rem 1rem rgba(0,0,0,.15) !important;
}
.product-cardx .card-img-top {
    width: 100%;
    height: 225px; /* Set the desired height */
    object-fit: cover;
    margin-right:auto;
    margin-left:auto;
}
.price-banner {
    position: absolute;
    top: 0;
    left: 0;
    background-color: #f15a29;
    color: #fff!important;
    padding: 5px 10px;
    font-weight: bold;
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 0% 100%);
}
.featured-column {
    position: relative;
    /* background-image: url('images/home_page/Slider_Ad_Static.png'); */
    background-size: cover;
    background-position: center;
    color: #fff!important;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
    height: 500px;
    box-shadow: 0 .5rem 1rem rgba(0,0,0,.15) !important;
}
.carousel-indicators li{
    background-color: #000;
}
.carousel-item {
    transition: transform 1.2s ease; /* Change 0.8s to your desired duration */
}
.carousel-itemp{
    flex: 1;
    padding: 15px;
}

.btn-edit {
    background-color: white;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
}

.overlay-edit {
    top: 0;
    left: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 10;
}

.overlay-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
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

<script>
\$(document).on({
    ajaxStart: function(){
        \$("body").addClass("loading");
    },
    ajaxStop: function(){
        \$("body").removeClass("loading");
    }
});
function selectMe(type,dfn){
    console.log(type);
    console.log(dfn);
}
\$(document).ready(function() {
    // Show the overlay when the edit button is clicked
    \$('.btn-edit').on('click', function() {
        \$(this).siblings('.overlay-edit').removeClass('d-none');
    });

    // Hide the overlay when the cancel button is clicked
    \$('.cancelButton').on('click', function() {
        \$(this).closest('.overlay-edit').addClass('d-none');
    });

});
function uploadSlice(imageId,inputId,dfn){
    var inputFile = \$('#' + inputId)[0].files[0];
    var formData = new FormData();
    formData.append('newImage', inputFile);
    formData.append('flag', 'BrandSlice');
    formData.append('dfn', dfn);
    var overlay = \$('#' + inputId).closest('.overlay-edit');
    var strURL = "storefront_image_upload.cgi";
    if (document.getElementById(inputId).value != ""){
        \$.ajax({
        url: strURL, 
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(newImageUrl) {
            // Assuming the response contains the URL of the uploaded image
            // var newImageUrl = response.newImageUrl;
            \$('#' + imageId).attr('src', newImageUrl);
            overlay.addClass('d-none');
        },
        error: function() {
            jQuery.alertable.alert('There was an error uploading the image.');
        }
    });
    } else{
        jQuery.alertable.alert("Please select a photo");
        return;
    }
}
function uploadCatGrid(imageId,inputId,dfn){
    var inputFile = \$('#' + inputId)[0].files[0];
    var formData = new FormData();
    formData.append('newImage', inputFile);
    formData.append('flag', 'CatGrid');
    formData.append('dfn', dfn);
    var overlay = \$('#' + inputId).closest('.overlay-edit');
    var strURL = "storefront_image_upload.cgi";
    if (document.getElementById(inputId).value != ""){
        \$.ajax({
        url: strURL, 
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(newImageUrl) {
            // Assuming the response contains the URL of the uploaded image
            // var newImageUrl = response.newImageUrl;
            \$('#' + imageId).attr('src', newImageUrl);
            overlay.addClass('d-none');
        },
        error: function() {
            jQuery.alertable.alert('There was an error uploading the image.');
        }
    });
    } else{
        jQuery.alertable.alert("Please select a photo");
        return;
    }
}
function updateCatGrid(element,dfn,val,elementid){
    var strURL = "storefront_image_upload.cgi";
    var flag = "updateCatGrid";
    var overlay = \$('#' + elementid).closest('.overlay-edit');
    \$.ajax({
      type: "POST",
      url: strURL, 
      data: "element=" + element + "&flag=" + flag + "&value=" + encodeURIComponent(val) + "&dfn=" + dfn,
      error: function() {
          jQuery.alertable.alert("We had an API connection issue. Please try again.");
      },
      success: function (x){
            //overlay.addClass('d-none');
            //return;
          document.location.reload();
          return;
        
      }
    });
}
function uploadFeatured(imageId,inputId,dfn){
    var inputFile = \$('#' + inputId)[0].files[0];
    var formData = new FormData();
    formData.append('newImage', inputFile);
    formData.append('flag', 'FeaturedImg');
    formData.append('dfn', dfn);
    var overlay = \$('#' + inputId).closest('.overlay-edit');
    var strURL = "storefront_image_upload.cgi";
    if (document.getElementById(inputId).value != ""){
        \$.ajax({
        url: strURL, 
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(newImageUrl) {
            // Assuming the response contains the URL of the uploaded image
            // var newImageUrl = response.newImageUrl;
            document.getElementById(imageId).style.backgroundImage = 'url(' + newImageUrl + ')';
            overlay.addClass('d-none');
        },
        error: function() {
            jQuery.alertable.alert('There was an error uploading the image.');
        }
    });
    } else{
        jQuery.alertable.alert("Please select a photo");
        return;
    }
}
function updateFeatured(element,dfn,val,elementid){
    var strURL = "storefront_image_upload.cgi";
    var flag = "updateFeatured";
    var overlay = \$('#' + elementid).closest('.overlay-edit');
    console.log(element + " " + dfn + " " + val);
    \$.ajax({
      type: "POST",
      url: strURL, 
      data: "element=" + element + "&flag=" + flag + "&value=" + encodeURIComponent(val) + "&dfn=" + dfn,
      error: function() {
          jQuery.alertable.alert("We had an API connection issue. Please try again.");
      },
      success: function (x){
            //overlay.addClass('d-none');
            //return;
            if (element == "PromoTitle"){
                document.getElementById("featuredTitle").innerHTML = x;
                overlay.addClass('d-none');
            } else if(element == "Status"){
                \$('#display' + dfn).hide();
                overlay.addClass('d-none');
            } else if (element == "DFN" && dfn != 1){
                window.location.reload();
            } else if (element == "newfeature"){
                window.location.reload();
            } else{
                overlay.addClass('d-none');
            }
          //document.location.reload();
          return;
        
      }
    });
}
</script>
</head>
<body style="background-color: #E8E8EB">
    <div class="overlay"><div class="spinner-border text-primary spinner" role="status"></div></div>
<div class="container-fluid">
<button type="button" class="btn btn-primary btn-sm float-left mt-1" onclick="location.href='rm_ow_menu.cgi'">Back</button>
<h4 class="text-center">Main storefront for dealers</h4>
</div>

<div id="carouselExampleIndicators" class="carousel slide" data-ride="carousel" style="height:80vh">
<div class="carousel-inner h-100">
];
foreach my $sh(sort {$a <=> $b} keys %slideHash){
    my $shvals = $slideHash{$sh};
    my ($title,$desc,$ltype,$dfn,$btxt,$img) = split(/\^/,$shvals);
    my ($pos,$slideid) = split(/\^/,$sh);
    if ($pos == 1){
        $active = "active";
    } else{
        $active = "";
    }
    print qq[
    <div class="carousel-item $active" style="background-image: url('$img');">
        <div class="carousel-caption d-block">
            <h2>$title</h2>
            <h5>$desc</h5>
            <button type="button" class="btn btn-orange">$btxt</button>
        </div>
    </div>
    ];
}
print qq[
<!-- <div class="carousel-item active" style="background-image: url('images/shop/HomePage_Header.png');">
    <div class="carousel-caption d-block">
        <h2>Demo Slide</h2>
        <h5>This is a description for the first slide.</h5>
        <button type="button" class="btn btn-orange">Action</button>
    </div>
</div>
<div class="carousel-item" style="background-image: url('1920x1080.png');">
    <div class="carousel-caption d-block">
        <h2>Second Slide</h2>
        <h5>This is a description for the second slide.</h5>
        <button type="button" class="btn btn-orange">Action</button>
    </div>
</div>
<div class="carousel-item" style="background-image: url('1920x1080.png');">
    <div class="carousel-caption d-block">
        <h2>Third Slide</h2>
        <h5>This is a description for the third slide.</h5>
        <button type="button" class="btn btn-orange">Action</button>
    </div>
</div>
<div class="carousel-item" style="background-image: url('1920x1080.png');">
    <div class="carousel-caption d-block">
        <h2>Fourth Slide</h2>
        <h5>This is a description for the fourth slide.</h5>
        <button type="button" class="btn btn-orange">Action</button>
    </div>
</div> -->
</div>
<a class="carousel-control-prev" href="#carouselExampleIndicators" role="button" data-slide="prev">
<span class="carousel-control-prev-icon" aria-hidden="true"></span>
<span class="sr-only">Previous</span>
</a>
<a class="carousel-control-next" href="#carouselExampleIndicators" role="button" data-slide="next">
<span class="carousel-control-next-icon" aria-hidden="true"></span>
<span class="sr-only">Next</span>
</a>
</div>

<!-- Cards Row -->
<div class="container mx-auto cards-row" style="max-width:1500px;">
    <div class="row mx-auto">
        <div class="col-md-3 d-md-flex align-items-stretch">
            <div class="card w-100 mx-auto cardx shadow position-relative">
                <img id="BrandSlice1" src="$brandSlice{1}" class="card-img" alt="Background Image">
                <div class="color-bar1 position-absolute"></div>
                <div class="card-img-overlay d-flex flex-column justify-content-center align-items-center">
                    <img src="images/logos/Aero_white_logo.png" alt="Logo" >
                    <!-- <h5 class="card-title">Title</h5> -->
                    <a href="#" class="btn btn-white mt-5">Shop Now</a>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                        
                            <div class="form-group">
                                <label for="newImage">Upload new image</label>
                                <input type="file" class="form-control" id="sliceImage1" name="newImage" autocomplete="off">
                            </div>
                            <button type="button" class="btn btn-primary mt-3" id="uploadButton1" onclick="uploadSlice('BrandSlice1','sliceImage1','1')">Upload</button>
                            <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                        
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3 d-md-flex align-items-stretch">
            <div class="card w-100 mx-auto cardx shadow position-relative">
                <img id="BrandSlice2" src="$brandSlice{2}" class="card-img" alt="Background Image">
                <div class="color-bar2 position-absolute"></div>
                <div class="card-img-overlay d-flex flex-column justify-content-center align-items-center">
                    <img src="images/logos/Stag_white_logo.png" alt="Logo" >
                    <!-- <h5 class="card-title">Title</h5> -->
                    <a href="#" class="btn btn-white mt-5">Shop Now</a>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                        
                            <div class="form-group">
                                <label for="newImage">Upload new image</label>
                                <input type="file" class="form-control" id="sliceImage2" name="newImage" autocomplete="off">
                            </div>
                            <button type="button" class="btn btn-primary mt-3" id="uploadButton1" onclick="uploadSlice('BrandSlice2','sliceImage2','2')">Upload</button>
                            <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                        
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3 d-md-flex align-items-stretch">
            <div class="card w-100 mx-auto cardx shadow position-relative">
                <img id="BrandSlice3" src="$brandSlice{3}" class="card-img" alt="Background Image">
                <div class="color-bar3 position-absolute"></div>
                <div class="card-img-overlay d-flex flex-column justify-content-center align-items-center">
                    <img src="images/logos/BA_white_logo.png" alt="Logo" >
                    <!-- <h5 class="card-title">Title</h5> -->
                    <a href="#" class="btn btn-white mt-5">Shop Now</a>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                        
                            <div class="form-group">
                                <label for="newImage">Upload new image</label>
                                <input type="file" class="form-control" id="sliceImage3" name="newImage" autocomplete="off">
                            </div>
                            <button type="button" class="btn btn-primary mt-3" id="uploadButton1" onclick="uploadSlice('BrandSlice3','sliceImage3','3')">Upload</button>
                            <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                        
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3 d-md-flex align-items-stretch">
            <div class="card w-100 mx-auto cardx shadow position-relative">
                <img id="BrandSlice4" src="$brandSlice{4}" class="card-img" alt="Background Image">
                <div class="color-bar4 position-absolute"></div>
                <div class="card-img-overlay d-flex flex-column justify-content-center align-items-center">
                    <img src="images/logos/VG6_white_logo.png" alt="Logo" >
                    <!-- <h5 class="card-title">Title</h5> -->
                    <a href="#" class="btn btn-white mt-5">Shop Now</a>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                        
                            <div class="form-group">
                                <label for="newImage">Upload new image</label>
                                <input type="file" class="form-control" id="sliceImage4" name="newImage" autocomplete="off">
                            </div>
                            <button type="button" class="btn btn-primary mt-3" id="uploadButton1" onclick="uploadSlice('BrandSlice4','sliceImage4','4')">Upload</button>
                            <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                        
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!--featured products 2-->
<div class="container mx-auto mt-2" style="max-width:1500px;">
<h4 class="pt-5 pb-5 mb-0 text-center text-secondary">FEATURED PRODUCTS</h4>
<div class="text-center"><a href="#newf" data-toggle="collapse" class="text-success font-weight-bold">+Add New Featured Product</a></div>
<div id="newf" class="collapse mb-3">
    <div class="form-group mx-auto w-50">
        <label class="label">Select Item</label>
        <select id="newfeatureditem" class="form-control form-control-sm" onchange="updateFeatured('newfeature','0',this.value,this.id)" autocomplete="off">
            <option value="0">-select-</option>
            ];
            foreach my $itemidx(sort {$a <=> $b} keys %itemName){
                my $iname = $itemName{$itemidx};
                my $isku  = $itemSku{$itemidx};
                print qq[<option value="$itemidx">$iname ($isku)</option>];
            }
            print qq[
        </select>
    </div>
</div>
    <div class="row no-gutters">
        <div class="col-3 d-none d-md-block">
            <div id="featuredPromo" class="featured-column" style="background-image: url('$featured{PromoImg}')">
                <h2 class="white" id="featuredTitle">$featured{"PromoTitle"}</h2>
                <a href="javascript:$featuredLink" class="btn btn-primary">Shop Now</a>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                        <div class="form-row">
                            <div class="col-12 small mb-1 text-danger">Link changes requires a refresh of the screen.</div>
                            <div class="col-12 mb-3">
                                <label class="label">Title</label>
                                <input id="PromoTitle1" type="text" class="form-control form-control-sm" onchange="updateFeatured('PromoTitle','1',this.value,this.id)" autocomplete="off" value="$featured{PromoTitle}">
                            </div>
                            <div class="col-12 mb-3">
                                <label class="label">Action Link <span class="small">where it takes you in the store</span></label>
                                <select id="1DFN" class="form-control form-control-sm" autocomplete="off" onchange="updateFeatured('DFN','1',this.value,this.id)">
                                    <option value="0^">change Category</option>
                                    ];
                                    foreach my $b(sort {$a <=> $b} keys %brandName){
                                        my $br = $brandName{$b};
                                        print qq[<option class="text-info" value="$b^Brand" $featuredDFNSelected{"1^Brand^$b"}>$br (Brand)</option>];
                                    }
                                    foreach my $ch(sort keys %catHash){
                                        my ($cat,$catid) = split(/\^/,$ch);
                                        print qq[<option class="text-dark" value="$catid^Cat" $featuredDFNSelected{"1^Cat^$catid"}>$cat (Category)</option>];
                                        foreach my $sh(sort keys %{ $subHash{$catid} }){
                                            my ($sub,$subid) = split(/\^/,$sh);
                                            print qq[<option class="text-danger" value="$subid^Sub" $featuredDFNSelected{"1^Sub^$subid"}>$sub (Subcategory)</option>];
                                        }
                                    }
                                    print qq[
                                </select>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="newImage">Upload new image</label>
                            <input type="file" class="form-control" id="featureImage1" name="newImage" autocomplete="off">
                        </div>
                        <button type="button" class="btn btn-primary mt-3" id="uploadButton1" onclick="uploadFeatured('featuredPromo','featureImage1','1')">Upload</button>
                        <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                        
                    </div>
                </div>
            </div>

        </div>
    <div class="col-12 col-md-9 pl-3">
    <div class="product-container">

    ];
foreach my $fi(sort {$a <=> $b} keys %featuredX){
    my $itemid = $featuredX{$fi};
    my $img    = $itemImage{$itemid};
    my $item   = $itemName{$itemid};
    my $redeem = $itemRedeem{$itemid};
    my $sku    = $itemSku{$itemid};
    print qq[
    <div id="display$fi" class="card product-cardx">
        <img src="$img" class="card-img-top" alt="Product 1">
        <div class="price-banner">$redeem</div>
        <div class="card-body">
            <p class="card-text"><b>$item</b><br>$sku</p>
            <p class="card-text font-weight-bold">$redeem pts</p>
            <button class="btn btn-primary" onclick="selectMe('Item','$itemid')">View Item</button>
        </div>
        <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;">
            <i class="fas fa-edit"></i>
        </button>
        <div class="overlay-edit position-absolute w-100 h-100 d-none">
            <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                <div class="form-row">
                    <div class="col-12">
                    <div class="form-group">
                        <label class="label">Change Item</label>
                        <select id="feaDFN$fi" class="form-control form-control-sm" onchange="updateFeatured('DFN','$fi',this.value,this.id)" autocomplete="off">
                            ];
                            foreach my $itemidx(sort {$a <=> $b} keys %itemName){
                                my $iname = $itemName{$itemidx};
                                my $isku  = $itemSku{$itemidx};
                                print qq[<option value="$itemidx^Item" $featuredDFNSelected{"$fi^Item^$itemidx"}>$iname ($isku)</option>];
                            }
                            print qq[
                        </select>
                    </div>
                    </div>
                    <div class="col-12">
                        <div class="form-group">
                            <label class="label d-block">Delete Featured Item</label>
                            <button id="delete$fi" type="button" class="btn btn-secondary" onclick="updateFeatured('Status','$fi','Inactive',this.id)">Delete</button>
                        </div>
                        </div>
                    <div class="col-12 text-center mt-3">
                        <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                    </div>
                </div>
                    
                
            </div>
        </div>
    </div>
    ];
}
    print qq[

</div><!--end product container-->
</div><!--end col-9-->
</div><!--end big row-->
</div><!--end featured-->

<!--category grid-->
<div class="container-fluid mt-2 p-0" style="background-color:#fff">
    <h4 class="pt-5 pb-5 mb-0 text-center text-secondary">SHOP CATEGORIES</h4>
<div class="container mt-4" style="background-color:#fff">
    <div class="form-row">
        <!-- row with 2 cards-->
        <div class="col-md-6 mb-2">
            <div class="card cardy shadow" $catGridLink{1}>
                <img id="catGrid1" src="$catGridImage{1}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{1}">
                    <img src="$catGridSquare{1}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{1}">$catGridBrand{1}</p>
                    <h5 class="text-bottom-left">$catGridCat{1}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA1" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','1',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB1" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','1',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage1" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton1" onclick="uploadCatGrid('catGrid1','catGridImage1','1')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-6 mb-2">
            <div class="card cardy shadow" $catGridLink{2}>
                <img id="catGrid2" src="$catGridImage{2}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{2}">
                        <img src="$catGridSquare{2}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{2}">$catGridBrand{2}</p>
                    <h5 class="text-bottom-left">$catGridCat{2}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA2" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','2',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB2" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','2',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage2" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton2" onclick="uploadCatGrid('catGrid2','catGridImage2','2')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="form-row">
        <!-- row with 1 card -->
        <div class="col-md-12 mb-2">
            <div class="card cardy shadow" $catGridLink{3}>
                <img id="catGrid3" src="$catGridImage{3}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{3}">
                        <img src="$catGridSquare{3}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{3}">$catGridBrand{3}</p>
                    <h5 class="text-bottom-left">$catGridCat{3}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA3" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','3',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB3" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','3',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage3" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton3" onclick="uploadCatGrid('catGrid3','catGridImage3','3')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="form-row">
        <!-- row with 3 cards -->
        <div class="col-md-4 mb-2">
            <div class="card cardy shadow" $catGridLink{4}>
                <img id="catGrid4" src="$catGridImage{4}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{4}">
                        <img src="$catGridSquare{4}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{4}">$catGridBrand{4}</p>
                    <h5 class="text-bottom-left">$catGridCat{4}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA4" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','4',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB4" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','4',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage4" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton4" onclick="uploadCatGrid('catGrid4','catGridImage4','4')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-2">
            <div class="card cardy shadow" $catGridLink{5}>
                <img id="catGrid5" src="$catGridImage{5}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{5}">
                        <img src="$catGridSquare{5}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{5}">$catGridBrand{5}</p>
                    <h5 class="text-bottom-left">$catGridCat{5}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA5" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','5',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB5" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','5',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage5" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton5" onclick="uploadCatGrid('catGrid5','catGridImage5','5')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-2">
            <div class="card cardy shadow" $catGridLink{6}>
                <img id="catGrid6" src="$catGridImage{6}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{6}">
                        <img src="$catGridSquare{6}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{6}">$catGridBrand{6}</p>
                    <h5 class="text-bottom-left">$catGridCat{6}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA6" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','6',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB6" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','6',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage6" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton16" onclick="uploadCatGrid('catGrid6','catGridImage6','6')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="form-row">
        <!-- Fourth row with 3 cards -->
         <div class="col-md-8 mb-2">
            <div class="form-row">
                <div class="col-md-6">
                    <div class="card cardy shadow mb-2" $catGridLink{7}>
                        <img id="catGrid7" src="$catGridImage{7}" class="card-img" alt="Image">
                        <div class="card-img-overlay2">
                            <div class="styled-square $catGridSquareClass{7}">
                                <img src="$catGridSquare{7}" class="" alt="Logo" >
                            </div>
                            <p class="text-bottom-left $catGridTxtClass{7}">$catGridBrand{7}</p>
                            <h5 class="text-bottom-left">$catGridCat{7}</h5>
                        </div>
                        <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                            <i class="fas fa-edit"></i>
                        </button>
                        <div class="overlay-edit position-absolute w-100 h-100 d-none">
                            <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                            <div class="form-row">
                                <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                                <div class="col-12 mb-3">
                                    <label class="label">Brand</label>
                                    <select id="CatGridA7" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','7',this.value,this.id)">
                                        <option value="0">change brand</option>
                                        ];
                                        foreach my $b(sort {$a <=> $b} keys %brandName){
                                            my $br = $brandName{$b};
                                            print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                        }
                                        print qq[
                                    </select>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                                    <select id="CatGridB7" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','7',this.value,this.id)">
                                        <option value="0^">change Category</option>
                                        ];
                                        foreach my $b(sort {$a <=> $b} keys %brandName){
                                            my $br = $brandName{$b};
                                            print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                        }
                                        foreach my $ch(sort keys %catHash){
                                            my ($cat,$catid) = split(/\^/,$ch);
                                            print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                            foreach my $sh(sort keys %{ $subHash{$catid} }){
                                                my ($sub,$subid) = split(/\^/,$sh);
                                                print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                            }
                                        }
                                        print qq[
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="newImage" class="label">Upload new image</label>
                                <input type="file" class="form-control form-control-sm" id="catGridImage7" name="newImage" autocomplete="off">
                            </div>
                            <button type="button" class="btn btn-primary mt-3" id="uploadButton17" onclick="uploadCatGrid('catGrid7','catGridImage7','7')">Upload</button>
                            <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                        
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card cardy shadow mb-2" $catGridLink{8}>
                        <img id="catGrid8" src="$catGridImage{8}" class="card-img" alt="Image">
                        <div class="card-img-overlay2">
                            <div class="styled-square $catGridSquareClass{8}">
                                <img src="$catGridSquare{8}" class="" alt="Logo" >
                            </div>
                            <p class="text-bottom-left $catGridTxtClass{8}">$catGridBrand{8}</p>
                            <h5 class="text-bottom-left">$catGridCat{8}</h5>
                        </div>
                        <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                            <i class="fas fa-edit"></i>
                        </button>
                        <div class="overlay-edit position-absolute w-100 h-100 d-none">
                            <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                            <div class="form-row">
                                <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                                <div class="col-12 mb-3">
                                    <label class="label">Brand</label>
                                    <select id="CatGridA8" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','8',this.value,this.id)">
                                        <option value="0">change brand</option>
                                        ];
                                        foreach my $b(sort {$a <=> $b} keys %brandName){
                                            my $br = $brandName{$b};
                                            print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                        }
                                        print qq[
                                    </select>
                                </div>
                                <div class="col-12 mb-3">
                                    <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                                    <select id="CatGridB8" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','8',this.value,this.id)">
                                        <option value="0^">change Category</option>
                                        ];
                                        foreach my $b(sort {$a <=> $b} keys %brandName){
                                            my $br = $brandName{$b};
                                            print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                        }
                                        foreach my $ch(sort keys %catHash){
                                            my ($cat,$catid) = split(/\^/,$ch);
                                            print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                            foreach my $sh(sort keys %{ $subHash{$catid} }){
                                                my ($sub,$subid) = split(/\^/,$sh);
                                                print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                            }
                                        }
                                        print qq[
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="newImage" class="label">Upload new image</label>
                                <input type="file" class="form-control form-control-sm" id="catGridImage8" name="newImage" autocomplete="off">
                            </div>
                            <button type="button" class="btn btn-primary mt-3" id="uploadButton18" onclick="uploadCatGrid('catGrid8','catGridImage8','8')">Upload</button>
                            <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                        
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card cardy shadow mb-2" $catGridLink{10}>
                <img id="catGrid10" src="$catGridImage{10}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{10}">
                        <img src="$catGridSquare{10}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{10}">$catGridBrand{10}</p>
                    <h5 class="text-bottom-left">$catGridCat{10}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA10" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','10',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB10" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','10',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage10" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton10" onclick="uploadCatGrid('catGrid10','catGridImage10','10')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
            
         </div>
         <div class="col-md-4 mb-2">
            <div class="card cardy shadow double-height" $catGridLink{9}>
                <img id="catGrid9" src="$catGridImage{9}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{9}">
                        <img src="$catGridSquare{9}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{9}">$catGridBrand{9}</p>
                    <h5 class="text-bottom-left">$catGridCat{9}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA9" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','9',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB9" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','9',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage9" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton19" onclick="uploadCatGrid('catGrid9','catGridImage9','9')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
        
        
    </div>
    <div class="form-row">
        <!-- Sixth row with 3 cards -->
        <div class="col-md-4 mb-2">
            <div class="card cardy shadow" $catGridLink{11}>
                <img id="catGrid11" src="$catGridImage{11}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{11}">
                        <img src="$catGridSquare{11}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{11}">$catGridBrand{11}</p>
                    <h5 class="text-bottom-left">$catGridCat{11}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA11" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','11',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB11" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','11',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage11" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton11" onclick="uploadCatGrid('catGrid11','catGridImage11','11')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-2">
            <div class="card cardy shadow" $catGridLink{12}>
                <img id="catGrid12" src="$catGridImage{12}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{12}">
                        <img src="$catGridSquare{12}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{12}">$catGridBrand{12}</p>
                    <h5 class="text-bottom-left">$catGridCat{12}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA12" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','12',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB12" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','12',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage12" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton12" onclick="uploadCatGrid('catGrid12','catGridImage12','12')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4 mb-2">
            <div class="card cardy shadow" $catGridLink{13}>
                <img id="catGrid13" src="$catGridImage{13}" class="card-img" alt="Image">
                <div class="card-img-overlay2">
                    <div class="styled-square $catGridSquareClass{13}">
                        <img src="$catGridSquare{13}" class="" alt="Logo" >
                    </div>
                    <p class="text-bottom-left $catGridTxtClass{13}">$catGridBrand{13}</p>
                    <h5 class="text-bottom-left">$catGridCat{13}</h5>
                </div>
                <button class="btn btn-edit position-absolute" style="top: 10px; right: 10px;z-index:9">
                    <i class="fas fa-edit"></i>
                </button>
                <div class="overlay-edit position-absolute w-100 h-100 d-none">
                    <div class="overlay-content d-flex flex-column justify-content-center align-items-center h-100">
                    <div class="form-row">
                        <div class="col-12 small mb-1 text-danger">Brand and Link changes requires a refresh of the screen.</div>
                        <div class="col-12 mb-3">
                            <label class="label">Brand</label>
                            <select id="CatGridA13" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('BrandID','13',this.value,this.id)">
                                <option value="0">change brand</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option value="$b" $brandSelectedGrid{"1^$b"}>$br</option>]
                                }
                                print qq[
                            </select>
                        </div>
                        <div class="col-12 mb-3">
                            <label class="label">Image Link <span class="small">where it takes you in the store</span></label>
                            <select id="CatGridB13" class="form-control form-control-sm" autocomplete="off" onchange="updateCatGrid('DFN','13',this.value,this.id)">
                                <option value="0^">change Category</option>
                                ];
                                foreach my $b(sort {$a <=> $b} keys %brandName){
                                    my $br = $brandName{$b};
                                    print qq[<option class="text-info" value="$b^Brand" $catSelectedGrid{"1^$b^Brand"}>$br (Brand)</option>];
                                }
                                foreach my $ch(sort keys %catHash){
                                    my ($cat,$catid) = split(/\^/,$ch);
                                    print qq[<option class="text-dark" value="$catid^Cat" $catSelectedGrid{"1^$catid^Cat"}>$cat (Category)</option>];
                                    foreach my $sh(sort keys %{ $subHash{$catid} }){
                                        my ($sub,$subid) = split(/\^/,$sh);
                                        print qq[<option class="text-danger" value="$subid^Sub" $catSelectedGrid{"1^$subid^Sub"}>$sub (Subcategory)</option>];
                                    }
                                }
                                print qq[
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newImage" class="label">Upload new image</label>
                        <input type="file" class="form-control form-control-sm" id="catGridImage13" name="newImage" autocomplete="off">
                    </div>
                    <button type="button" class="btn btn-primary mt-3" id="uploadButton13" onclick="uploadCatGrid('catGrid13','catGridImage13','13')">Upload</button>
                    <button type="button" class="btn btn-secondary mt-3 cancelButton">Cancel</button>
                
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</div>
<div class="text-center mt-3"><button type="button" class="btn btn-primary" onclick="location.href='rm_ow_menu.cgi'">Back</button></div>

<br><br><br><br><br><br>
</body>

</html>

];
exit;

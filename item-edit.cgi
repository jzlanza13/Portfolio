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
($loginType,$loginDfn,$loginShooter,$sec_code,$loginToken) = split(/\^/,$sid);

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
# $catfilter = $q->param("catfilter");
# $modelfilter = $q->param("modelfilter");
# $purposefilter = $q->param("purposefilter");
# if ($catfilter eq ""){$catfilter = "All"}
# if ($modelfilter eq ""){$modelfilter = "All"}
# if ($purposefilter eq ""){$purposefilter = "All"}
# 	$parentsearch = $q->param("parentsearch");

# 	if ($parentsearch > 0){
# 		$gotox = "#info".$parentsearch;
# 	} else{
# 		$gotox = "";
# 	}
# 	# print qq[$gotox];
# $catFilter{$catfilter} = "selected";
# $modelFilter{$modelfilter} = "selected";
# $purposeFilter{$purposefilter} = "selected";

$dbh = DBI->connect("DBI:mysql:rewardsaero_$localdb:localhost","$usr","$pw") ;

$catName{0} = "No Category";
$sql = "SELECT `ID`, `Category` from `Categories` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
	my $catid  = $row[0];
	my $cat    = $row[1];
	$catList{"$cat^$catid"} = 1;
	$catName{$catid} = $cat;
}
$sth->finish();

$subName{0} = "No Subcategory";
$sql = "SELECT `ID`, `Category_ID`, `Subcategory` from `Categories_Sub` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
	my $subid  = $row[0];
	my $catid  = $row[1];
	my $sub    = $row[2];
	$subList{"$catid^$sub^$subid"} = 1;
	$subName{$subid} = $sub;
}
$sth->finish();

$brandName{0} = "No Brand";
$sql = "SELECT `ID`, `Brand` FROM `Brand_Management` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
	my $brandid  = $row[0];
	my $brand    = $row[1];
	$brandList{"$brand^$brandid"} = 1;
	$brandName{$brandid} = $brand;
}
$sth->finish();

$parentName{0} = "";
$sql = "SELECT `Item`, `ID`, `from `rm1_items` WHERE `Type` = 'Parent'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
	my $parent   = $row[0];
	my $parentid = $row[1];
	$parentName{$parentid} = $parent;
}
$sth->finish();

$sql = "SELECT `ID`, `Item`, `Category_ID`, `Subcategory_ID`, `Type`, `ParentID`, `Brand`, `SKU`, `Image_Location_Small`, `Accrue`, `Redeem`, `Serialized` from `rm1_items` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while(@row = $sth->fetchrow_array()){
	my $itemID  = $row[0];
	my $item    = $row[1];
	my $catid   = $row[2];
	my $subid   = $row[3];
	my $iType   = $row[4];
	my $pid     = $row[5];
	my $brandid = $row[6];
	my $sku     = $row[7];
	my $img     = $row[8];
	my $accr    = $row[9];
	my $redeem  = $row[10];
	my $serial  = $row[11];
	if ($img eq ""){$img = "Image_not_available.png"}
	$serialSelected{"$itemID^$serial"} = "selected";
	$catSelected{"$itemID^$catid"} = "selected";
	$subSelected{"$itemID^$subid"} = "selected";
	$brandSelected{"$itemID^$brandid"} = "selected";
	if ($iType eq "Parent"){
		$sort = $item.$itemID;
	} else{
		$pitem = $parentName{$pid};
		$sort = $pitem.$pid;
	}
	$itemHash{$sort}{"$item^$itemID"} = "$itemID^$item^$sku^$img^$accr^$redeem^$pid^$iType^$brandid^$catid^$subid^$serial";
}
$sth->finish();

$dbh->disconnect;

print qq[
<!DOCTYPE html>
<html>
<head>
<title>$shop</title>

<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

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

<style type="text/css">
.label{
	font-weight: 650!important;
}

.points{
	border-top-style: hidden;
	border-right-style: hidden;
	border-left-style: hidden;
	border-bottom-style: groove;
	background-color: #eee;
	}
	
	.no-outline:focus {
	outline: none;
	}
	#scroll-to-top {
	position: fixed;
	bottom: 20px;
	right: 20px;
	display: none;
}

#scrollToTopButton {
	display: block;
	width: 40px;
	height: 40px;
	background-color: #333;
	color: #fff;
	text-align: center;
	line-height: 40px;
	border-radius: 50%;
	text-decoration: none;
}

#scrollToTopButton:hover {
	background-color: #555;
}
.pointer {
    cursor: pointer;
	position: relative;
}
.pointer:hover{
	font-weight: 625!important;
}
.pointer::after {
	content: 'click to edit'; /* Use the data-title attribute for the hover text */
	position: absolute;
	font-size: 12px;
	bottom: 100%; /* Position the tooltip above the element */
	left: 50%;
	transform: translateX(-50%);
	background-color: #333;
	color: #fff;
	padding: 5px;
	border-radius: 3px;
	white-space: nowrap;
	opacity: 0;
	visibility: hidden;
	transition: opacity 0.3s ease;
	pointer-events: none; /* Prevent tooltip from blocking interactions */
}

.pointer:hover::after {
	opacity: 1;
	visibility: visible;
}
.form-control-sm{
    border: 1px solid black;
    margin-top: 5px;
}
.label{
	color: #000000!important;
}
.card-header .form-control-sm{
	margin-top: 0px;
	margin-bottom: 5px;
}
</style>

<script>
	// turn off ENTER key
	jQuery(document).ready(function() {
	  jQuery(window).keydown(function(event){
	    if(event.keyCode == 13) {
	      event.preventDefault();
	      return false;
	    }
	  });
	});

function reloadPage(){
    location.reload(true);
}


window.history.forward();
function noBack() { window.history.forward(); }

function backme(){
    var frm = document.getElementById("back");
    frm.submit();
}



function positionCursor(id){
	var input = document.getElementById(id);
	//input.focus();
	input.setSelectionRange(0,1);
}


function updateItem(elementid,val){
	var rec = elementid.split("^");
	var element = rec[0];
	var dfn     = rec[1];
	\$.ajax({
		type: "POST",
		url: "item_edit_ajax.cgi", // URL of the Perl ajax program
		// send data to the Perl script
		data: 'itemid=' + encodeURIComponent(dfn) + '&value=' + encodeURIComponent(val) + '&element=' + encodeURIComponent(element),
		// script call was *not* successful
		error: function() {
				jQuery.alertable.alert("We had an API connection issue. Please try again.");
		},
		success: function (x){
			var res = x.split("^");
			var y = res[0];
			var v = res[1];
			if (document.getElementById(y)){
				document.getElementById(y).innerHTML = v;
			}
			if (element == "Category_ID"){
				var subclass = "subs" + dfn;
				var ele1 = document.getElementsByClassName(subclass);
				for (var i = 0; i < ele1.length; i++) {
					ele1[i].style.display = "none";
				}
				var catclass = "Cats" + val + dfn;
				var ele2 = document.getElementsByClassName(catclass);
				for (var j = 0; j < ele2.length; j++) {
					ele2[j].style.display = "block";
				}
			}
			return;
		}
	});
	
}
function updateSubCat(x){
	var subclass = "subsx"
	var ele1 = document.getElementsByClassName(subclass);
	for (var i = 0; i < ele1.length; i++) {
		ele1[i].style.display = "none";
	}
	var catclass = x;
	var ele2 = document.getElementsByClassName(catclass);
	for (var j = 0; j < ele2.length; j++) {
		ele2[j].style.display = "block";
	}
}
function typeS(x){
	if (x == "Parent"){
		document.getElementById("Caliber").readOnly = true;
		var newOption = document.createElement("option");
		newOption.value = "";
		newOption.text  = "New Model";
		document.getElementById("Model").add(newOption);
		document.getElementById("Model").value = "";
		document.getElementById("Model").disabled = true;
		document.getElementById("Item").readOnly = false;
		document.getElementById("sku2").style.display = "none";
		document.getElementById("Item2").style.display = "";
		document.getElementById("imgbin").style.display = "block";
		\$('#access').hide();
	}
	else{
		document.getElementById("Caliber").readOnly = false;
		document.getElementById("Model").disabled = false;
		document.getElementById("Item").readOnly = true;
		document.getElementById("sku2").style.display = "";
		document.getElementById("Item2").style.display = "none";
		document.getElementById("imgbin").style.display = "none";
		\$('#access').show();
		var select = document.getElementById("Model");
		var opts = select.options;
		for (var i = 0;i < opts.length;i++){
			if (opts[i].value == ""){
				select.remove(i);
				break;
			}
		}
	}
}

const lastplace = "$gotox";
\$(document).ready(function() {
	if (lastplace !== null || lastplace.length > 0){
    var element = \$(lastplace);
    if (element.length) {
		\$('#scroll-to-top').fadeIn();
        \$('html, body').animate({
            scrollTop: element.offset().top
        }, 1000); // Adjust the duration as needed
    }
	}

	\$(window).scroll(function() {
        if (\$(this).scrollTop() > 100) { // Adjust the value as needed
            \$('#scroll-to-top').fadeIn();
        } else {
            \$('#scroll-to-top').fadeOut();
        }
    });

    \$('#scrollToTopButton').click(function() {
        \$('html, body').animate({scrollTop : 0}, 800); // Adjust the duration as needed
        return false;
    });
});


function clearSearch(){
document.getElementById('myInput').focus()
document.getElementById('myInput').value = ""
myFunction();
}

function myFunction() {
	var input, filter, x, i, txtValue;
	input = document.getElementById("myInput");
	filter = input.value.toUpperCase();
	var x = document.getElementsByClassName("lookup");
	var i;
	for (i = 0; i < x.length; i++) {
	  var txt = x[i].innerHTML;
	  txtValue = txt.toUpperCase();
	  var n = txtValue.includes(filter);
	  //alert("txt is " + txt);
	  //alert("i is " + i + " text is " + txt + " txtValue is " + txtValue)
	  //if (txtValue.toUpperCase().indexOf(filter) > -1) {}
	  if (n == true){
	      x[i].style.display = "";
	  } else {
	     x[i].style.display = "none";
	  }
	}
}
function openNew(btnid,divid){
	var cur = document.getElementById(divid).style.display;
	document.getElementById(btnid).classList.toggle("btn-success");
	document.getElementById(btnid).classList.toggle("btn-warning");
	if (cur == "none"){
		document.getElementById(divid).style.display = "block";
		document.getElementById(btnid).innerHTML = "Hide New";
	}
	else{
		document.getElementById(divid).style.display = "none";
		document.getElementById(btnid).innerHTML = "+ Add Item";
	}
}
function addCat(val,newdiv){
	document.getElementById(newdiv).style.display = "none";
	document.getElementById("Category").value = val;

	if (val == "newone"){
		document.getElementById(newdiv).style.display = "block";
		document.getElementById("newcat").focus();
	}
}

\$(document).ready(function() {
            \$('.pointer').on('click', function() {
                var elementId = \$(this).attr('id');
                handlePointerClick(elementId);
            });
        });

        // Function to handle the ID of the clicked element
        function handlePointerClick(id) {
            var regex = /^([a-zA-Z_]+)(\\d+)\$/;
        	var match = id.match(regex);
			// console.log(match)
			console.log(id);
			if (match){
			var textPart = match[1];
            var numberPart = match[2];
			var inputID = textPart + '^' + numberPart;
			console.log(inputID); 
			var cur = document.getElementById(inputID).style.display;
			if (cur == "none"){
				document.getElementById(inputID).style.display = "block";
				document.getElementById(inputID).focus();
			} else{ document.getElementById(inputID).style.display = "none"}
			}
            // Add your function details here
        }

function createNewImage(itemid,elementid){
    var flag   = "itemimage";
    var formData = new FormData();
    var imageFile = \$('#' + elementid)[0].files[0];
    formData.append('image', imageFile);
    formData.append('itemid', itemid);
    formData.append('flag', flag)
    //console.log(formData);
    var imgsrc = "itemimg" + itemid;
    var strURL = "item_edit_ajax.cgi";

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
                var rec = x.split("^");
                var img = rec[1];
                document.getElementById(imgsrc).src = img;
            }
        });
}
</script>
</head>

<body oncontextmenu="return false;" onload="">
];
&nav_bar();
print qq[

<div class="card mx-auto mt-3 shadow" style="width:96%;">
<form id="back" action="rm_ow_menu.cgi" method="post">
</form>
    <div class="card-header text-center">
    
        <div class="form-row m-2 text-center">
            <div class="col-md-3">
                <button type="button" onclick="backme()" class="btn btn-white"><i class="fa fa-chevron-left"></i> BACK</button>
            </div>
            <div class="col-md-6">
            <h4>Edit Items</h4>
            </div>
            <div class="col-md-3">
                <button type="button" id="newbtn" class="btn btn-success" onclick="openNew(this.id,'newdiv')">+ Add Item</button>
            </div>
        </div>
		<div id="newdiv" class="mt-3 mb-3 text-left" style="display:none;">
		<form id="NewForm" method="post" action="new_item_update.cgi" enctype="multipart/form-data">
		
		<div class="form-row">
			
			<div class="col-md-3">
				<label class="label">Item</label>
				<input type="text" class="form-control form-control-sm" id="Item" name="Item" autocomplete="off" placeholder="Item Description">
			</div>
			<div class="col-md-3">
				<label class="label">SKU</label>
				<input type="text" placeholder="SKU" class="form-control form-control-sm" id="SKU" name="SKU" autocomplete="off">
			</div>
			<div class="col-md-3">
				<label class="label">Brand</label>
				<select class="form-control form-control-sm" id="Brand" name="Brand" autocomplete="off">
					<option value="0">No Brand</option>
					];
					foreach $b(sort keys %brandList){
						my ($brandx,$brandidx) = split(/\^/,$b);
						print qq[<option value="$brandidx">$brandx</option>];
					}
					print qq[
				</select>
			</div>
			<div class="col-md-3">
				<label class="label">Category</label>
				<select class="form-control form-control-sm" id="Category" name="Category" autocomplete="off" onchange="updateSubCat(this.value)">
					<option value="0">No Category</option>
					];
					foreach $c(sort keys %catList){
						my ($catx,$catidx) = split(/\^/,$c);
						print qq[<option value="$catidx">$catx</option>];
					}
					print qq[
				</select>
			</div>
		</div>
		<div class="form-row">
			<div class="col-md-3">
				<label class="label">Subcategory</label>
				<select class="form-control form-control-sm" id="Subcategory" name="Subcategory" autocomplete="off">
					<option value="0">No Subcategory</option>
					];
					foreach my $s(sort keys %subList){
						my ($cid,$sr,$sid) = split(/\^/,$s);
						print qq[<option value="$sid" class="$cid subsx" style="display:none">$sr</option>];
					}
					print qq[
				</select>
			</div>
			<div class="col-md-3">
				<label class="label">Earn Points</label>
				<input type="text" placeholder="Accrue" class="form-control form-control-sm" id="Accrue" name="Accrue" autocomplete="off">
			</div>
			<div class="col-md-3">
				<label class="label">Redeem Points</label>
				<input type="text" placeholder="Redeem value" class="form-control form-control-sm" name="Redeem" id="Redeem" autocomplete="off">
			</div>
			<div class="col-md-3">
				<label class="label">Image</label>
				<input type="file" class="form-control form-control-sm" name="file" id="file" accept="image/png, image/jpeg">
			</div>
			
		</div>
			


		<div class="text-center mt-2">
			<button type="submit" form="NewForm" class="btn btn-primary btn-sm">Submit New Item</button>
		</div>
		</form>
		</div>
    </div><!--end header-->

<div class="card-body">
<form id="filterform" method="post" action="item-edit.cgi">
<div class="form-row w-50 mx-auto d-none">
  <div class="col-md-4">
      <div class="form-group">
        <label class="label">Filter by Category</label>
        <select id="catfilter" name="catfilter" class="form-control" autocomplete="off" onchange="this.form.submit()">
        <option value="All" $catFilter{"All"}>All Categories</option>
      ];
foreach $c(sort keys %catList){
  $ccnt = $CatCnt{$c};
  if ($ccnt < 1){$ccnt = 0}
  print qq[<option value="$c" $catFilter{$c}>$c ($ccnt)</option>];
}
      print qq[
        </select>
      </div>
  </div>
  <div class="col-md-4">
    <div class="form-group">
          <label class="label">Filter by Model</label>
          <select id="modelfilter" name="modelfilter" class="form-control" autocomplete="off" onchange="this.form.submit()">
          <option value="All" $modelFilter{"All"}>All Models</option>
        ];
  foreach $p(sort keys %modelHash){
    my $pitem = $p;
    my $pid = $modelHash{$p};
    $pcnt = $parentCnt{$pid};
    if ($pcnt < 1){$pcnt = 0}
    print qq[<option value="$pid" $modelFilter{$pid}>$pitem ($pcnt)</option>];
  }
        print qq[
          </select>
      </div>
  </div>
  <div class="col-md-4">
    <div class="form-group">
          <label class="label">Filter by Access</label>
          <select id="purposefilter" name="purposefilter" class="form-control" autocomplete="off" onchange="this.form.submit()">
            <option value="All" $purposeFilter{"All"}>Both - Redeem & Claim</option>
            <option value="Redeem" $purposeFilter{"Redeem"}>Redeem Only</option>
            <option value="Claim" $purposeFilter{"Claim"}>Claim Only</option>
          </select>
    </div>
  </div>
</div>
</form>
<div class="w-50 mx-auto mt-4 text-center">

        <input class="form-control" type="text" placeholder="Search for an item..." id="myInput" onkeyup="myFunction()" onchange="myFunction()" autocomplete="off">
        <button type="button" class="btn btn-link text-danger" onclick="clearSearch()">clear search</button>
</div>

<div class="table-responsive-md">
<button type="button" onclick="location.href='$csvFile'" class="btn btn-link text-info">EXPORT .CSV</button>
<table class="table mx-auto table-hover table-striped table-bordered data sortable">
<thead>
<tr>
	<th>Image</th>
    <th style="width:30%;">Item</th>
	<th>SKU</th>
	<th>Brand</th>
	<th>Category</th>
    <th>Points</th>
	<th>Serialized?</th>
    <th>Status</th>
</tr>
</thead>
<tbody>
];
foreach my $i(sort keys %itemHash){
	foreach $it(sort keys %{ $itemHash{$i} }){
		my $itvals = $itemHash{$i}{$it};
		my ($itemID,$item,$sku,$img,$accr,$redeem,$pid,$iType,$brandid,$catid,$subid,$serial) = split(/\^/,$itvals);
		$sku2 = $sku;
		if ($sku2 eq ""){$sku2 = "edit"}
		if ($img eq "Image_not_available.png"){
			$sortablekey = 0;
		} else{
			$sortablekey = 1;
		}
		print qq[
			<tr class="lookup">
				<td sorttable_customkey="$sortablekey">
					<img id="itemimg$itemID" style="height: 150px;width: 150px;object-fit:contain" src="$img">
					<div class="input-group mb-1 mt-1">
                        <input type="file" style="margin-top:0px!important;" class="form-control form-control-sm" placeholder="new image" id="newimage$itemID" autocomplete="off" accept=".png, .jpeg, .jpg">
                        <div class="input-group-append">
                        <button class="btn btn-primary btn-sm" type="button" onclick="createNewImage('$itemID','newimage$itemID')">Submit</button>
                        </div>
                    </div>
				</td>
				<td sorttable_customkey="$i">
					<h5 id="Item$itemID" class="mb-1 pointer" onclick="">$item</h5>
					<input type="text" id="Item^$itemID" class="form-control form-control-sm" style="display:none" value='$item' onchange="updateItem(this.id,this.value)" autocomplete="off">
				</td>
				<td sorttable_customkey="$sku">
					<h7 id="SKU$itemID" class="mb-1 pointer">$sku2</h7>
					<input type="text" id="SKU^$itemID" class="form-control form-control-sm" style="display:none" value="$sku" onchange="updateItem(this.id,this.value)" autocomplete="off">
				</td>
				<td sorttable_customkey="$brandid">
					<h7 id="Brand$itemID" class="mb-1 d-block pointer">$brandName{$brandid}</h7>
					<select id="Brand^$itemID" class="form-control form-control-sm" style="display:none" onchange="updateItem(this.id,this.value)" autocomplete="off">
						<option value="0">No Brand</option>
						];
						foreach my $b(sort keys %brandList){
							my ($br,$bid) = split(/\^/,$b);
							print qq[<option value="$bid" $brandSelected{"$itemID^$bid"}>$br</option>];
						}
						print qq[
					</select>
				</td>
				<td sorttable_customkey="$catid">
					<h7 id="Category_ID$itemID" class="mb-1 pointer d-block">$catName{$catid}</h7>
					<select id="Category_ID^$itemID" class="form-control form-control-sm" style="display:none" onchange="updateItem(this.id,this.value)" autocomplete="off">
						<option value="0">No Category</option>
						];
						foreach my $c(sort keys %catList){
							my ($cr,$cid) = split(/\^/,$c);
							print qq[<option value="$cid" $catSelected{"$itemID^$cid"}>$cr</option>];
						}
						print qq[
					</select>
					<h7 id="Subcategory_ID$itemID" class="mb-1 pointer d-block">$subName{$subid}</h7>
					<select id="Subcategory_ID^$itemID" class="form-control form-control-sm" style="display:none" onchange="updateItem(this.id,this.value)" autocomplete="off">
						<option value="0">No Subcategory</option>
						];
						foreach my $s(sort keys %subList){
							my ($cid,$sr,$sid) = split(/\^/,$s);
							if ($cid != $catid){
								$style = "none";
							} else{
								$style = "block";
							}
							$catclass = "Cats".$cid.$itemID;
							$subclass = "subs".$itemID;
							print qq[<option value="$sid" class="$catclass $subclass" style="display:$style" $subSelected{"$itemID^$sid"}>$sr</option>];
						}
						print qq[
					</select>
				</td>
				<td sorttable_customkey="$accr">
					<h7 id="Accrue$itemID" class="mb-1 pointer d-block">Earn <span class="font-weight-bold text-success" id="accr$itemID">$accr</span> pts</h7>
					<input type="text" id="Accrue^$itemID" step="1" value="$accr" class="form-control form-control-sm" style="display:none" onchange="updateItem(this.id,this.value)" autocomplete="off">
					
					<h7 id="Redeem$itemID" class="mb-1 pointer d-block">Redeem for <b><span class="font-weight-bold text-danger" id="red$itemID">$redeem</span></b> pts</h7>
					<input type="text" id="Redeem^$itemID" step="1" value="$redeem" class="form-control form-control-sm" style="display:none" onchange="updateItem(this.id,this.value)" autocomplete="off">
					
				</td>
				<td sorttable_customkey="$serial">
					<h7 id="Serialized$itemID" class="mb-1 pointer d-block">$serial</h7>
					<select id="Serialized^$itemID" class="form-control form-control-sm" style="display:none" onchange="updateItem(this.id,this.value)" autocomplete="off">
						<option value="Yes" $serialSelected{"$itemID^Yes"}>Yes</option>
						<option value="No" $serialSelected{"$itemID^No"}>No</option>
					</select>
				</td>
				<td sorttable_customkey="Active">
					<h7 class="mb-1 pointer d-block" id="Status$itemID">Active</h7>
					<button id="Status^$itemID" type="button" class="btn btn-danger btn-sm" onclick="updateItem(this.id,'Inactive')" autocomplete="off">Delete Item</button>
				</td>


			</tr>
		
		
		];
	}
}
print qq[
</tbody>
</table>
</div>

</div><!--end card body-->
</div><!--end card-->
<div id="scroll-to-top">
	<a href="#" id="scrollToTopButton"><i class="fas fa-arrow-up" style="color:white!important;"></i></a>
</div>
</body>
</html>
];
####################################################################################################
sub CURRENCY {
	$x = shift ;
	$y = sprintf("%.2f", $x) ;
	return $y ;
}
exit;
################################################################################################
sub Test{
	foreach $element ( $q->param) {
		print "<br>$element:";
		foreach $value ($q->param( $element )){
			print " $value";
		}
	}

	print qq[<br><br>];

	@orderList = sort(keys(%orderHash));
	foreach $key (@orderList){
		$qty = $orderHash{$key};
		print qq[key: $key, qty: $qty<br>];
	}

	print qq[<br><br>];

	print qq[<input type="button" name="Button" value="Close" class="button" onclick="window.location.href='rm_store_categories.cgi?anchor=$company'">];

	return;;
}
exit;
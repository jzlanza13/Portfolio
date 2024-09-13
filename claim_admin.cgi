#!/usr/bin/perl

print "Content-type: text/html\n\n";
# print "<body bgcolor=#ffffff text=#000000>\n" ;

use CGI;
use DBI;
use CGI::Carp qw/fatalsToBrowser/;
use DateTime ;
use CGI::Cookie;
use CGI::Session;
use MIME::Base64;
use Time::Piece;

my $cgi = CGI->new;
my $session_id = $cgi->cookie('CGISESSID');

$session = CGI::Session->load(undef, $session_id, {Directory=>'sessions'});
my $sid = $session->param("sid");


require("rm_config.cgi") ;
require("rm_dt_now.cgi") ;
require("ab_nav_bar.cgi");

&Security();

if ($loginType ne "Admin"){
	MyAlert("Your session has ended.","login.cgi");
}



my $localdb = &DB();my $master = &MASTER();my $usr = &USR();my $pw = &PW();
my $shop    = &Shop() ;
my $tz      = &TZ() ;
@data = &TimeNow($tz) ;

my $sqlnow = $data[0] ;
my $ymd    = $data[1] ;#yyyy-mm-dd
($yyyy,$mm,$dd) = split(/-/,$ymd) ;
my $hms    = $data[2] ;#hr:mn:sc
my $month  = $data[3] ;#month abbr
my $day    = $data[4] ;#day abbr
my $mydate = "$day $month $dd,$yyyy" ;

my $format_from = '%Y-%m-%d %H:%M:%S';
my $format_to = '%m/%d/%Y %I:%M %p';

my $format_from2 = '%Y-%m-%d';
my $format_to2 = '%m/%d/%Y';

###filter stuff
$fstatus = $cgi->param("fstatus");
$fstart  = $cgi->param("fstart");
$fend    = $cgi->param("fend");
$fuser   = $cgi->param("fuser");

if ($fstatus eq ""){
    $fstatus = "All";
}
$filterStatus{$fstatus} = "selected";
if ($fstart eq ""){
    $fstart = "0000-00-00";
}
if ($fend eq ""){
    $fend = $ymd;
}
if ($fuser eq "" || $fuser < 1){
    $fuser = "All";
}
$filterUser{$fuser} = "selected";

$dbh = DBI->connect("DBI:mysql:rewardsaero_$localdb:localhost","$usr","$pw") ;

$allclaims = 0;
$filtercnt = 0;
$sql = "SELECT `ID`, `Unique_ID`, `DT_Started`, `DT_Submitted`, `DT_Approved`, `Images`, `Status`, `Denial_ID`, `Shooter_ID`, `Dealer_ID`, DATE(`DT_Submitted`) from `Claim` WHERE `Status` IN ('Submitted','Approved','Denied','Saved')";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $claimid = $row[0];
    my $unique  = $row[1];
    my $dtA     = $row[2];
    my $dtB     = $row[3];
    my $dtC     = $row[4];
    my $img     = $row[5];
    my $status  = $row[6];
    my $dID     = $row[7];
    my $shooter = $row[8];
    my $dealer  = $row[9];
    my $justdate = $row[10];
    if ($status eq "Saved" && $fstatus ne "Saved"){next}
    if ($status ne "Saved"){
        if ($justdate lt $fstart){next}
        if ($justdate gt $fend){next}
    }
    if ($fstatus ne "All" && $fstatus ne $status){next}
    if ($fuser ne "All" && $fuser != $shooter){next}
    $filtercnt++;
    if ($dtA ne "0000-00-00" && $dtA gt "2024-01-01" && $dtA ne ""){
        my $dta = Time::Piece->strptime($dtA, $format_from);
        $dtA2 = $dta->strftime($format_to);
    } else{
        $dtA2 = "N/A";
    }
    if ($dtB ne "0000-00-00" && $dtB gt "2024-01-01" && $dtB ne ""){
        my $dtb = Time::Piece->strptime($dtB, $format_from);
        $dtB2 = $dtb->strftime($format_to);
    } else{
        $dtB2 = "N/A";
    }
    if ($dtC ne "0000-00-00" && $dtC gt "2024-01-01" && $dtC ne ""){
        my $dtc = Time::Piece->strptime($dtC, $format_from);
        $dtC2 = $dtc->strftime($format_to);
    } else{
        $dtC2 = "N/A";
    }
    $deniedSelected{$claimid}{$dID} = "selected";
    $statusSelected{$claimid}{$status} = "selected";
    $receiptHash{$claimid} = $img;
    $grandTotal{$claimid} = 0;
    $grandQty{$claimid} = 0;

    $Hash{"$dtA^$claimid"} = "$claimid^$unique^$dtA2^$dtB2^$dtC2^$status^$dID^$shooter^$dealer";
}
$sth->finish();

$sql = "SELECT `ID`, `Item_ID`, `Qty`, `Unit_Points`, `Points`, `Status`, `Redemption_ID` from `Claim_Items` WHERE  1";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $itemrow = $row[0];
    my $itemid  = $row[1];
    my $iqty    = $row[2];
    my $iunit   = $row[3];
    my $itot    = $row[4];
    my $istat   = $row[5];
    my $claim   = $row[6];
    $iqty  = int($iqty);
    $iunit = int($iunit);
    $itot  = int($itot);
    $grandTotal{$claim} = $itot + $grandTotal{$claim};
    $grandQty{$claim}   = $iqty + $grandQty{$claim};
    $iHash{$claim}{$itemrow} = "$itemid^$iqty^$iunit^$itot^$istat";
}
$sth->finish();

$sql = "SELECT `ID`, `Item_ID`, `Serial_Number`, `Redeem_ID` from `rm1_serial_numbers` WHERE `Redeem_ID` = ?";
$sth = $dbh->prepare($sql);
$sth->execute($dfn);
while (@row = $sth->fetchrow_array()){
    my $serialid  = $row[0];
    my $iserial   = $row[1];
    my $serial    = $row[2];
    my $claim     = $row[3];
    $sHash{$claim}{$iserial}{$serialid} = $serial;
    $serial   =~ s/^\s+|\s+$//g;
    $serialx  = uc($serial);
    $serialCnt{$serialx} = 1 + $serialCnt{$serialx};
    $serialRedeem{$serialx}{$claim} = 1;
}
$sth->finish();

$denialHash{-1} = "Deny with no email";
$sql = "SELECT `ID`, `Content` from `Denial_Reasons` WHERE `Type` = 'Redemption' and `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    $did    = $row[0];
    $denial = $row[1];
    $denialHash{$did} = $denial;
}
$sth->finish();

$sql = "SELECT `ID`, `Category`, `Image` from `Categories` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
  my $catID = $row[0];
  my $cat   = $row[1];
  my $catimg = $row[2];
  $catName{$catID} = $cat;
}
$sth->finish();

$sql = "SELECT `ID`, `Category_ID`, `Subcategory`, `Image` from `Categories_Sub` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
  my $subid = $row[0];
  my $catid = $row[1];
  my $sub   = $row[2];
  $subName{$subid} = $sub;
}
$sth->finish();

$sql = "SELECT `ID`, `Brand` from `Brand_Management` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $brandID  = $row[0];
    my $brand    = $row[1];
    $brandName{$brandID} = $brand;
}
$sth->finish();

$sql = "SELECT `ID`, `Item`, `SKU`, `Brand`, `Accrue`, `Category_ID`, `Subcategory_ID`, `Image_Location_Small` from `rm1_items` WHERE 1";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $itemID  = $row[0];
    my $item    = $row[1];
    my $sku     = $row[2];
    my $brandID = $row[3];
    my $pts     = $row[4];
    my $catID   = $row[5];
    my $subID   = $row[6];
    my $iimg     = $row[7];
    my $brand = $brandName{$brandID};
    my $cat   = $catName{$catID};
    my $sub   = $subName{$subID};
    if ($pts eq ""){$pts = "TBD"}
    if ($iimg eq ""){$iimg = "Image_not_available.png"}
    $itemName{$itemID} = $item;
    $itemSku{$itemID} = $sku;
    $itemPts{$itemID} = $pts;
    $itemCat{$itemID} = $cat;
    $itemSub{$itemID} = $sub;
    $itemImg{$itemID} = $iimg;
    $itemBrand{$itemID} = $brand;
}
$sth->finish();


$sql = "SELECT `ID`, `First`, `Last`, `Email`, `Cell_Phone`, `FFL`, `FFL_Expiration` from `rm1_shooter_card` WHERE `Type` = 'Dealer'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $shooterID = $row[0];
    my $first     = $row[1];
    my $last      = $row[2];
    my $email     = $row[3];
    my $cell      = $row[4];
    my $ffl       = $row[5];
    my $ffl_exp   = $row[6];
    if ($ffl_exp ne "" && $ffl_exp gt "0000-00-00"){
        my $ftc = Time::Piece->strptime($ffl_exp, $format_from2);
        $fflexp = $ftc->strftime($format_to2);
    } else{
        $fflexp = "N/A";
    }
    $shooterName{$shooterID} = "$first $last";
    $shooterFFL{$shooterID} = "$ffl^$fflexp";
    $shooterContact{$shooterID} = "$email^$cell";
    $shooterList{"$first $last^$shooterID"} = 1;
}
$sth->finish();

$sql = "SELECT `ID`, `Shop_Name` from `rm1_members` WHERE 1";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $dealerID = $row[0];
    my $dealer   = $row[1];
    $dealerName{$dealerID} = $dealer;
}
$sth->finish();

$sql = "SELECT `ID`, `Customer_ID`, `Type`, `Address1`, `Address2`, `City`, `State`, `Zip`, `Country`, `Ship_To_Name` from `rm1_shipping` WHERE `Status` = 'Active'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    my $shipID     = $row[0];
    my $dealerID   = $row[1];
    my $sType      = $row[2];
    my $ad1        = $row[3];
    my $ad2        = $row[4];
    my $city       = $row[5];
    my $state      = $row[6];
    my $zip        = $row[7];
    my $ctry       = $row[8];
    $streets = "$ad1 $ad2";
    $streets =~ s/^\s+|\s+$//g;
    $addressHash{$dealerID}{$sType} = "$streets, $city, $state, $zip $ctry";
}
$sth->finish();

$dbh->disconnect;


# exit;

print qq[
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<title>Claimed Sales</title>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script><!--needed for boostrap-->
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.bundle.min.js" integrity="sha384-6khuMg9gaYr5AxOqhkVIODVIvm9ynTT5J4V1cfthmT+emCG6yVmEZsRHdxlotUnm" crossorigin="anonymous"></script><!--javascript + popper-->
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous"><!--stylesheet-->

<!-- Font awesome 5 -->
<link href="fonts/fontawesome/css/all.min.css" type="text/css" rel="stylesheet">

<!-- Alert Styling -->
<link rel="stylesheet" href="style/jquery.alertable.css">
<script src="script/jquery.alertable.min.js"></script>

<link rel="icon" type="image/png" href="favicon.png">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="shortcut icon" href="favicon.ico">

<link rel="stylesheet" href="style/style2.css">
<style>
.td-content5{
    cursor: pointer;
}
.btn.btn-link.text-success:hover{
    color: #fff!important;
}
.btn.btn-link.text-danger:hover{
    color: #fff!important;
}
.btn.btn-link.text-info:hover{
    color: #fff!important;
}
.details-popup {
    position: absolute;
    width: 575px; /* Set the desired width */
    background-color: white;
    //border: 1px solid #ddd;
    //box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    z-index: 1000;
  }

.popup-content {
padding: 10px;
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
function goBack(){
    var frm = document.getElementById("back");
    frm.submit();
}
function printMe(){
    \$('.hideme').hide();
    window.print();
    window.close();
    \$('.hideme').show();
}
function Review(x){
    document.getElementById("dfn2").value = x;
    var frm = document.getElementById("details");
    frm.submit();
}
function Approve(x,em){
    jQuery.alertable.confirm("This will send an approval email to <b>" + em + "</b><br><br>Are you sure?",{html:true}).then( function (){
        reallyApprove(x);
    }, function() {
        return;
    });
}
function reallyApprove(x){
    var strURL = "status_update.cgi";
    var flag   = "claim";
    var val    = "Approved";
    \$('#approve' + x).hide();
    \$.ajax({
        type: "POST",
        url: strURL,
        data: "dfn=" + encodeURIComponent(x) + "&flag=" + encodeURIComponent(flag) + "&value=" + encodeURIComponent(val),
        error: function() {
            \$('#approve' + x).show();
                jQuery.alertable.alert("We had an API connection issue. Please try again.");
        },
        success: function (msgback){
            var rec = msgback.split("^");
            var fl = rec[0];
            var mg = rec[1];
            if (fl == 99){
                \$('#approve' + x).show();
            } else{
                \$('#status' + x).html('<b>APPROVED</b>');
                \$('#status' + x).removeClass('bg-success bg-danger bg-warning bg-info').addClass('bg-success');
            }
            jQuery.alertable.alert(mg);
            return;
            
        }
	});
}
function Deny(x,em){
    var denial = document.getElementById("denyreason" + x).value;
    if (denial == -1){
        var msg = "This will deny the claim and will <b>NOT</b> send an email.<br><br>Are you sure?";
    } else{
        var msg = "This will send a denial email to <b>" + em + ".</b><br><br>Are you sure?"; 
    }
    jQuery.alertable.confirm(msg,{html:true}).then( function (){
        reallyDeny(x,denial);
    }, function() {
        return;
    });
}
function reallyDeny(x,d){
    var strURL = "status_update.cgi";
    var flag   = "claim";
    var val    = "Denied";
    // \$('#approve' + x).show();
    \$('#deny' + x).hide();
    \$.ajax({
        type: "POST",
        url: strURL,
        data: "dfn=" + encodeURIComponent(x) + "&flag=" + encodeURIComponent(flag) + "&value=" + encodeURIComponent(val) + "&denialID=" + encodeURIComponent(d) ,
        error: function() {
            \$('#deny' + x).show();
                jQuery.alertable.alert("We had an API connection issue. Please try again.");
        },
        success: function (msgback){
            var rec = msgback.split("^");
            var fl = rec[0];
            var mg = rec[1];
            \$('#denydiv' + x).removeClass('show');
            if (fl == 99){
                \$('#deny' + x).show();
            } else{
                \$('#status' + x).html('<b>DENIED</b>');
                \$('#status' + x).removeClass('bg-success bg-danger bg-warning bg-info').addClass('bg-danger');
            }
            jQuery.alertable.alert(mg);
            return;
            
        }
	});
}
</script>

</head>

<body>
];
&nav_bar();
print qq[
<div class="overlay"><div class="spinner-border text-primary spinner" role="status"></div></div>
<form id="details" method="post" action="details_admin.cgi">
    <input type="hidden" name="dfntype" value="Claim">
    <input type="hidden" name="dfn" id="dfn2" value="" autocomplete="off">
    <input type="hidden" name="back" value="claim_admin.cgi">
    <input type="hidden" name="fstatus" value="$fstatus" autocomplete="off">
    <input type="hidden" name="fstart" value="$fstart" autocomplete="off">
    <input type="hidden" name="fend" value="$fend" autocomplete="off">
    <input type="hidden" name="fuser" value="$fuser" autocomplete="off">
</form>

<div class="container-fluid mt-4">
    <div class="card shadow">
        <div class="card-header text-center">
            <h4>Claimed Sales</h4>
            <button type="button" class="hideme btn btn-white" onclick="location.href='rm_ow_menu.cgi'">BACK</button>
        </div><!--end header-->
        <div class="card-body">
            <div class="table-responsive mb-4">
                <form id="filter" method="post" action="claim_admin.cgi">
                <table class="table table-sm">
                <tr>
                    <th>Status</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>User</th>
                    <th>&nbsp;</th>
                </tr>
                <tr class="text-center">
                    <td>
                        <select id="fstatus" name="fstatus" class="form-control form-control-sm" autocomplete="off">
                        <option value="All" $filterStatus{"All"}>All</option>
                        <option value="Submitted" $filterStatus{"Submitted"}>Submitted</option>
                        <option value="Approved" $filterStatus{"Approved"}>Approved</option>
                        <option value="Denied" $filterStatus{"Denied"}>Denied</option>
                        <option value="Saved" $filterStatus{"Saved"}>Saved</option>
                        </select>
                    </td>
                    <td>
                    <input type="date" class="form-control form-control-sm" name="fstart" id="fstart" autocomplete="off" value="$fstart">
                    </td>
                    <td>
                    <input type="date" class="form-control form-control-sm" name="fend" id="fend" autocomplete="off" value="$fend">
                    </td>
                    <td>
                        <select id="fuser" name="fuser" class="form-control form-control-sm" autocomplete="off">
                        <option value="All" $filterUser{"All"}>All Users</option>
];
                    foreach my $s(sort keys %shooterList){
                        my ($sname,$sid) = split(/\^/,$s);
                        print qq[<option value="$sid" $filterUser{$sid}>$sname</option>];
                    }
print qq[
                        </select>
                    </td>
                    <td><button type="submit" class="btn btn-sm btn-primary" form="filter">Filter</button></td>
                </tr>
                </table>
                </form>
            </div>
            <div class="table-responsive">
            <table class="table table-bordered table-sm table-hover">
                <tr class="small">
                    <th>Claim #</th>
                    <th>Status</th>
                    <th>Submit Date</th>
                    <th>Customer</th>
                    <th>FFL</th>
                    <th>Receipts</th>
                    <th>Items</th>
                    <th>Actions</th>
                </tr>
            
            ];
foreach my $claim(sort keys %Hash){
    my $cvals = $Hash{$claim};
    my ($claimID,$unique,$startDate,$submitDate,$actionDate,$status,$denialID,$shooterID,$dealerID) = split(/\^/,$cvals);
    my $totalPts      = $grandTotal{$claimID};
    my $totalQty      = $grandQty{$claimID};
    my $shooter       = $shooterName{$shooterID};
    my $fflinfo       = $shooterFFL{$shooterID};
    my ($ffl,$exp)    = split(/\^/,$fflinfo);
    my $dealer        = $dealerName{$dealerID};
    my $receipts      = $receiptHash{$claimID};
    my $contact       = $shooterContact{$shooterID};
    my ($email,$cell) = split(/\^/,$contact);
    @r = split(/\;/,$receipts);
    %stat = ();
    $stat{$status} = "selected";
    $approved = "d-none";
    $denied   = "d-none";
    $canapprove = "d-none";
    $candeny    = "d-none";
    if ($status eq "Approved"){
        $bg = "bg-success text-light";
        $approved = "";
        $candeny    = "";
    }
    if ($status eq "Denied"){
        $bg = "bg-danger text-light";
        $denied = "";
        $canapprove = "";
    }
    if ($status eq "Submitted"){
        $bg = "bg-warning text-light";
        $canapprove = "";
        $candeny    = "";
    }
    if ($status eq "Saved"){
        $bg = "bg-info text-light";
    }
    $status2 = uc($status);
    print qq[
        <tr class="small">
            <td><b>\#$unique</b><br><a class="btn btn-sm btn-link text-info" href="javascript:Review('$claimID')">Expanded View</a></td>
            <td id="status$claimID" class="$bg align-middle text-center"><b>$status2</b></td>
            <td>$submitDate</td>
            <td><b>$shooter</b> ($dealer)<br>
            <span class=""><a href="mailto:$email" class="mr-4">$email</a> <a href="tel:$cell">$cell</a></span><br>
            $addressHash{$dealerID}{"Non_FFL"}
            </td>
            <td>
                <a href="$ffl" target="_blank">View FFL</a><br>
                expires <b>$exp</b><br>
                $addressHash{$dealerID}{"FFL"}
            </td>
            <td>
                ];
                $rcnt = 0;
                foreach my $r2(@r){
                    if ($r2 eq ""){next}
                    $rcnt++;
                    print qq[<a class="d-block" href="$r2" target="_blank">view receipt $rcnt</a>];
                }
                print qq[
            </td>
            <td style="position: relative;" class="clickable-td">
                <span class="td-content5">
                    $totalQty items<br>$totalPts points <i class="fas fa-chevron-down small"></i>
                  </span>
                  <span class="td-content d-none">
                    ];
                    foreach my $i(sort {$a <=> $b} keys %{ $iHash{$claimID} }){
                        my $ival = $iHash{$claimID}{$i};
                        my ($iid,$qty,$unit,$tot,$stat) = split(/\^/,$ival);
                        my $it = $itemName{$iid};
                        my $sk = $itemSku{$iid};
                        print qq[
                        <hr>
                            <div class="form-row">
                                <div class="col-12 small"><b>$it</b></div>
                                <div class="col-12 small">$qty qty | $tot pts</div>
                                <!-- <div class="col-1 small">$tot pts</div> -->
                            </div>
                            
                        ];
                    }

                    print qq[
                  </span>
                  <!-- <div class="details-popup" style="display: none;">
                    <div class="popup-content p-2">
                      Detailed information about $totalQty1 items and $totalPts1 points.
                    </div>
                  </div> -->
                <!-- $totalQty items<br>$totalPts points 
                <span id="td-content$claimID" onclick="openItems(this.id,'$claimID','clickable-td$claimID','details-popup$claimID')">
                    <i class="fas fa-chevron-down"></i>
                </span>
                <div id="details-popup$claimID" class="details-popup" style="display: none;">
                    <div class="popup-content p-2">
                      Detailed information about $totalQty items and $totalPts points.
                    </div>
                </div> -->
            </td>
            <td>
                <div class="mb-1 text-success $approved">Approved on $actionDate</div>
                <div class="mb-1 text-danger $denied">Denied on $actionDate<br><i>$denialHash{$denialID}</i></div>
                <a id="approve$claimID" class="btn btn-sm btn-link text-success $canapprove" href="javascript:Approve('$claimID','$email')">Approve</a>
                <a id="deny$claimID" class="btn btn-sm btn-link text-danger $candeny" href="#denydiv$claimID" data-toggle="collapse">Deny</a>
                <div class="mt-1 collapse" id="denydiv$claimID">
                    <label class="label">Select Reason</label>
                    <select id="denyreason$claimID" class="form-control form-control-sm" autocomplete="off">
                        ];
                            foreach my $dh(sort keys %denialHash){
                                my $d = $denialHash{$dh};
                                print qq[<option value="$dh">$d</option>];
                            }
                        print qq[
                    </select>
                    <button class="btn btn-sm btn-danger mt-1" type="button" onclick="Deny('$claimID','$email')">Submit Denial</button>
                </div>
            </td>
        </tr>
        
    ];

}
print qq[
        </table>
        </div><!--end orders-->
        </div><!--end card body-->
    </div><!--end card-->
</div><!--end container-fluid-->

<div id="details-popup" class="details-popup border border-secondary shadow" style="display: none;">
    <div class="popup-content p-2">
      Detailed information will appear here.
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var tds = document.querySelectorAll('.clickable-td');
    var popup = document.getElementById('details-popup');

    tds.forEach(function(td) {
      td.addEventListener('click', function(event) {
        // Hide any other open popups
        popup.style.display = 'none';
        
        // Set the content of the popup dynamically (this example assumes static text)
        popup.querySelector('.popup-content').innerHTML = 'Items <br>' + td.querySelector('.td-content').innerHTML;

        // Get the position of the clicked <td>
        var rect = td.getBoundingClientRect();

        // Position the popup to the left of the <td>
var margin = 450; // Adjust this value for spacing between the popup and <td>
popup.style.top = rect.top + window.scrollY + 'px'; // Align with the top of the <td>
popup.style.left = (rect.left + window.scrollX - popup.offsetWidth - rect.width - margin) + 'px'; // Fully clear the <td> and position to the left
    console.log(window.scrollX);
    console.log(rect.left);
    



        
        // Show the popup
        popup.style.display = 'block';

        // Stop event propagation to prevent the document click listener from immediately closing the popup
        event.stopPropagation();
      });
    });

    // Hide the popup when clicking outside of any <td>
    document.addEventListener('click', function() {
      popup.style.display = 'none';
    });

    // Prevent the popup from closing when clicking inside it
    popup.addEventListener('click', function(event) {
      event.stopPropagation();
    });
  });
</script>

</body>
</html>
];
exit;

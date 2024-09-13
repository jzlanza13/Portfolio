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

require("rm_config.cgi") ;
require("rm_dt_now.cgi") ;
require("ab_nav_bar.cgi");

&Security();

$sid = "";
$sid = $session->param("sid");


if ($loginType ne "Admin"){
	MyAlert("Your session has ended.","login.cgi");
}

$localdb = &DB();$master = &MASTER();my $usr = &USR();my $pw = &PW();
$shop    = &Shop() ;
$tz      = &TZ() ;



($date,$time) = split(/ /,$sqlnow);
($hh,$mm,$ss) = split(/:/,$time);
if ($ymd eq "2020-08-21"){
	if ($hh.":".$mm ge "05:20" and $hh.":".$mm le "05:49"){
		print qq[Content-type: text/html\n\n];
		$msg = qq[System down briefly for maintenance...<br><br>Back online at 08:50am EDT (05:50am PDT)];
		$pgm = "rm_support.cgi";
		&Alert($msg,$pgm);
		exit;
	}
}

@data = &TimeNow($tz) ;

my $sqlnow = $data[0] ;
my $ymd    = $data[1] ;#yyyy-mm-dd
($yyyy,$mm,$dd) = split(/-/,$ymd) ;
my $hms    = $data[2] ;#hr:mn:sc
my $month  = $data[3] ;#month abbr
my $day    = $data[4] ;#day abbr
my $mydate = "$day $month $dd,$yyyy" ;


my $today = localtime;
my $seven_days_ago = $today - 7*24*3600;   # 7 days * 24 hours * 3600 seconds
my $fourteen_days_ago = $today - 14*24*3600;
my $thirty_days_ago = $today - 30*24*3600;
my $ymd_seven    = $seven_days_ago->strftime('%Y-%m-%d');
my $ymd_fourteen = $fourteen_days_ago->strftime('%Y-%m-%d');
my $ymd_thirty   = $thirty_days_ago->strftime('%Y-%m-%d');

my $q = new CGI;
$dealer_time = $q->param("dealer_time");
$redeem_time = $q->param("redeem_time");
$claim_time  = $q->param("claim_time");
$pts_time    = $q->param("pts_time");

if ($dealer_time eq ""){
	$dealer_time = $ymd_seven;
}
if ($redeem_time eq ""){
	$redeem_time = $ymd_seven;
}
if ($pts_time eq ""){
	$pts_time = $ymd_seven;
}
if ($claim_time eq ""){
	$claim_time = $ymd_seven;
}

$dSelected{$dealer_time} = "red";
$cSelected{$claim_time}  = "red";
$rSelected{$redeem_time} = "red";
$pSelected{$pts_time}    = "red";

#print qq[$dealer_time and $redeem_time and $pts_time<br>];
$dbh = DBI->connect("DBI:mysql:rewardsaero_$localdb:localhost","$usr","$pw");

%claims = ();
$claims{"All"}  = 0;
$claims{"Approved"} = 0;
$claims{"Submitted"} = 0;
$claims{"Denied"} = 0;
$claims{"Saved"} = 0;

my $sql = "SELECT `Status`, Count(*) from `Claim` WHERE Date(`DT_Started`) >= ? and `Status` IN('Saved','Approved','Submitted','Denied') group by `Status`";
my $sth = $dbh->prepare($sql);
$sth->execute($claim_time);
while (my @row = $sth->fetchrow_array()){
    my $s = $row[0];
    my $c = $row[1];
    $claims{$s} = $c;
    $claims{"All"} = $c + $claims{"All"};
}
$sth->finish();

%redeem = ();
$redeem{"All"}  = 0;
$redeem{"Approved"} = 0;
$redeem{"Submitted"} = 0;
$redeem{"Denied"} = 0;
$redeem{"Saved"} = 0;

my $sql = "SELECT `Status`, Count(*) from `Redeem` WHERE Date(`DT_Started`) >= ? and `Status` IN('Saved','Approved','Submitted','Denied') group by `Status`";
my $sth = $dbh->prepare($sql);
$sth->execute($redeem_time);
while (my @row = $sth->fetchrow_array()){
    my $s = $row[0];
    my $c = $row[1];
    $redeem{$s} = $c;
    $redeem{"All"} = $c + $redeem{"All"};
}
$sth->finish();

$redeem2{"All"} = $redeem{"All"};
if ($redeem{"All"} == 0){
    $rtotal = 5;
    $redeem{"All"} = 1;
} else{
    $rtotal = 100;
}

$claims2{"All"} = $claims{"All"};
if ($claims{"All"} == 0){
    $ctotal = 5;
    $claims{"All"} = 1
} else{
    $ctotal = 100;
}

$dealer{"Approved"} = 0;
$dealer{"Pending"}  = 0;
$dealer{"Denied"}   = 0;
$dealer{"All"}      = 0;
$dealer{"login"}    = 0;
my $sql = "SELECT `Approval_Status`, Count(*) from `rm1_members` WHERE `Approval_Status_Updated` >= ?";
my $sth = $dbh->prepare($sql);
$sth->execute($dealer_time);
while (my @row = $sth->fetchrow_array()){
    my $a = $row[0];
    my $c = $row[1];
    $dealer{$a} = $c;
    $dealer{"All"} = $c + $dealer{"All"};
}
$sth->finish();

$dealer2{"All"} = $dealer{"All"};
if ($dealer{"All"} == 0){
    $dtotal = 5;
    $dealer{"All"} = 1;
} else{
    $dtotal = 100;
}

my $sql = "SELECT Count(*) from `rm1_shooter_card` WHERE Date(`Last_Login`) >= ? and `Type` = 'Dealer'";
my $sth = $dbh->prepare($sql);
$sth->execute($dealer_time);
$llcnt = $sth->fetchrow_array();
$sth->finish();

my $sql = "SELECT Count(*) from `rm1_shooter_card` WHERE `Type` = 'Dealer' and `Status` = 'Active'";
my $sth = $dbh->prepare($sql);
$sth->execute();
$dealercnt = $sth->fetchrow_array();
$sth->finish();

if ($dealercnt > 0){
    $llpercent = ($llcnt/$dealercnt) * 100;
    $llpercent = sprintf("%.1f", $llpercent);
} else{
    $llpercent = "0";
}
$llpercent2 = $llpercent;
if ($llpercent2 < 15){$llpercent2 = 15}


my $sql = "SELECT SUM(`Points`), `Redemption_ID` from `Claim_Items` WHERE 1 Group By `Redemption_ID`";
my $sth = $dbh->prepare($sql);
$sth->execute();
while (my @row = $sth->fetchrow_array()){
    my $pts = $row[0];
    my $c   = $row[1];
    $pts = int($pts);
    $claimPts{$c} = $pts;
}
$sth->finish();

my $sql = "SELECT SUM(`Points`), `Redemption_ID` from `Redeem_Items` WHERE 1 Group By `Redemption_ID`";
my $sth = $dbh->prepare($sql);
$sth->execute();
while (my @row = $sth->fetchrow_array()){
    my $pts = $row[0];
    my $r   = $row[1];
    $pts = int($pts);
    $redeemPts{$r} = $pts;
}
$sth->finish();

$pts_claim_approved = 0;
$pts_claim_denied   = 0;

$pts_redeem_approved = 0;
$pts_redeem_denied   = 0;

my $sql = "SELECT `ID`, `Status` from `Claim` WHERE `Status` IN ('Approved','Denied') and Date(`DT_Approved`) >= ?";
my $sth = $dbh->prepare($sql);
$sth->execute($pts_time);
while (my @row = $sth->fetchrow_array()){
    my $cid = $row[0];
    my $cst = $row[1];
    my $pts = $claimPts{$cid};
    if ($cst eq "Approved"){
        $pts_claim_approved = $pts + $pts_claim_approved;
    } else{
        $pts_claim_denied = $pts + $pts_claim_denied;
    }
}
$sth->finish();

my $sql = "SELECT SUM(`Points`) from `Claim_Items` WHERE `Redemption_ID` = '-1' and `Status` = 'Approved' and Date(`FreeDT`) >= ?";
my $sth = $dbh->prepare($sql);
$sth->execute($pts_time);
$free_pts = $sth->fetchrow_array();
$sth->finish();

$pts_claim_approved = $pts_claim_approved + $free_pts;

$pts_claim_approved = int($pts_claim_approved);

my $sql = "SELECT `ID`, `Status` from `Redeem` WHERE `Status` IN ('Approved','Denied') and Date(`DT_Approved`) >= ?";
my $sth = $dbh->prepare($sql);
$sth->execute($pts_time);
while (my @row = $sth->fetchrow_array()){
    my $cid = $row[0];
    my $cst = $row[1];
    my $pts = $redeemPts{$cid};
    if ($cst eq "Approved"){
        $pts_redeem_approved = $pts + $pts_redeem_approved;
    } else{
        $pts_redeem_denied = $pts + $pts_redeem_denied;
    }
}
$sth->finish();



$pts_redeem_approved = int($pts_redeem_approved);

my $sql = "SELECT SUM(`Points`) from `Claim_Items` WHERE `Status` = 'Approved'";
my $sth = $dbh->prepare($sql);
$sth->execute();
$pts_earned = $sth->fetchrow_array();
$sth->finish();

if ($pts_earned eq ""){$pts_earned = 0}

$pts_earned = int($pts_earned);

my $sql = "SELECT SUM(`Points`) from `Redeem_Items` WHERE `Status` = 'Approved'";
my $sth = $dbh->prepare($sql);
$sth->execute();
$pts_used = $sth->fetchrow_array();
$sth->finish();

if ($pts_used eq ""){$pts_used = 0}

$pts_used = int($pts_used);

$pts_balance = $pts_earned - $pts_used;

$period_balance = $pts_claim_approved - $pts_redeem_approved;



if ($pts_earned > 0){
$claim_percent = ($pts_claim_approved / $pts_earned) * 100;
$claim_percent = sprintf("%.1f", $claim_percent); 
$claim_all_time = 100;
} else{
    $claim_percent = 0;
    $claim_all_time = 15;
}

if ($claim_percent < 15){$claim_percent = 15}

if ($pts_used > 0){
$redeem_percent = ($pts_redeem_approved / $pts_used) * 100;
$redeem_percent = sprintf("%.1f", $redeem_percent); 
$redeem_all_time = 100;
} else{
    $redeem_percent = 0;
    $redeem_all_time = 15;
}

if ($redeem_percent < 15){$redeem_percent = 15}

$dbh->disconnect;

print qq[
<!DOCTYPE html>
<html>
<head>
<title>$shop</title>

   <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">


   <!--
   <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
   <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
   <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.bundle.min.js" integrity="sha384-6khuMg9gaYr5AxOqhkVIODVIvm9ynTT5J4V1cfthmT+emCG6yVmEZsRHdxlotUnm" crossorigin="anonymous"></script>
   <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">-->

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

<SCRIPT type="text/javascript">
    window.history.forward();
    function noBack() { window.history.forward(); }

function delayer(){
  //location.reload(true);
 	//window.location = "rm_mgr_sub_profile.cgi"
}

function loadwindow() {
	//document.myform.password.focus();
	}

function popup11(url){
  var win = window.open(url, '_blank');
	if(win){
    	//Browser has allowed it to be opened
      sessionStorage.setItem("from", "shop");
    	win.focus();
	}
	else{
    	//Broswer has blocked it
    	alert('Please allow popups for this site');
	}
}

    function popup(url)
    {
     var width  = 800;
     var height = 700;
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
     newwin=window.open(url,'newwin777', params);
     if (window.focus) {newwin.focus()}
    }


  function popup99(url)
  {
    var width  = 1200;
   var height = 800;
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
   newwin=window.open(url,'newwin778', params);
   if (window.focus) {newwin.focus()}
}
function adjustTime(id,val){
	document.getElementById(id).value = val;
	var frm = document.getElementById("filterform");
	frm.submit();
}
</SCRIPT>
<style>
.red{
	color: #148831 !important
}
a.list-group-item:hover {
  font-weight: 900;
	color: #8a0f34!important;
}
a.list-group-item{
	font-size: 1.1rem;
}
/* Custom styles for the sidebar */
.sidebar {
	height: 100vh;
	position: fixed;
	top: 70px;
	left: 0;
	padding-top: 15px; /* Adjust if you have a fixed navbar */
	background-color: inherit;
	border-right: 1px solid #dee2e6;
}

/* Styles for the content area */
.content {
	margin-left: 250px; /* Width of the sidebar */
	padding: 20px;
}
\@media (max-width:768px){
   .content{
	margin-left: 0px;
   }
}
.badge-pill{
	padding-right:inherit;
	padding-left:inherit;
}
.bar {
        background-color: #989999;
        height: 20px;
        margin-bottom: 5px;
    }

</style>

</head>

<body oncontextmenu="return false;" onload="noBack();" onpageshow="if (event.persisted) noBack();" >
];
&nav_bar();
print qq[
<div class="sidebar d-none d-md-block px-4 shadow">
    <h6 class="mb-0"><i class="fas fa-user"></i> Dealers</h6>
	<ul class="nav flex-column">
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm0">$msg0 <span class="badge badge-warning badge-pill p-1">$customer_pending</span></a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm1">$msg1 <span class="badge badge-success badge-pill p-1">$customer_approved</span></a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm2">$msg2</a>
        </li>
    </ul>
	<hr class="">
	<h6 class="mb-0"><i class="fas fa-exchange-alt"></i>
		Redemption</h6>
	<ul class="nav flex-column">
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm3">$msg3 <span class="badge badge-warning badge-pill p-1">$inreview</span></a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm3b">$msg3b <span class="badge badge-warning badge-pill p-1">$inreviewb</span></a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm4">$msg4</a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm5">$msg5</a>
        </li>
    </ul>
	<hr class="">
	<h6 class="mb-0"><i class="fas fa-box"></i> Inventory</h6>
	<ul class="nav flex-column">
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm7">$msg7</a>
        </li>
        <li class="nav-item d-none">
            <a class="nav-link p-0" href="$pgm9">$msg9</a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm11">$msg11</a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm13">$msg13</a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm14">$msg14</a>
        </li>
        
    </ul>
    <hr class="">
	<h6 class="mb-0"><i class="fas fa-store"></i> Store</h6>
	<ul class="nav flex-column">
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm16">$msg16</a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm12">$msg12</a>
        </li>
    </ul>
    <hr class="">
	<h6 class="mb-0"><i class="fas fa-envelope"></i> Communication</h6>
	<ul class="nav flex-column">
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm10">$msg10</a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm8">$msg8</a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0" href="$pgm15">$msg15</a>
        </li>
    </ul>
	<hr class="">
	<h6 class="mb-0"><i class="fas fa-user-tie"></i> Your Account</h6>
	<ul class="nav flex-column">
        <li class="nav-item">
            <a class="nav-link p-0" href="account_management.cgi">Account Management</a>
        </li>
        <li class="nav-item">
            <a class="nav-link p-0 text-danger" href="rm_support.cgi">Log Out</a>
        </li>
    </ul>
</div>

<div class="content">
<div class="container-fluid mb-2 mt-2">
<h4><u>Recent Activity</u></h4>
</div>

<form id="filterform" method="post" action="rm_ow_menu.cgi">
	<input type="hidden" name="dealer_time" id="dealer_time" value="$dealer_time" autocomplete="off">
	<input type="hidden" name="redeem_time" id="redeem_time" value="$redeem_time" autocomplete="off">
	<input type="hidden" name="pts_time" id="pts_time" value="$pts_time" autocomplete="off">
    <input type="hidden" name="claim_time" id="claim_time" value="$claim_time" autocomplete="off">
</form>

<div class="container-fluid mb-3">
    <h5 class="mb-0 text-warning font-weight-bold">Dealers</h5>
	<a href="javascript:adjustTime('dealer_time','$ymd_seven')" class="d-inline small $dSelected{$ymd_seven}">last week</a>&nbsp;&nbsp;
	<a href="javascript:adjustTime('dealer_time','$ymd_fourteen')" class="d-inline small $dSelected{$ymd_fourteen}">last 2 weeks</a>&nbsp;&nbsp;
	<a href="javascript:adjustTime('dealer_time','$ymd_thirty')" class="d-inline small $dSelected{$ymd_thirty}">last month</a><br>
	<div class="border border-secondary p-1 w-75">
        <div class="row">
            <div class="col-sm-3">Account Created</div>
            <div class="col-sm-9">
                <div class="bar" style="width: $dtotal%"><span class="pl-1 text-light">$dealer2{"All"}</span></div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-3">Pending</div>
            <div class="col-sm-9">
                <div class="bar bg-warning" style="width: calc((95% * $dealer{Pending}/$dealer{All}) + 5% )"><span class="pl-1 text-light">$dealer{"Pending"}</span></div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-3">Approved</div>
            <div class="col-sm-9">
                <div class="bar bg-success" style="width: calc((95% * $dealer{Approved}/$dealer{All}) + 5%)"><span class="pl-1 text-light">$dealer{"Approved"}</span></div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-3">Denied</div>
            <div class="col-sm-9">
                <div class="bar bg-danger" style="width: calc((95% * $dealer{Denied}/$dealer{All}) + 5%)"><span class="pl-1 text-light">$dealer{"Denied"}</span></div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-3">Logged In</div>
            <div class="col-sm-9">
                <div class="bar bg-info" style="width: $llpercent2%"><span class="pl-1 text-light">$llcnt ($llpercent\% of dealers)</span></div>
            </div>
        </div>
	</div>
</div>

<div class="container-fluid mb-3">
    <h5 class="mb-0 text-warning font-weight-bold">Claims</h5>
	<a href="javascript:adjustTime('claim_time','$ymd_seven')" class="d-inline small $cSelected{$ymd_seven}">last week</a>&nbsp;&nbsp;
	<a href="javascript:adjustTime('claim_time','$ymd_fourteen')" class="d-inline small $cSelected{$ymd_fourteen}">last 2 weeks</a>&nbsp;&nbsp;
	<a href="javascript:adjustTime('claim_time','$ymd_thirty')" class="d-inline small $cSelected{$ymd_thirty}">last month</a><br>
	<div class="border border-secondary p-1 w-75">
    <div class="row">
        <div class="col-sm-3">Total Claims</div>
        <div class="col-sm-9">
            <div class="bar" style="width: $ctotal%"><span class="pl-1 text-light">$claims2{"All"}</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Submitted</div>
        <div class="col-sm-9">
            <div class="bar bg-warning" style="width: calc((95% * $claims{Submitted}/$claims{All}) + 5% )"><span class="pl-1 text-light">$claims{"Submitted"}</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Approved</div>
        <div class="col-sm-9">
            <div class="bar bg-success" style="width: calc((95% * $claims{Approved}/$claims{All}) + 5%)"><span class="pl-1 text-light">$claims{"Approved"}</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Denied</div>
        <div class="col-sm-9">
            <div class="bar bg-danger" style="width: calc((95% * $claims{Denied}/$claims{All}) + 5%)"><span class="pl-1 text-light">$claims{"Denied"}</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Saved</div>
        <div class="col-sm-9">
            <div class="bar bg-info" style="width: calc((95% * $claims{Saved}/$claims{All}) + 5%)"><span class="pl-1 text-light">$claims{"Saved"}</span></div>
        </div>
    </div>
	</div>
</div>

<div class="container-fluid mb-3">
    <h5 class="mb-0 text-warning font-weight-bold">Redemptions</h5>
	<a href="javascript:adjustTime('redeem_time','$ymd_seven')" class="d-inline small $rSelected{$ymd_seven}">last week</a>&nbsp;&nbsp;
	<a href="javascript:adjustTime('redeem_time','$ymd_fourteen')" class="d-inline small $rSelected{$ymd_fourteen}">last 2 weeks</a>&nbsp;&nbsp;
	<a href="javascript:adjustTime('redeem_time','$ymd_thirty')" class="d-inline small $rSelected{$ymd_thirty}">last month</a><br>
	<div class="border border-secondary p-1 w-75">
        <div class="row">
            <div class="col-sm-3">Total Redemptions</div>
            <div class="col-sm-9">
                <div class="bar" style="width: $rtotal%"><span class="pl-1 text-light">$redeem2{"All"}</span></div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-3">Submitted</div>
            <div class="col-sm-9">
                <div class="bar bg-warning" style="width: calc((95% * $redeem{Submitted}/$redeem{All}) + 5% )"><span class="pl-1 text-light">$redeem{"Submitted"}</span></div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-3">Approved</div>
            <div class="col-sm-9">
                <div class="bar bg-success" style="width: calc((95% * $redeem{Approved}/$redeem{All}) + 5%)"><span class="pl-1 text-light">$redeem{"Approved"}</span></div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-3">Denied</div>
            <div class="col-sm-9">
                <div class="bar bg-danger" style="width: calc((95% * $redeem{Denied}/$redeem{All}) + 5%)"><span class="pl-1 text-light">$redeem{"Denied"}</span></div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-3">Saved</div>
            <div class="col-sm-9">
                <div class="bar bg-info" style="width: calc((95% * $redeem{Saved}/$redeem{All}) + 5%)"><span class="pl-1 text-light">$redeem{"Saved"}</span></div>
            </div>
        </div>
	</div>
</div>

<div class="container-fluid mb-3">
    <h5 class="mb-0 text-warning font-weight-bold">Reward Points</h5>
	<a href="javascript:adjustTime('pts_time','$ymd_seven')" class="d-inline small $pSelected{$ymd_seven}">last week</a>&nbsp;&nbsp;
	<a href="javascript:adjustTime('pts_time','$ymd_fourteen')" class="d-inline small $pSelected{$ymd_fourteen}">last 2 weeks</a>&nbsp;&nbsp;
	<a href="javascript:adjustTime('pts_time','$ymd_thirty')" class="d-inline small $pSelected{$ymd_thirty}">last month</a><br>
	<div class="border border-secondary p-1 w-75">
    <div class="row">
        <div class="col-sm-3">Points Earned</div>
        <div class="col-sm-9">
            <div class="bar bg-success" style="width: $claim_percent%"><span class="pl-1 text-light">$pts_claim_approved</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Points Earned <span class="small">(all time)</span></div>
        <div class="col-sm-9">
            <div class="bar bg-success" style="width: $claim_all_time%;"><span class="pl-1 text-light">$pts_earned</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Points Used</div>
        <div class="col-sm-9">
            <div class="bar bg-danger" style="width: $redeem_percent%"><span class="pl-1 text-light">$pts_redeem_approved</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Points Used <span class="small">(all time)</span></div>
        <div class="col-sm-9">
            <div class="bar bg-danger" style="width: $redeem_all_time %;"><span class="pl-1 text-light">$pts_used</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Balance  <span class="small">(this period)</span></div>
        <div class="col-sm-9">
            <div class="bar bg-light" style="width: 100%;"><span class="pl-1 text-dark">$period_balance</span></div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-3">Balance  <span class="small">(all time)</span></div>
        <div class="col-sm-9">
            <div class="bar bg-light" style="width: 100%;"><span class="pl-1 text-dark">$pts_balance</span></div>
        </div>
    </div>
	</div>
</div>

</div><!--end content-->

<br><br><br>
</body>
</html>

];
exit ;
###############################################################################

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

$localdb = &DB();$master = &MASTER();my $usr = &USR();my $pw = &PW();
$shop    = &Shop() ;
$tz      = &TZ() ;

@data = &TimeNow($tz) ;

my $sqlnow = $data[0] ;
my $ymd    = $data[1] ;#yyyy-mm-dd
($yyyy,$mm,$dd) = split(/-/,$ymd) ;
my $hms    = $data[2] ;#hr:mn:sc
my $month  = $data[3] ;#month abbr
my $day    = $data[4] ;#day abbr
my $mydate = "$day $month $dd,$yyyy" ;

my $q = new CGI;
$statfilter = $q->param("status");

if ($statfilter eq ""){
    $statfilter = "Active";
}
$statSelected{$statfilter} = "checked";

$dbh = DBI->connect("DBI:mysql:rewardsaero_$localdb:localhost","$usr","$pw") ; ;

$sql = "SELECT `ID`, `Purpose`, `Description` from `SG_Email_Template`";

$sql = "SELECT `ID`, `Name`, `Subject`, `Purpose` from `Emails` WHERE `Status` = '$statfilter'";
$sth = $dbh->prepare($sql);
$sth->execute();
while (@row = $sth->fetchrow_array()){
    $emailID = $row[0];
    $emailN  = $row[1];
    $sub     = $row[2];
    $purpose = $row[3];
    $emailHash{"$emailN^$emailID^$purpose"} = $sub;
}
$sth->finish();

$dbh->disconnect;

print qq[
<!DOCTYPE html>
<html lang="en">
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

<link rel="icon" type="image/png" href="favicon.png">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="shortcut icon" href="favicon.ico">

<link rel="stylesheet" href="style/style2.css">

<style>
.hoverme:hover{
    cursor:pointer;
}
</style>

<script>
window.history.forward();
function noBack() { window.history.forward(); }

function filter(x){
    document.getElementById("status").value = x;
    var frm = document.getElementById("reload");
    frm.submit();
}
function Go(x){
    console.log(x)
    document.getElementById("dfn").value = x;
    var frm = document.getElementById("go");
    frm.submit();
}
</script>

</head>

<body oncontextmenu="return false;" onload="noBack();" onpageshow="if (event.persisted) noBack();" >
];
&nav_bar();
print qq[
<form id="reload" method="post" action="send_grid_start.cgi">
<input type="hidden" name="status" id="status" value="$statfilter" autocomplete="off">
</form>

<form id="go" method="post" action="send_grid_design.cgi">
<input type="hidden" name="dfn" id="dfn" value="0" autocomplete="off">
</form>

<div class="card mt-3 mx-auto w-75">
<div class="card-header text-center">
<h4>Email Maintenance</h4>
<div class="form-row">
<div class="col-md-3">
    &nbsp;
</div>
<div class="col-md-6 text-center">
<button type="button" class="btn btn-white" onclick="location.href='rm_ow_menu.cgi'"><i class="fas fa-arrow-left"></i> Back</button>
</div>
<div class="col-md-3 d-none">
    <button class="btn btn-link text-success p-0" data-toggle="collapse" data-target="#demo">+ New Email</button>

    <div id="demo" class="collapse mt-1">
        <div class="input-group">
            <input type="text" class="form-control form-control-sm" placeholder="new category" id="newcat" autocomplete="off">
            <div class="input-group-append">
              <button class="btn btn-primary btn-sm" type="button" onclick="createNew('newcat')">Submit</button>
            </div>
        </div>
    </div>
</div>
</div>

</div><!--end header-->
<div class="card-body">
<div class="form-check-inline">
    <label class="form-check-label">
        <input type="radio" class="form-check-input" name="option" autocomplete="off" onclick="filter('Active')" $statSelected{'Active'}>Active Emails
    </label>
</div>
<div class="form-check-inline">
    <label class="form-check-label text-danger">
        <input type="radio" class="form-check-input" name="option" autocomplete="off" onclick="filter('Inactive')" $statSelected{'Inactive'}>Inactive Emails
    </label>
</div>
<div class="table-responsive mt-3 mb-3 p-3">
    <p class="mb-0">*click to edit</p>
    <table class="table table-bordered table-striped table-hover">
        <thead>
            <tr>
                <th>Name</th>
                <th>Subject</th>
                <th>Purpose</th>
            </tr>
        </thead>
        <tbody>
    ];
        foreach $e(sort keys %emailHash){
            ($ename,$eid,$pur) = split(/\^/,$e);
            $sub = $emailHash{$e};
            print qq[
                <tr class="hoverme" onclick="Go('$eid')">
                    <td><b>$ename</b></td>
                    <td>$sub</td>
                    <td>$pur</td>
                </tr>
            ];
        }
    print qq[
        </tbody>
    </table>
</div>
</div><!--end card body-->

</div><!--end card-->
<br><br>
</body>
</html>
];
exit;

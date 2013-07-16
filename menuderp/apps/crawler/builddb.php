<?php
//structured statements
$insQuery = $mysql->prepare("INSERT INTO food VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
$serQuery = $mysql->prepare("SELECT * FROM food WHERE food_name=?");
$delQuery = $mysql->prepare("DELETE FROM food WHERE food_name=?");

function builddb($mysql) {
  date_default_timezone_set('America/New_York');
  $date = getDate();

  $mysql->query("TRUNCATE TABLE food");

  if ($date['wday'] > 0 && $date['wday'] < 6) {
    $mealstoday = array("Breakfast", "Lunch", "Dinner");
  } else {
    $mealstoday = array("Brunch", "Dinner");
  }

  $locs = array("Moulton", "Thorne");

  foreach($mealstoday as &$meal) {
    foreach($locs as &$loc) { //48=moulton, 49=thorne
      $html = getHTML($date, $loc, $meal);
      processAndAdd($html, $date, $loc, $meal);
    }
  }
  $GLOBALS['insQuery']->close();
  $GLOBALS['serQuery']->close();
  $GLOBALS['delQuery']->close();
}

//grab the html from bowdoin's atreus server
function getHTML($date, $loc, $meal){
  if($loc=='Moulton') {
    $locnum=48;
   } else {
     $locnum=49;
   }

  $url = 'http://www.bowdoin.edu/atreus/views?unit='.$locnum.'&meal='.$meal.'&mo='.($date['mon']-1).'&dy='.$date['mday'].'&yr='.$date['year'];

  //this code based in large part on code from a post by stackoverflow user 728241 (David)
  //let me just take this chance to say: god bless stackoverflow
  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, $url);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
  curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);

  if($html = curl_exec($ch)) {
    $dom = new DOMDocument();
    $dom->recover = true;
    $dom->strictErrorChecking = false;
    $dom->loadHTML($html);
    $html = $dom->saveHTML();
    curl_close($ch);
    return $html;
  } else {
    echo "<p id='errormsg'>Menu content could not be loaded.</p>";
  }
}

function processAndAdd($html, $date, $loc, $meal) {
  //chop off the head up to the first section heading
  $html = str_replace("<br>", "", substr($html, strpos($html,"<h3>"), -1));

  //segment into food sections (divide at the h3's)
  $html = explode("<h3>", $html);

  //find the express meal and KILL IT
  $searchword = "Express Meal";
  $matches = array_filter($html, function($var) use ($searchword) { return preg_match("/\b$searchword\b/i", $var); });
  $matches = array_values($matches);

  for($expmeal=0; $expmeal<count($html); $expmeal++) {
    if ($html[$expmeal] == $matches[0]) {
      break;
    }
  }

  //starting at $expmeal+1 skips over all express meals and the "empty" item created by explode
  //seriously, fuck express meal
  for($i=($expmeal+1); $i<count($html); $i++) {
    $foodgroup = substr($html[$i], 0, strpos($html[$i], '<span>'));

    //some foodgroups still have a </h3>
    $stupidh3 = explode("</h3>", $foodgroup);
    $foodgroup = $stupidh3[0];

    $foods = explode("<span>", substr($html[$i], strpos($html[$i], '<span>'), -1));
    for($item=1; $item<count($foods); $item++) {
      // cut off the (ve) (gf) etc
      $attrs = explode("(", $foods[$item]);
      $foodname = $attrs[0];

      //some $foodnames still have a </span>
      $stupidspan = explode("</span>", $foodname);
      $foodname = $stupidspan[0];
      //also there's issues with &amp;
      $foodname = str_replace("&amp;", "&", $foodname);

      //make a csl of the attributes
      for($attrnum = 1; $attrnum<count($attrs); $attrnum++) {
        $attrs[$attrnum] = substr($attrs[$attrnum], 0, strpos($attrs[$attrnum], ')'));
      }
      unset($attrs[0]);
      $attrs=array_values($attrs); //fix the indicies. php is weird sometimes
      $attrcsv = implode(",",$attrs); //make the array a comma separated list

      // we've now extracted
      // $foodname, $attrcsv, $foodgroup
      // and we were passed
      // $date, $loc, $meal
      addRowMySQL($foodname, $attrcsv, $foodgroup, $date, $loc, $meal);
    }
  }
}

function addRowMySQL($foodname, $attrcsv, $foodgroup, $date, $loc, $meal){
  $TODAY = $date['year']."-".$date['mon']."-".$date['mday'];
  $NOW = date('Y-m-d H:i:s');
  $sero = 0;

  printf("<p>trying to add %s, %s, %s, %s, %s, %s, %s, %s, %s </p>", $foodname, $attrcsv, $foodgroup, $meal, $loc, $loc, $TODAY, $TODAY, $NOW);

  if($GLOBALS['serQuery']){
    $GLOBALS['serQuery']->bind_param("s", $foodname);
    $GLOBALS['serQuery']->execute();

    $result = getResult($GLOBALS['serQuery']);

    if($result){
      if($GLOBALS['delQuery']){
        echo "<p>deleting old entry</p>";
        $GLOBALS['delQuery']->bind_param("s", $food_name);
        $GLOBALS['delQuery']->execute();
      }
      if($GLOBALS['insQuery']){
        echo "<p>replacing entry</p>";
        $GLOBALS['insQuery']->bind_param("isssssssss", $result['id'], $foodname, $attrcsv, $foodgroup, $meal, $result['next_loc'], $loc, $result['next_date'], $TODAY, $NOW);
        $GLOBALS['insQuery']->execute();
      }
    } else {
      if($GLOBALS['insQuery']){
        echo "<p>adding brand-new entry</p>";
        $GLOBALS['insQuery']->bind_param("isssssssss", $zero, $foodname, $attrcsv, $foodgroup, $meal, $loc, $loc, $TODAY, $TODAY, $NOW);
        $GLOBALS['insQuery']->execute();
      }
    }
  }
}


//courtesy of poster "hamidhossain at gmail dot com" on the php manpages
function getResult($stmt){
  $result = NULL;
  $meta = $stmt->result_metadata();
  while ($field = $meta->fetch_field())
  {
    $params[] = &$row[$field->name];
  }

  call_user_func_array(array($stmt, 'bind_result'), $params);

  while ($stmt->fetch()) {
    foreach($row as $key => $val)
    {
      $c[$key] = $val;
    }
    $result[] = $c;
  }
  return $result[0];
}

function whichMeal($wday, $hour) {
  if($wday > 0 && $wday <5) {
    if ($hour < 10) {
      $meal = 'Breakfast';
    } else if ($hour < 14) {
      $meal = 'Lunch';
    } else {
      $meal = 'Dinner';
    }
  } else {
    if ($hour < 14) {
      $meal = 'Brunch';
    } else {
      $meal = 'Dinner';
    }
  }
}


?>

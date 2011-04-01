<?php echo '<?xml version="1.0" encoding="iso-8859-1"?>' ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">
  <head>
    <title>euscan</title>
    <meta http-equiv="Content-Type" content="text/HTML; charset=iso-8859-1" />
    <link rel="stylesheet" type="text/css" href="/style.css" media="screen" title="Normal" />
    <script src="sorttable.js"></script>
  </head>
  <body>
    <div id="header">
      <h1>euscan</h1>
    </div>
    <div id="content">
<?php
$db = new SQLite3('euscan.db');

$act = isset($_GET['act']) ? $_GET['act'] : "home";
$cat = isset($_GET['cat']) ? $_GET['cat'] : '';
$pkg = isset($_GET['pkg']) ? $_GET['pkg'] : '';
$herd = isset($_GET['herd']) ? $_GET['herd'] : '';
$mtnr = isset($_GET['maintainer']) ? $_GET['maintainer'] : '';

if ($act == "home") {

} else if ($act == "categories") {
  $sql = "SELECT category, COUNT(version) as versions, SUM(packaged) as ebuilds";
  $sql.= " FROM packages JOIN versions ON package_id = packages.id";
  $sql.= " GROUP BY category";

  $results = $db->query($sql);

  echo "<table class=\"sortable\"><tr><th>Category</th><th>Ebuilds</th><th>New versions</th></tr>";
  while ($row = $results->fetchArray()) {
    $new = $row['versions'] - $row['ebuilds'];
    $color = $new == 0 ? 'green' : 'red';
    echo "<tr>";
    echo "<td><a href=\"?act=packages&amp;cat={$row['category']}\">{$row['category']}</a></td>";
    echo "<td>{$row['versions']}</td>";
    echo "<td style=\"color: $color\">$new</td>";
    echo "</tr>";
  }
  echo "</table>";
} else if ($act == "herds") {
  $sql = "SELECT herd, COUNT(version) as versions, SUM(packaged) as ebuilds";
  $sql.= " FROM herds";
  $sql.= " JOIN package_herds ON herds.id = herd_id";
  $sql.= " JOIN packages ON package_herds.package_id = packages.id";
  $sql.= " JOIN versions ON versions.package_id = packages.id";
  $sql.= " GROUP BY herd";

  $results = $db->query($sql);

  echo "<table class=\"sortable\"><tr><th>Herd</th><th>Ebuilds</th><th>New versions</th></tr>";
  while ($row = $results->fetchArray()) {
    $new = $row['versions'] - $row['ebuilds'];
    $color = $new == 0 ? 'green' : 'red';
    echo "<tr>";
    echo "<td><a href=\"?act=packages&amp;herd={$row['herd']}\">{$row['herd']}</a></td>";
    echo "<td>{$row['versions']}</td>";
    echo "<td style=\"color: $color\">$new</td>";
    echo "</tr>";
  }
  echo "</table>";
} else if ($act == "maintainers") {
  $sql = "SELECT maintainer, COUNT(version) as versions, SUM(packaged) as ebuilds";
  $sql.= " FROM maintainers";
  $sql.= " JOIN package_maintainers ON maintainers.id = maintainer_id";
  $sql.= " JOIN packages ON package_maintainers.package_id = packages.id";
  $sql.= " JOIN versions ON versions.package_id = packages.id";
  $sql.= " GROUP BY maintainer";

  $results = $db->query($sql);

  echo "<table class=\"sortable\"><tr><th>Maintainer</th><th>Ebuilds</th><th>New versions</th></tr>";
  while ($row = $results->fetchArray()) {
    $new = $row['versions'] - $row['ebuilds'];
    $color = $new == 0 ? 'green' : 'red';
    echo "<tr>";
    echo "<td><a href=\"?act=packages&amp;maintainer={$row['maintainer']}\">{$row['maintainer']}</a></td>";
    echo "<td>{$row['versions']}</td>";
    echo "<td style=\"color: $color\">$new</td>";
    echo "</tr>";
  }
  echo "</table>";
} else if ($act == "categories") {
  $sql = "SELECT category, COUNT(version) as versions, SUM(packaged) as ebuilds";
  $sql.= " FROM packages JOIN versions ON package_id = packages.id";
  $sql.= " GROUP BY category";

  $results = $db->query($sql);

  echo "<table class=\"sortable\"><tr><th>Category</th><th>Ebuilds</th><th>New versions</th></tr>";
  while ($row = $results->fetchArray()) {
    $new = $row['versions'] - $row['ebuilds'];
    $color = $new == 0 ? 'green' : 'red';
    echo "<tr>";
    echo "<td><a href=\"?act=packages&amp;cat={$row['category']}\">{$row['category']}</a></td>";
    echo "<td>{$row['versions']}</td>";
    echo "<td style=\"color: $color\">$new</td>";
    echo "</tr>";
  }
  echo "</table>";
} else if ($act == 'packages') {
  $db_cat = $db->escapeString($cat);
  $db_herd = $db->escapeString($herd);
  $db_mtnr = $db->escapeString($mtnr);

  if ($db_cat) {
    $sql = "SELECT category, package, COUNT(version) as versions, SUM(packaged) as ebuilds";
    $sql.= " FROM packages JOIN versions ON package_id = packages.id";
    $sql.= " WHERE category = '$db_cat'";
    $sql.= " GROUP BY category, package";
  } else if ($db_herd) {
    $sql = "SELECT category, package, COUNT(version) as versions, SUM(packaged) as ebuilds";
    $sql.= " FROM herds";
    $sql.= " JOIN package_herds ON herds.id = herd_id";
    $sql.= " JOIN packages ON package_herds.package_id = packages.id";
    $sql.= " JOIN versions ON versions.package_id = packages.id";
    $sql.= " WHERE herd LIKE '$db_herd'";
    $sql.= " GROUP BY category, package";
  } else if ($db_mtnr) {
    $sql = "SELECT category, package, COUNT(version) as versions, SUM(packaged) as ebuilds";
    $sql.= " FROM maintainers";
    $sql.= " JOIN package_maintainers ON maintainers.id = maintainer_id";
    $sql.= " JOIN packages ON package_maintainers.package_id = packages.id";
    $sql.= " JOIN versions ON versions.package_id = packages.id";
    $sql.= " WHERE maintainer LIKE '%$db_mtnr%'";
    $sql.= " GROUP BY category, package";
  }

  if ($sql) {
    $results = $db->query($sql);

    echo "<table class=\"sortable\"><tr><th>Category</th><th>Ebuilds</th><th>New versions</th></tr>";
    while ($row = $results->fetchArray()) {
      $new = $row['versions'] - $row['ebuilds'];
      $catpkg = "{$row['category']}/{$row['package']}";
      $color = $new == 0 ? 'green' : 'red';
      echo "<tr>";
      echo "<td><a href=\"?act=package&amp;pkg=$catpkg\">$catpkg</td>";
      echo "<td>{$row['versions']}</td>";
      echo "<td style=\"color: $color\">$new</td>";
      echo "</tr>";
    }
    echo "</table>";
  }
} else if ($act == 'package') {
  $pkg = explode("/", $pkg);

  if (count($pkg) == 2) {
    $cat = $db->escapeString($pkg[0]);
    $pkg = $db->escapeString($pkg[1]);
  } else {
    $cat = $pkg = "";
  }

  $sql = "SELECT * FROM packages WHERE category = '$cat' AND package = '$pkg'";
  $infos = $db->query($sql);
  $infos = $infos->fetchArray();

  if ($infos) {
    $sql = "SELECT * FROM versions WHERE package_id = ${infos['id']} AND packaged = 1";
    $results = $db->query($sql);

    echo '<p>Packaged versions:</p><ul>';
    while ($version = $results->fetchArray()) {
      echo "<li>${version['version']}-${version['revision']}:${version['slot']}</li>";
    }

    $sql = "SELECT * FROM versions ";
    $sql.= "JOIN upstream_urls ON versions.id = version_id ";
    $sql.= "WHERE package_id = ${infos['id']} AND packaged = 0";
    $results = $db->query($sql);

    echo '</ul>';
    echo '<p>Upstream versions:</p><ul>';

    while ($version = $results->fetchArray()) {
      echo "<li>${version['version']} - ${version['url']}</li>";
    }

    echo '</ul>';
  } else {
    echo '<div class="error">Invalid package</div>';
  }
}

?>
    </div>
    <div id="menus">
      <div id="menu">
	<ul>
	  <li><a href="?act=categories">Categories</a></li>
	  <li><a href="?act=herds">Herds</a></li>
	  <li><a href="?act=maintainers">Maintainers</a></li>
	</div>
      </div>
    </div>
    <div id="footer">
      Powered by:
      <a href="http://kernel.org"><img  src="/linux.png" alt="Linux" /></a>
      <a href="http://gentoo.org"><img  src="/gentoo.png" alt="Gentoo Linux" /></a>
      -
      Copyright (C) 2011 <strong>Corentin Chary</strong>
    </div>
  </body>
</html>

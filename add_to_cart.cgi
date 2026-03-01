#!/usr/bin/php
<?php
if (isset($_SERVER['HTTP_COOKIE'])) {
    $cookies = explode(';', $_SERVER['HTTP_COOKIE']);
    foreach ($cookies as $cookie) {
        $parts = explode('=', $cookie);
        $name = trim($parts[0]);
        if (count($parts) > 1) {
            $value = trim($parts[1]);
            $_COOKIE[$name] = $value;
        }
    }
}

session_start();
require_once('db.php');

if ($_SERVER['REQUEST_METHOD'] === 'POST'){
    $fh = file_get_contents("php://stdin");
    parse_str($fh, $_POST);
    if(isset($_POST['game_id'])) {
    $gameId = (int)$_POST['game_id'];
    
    if (!isset($_SESSION['cart'])) {
        $_SESSION['cart'] = [];
    }

    if (isset($_SESSION['cart'][$gameId])) {
        $_SESSION['cart'][$gameId]++;
    } else {
        $_SESSION['cart'][$gameId] = 1;
    }
    
    $_SESSION['flash_message'] = "Gra zostala dodana do koszyka!";
}
}


echo "Status: 302 Found\n";
echo "Location: index.cgi\n\n";
exit;
?>
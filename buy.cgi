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
require 'db.php';

if(!isset($_SESSION['user_id'])) {
    $_SESSION['flash_message'] = "Zaloguj się";
    echo "Status: 302 Found\n";
    echo "Location: login.cgi\n\n";
    exit;
}

echo "Content-type: text/html\n\n";

if($_SERVER['REQUEST_METHOD'] === 'POST') {
    $clientId = $_SESSION['user_id'];
    $fh = file_get_contents("php://stdin");
    parse_str($fh, $_POST);
    $graId = (int)$_POST['game_id'];
    $quantity = 1;
    
    try{
        $pg_games_array = "{" . $graId . "}";
        $pg_qty_array = "{" . $quantity . "}";
        
        $stmt = $pdo->prepare("CALL zloz_zamowienie(?, ?, ?)");
        $stmt->bindParam(1, $clientId, PDO::PARAM_INT);
        $stmt->bindParam(2, $pg_games_array, PDO::PARAM_STR);
        $stmt->bindParam(3, $pg_qty_array, PDO::PARAM_STR);
        $stmt->execute();
        
        $message = "Zamówienie zostało poprawnie stworzone";
    } catch(PDOException $e) {
        $message = "Wystąpił błąd podczas złożenia zamówienia: " . $e->getMessage();
    }
} else {
    echo "Status: 302 Found\n";
    echo "Location: index.cgi\n\n";
    exit;
}
?>

<!DOCTYPE html>
<html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Status zamówienia</title>
    </head>
    <body>
        <div class="container" style="text-align: center; margin-top: 50px; ">
            <h2><?= htmlspecialchars($message) ?></h2>
            <a href="index.cgi">Wrócić do sklepu</a>
        </div>
    </body>
</html>
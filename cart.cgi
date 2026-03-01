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
require_once 'db.php';

if (isset($_SERVER['QUERY_STRING'])) {
	parse_str($_SERVER['QUERY_STRING'], $_GET);
	if (isset($_GET['action']) && $_GET['action'] == 'clear') {
    		unset($_SESSION['cart']);
    		echo "Status: 302 Found\n";
    		echo "Location: cart.cgi\n\n";
    		exit;
	}
}

$message = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') { 
    $fh = file_get_contents("php://stdin");
    parse_str($fh, $_POST);
    if(isset($_POST['checkout'])) {
    if (!isset($_SESSION['user_id'])) {
        $_SESSION['flash_message'] = "Zaloguj sie zeby zlozyc zamowienie.";
        echo "Status: 302 Found\n";
        echo "Location: login.cgi\n\n";
        exit;
    }

    if (!empty($_SESSION['cart'])) {
        try {
            $ids = [];
            $qtys = [];
            
            foreach ($_SESSION['cart'] as $gameId => $qty) {
                $ids[] = $gameId;
                $qtys[] = $qty;
            }
            
            $pg_ids_str = "{" . implode(',', $ids) . "}";
            $pg_qtys_str = "{" . implode(',', $qtys) . "}";
            
            $stmt = $pdo->prepare("CALL zloz_zamowienie(?, ?, ?)");
            $stmt->bindParam(1, $_SESSION['user_id'], PDO::PARAM_INT);
            $stmt->bindParam(2, $pg_ids_str, PDO::PARAM_STR);
            $stmt->bindParam(3, $pg_qtys_str, PDO::PARAM_STR);
            $stmt->execute();
            
            unset($_SESSION['cart']);
            $message = "Zlozenie zostalo zlozone poprawnie! Przejdz do <a href='profile.cgi'>Profilu</a> zeby oplacic.";
            
        } catch (PDOException $e) {
            $message = "Podczas zlozenia zamowienia wystapil blad: " . $e->getMessage();
        }
    }
}
}

$cartItems = [];
$totalPrice = 0;

if (!empty($_SESSION['cart'])) {
    $ids = array_keys($_SESSION['cart']);
    
    $inQuery = implode(',', array_fill(0, count($ids), '?'));
    
    $stmt = $pdo->prepare("SELECT id, nazwa, cena FROM Gra WHERE id IN ($inQuery)");
    $stmt->execute($ids);
    $games = $stmt->fetchAll();
    
    foreach ($games as $game) {
        $qty = $_SESSION['cart'][$game['id']];
        $sum = $game['cena'] * $qty;
        $totalPrice += $sum;
        
        $cartItems[] = [
            'nazwa' => $game['nazwa'],
            'cena' => $game['cena'],
            'qty' => $qty,
            'sum' => $sum
        ];
    }
}

echo "Content-type: text/html\n\n";
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Koszyk</title>
</head>
<body>
    <header>
        <h1>Twoj koszykk</h1>
        <a href="index.cgi">Wrocic do sklepu</a>
    </header>

    <?php if($message): ?>
        <p style="background: #eee; padding: 15px; border: 1px solid #333;"><?= $message ?></p>
    <?php endif; ?>

    <?php if (empty($cartItems) && empty($message)): ?>
        <p>Koszyk jest pusty. <a href="index.cgi">Idziemy na zakupy?</a></p>
    <?php elseif (!empty($cartItems)): ?>
        
        <table border="1" cellpadding="10" cellspacing="0" width="100%">
            <thead>
                <tr>
                    <th>Gra</th>
                    <th>Cena za szt.</th>
                    <th>Ilosc</th>
                    <th>Suma</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($cartItems as $item): ?>
                <tr>
                    <td><?= htmlspecialchars($item['nazwa']) ?></td>
                    <td><?= $item['cena'] ?> PLN</td>
                    <td><?= $item['qty'] ?> szt.</td>
                    <td><?= number_format($item['sum'], 2) ?> PLN</td>
                </tr>
                <?php endforeach; ?>
                
                <tr style="background-color: #f0f0f0; font-weight: bold;">
                    <td colspan="3" align="right">RAZEM DO SPLATY:</td>
                    <td><?= number_format($totalPrice, 2) ?> PLN</td>
                </tr>
            </tbody>
        </table>

        <div style="margin-top: 20px;">
            <a href="cart.cgi?action=clear" style="color: red; margin-right: 20px;">Wyczyscic koszyk</a>
            
            <form method="POST" style="display: inline;">
                <input type="hidden" name="checkout" value="1">
                <button type="submit" style="font-size: 1.2em; padding: 10px 20px; cursor: pointer;">
                    Zlozyc zamowienie
                </button>
            </form>
        </div>

    <?php endif; ?>
</body>
</html>
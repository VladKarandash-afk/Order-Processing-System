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


ini_set('display_errors', 0);
error_reporting(E_ALL);

ob_start();
session_start();

$error = '';
$success = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    
    require 'db.php';

    $fh = file_get_contents("php://stdin");
    parse_str($fh, $_POST);

    $imie = trim($_POST['imie'] ?? '');
    $nazwisko = trim($_POST['nazwisko'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $phone = trim($_POST['telefon'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if (empty($imie) || empty($email) || empty($password) || empty($phone)) {
        $error = "Wypelnij wszystkie niezbedne pola!";
    } else {
        try {
            $stmt = $pdo->prepare("SELECT id FROM Klient WHERE mail = ?");
            $stmt->execute([$email]);
            
            if ($stmt->rowCount() > 0) {
                $error = "Ten mail juz jest zarejestrowany!";
            } else {
                $sql = "INSERT INTO Klient (imie, nazwisko, mail, telefon, haslo) VALUES (?, ?, ?, ?, ?)";
                $stmt_insert = $pdo->prepare($sql);
                $stmt_insert->execute([$imie, $nazwisko, $email, $phone, $password]);
    		echo "Status: 302 Found\n";
    		echo "Location: login.cgi?registered=1\n\n";
                exit;
            }
        } catch (PDOException $e) {
            $error = "Podczas rejestracji wystapil blad: " . $e->getMessage();
        }
    }
}

echo "Content-type: text/html; charset=utf-8\n\n";
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Rejestracja</title>
</head>
<body>

<div class="reg-container">
    <h2 style="text-align:center">Rejestracja</h2>

    <?php if ($error): ?>
        <div class="error"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>

    <form method="post">
        <label>Imie <span style="color:red">*</span></label>
        <input type="text" name="imie" required value="<?= htmlspecialchars($imie ?? '') ?>">

        <label>Nazwisko</label>
        <input type="text" name="nazwisko" value="<?= htmlspecialchars($nazwisko ?? '') ?>">

        <label>Email <span style="color:red">*</span></label>
        <input type="email" name="email" required value="<?= htmlspecialchars($email ?? '') ?>">

        <label>Telefon <span style="color:red">*</span></label>
        <input type="telefon" name="telefon" required value="<?= htmlspecialchars($phone ?? '') ?>">

        <label>Haslo <span style="color:red">*</span></label>
        <input type="password" name="password" required>

        <button type="submit">Zarejestrowac sie</button>
    </form>

    <div class="links">
        Masz konto? <a href="login.cgi">Zalogowac sie</a>
    </div>
</div>

</body>
</html>
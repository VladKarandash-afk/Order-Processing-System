#!/usr/bin/php
<?php
ini_set('display_errors', 0);
ini_set('log_errors', 1);
error_reporting(E_ALL);
ob_start();

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

$error = '';
$email='';
$password='';

$method = $_SERVER["REQUEST_METHOD"] ?? 'CLI';

if ($method == "POST") {
    $fh = file_get_contents("php://stdin");
    parse_str($fh, $form_data);
    $email = $form_data['email'];
    $password = $form_data['password'];

    if (trim($email) == 'admin@shop.com' && trim($password) == 'admin123') {
        $_SESSION['user_role'] = 'admin';

	session_write_close();

	$sess_name = session_name();
	$sess_id = session_id();

	echo "Set-Cookie: $sess_name=$sess_id; path=/\n";
        echo "Status: 302 Found\n";
	echo "Location: admin.cgi\n\n";	
        exit;
    }

    $stmt = $pdo->prepare("SELECT id, imie, haslo FROM Klient WHERE mail = :email");
    $stmt->execute(['email' => $email]);
    $user = $stmt->fetch();

    if ($user && $password === $user['haslo']) { 
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['user_name'] = $user['imie'];
        $_SESSION['user_role'] = 'client';

	session_write_close();

	$sess_name = session_name();
	$sess_id = session_id();
        
        echo "Set-Cookie: $sess_name=$sess_id; path=/\n";
        echo "Status: 302 Found\n";
	echo "Location: index.cgi\n\n";	
        exit;
    } else {
        $error = "Niepoprawne dane logowania!";
    }
}

if (isset($_SERVER['QUERY_STRING'])) {
	parse_str($_SERVER['QUERY_STRING'], $_GET);
}

echo "Content-type: text/html\n\n";
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Logowanie do systemu</title>
</head>
<body>
    <?php if (isset($_GET['registered'])): ?>
    <div style="color: green; font-weight: bold; text-align: center; margin-bottom: 10px;">
        Konto zostalo stworzone! Zaloguj sie.
    </div>
    <?php endif; ?>

    <div class="login-container">
        <h2>Logowanie</h2>
        <?php if($error) echo "<p style='color:red'>$error</p>"; ?>
        
        <form method="post">
            <label>Email:</label><br>
            <input type="text" name="email" required><br><br>
            
            <label>Haslo:</label><br>
            <input type="password" name="password" required><br><br>
            
            <button type="submit">Zalogowac sie</button>
        </form>
    </div>

    <a href="register.cgi">Nie masz konta? Zarejestruj sie</a>
</body>
</html>
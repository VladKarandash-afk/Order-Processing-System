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

if (!isset($_SESSION['user_id'])) {
    echo "Status: 302 Found\n";
    echo "Location: login.cgi\n\n";
    exit;
}

$user_id = $_SESSION['user_id'];
$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST'){
    $fh = file_get_contents("php://stdin");
    parse_str($fh, $_POST);
    if(isset($_POST['pay_order_id'])) {
    try {
        $stmt = $pdo->prepare("CALL zrealizuj_zamowienie(?)");
        $stmt->bindParam(1, $_POST['pay_order_id'], PDO::PARAM_INT);
        $stmt->execute();
        
        $message = "Zamowienie #{$_POST['pay_order_id']} poprawnie oplacone! Klucze zostaly dodane do biblioteki.";
    } catch (PDOException $e) {
        $message = "Podczas oplaty zamowienia wystapil blad: " . $e->getMessage();
    }
}
}

if (isset($_SERVER['QUERY_STRING'])) {
	parse_str($_SERVER['QUERY_STRING'], $_GET);
}

$sort_whitelist = [      
    'name_asc'   => 'g.nazwa ASC',      
    'name_desc'  => 'g.nazwa DESC',
    'data_asc'   => 'z.data ASC',
    'data_desc'  => 'z.data DESC',
    'status'     => 'z.status ASC'    
];

$sort_key1 = $_GET['sort1'] ?? 'name_asc';

if (array_key_exists($sort_key1, $sort_whitelist)) {
    $order_by_sql1 = $sort_whitelist[$sort_key1];
} else {
    $order_by_sql1 = 'g.nazwa ASC';
}

$sql_orders = "
    SELECT z.id, z.data, z.status, 
           g.nazwa, pz.ilosc, pz.cena_historyczna
    FROM Zamowienie z
    JOIN Pozycja_zamowienia pz ON z.id = pz.zamowienie
    JOIN Gra g ON pz.gra = g.id
    WHERE z.klient = ?
    ORDER BY $order_by_sql1, z.id DESC
";

$stmt = $pdo->prepare($sql_orders);
$stmt->execute([$user_id]);
$raw_rows = $stmt->fetchAll();

$grouped_orders = [];

foreach ($raw_rows as $row) {
    $order_id = $row['id'];
    
    if (!isset($grouped_orders[$order_id])) {
        $grouped_orders[$order_id] = [
            'id' => $row['id'],
            'data' => $row['data'],
            'status' => $row['status'],
            'games' => []
        ];
    }
    
    $grouped_orders[$order_id]['games'][] = [
        'nazwa' => $row['nazwa'],
        'ilosc' => $row['ilosc']
    ];
}

$sort_key = $_GET['sort'] ?? 'name_asc';

if (array_key_exists($sort_key, $sort_whitelist)) {
    $order_by_sql = $sort_whitelist[$sort_key];
} else {
    $order_by_sql = 'g.nazwa ASC';
}

$sql_keys = "
    SELECT g.nazwa, k.klucz_aktywacji
    FROM Kopia_gry k
    JOIN Gra g ON k.gra = g.id
    WHERE k.klient = ?
";

$search = $_GET['search'] ?? '';
$params = [$user_id];

if ($search) {
    $sql_keys .= " AND g.nazwa ILIKE ?";
    $params[] = "%$search%";
}

$sql_keys .= " ORDER BY $order_by_sql";

$stmt = $pdo->prepare($sql_keys);
$stmt->execute($params);
$my_keys = $stmt->fetchAll();

echo "Content-type: text/html\n\n";
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Moj profil</title>
</head>
<body>
    <header>
        <h1>Profil: <?= htmlspecialchars($_SESSION['user_name']) ?></h1>
        <a href="index.cgi">Wrocic do sklepu</a> | <a href="logout.cgi">Wylogowac sie</a>
    </header>

    <?php if($message): ?>
        <div style="background: #dff0d8; padding: 15px; margin: 10px 0; border: 1px solid #d6e9c6;">
            <?= htmlspecialchars($message) ?>
        </div>
    <?php endif; ?>

    <section>
        <h2>Biblioteka (moje klucze)</h2>
	<form method="get" style="margin: 20px 0;">
        	<input type="text" name="search" placeholder="Wpisz gre..." value="<?= htmlspecialchars($search) ?>">
        	<button type="submit">Wyszukaj</button>
        	<?php if($search): ?><a href="profile.cgi">Zresetuj</a><?php endif; ?>
        </form>
	<div class="sort-panel">
           Sortowanie: 
            <a href="?sort=name_asc">Za nazwa (A-Z)</a> |
	    <a href="?sort=name_desc">Za nazwa (Z-A)</a>
        </div>
        <?php if (count($my_keys) > 0): ?>
            <table border="1" cellpadding="10">
                <tr>
                    <th>Gra</th>
                    <th>Klucz aktywacji</th>
                </tr>
                <?php foreach ($my_keys as $key): ?>
                <tr>
                    <td><b><?= htmlspecialchars($key['nazwa']) ?></b></td>
                    <td style="font-family: monospace; color: green;"><?= htmlspecialchars($key['klucz_aktywacji']) ?></td>
                </tr>
                <?php endforeach; ?>
            </table>
        <?php else: ?>
            <p>Jeszcze nie ma kupionych gier</p>
        <?php endif; ?>
    </section>

    <hr>

    <section>
        <h2>Historia zamowien</h2>
	<div class="sort-panel">
            Sortowanie: 
            <a href="?sort1=name_asc">Za nazwa (A-Z)</a> |
	    <a href="?sort1=name_desc">Za nazwa (Z-A)</a> |
	    <a href="?sort1=data_asc">Najpierw wczesniejsze</a> |
	    <a href="?sort1=data_desc">Najpierw nowsze</a> |
	    <a href="?sort1=status">Najpierw nieoplacone</a>
        </div>
        <table border="1" cellpadding="10">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Data</th>
                    <th>Gry</th>
                    <th>Status</th>
                    <th>Akcja</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($grouped_orders as $order): ?>
                <tr>
                    <td>#<?= $order['id'] ?></td>
                    <td><?= $order['data'] ?></td>
                    <td>
            		<?php foreach ($order['games'] as $game): ?>
                	    <div> <?= htmlspecialchars($game['nazwa']) ?> (<?= $game['ilosc'] ?> szt.)</div>
            		<?php endforeach; ?>
        	    </td>
                    <td>
                        <?php if($order['status'] == 'nieoplacone'): ?>
                            <span style="color:red">Nieoplacone</span>
                        <?php else: ?>
                            <span style="color:green"><?= $order['status'] ?></span>
                        <?php endif; ?>
                    </td>
                    <td>
                        <?php if($order['status'] == 'nieoplacone'): ?>
                            <form method="post">
                                <input type="hidden" name="pay_order_id" value="<?= $order['id'] ?>">
                                <button type="submit">Oplacic teraz</button>
                            </form>
                        <?php else: ?>
                            Zrealizowane
                        <?php endif; ?>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </section>
</body>
</html>
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
}

$search = $_GET['search'] ?? '';
$params = [];

try {
    $stmt_genres = $pdo->query("SELECT id, nazwa FROM Rodzaj ORDER BY nazwa ASC");
    $all_genres = $stmt_genres->fetchAll();
} catch (PDOException $e) {
    $all_genres = [];
}

try {
    $stmt_authors = $pdo->query("
        SELECT DISTINCT autor 
        FROM Gra 
        WHERE autor IS NOT NULL AND autor != '' 
        ORDER BY autor ASC
    ");
    $all_authors = $stmt_authors->fetchAll();
} catch (PDOException $e) {
    $all_authors = [];
}

try {
    $stmt_dyst = $pdo->query("SELECT id, nazwa FROM Dystrybutor ORDER BY nazwa ASC");
    $all_dyst = $stmt_dyst->fetchAll();
} catch (PDOException $e) {
    $all_dyst = [];
}

$sql = "
    SELECT g.id, g.nazwa, g.cena, g.autor, d.nazwa as dystrybutor,
           STRING_AGG(r.nazwa, ', ') as gatunki
    FROM Gra g
    JOIN Dystrybutor d ON g.dystrybutor = d.id
    LEFT JOIN Gra_Rodzaj gr ON g.id = gr.gra
    LEFT JOIN Rodzaj r ON gr.rodzaj = r.id
    WHERE 1=1
";

$selected_genre = $_GET['genre'] ?? '';
$selected_author = $_GET['author'] ?? '';
$selected_dyst = $_GET['dystrybutor'] ?? '';
$search = $_GET['search'] ?? '';

if ($selected_genre) {
    $sql .= " AND r.id = ?";
    $params[] = $selected_genre;
}

if ($selected_author) {
    $sql .= " AND g.autor = ?";
    $params[] = $selected_author;
}

if ($selected_dyst) {
    $sql .= " AND g.dystrybutor = ?";
    $params[] = $selected_dyst;
}

if ($search) {
    $sql .= " AND g.nazwa ILIKE ?";
    $params[] = "%$search%";
}

$sort_whitelist = [
    'price_asc'  => 'g.cena ASC',       
    'price_desc' => 'g.cena DESC',      
    'name_asc'   => 'g.nazwa ASC',      
    'name_desc'  => 'g.nazwa DESC'      
];

$sort_key = $_GET['sort'] ?? 'name_asc';

if (array_key_exists($sort_key, $sort_whitelist)) {
    $order_by_sql = $sort_whitelist[$sort_key];
} else {
    $order_by_sql = 'g.nazwa ASC';
}

$sql .= " GROUP BY g.id, g.nazwa, g.cena, g.autor, d.nazwa ORDER BY $order_by_sql";

$stmt = $pdo->prepare($sql);
$stmt->execute($params);
$gry = $stmt->fetchAll();

echo "Content-Type: text/html\n\n";
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Sklep gier komputerowych</title>
</head>
<body>
    <header>
        <h1>Katalog gier</h1>
        <div class="header-menu">
    	<?php $count = isset($_SESSION['cart']) ? array_sum($_SESSION['cart']) : 0;
        if (isset($_SESSION['user_id'])): ?>
        	Czesc, <b><?= htmlspecialchars($_SESSION['user_name']) ?></b>!
        	<a href="profile.cgi">Moj profil</a> |
		<a href="cart.cgi" style="font-weight: bold; color: blue;">
        		Koszyk (<?= $count ?>)
    		</a> |
		<a href="logout.cgi">Wylogowac sie</a>
    	<?php else: ?>
        	<a href="login.cgi">Zalogowac sie</a>
    <?php endif; ?>
</div>
    </header>

    <form method="get" style="margin: 20px 0;">
        <input type="text" name="search" placeholder="Wyszukaj gre..." value="<?= htmlspecialchars($search) ?>">
        <button type="submit">Wyszukaj</button>
        <?php if($search): ?><a href="index.cgi">Zresetuj</a><?php endif; ?>
    </form>

   <div class="filters" style="background: #f4f4f4; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
       <form method="get" action="index.cgi" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
        
            <?php if($search): ?>
                <input type="hidden" name="search" value="<?= htmlspecialchars($search) ?>">
            <?php endif; ?>

            <div>
                <label>Rodzaj:</label>
                <select name="genre" onchange="this.form.submit()">
                    <option value="">-- Wszystkie --</option>
                    <?php foreach ($all_genres as $item): ?>
                        <option value="<?= $item['id'] ?>" <?= ($selected_genre == $item['id']) ? 'selected' : '' ?>>
                            <?= htmlspecialchars($item['nazwa']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div>
                <label>Autor:</label>
                <select name="author" onchange="this.form.submit()">
                    <option value="">-- Wszystkie --</option>
                    <?php foreach ($all_authors as $item): ?>
                        <option value="<?= htmlspecialchars($item['autor']) ?>" <?= ($selected_author == $item['autor']) ? 'selected' : '' ?>>
                             <?= htmlspecialchars($item['autor']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

	   <div>
                <label>Dystrybutor:</label>
                <select name="dystrybutor" onchange="this.form.submit()">
                    <option value="">-- Wszystkie --</option>
                    <?php foreach ($all_dyst as $item): ?>
                        <option value="<?= $item['id'] ?>" <?= ($selected_dyst == $item['id']) ? 'selected' : '' ?>>
                             <?= htmlspecialchars($item['nazwa']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

	    <div>
	       <label>Sortowanie:</label>
    		    <select name="sort" onchange="this.form.submit()">
			<option value="">-- Wszystkie --</option>
        		<option value="price_asc" <?= ($_GET['sort'] ?? '') == 'price_asc' ? 'selected' : '' ?>>Najpierw tansze</option>
        		<option value="price_desc" <?= ($_GET['sort'] ?? '') == 'price_desc' ? 'selected' : '' ?>>Najpierw drozsze</option>
        		<option value="name_asc" <?= ($_GET['sort'] ?? '') == 'name_asc' ? 'selected' : '' ?>>Za nazwa (A-Z)</option>
			<option value="name_desc" <?= ($_GET['sort'] ?? '') == 'name_desc' ? 'selected' : '' ?>>Za nazwa (Z-A)</option>
    		    </select>
	    </div>
        
            <?php if($selected_genre || $selected_author || $selected_dyst || $search || $sort_key): ?>
                <a href="index.cgi" style="color: red; text-decoration: none;">Zresetowac</a>
            <?php endif; ?>
        
            <noscript><button type="submit">Zastosowac</button></noscript>
        </form>
   </div>

    <table border="1" cellpadding="10" cellspacing="0">
        <thead>
            <tr>
                <th>Nazwa</th>
                <th>Rodzaje</th>
		<th>Autor</th>
                <th>Dystrybutor</th>
                <th>Cena</th>
                <th>Akcja</th> </tr>
        </thead>
        <tbody>
            <?php foreach ($gry as $gra): ?>
            <tr>
                <td><?= htmlspecialchars($gra['nazwa']) ?></td>
                <td><?= htmlspecialchars($gra['gatunki']) ?></td>
		<td><?= htmlspecialchars($gra['autor']) ?></td>
                <td><?= htmlspecialchars($gra['dystrybutor']) ?></td>
                <td><?= number_format($gra['cena'], 2) ?> PLN</td>
                <td>
                    <form action="add_to_cart.cgi" method="POST">
        	    <input type="hidden" name="game_id" value="<?= $gra['id'] ?>">
        	    <button type="submit">Dodac do koszyku</button>
    		    </form>
                </td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</body>
</html>
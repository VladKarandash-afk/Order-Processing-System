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

if (!isset($_SESSION['user_role']) || $_SESSION['user_role'] !== 'admin') {
    echo "Status: 302 Found\n";
    echo "Location: login.cgi\n\n";
    exit;
}

$message = '';
$params = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $fh = file_get_contents("php://stdin");
    parse_str($fh, $_POST);

    $action = $_POST['action'] ?? '';

    if ($action === 'delete_game') {
        $id = $_POST['id'];
	try {
        $pdo->prepare("DELETE FROM Gra WHERE id = ?")->execute([$id]);
        $message = "Gra zostala usunieta";
	} catch (Exception $e) {
	    $message = "Podczas usuwania gry wystapil blad: " . e->getMessage();
	}
    }

    if ($action === 'save_game') {
        $id = $_POST['id'] ?? '';
        $name = $_POST['nazwa'];
	$author = $_POST['autor'];
        $price = $_POST['cena'];
        $genres = $_POST['genres'] ?? [];
	$dist = $_POST['dystrybutor'];

        if (empty($genres)) {
            die("Blad: musisz wybrac co najmniej jeden rodzaj!");
        }

	try{

	    $pdo -> beginTransaction();

            if ($id) {
                $stmt = $pdo->prepare("UPDATE Gra SET nazwa=?, autor=?, cena=?, dystrybutor=? WHERE id=?");
                $stmt->execute([$name, $author, $price, $dist, $id]);
                
                $pdo->prepare("DELETE FROM Gra_rodzaj WHERE gra=?")->execute([$id]);
            } else {
                $stmt = $pdo->prepare("INSERT INTO Gra (nazwa, autor, cena, dystrybutor) VALUES (?, ?, ?, ?) RETURNING id");
                $stmt->execute([$name, $author, $price, $dist]);
                $id = $stmt->fetchColumn();
            }

            $insert_genre = $pdo->prepare("INSERT INTO Gra_rodzaj (gra, rodzaj) VALUES (?, ?)");
            foreach ($genres as $gid) {
                $insert_genre->execute([$id, $gid]);
            }

            $pdo->commit();
            
            $message = "Dane gry zostaly poprawnie zmnienione!";

        } catch (Exception $e) {
            $pdo->rollBack();
            $message = "Podczas zmiany danych gry wystapil blad: " . $e->getMessage();
        }
    }
    
    if ($action === 'delete_key') {
        $id = $_POST['id'];
        $pdo->prepare("DELETE FROM Kopia_gry WHERE id = ?")->execute([$id]);
        $message = "Klucz zostal usuniety";
    }

    if ($action === 'save_key') {
        $id = $_POST['id'] ?? '';
        $key = $_POST['klucz_aktywacji'];
        $game = $_POST['gra'];
        $state = $_POST['status'];

        $client = empty($_POST['klient']) ? null : $_POST['klient'];

	try {
        if ($id) {
            $stmt = $pdo->prepare("UPDATE Kopia_gry SET klucz_aktywacji=?, gra=?, status=?, klient=? WHERE id=?");
            $stmt->execute([$key, $game, $state, $client, $id]);
        } else {
            $stmt = $pdo->prepare("INSERT INTO Kopia_gry (klucz_aktywacji, gra, status, klient) VALUES (?, ?, ?, ?)");
            $stmt->execute([$key, $game, $state, $client]);
        }
        
        $message = "Dane klucza zostale poprawnie zmienione!";
	} catch (Exception $e) {
	    $message = "Podczas zapisu zmian danych klucza wystapil blad: " . e->getMessage();
	}
    }

    if ($action === 'delete_genre') {
        $id = $_POST['id'];
	try {
        $pdo->prepare("DELETE FROM Rodzaj WHERE id = ?")->execute([$id]);
        $message = "Rodzaj zostal usuniety";
	} catch (PDOException $e) {
	    $message = "Podczas usuwania rodzaju wystapil blad: " . $e->getMessage();
	}
    }

    if ($action === 'save_genre') {
        $id = $_POST['id'] ?? '';
        $name = $_POST['nazwa'];

	try {
        if ($id) {
            $stmt = $pdo->prepare("UPDATE Rodzaj SET nazwa=? WHERE id=?");
            $stmt->execute([$name, $id]);
        } else {
            $stmt = $pdo->prepare("INSERT INTO Rodzaj (nazwa) VALUES (?)");
            $stmt->execute([$name]);
        }
        
        $message = "Dane rodzaju zostale poprawnie zmienione!";
	} catch (Exception $e) {
	    $message = "Podczas zapisu zmian danych rodzaju wystapil blad: " . e->getMessage();
	}
    }

    if ($action === 'delete_user') {
        $id = $_POST['id'];
	try {
        $pdo->prepare("DELETE FROM Klient WHERE id = ?")->execute([$id]);
        $message = "Klient zostal usuniety";
	} catch (Exception $e) {
	    $message = "Podczas usuwania klienta wystapil blad: " . e->getMessage();
	}
    }

    if ($action === 'update_order_status') {
        $id = $_POST['id'];
        $new_status = $_POST['status'];
        
        try {
            $stmt = $pdo->prepare("UPDATE Zamowienie SET status = ? WHERE id = ?");
            $stmt->execute([$new_status, $id]);
            $message = "Status zamowienia #$id zostal zmieniony na '$new_status'";
        } catch (PDOException $e) {
            $message = "Blad zmiany statusu: " . $e->getMessage();
        }
    }

   if ($action === 'delete_dyst') {
        $id = $_POST['id'];
	try {
        $pdo->prepare("DELETE FROM Dystrybutor WHERE id = ?")->execute([$id]);
        $message = "Dystrybutor zostal usuniety";
	} catch (Exception $e) {
	    $message = "Podczas usuwania dystrybutora wystapil blad: " . e->getMessage();
	}
    }

    if ($action === 'save_dyst') {
        $id = $_POST['id'] ?? '';
        $name = $_POST['nazwa'];
        $email = $_POST['mail'];

	try {
        if ($id) {
            $stmt = $pdo->prepare("UPDATE Dystrybutor SET nazwa=?, email=? WHERE id=?");
            $stmt->execute([$name, $email, $id]);
        } else {
            $stmt = $pdo->prepare("INSERT INTO Dystrybutor (nazwa, email) VALUES (?, ?)");
            $stmt->execute([$name, $email]);
        }
        
        $message = "Dane dystrybutora zostale poprawnie zmienione!";
	} catch (Exception $e) {
	    $message = "Podczas zapisu zmian danych dystrybutora wystapil blad: " . e->getMessage();
	}
    }
}

if (isset($_SERVER['QUERY_STRING'])) {
	parse_str($_SERVER['QUERY_STRING'], $_GET);
}

$section = $_GET['section'] ?? 'games';
$edit_id = $_GET['edit'] ?? null;      

$data_list = [];
if ($section == 'games') {
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
    	$data_list = $stmt->fetchAll();
    
    	$all_genres = $pdo->query("SELECT * FROM Rodzaj ORDER BY nazwa")->fetchAll();
    
    	$edit_data = [];
    	$current_genres = [];
    	if ($edit_id) {
        $stmt = $pdo->prepare("SELECT * FROM Gra WHERE id = ?");
        $stmt->execute([$edit_id]);
        $edit_data = $stmt->fetch();
        
        $stmt_g = $pdo->prepare("SELECT rodzaj FROM Gra_rodzaj WHERE gra = ?");
        $stmt_g->execute([$edit_id]);
        $current_genres = $stmt_g->fetchAll(PDO::FETCH_COLUMN);
    }
}

elseif ($section == 'keys') {
	$sql = "
    	SELECT k.id, k.klucz_aktywacji, k.status, g.nazwa as gra_naz,
           kl.imie as klient_im, kl.nazwisko as klient_na
    	FROM Kopia_gry k
    	JOIN Gra g ON k.gra = g.id
    	LEFT JOIN Klient kl ON k.klient = kl.id
    	WHERE 1=1
	";

	$selected_state = $_GET['state'] ?? '';
	$search = $_GET['search'] ?? '';

	if ($selected_state) {
    	$sql .= " AND k.status = ?";
    	$params[] = $selected_state;
	}

	if ($search) {
    	$sql .= " AND g.nazwa ILIKE ?";
    	$params[] = "%$search%";
	}

	$sort_whitelist = [    
    	'name_asc'   => 'g.nazwa ASC',      
    	'name_desc'  => 'g.nazwa DESC',
    	'surname_asc'   => 'kl.nazwisko ASC',      
    	'surname_desc'  => 'kl.nazwisko DESC'      
	];

	$sort_key = $_GET['sort'] ?? 'name_asc';
	
	if (array_key_exists($sort_key, $sort_whitelist)) {
    	$order_by_sql = $sort_whitelist[$sort_key];
	} else {
    	$order_by_sql = 'g.nazwa ASC';
	}

	$sql .= " GROUP BY k.id, k.klucz_aktywacji, k.status, g.nazwa, kl.imie, kl.nazwisko ORDER BY $order_by_sql";
    	$stmt = $pdo->prepare($sql);
	$stmt->execute($params);
    	$data_list = $stmt->fetchAll();
    
    	$edit_data = [];
    	if ($edit_id) {
        $stmt = $pdo->prepare("SELECT * FROM Kopia_gry WHERE id = ?");
        $stmt->execute([$edit_id]);
        $edit_data = $stmt->fetch();
    }
}

elseif ($section == 'genres') {
	$sql = "
    	SELECT r.id, r.nazwa
    	FROM Rodzaj r
	";

	$search = $_GET['search'] ?? '';

	if ($search) {
    	$sql .= " WHERE r.nazwa ILIKE ?";
    	$params[] = "%$search%";
	}

	$sort_whitelist = [    
    	'name_asc'   => 'r.nazwa ASC',      
    	'name_desc'  => 'r.nazwa DESC',    
	];

	$sort_key = $_GET['sort'] ?? 'name_asc';
	
	if (array_key_exists($sort_key, $sort_whitelist)) {
    	$order_by_sql = $sort_whitelist[$sort_key];
	} else {
    	$order_by_sql = 'g.nazwa ASC';
	}

	$sql .= " ORDER BY $order_by_sql";
    	$stmt = $pdo->prepare($sql);
	$stmt->execute($params);
    	$data_list = $stmt->fetchAll();
    
    	$edit_data = [];
    	if ($edit_id) {
        $stmt = $pdo->prepare("SELECT * FROM Rodzaj WHERE id = ?");
        $stmt->execute([$edit_id]);
        $edit_data = $stmt->fetch();
    }
}

elseif ($section == 'users') {
	$sql = "
    	SELECT k.id, k.imie, k.nazwisko, k.mail, k.telefon
    	FROM Klient k
	";

	$search_client = trim($_GET['search'] ?? '');

    	if ($search_client) {
             $sql .= " WHERE (
                (k.imie || ' ' || k.nazwisko) ILIKE ? 
                OR 
                (k.nazwisko || ' ' || k.imie) ILIKE ?
                OR
                k.mail ILIKE ?
            )";

            $term = "%$search_client%";
            $params[] = $term;
            $params[] = $term;
            $params[] = $term;
    	}

	$sort_whitelist = [    
    	'name_asc'   => 'k.nazwisko ASC',      
    	'name_desc'  => 'k.nazwisko DESC',    
	];

	$sort_key = $_GET['sort'] ?? 'name_asc';
	
	if (array_key_exists($sort_key, $sort_whitelist)) {
    	$order_by_sql = $sort_whitelist[$sort_key];
	} else {
    	$order_by_sql = 'k.nazwisko ASC';
	}

	$sql .= " ORDER BY $order_by_sql";
    	$stmt = $pdo->prepare($sql);
	$stmt->execute($params);
    	$data_list = $stmt->fetchAll();
    
    	$edit_data = [];
    	if ($edit_id) {
        $stmt = $pdo->prepare("SELECT * FROM Klient WHERE id = ?");
        $stmt->execute([$edit_id]);
        $edit_data = $stmt->fetch();
	}
}

elseif ($section == 'orders') {
    $sort_whitelist = [      
    'name_asc'   => 'g.nazwa ASC',      
    'name_desc'  => 'g.nazwa DESC',
    'surname_asc'   => 'k.nazwisko ASC',      
    'surname_desc'  => 'k.nazwisko DESC',
    'data_asc'   => 'z.data ASC',
    'data_desc'  => 'z.data DESC',
    'status'     => 'z.status ASC'    
];

$sort_key = $_GET['sort'] ?? 'surname_asc';

if (array_key_exists($sort_key, $sort_whitelist)) {
    $order_by_sql = $sort_whitelist[$sort_key];
} else {
    $order_by_sql = 'k.nazwisko ASC';
}

$sql = "
    SELECT z.id, z.data, z.status, k.imie, k.nazwisko,
           g.nazwa, pz.ilosc, pz.cena_historyczna
    FROM Zamowienie z
    JOIN Pozycja_zamowienia pz ON z.id = pz.zamowienie
    JOIN Gra g ON pz.gra = g.id
    JOIN Klient k ON z.klient = k.id
    WHERE 1=1
";

    $selected_state = $_GET['state'] ?? '';

    if ($selected_state) {
        $sql .= " AND z.status = ?";
    	$params[] = $selected_state;
    }

$search_client = trim($_GET['search'] ?? '');

    	if ($search_client) {
             $sql .= " AND (
                (k.imie || ' ' || k.nazwisko) ILIKE ? 
                OR 
                (k.nazwisko || ' ' || k.imie) ILIKE ?
                OR
                k.mail ILIKE ?
            )";

            $term = "%$search_client%";
            $params[] = $term;
            $params[] = $term;
            $params[] = $term;
    	}

$sql .= " ORDER BY $order_by_sql";


$stmt = $pdo->prepare($sql);
$stmt->execute($params);
$raw_rows = $stmt->fetchAll();

$grouped_orders = [];

foreach ($raw_rows as $row) {
    $order_id = $row['id'];
    
    if (!isset($grouped_orders[$order_id])) {
        $grouped_orders[$order_id] = [
            'id' => $row['id'],
            'data' => $row['data'],
            'status' => $row['status'],
            'imie' => $row['imie'],
            'nazwisko' => $row['nazwisko'],
            'games' => [],
            'suma' => 0
        ];
    }
    
    $grouped_orders[$order_id]['games'][] = [
        'nazwa' => $row['nazwa'],
        'ilosc' => $row['ilosc'],
        'cena' => $row['cena_historyczna']
    ];

    $grouped_orders[$order_id]['suma'] += $row['ilosc'] * $row['cena_historyczna'];
}

}

if ($section == 'dyst') {
	$sql = "
    	SELECT d.id, d.nazwa, d.email,
           STRING_AGG(g.nazwa, '|||') as lista_gier
    	FROM Dystrybutor d
    	LEFT JOIN Gra g ON g.dystrybutor = d.id
	";

	$search = $_GET['search'] ?? '';

	if ($search) {
    	$sql .= " WHERE d.nazwa ILIKE ?";
    	$params[] = "%$search%";
	}

	$sort_whitelist = [  
    	'name_asc'   => 'd.nazwa ASC',      
    	'name_desc'  => 'd.nazwa DESC'      
	];

	$sort_key = $_GET['sort'] ?? 'name_asc';
	
	if (array_key_exists($sort_key, $sort_whitelist)) {
    	$order_by_sql = $sort_whitelist[$sort_key];
	} else {
    	$order_by_sql = 'd.nazwa ASC';
	}

	$sql .= " GROUP BY d.id, d.nazwa, d.email ORDER BY $order_by_sql";
    	$stmt = $pdo->prepare($sql);
	$stmt->execute($params);
    	$data_list = $stmt->fetchAll();
    
    	$edit_data = [];
    	if ($edit_id) {
        $stmt = $pdo->prepare("SELECT * FROM Dystrybutor WHERE id = ?");
        $stmt->execute([$edit_id]);
        $edit_data = $stmt->fetch();
    }
}

$distributors = $pdo->query("SELECT id, nazwa FROM Dystrybutor")->fetchAll();
$genres = $pdo->query("SELECT id, nazwa FROM Rodzaj")->fetchAll();

$games = $pdo->query("SELECT id, nazwa, cena FROM Gra ORDER BY id DESC")->fetchAll();

$clients = $pdo->query("SELECT id, imie, nazwisko FROM Klient ORDER BY id DESC")->fetchAll();

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

$states = [
    ['status' => 'dostepna'],
    ['status' => 'zarezerwowana'],
    ['status' => 'wyprzedana']
];

echo "Content-type: text/html\n\n";
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Panel administracyjny</title>
</head>
<body>
<nav>
    <h1>Admin Panel</h1>
    <a href="?section=games" class="<?= $section=='games'?'active':'' ?>">Gry</a>
    <a href="?section=keys" class="<?= $section=='keys'?'active':'' ?>">Klucze</a>
    <a href="?section=genres" class="<?= $section=='genres'?'active':'' ?>">Rodzaje</a>
    <a href="?section=users" class="<?= $section=='users'?'active':'' ?>">Klienci</a>
    <a href="?section=orders" class="<?= $section=='orders'?'active':'' ?>">Zamowienia</a>
    <a href="?section=dyst" class="<?= $section=='dyst'?'active':'' ?>">Dystrybutorzy</a>
    <hr>
    <a href="index.cgi">Powrot do sklepu</a>
    <a href="logout.cgi">Wylogowac sie</a>
</nav>

<main>
    <h2>Kierowanie sklepem: <?= ucfirst($section) ?></h2>
    
    <?php if($message): ?>
        <p style="color:green; font-weight:bold"><?= $message ?></p>
    <?php endif; ?>

    <?php if ($section == 'games'): ?>
        
        <div class="form-box">
            <h3><?= $edit_id ? 'Redagowac gre' : 'Dodac nowa gre' ?></h3>
            <form method="post" action="?section=games">
                <input type="hidden" name="action" value="save_game">
                <?php if($edit_id): ?>
                    <input type="hidden" name="id" value="<?= $edit_data['id'] ?>">
                <?php endif; ?>

                <label>Nazwa:</label><br>
                <input type="text" name="nazwa" value="<?= $edit_data['nazwa'] ?? '' ?>" required style="width:50%"><br><br>

		<label>Autor:</label><br>
                <input type="text" name="autor" value="<?= $edit_data['autor'] ?? '' ?>" required style="width:50%"><br><br>

                <label>Cena:</label><br>
                <input type="number" step="0.01" name="cena" value="<?= $edit_data['cena'] ?? '' ?>" required><br><br>

                <label>Rodzaje (Wcisnij CTRL do wielokrotnego wyboru):</label><br>
                <select name="genres[]" multiple>
                    <?php foreach($all_genres as $g): ?>
                        <option value="<?= $g['id'] ?>" 
                            <?= (isset($current_genres) && in_array($g['id'], $current_genres)) ? 'selected' : '' ?>>
                            <?= htmlspecialchars($g['nazwa']) ?>
                        </option>
                    <?php endforeach; ?>
                </select><br><br>
		
		<label>Dystrybutor:</label><br>
            	    <select name="dystrybutor">
                	<?php foreach($distributors as $d): ?>
                    	    <option value="<?= $d['id'] ?>"><?= htmlspecialchars($d['nazwa']) ?></option>
                	<?php endforeach; ?>
                </select><br><br>

                <button type="submit" class="btn">Zatwierdz</button>
                <a href="?section=games" class="btn" style="background:#777">Zresetuj</a>
            </form>
        </div>

	</div>

    <h3>Kierowanie grami</h3>

    <form method="get" style="margin: 20px 0;">
	<input type="hidden" name="section" value="games">
        <input type="text" name="search" placeholder="Wyszukaj gre..." value="<?= htmlspecialchars($search) ?>">
        <button type="submit">Wyszukaj</button>
        <?php if($search): ?><a href="?section=games">Zresetuj</a><?php endif; ?>
    </form>

   <div class="filters" style="background: #f4f4f4; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
       <form method="get" action="admin.cgi" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
	    <input type="hidden" name="section" value="games">
        
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
                    <?php foreach ($distributors as $item): ?>
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
                <a href="?section=games" style="color: red; text-decoration: none;">Zresetowac</a>
            <?php endif; ?>
        
            <noscript><button type="submit">Zastosowac</button></noscript>
        </form>
   </div>

        <table border="1" cellpadding="10" cellspacing="0">
	    <thead>
               <tr><th>ID</th><th>Nazwa</th><th>Autor</th><th>Cena</th><th>Dystrybutor</th><th>Rodzaje</th><th>Akcja</th></tr>
            </thead>
	    <tbody>
	       <?php foreach($data_list as $row): ?>
               <tr>
                    <td><?= $row['id'] ?></td>
                    <td><?= htmlspecialchars($row['nazwa']) ?></td>
		    <td><?= htmlspecialchars($row['autor']) ?></td>
                    <td><?= $row['cena'] ?> PLN</td>
		    <td><?= htmlspecialchars($row['dystrybutor']) ?></td>
		    <td><?= htmlspecialchars($row['gatunki']) ?></td>
                    <td>
                        <a href="?section=games&edit=<?= $row['id'] ?>" class="btn">Edytowac</a>
                    
                        <form method="post" style="display:inline" onsubmit="return confirm('Usunac?');">
                            <input type="hidden" name="action" value="delete_game">
                            <input type="hidden" name="id" value="<?= $row['id'] ?>">
                            <button type="submit" class="btn btn-danger">Usunac</button>
                        </form>
                   </td>
                </tr>
                <?php endforeach; ?>
	    </tbody>
        </table>
    <?php endif; ?>

    <?php if ($section == 'keys'): ?>

	<div class="form-box">
            <h3><?= $edit_id ? 'Redagowac klucz' : 'Dodac nowy klucz' ?></h3>
            <form method="post" action="?section=keys">
                <input type="hidden" name="action" value="save_key">
                <?php if($edit_id): ?>
                    <input type="hidden" name="id" value="<?= $edit_data['id'] ?>">
                <?php endif; ?>

                <label>Klucz aktywacji:</label><br>
                <input type="text" name="klucz_aktywacji" value="<?= $edit_data['klucz_aktywacji'] ?? '' ?>" required style="width:50%"><br><br>
		
		<label>Gra:</label><br>
            	    <select name="gra">
                	<?php foreach($games as $g): ?>
                    	    <option value="<?= $g['id'] ?>"><?= htmlspecialchars($g['nazwa']) ?></option>
                	<?php endforeach; ?>
                </select><br><br>

		<label>Status:</label><br>
            	    <select name="status">
                	<?php foreach($states as $s): ?>
                    	    <option value="<?= $s['status'] ?>"><?= $s['status'] ?></option>
                	<?php endforeach; ?>
                </select><br><br>

		<label>Klient:</label><br>
            	    <select name="klient">
			<option value="">Nie ma klienta</option>
                	<?php foreach($clients as $c): ?>
                    	    <option value="<?= $c['id'] ?>"><?= htmlspecialchars($c['imie']) ?> <?= htmlspecialchars($c['nazwisko']) ?></option>
                	<?php endforeach; ?>
                </select><br><br>

                <button type="submit" class="btn">Zatwierdz</button>
                <a href="?section=keys" class="btn" style="background:#777">Zresetuj</a>
            </form>
        </div>

    <h3>Kierowanie kluczami</h3>

    <form method="get" style="margin: 20px 0;">
	<input type="hidden" name="section" value="keys">
        <input type="text" name="search" placeholder="Wyszukaj gre..." value="<?= htmlspecialchars($search) ?>">
        <button type="submit">Wyszukaj</button>
        <?php if($search): ?><a href="?section=keys">Zresetuj</a><?php endif; ?>
    </form>

   <div class="filters" style="background: #f4f4f4; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
       <form method="get" action="admin.cgi" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
	    <input type="hidden" name="section" value="keys">
        
            <?php if($search): ?>
                <input type="hidden" name="search" value="<?= htmlspecialchars($search) ?>">
            <?php endif; ?>

            <div>
                <label>Status:</label>
                <select name="state" onchange="this.form.submit()">
                    <option value="">-- Wszystkie --</option>
                    <?php foreach ($states as $item): ?>
                        <option value="<?= htmlspecialchars($item['status']) ?>" <?= ($selected_state == $item['status']) ? 'selected' : '' ?>>
                             <?= htmlspecialchars($item['status']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

	    <div>
	       <label>Sortowanie:</label>
    		    <select name="sort" onchange="this.form.submit()">
			<option value="">-- Wszystkie --</option>
        		<option value="name_asc" <?= ($_GET['sort'] ?? '') == 'name_asc' ? 'selected' : '' ?>>Za nazwa gry (A-Z)</option>
			<option value="name_desc" <?= ($_GET['sort'] ?? '') == 'name_desc' ? 'selected' : '' ?>>Za nazwa gry (Z-A)</option>
			<option value="surname_asc" <?= ($_GET['sort'] ?? '') == 'surname_asc' ? 'selected' : '' ?>>Za nazwiskiem klienta (A-Z)</option>
			<option value="surname_desc" <?= ($_GET['sort'] ?? '') == 'surname_desc' ? 'selected' : '' ?>>Za nazwiskiem klienta (Z-A)</option>
    		    </select>
	    </div>
        
            <?php if($selected_state || $search || $sort_key): ?>
                <a href="?section=keys" style="color: red; text-decoration: none;">Zresetowac</a>
            <?php endif; ?>
        
            <noscript><button type="submit">Zastosowac</button></noscript>
        </form>
   </div>

        <table border="1" cellpadding="10" cellspacing="0">
	    <thead>
            <tr><th>ID</th><th>Gra</th><th>Klucz_aktywacji</th><th>Status</th><th>Klient</th><th>Akcja</th></tr>
	    </thead>
	    <tbody>
            <?php foreach($data_list as $row): ?>
            <tr>
                <td><?= $row['id'] ?></td>
                <td><?= htmlspecialchars($row['gra_naz']) ?></td>
                <td><?= htmlspecialchars($row['klucz_aktywacji']) ?></td>
		<td><?= htmlspecialchars($row['status']) ?></td>
		<td><?= htmlspecialchars($row['klient_im']) ?> <?= htmlspecialchars($row['klient_na']) ?></td>
                <td>
                    <a href="?section=keys&edit=<?= $row['id'] ?>" class="btn">Edytowac</a>
                    
                    <form method="post" style="display:inline" onsubmit="return confirm('Usunac?');">
                        <input type="hidden" name="action" value="delete_key">
                        <input type="hidden" name="id" value="<?= $row['id'] ?>">
                        <button type="submit" class="btn btn-danger">Usunac</button>
                    </form>
                </td>
            </tr>
            <?php endforeach; ?>
	    </tbody>
        </table>
    <?php endif; ?>

    <?php if ($section == 'genres'): ?>

	<div class="form-box">
            <h3><?= $edit_id ? 'Redagowac rodzaj' : 'Dodac nowy rodzaj' ?></h3>
            <form method="post" action="?section=genres">
                <input type="hidden" name="action" value="save_genre">
                <?php if($edit_id): ?>
                    <input type="hidden" name="id" value="<?= $edit_data['id'] ?>">
                <?php endif; ?>

                <label>Nazwa:</label><br>
                <input type="text" name="nazwa" value="<?= $edit_data['nazwa'] ?? '' ?>" required style="width:50%"><br><br>

                <button type="submit" class="btn">Zatwierdz</button>
                <a href="?section=genres" class="btn" style="background:#777">Zresetuj</a>
            </form>
        </div>

    <h3>Kierowanie rodzajami</h3>

    <form method="get" style="margin: 20px 0;">
	<input type="hidden" name="section" value="genres">
        <input type="text" name="search" placeholder="Imie, nazwisko lub mail..." value="<?= htmlspecialchars($search) ?>">
        <button type="submit">Wyszukaj</button>
        <?php if($search): ?><a href="?section=genres">Zresetuj</a><?php endif; ?>
    </form>

   <div class="filters" style="background: #f4f4f4; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
       <form method="get" action="admin.cgi" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
	    <input type="hidden" name="section" value="genres">
        
            <?php if($search): ?>
                <input type="hidden" name="search" value="<?= htmlspecialchars($search) ?>">
            <?php endif; ?>

	    <div>
	       <label>Sortowanie:</label>
    		    <select name="sort" onchange="this.form.submit()">
			<option value="">-- Wszystkie --</option>
        		<option value="name_asc" <?= ($_GET['sort'] ?? '') == 'name_asc' ? 'selected' : '' ?>>Za nazwa (A-Z)</option>
			<option value="name_desc" <?= ($_GET['sort'] ?? '') == 'name_desc' ? 'selected' : '' ?>>Za nazwa (Z-A)</option>
    		    </select>
	    </div>
        
            <?php if($search || $sort_key): ?>
                <a href="?section=genres" style="color: red; text-decoration: none;">Zresetowac</a>
            <?php endif; ?>
        
            <noscript><button type="submit">Zastosowac</button></noscript>
        </form>
   </div>

        <table border="1" cellpadding="10" cellspacing="0">
	    <thead>
            <tr><th>ID</th><th>Nazwa</th><th>Akcja</th></tr>
	    </thead>
	    <tbody>
            <?php foreach($data_list as $row): ?>
            <tr>
                <td><?= $row['id'] ?></td>
                <td><?= htmlspecialchars($row['nazwa']) ?></td>
                <td>
                    <a href="?section=genres&edit=<?= $row['id'] ?>" class="btn">Edytowac</a>
                    
                    <form method="post" style="display:inline" onsubmit="return confirm('Usunac?');">
                        <input type="hidden" name="action" value="delete_genre">
                        <input type="hidden" name="id" value="<?= $row['id'] ?>">
                        <button type="submit" class="btn btn-danger">Usunac</button>
                    </form>
                </td>
            </tr>
            <?php endforeach; ?>
	    </tbody>
        </table>
    <?php endif; ?>

    <?php if ($section == 'users'): ?>
    <form method="get" style="margin: 20px 0;">
	<input type="hidden" name="section" value="users">
        <input type="text" name="search" placeholder="Wyszukaj uzytkownika..." value="<?= htmlspecialchars($search) ?>">
        <button type="submit">Wyszukaj</button>
        <?php if($search): ?><a href="?section=users">Zresetuj</a><?php endif; ?>
    </form>

   <div class="filters" style="background: #f4f4f4; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
       <form method="get" action="admin.cgi" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
	    <input type="hidden" name="section" value="users">
        
            <?php if($search): ?>
                <input type="hidden" name="search" value="<?= htmlspecialchars($search) ?>">
            <?php endif; ?>

	    <div>
	       <label>Sortowanie:</label>
    		    <select name="sort" onchange="this.form.submit()">
			<option value="">-- Wszystkie --</option>
        		<option value="name_asc" <?= ($_GET['sort'] ?? '') == 'name_asc' ? 'selected' : '' ?>>Za nazwiskiem (A-Z)</option>
			<option value="name_desc" <?= ($_GET['sort'] ?? '') == 'name_desc' ? 'selected' : '' ?>>Za nazwiskiem (Z-A)</option>
    		    </select>
	    </div>
        
            <?php if($search || $sort_key): ?>
                <a href="?section=users" style="color: red; text-decoration: none;">Zresetowac</a>
            <?php endif; ?>
        
            <noscript><button type="submit">Zastosowac</button></noscript>
        </form>
   </div>
        <table border="1" cellpadding="10" cellspacing="0">
	    <thead>
            <tr><th>ID</th><th>Imie</th><th>Nazwisko</th><th>Email</th><th>Telefon</th><th>Akcja</th></tr>
	    </thead>
	    <tbody>
            <?php foreach($data_list as $row): ?>
            <tr>
                <td><?= $row['id'] ?></td>
                <td><?= htmlspecialchars($row['imie']) ?></td>
		<td><?= htmlspecialchars($row['nazwisko']) ?></td>
                <td><?= htmlspecialchars($row['mail']) ?></td>
                <td><?= htmlspecialchars($row['telefon']) ?></td>
                <td>
                    <form method="post" style="display:inline" onsubmit="return confirm('Usunac?');">
                        <input type="hidden" name="action" value="delete_user">
                        <input type="hidden" name="id" value="<?= $row['id'] ?>">
                        <button type="submit" class="btn btn-danger">Usunac</button>
                    </form>
                </td>
            </tr>
            <?php endforeach; ?>
	    </tbody>
        </table>
    <?php endif; ?>

    <?php if ($section == 'orders'): ?>
        <h3>Lista zamowien</h3>

    <form method="get" style="margin: 20px 0;">
	<input type="hidden" name="section" value="orders">
        <input type="text" name="search" placeholder="Imie, nazwisko lub email klienta..." value="<?= htmlspecialchars($search) ?>">
        <button type="submit">Wyszukaj</button>
        <?php if($search): ?><a href="?section=orders">Zresetuj</a><?php endif; ?>
    </form>


   <div class="filters" style="background: #f4f4f4; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
       <form method="get" action="admin.cgi" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
	    <input type="hidden" name="section" value="orders">
        
            <?php if($search): ?>
                <input type="hidden" name="search" value="<?= htmlspecialchars($search) ?>">
            <?php endif; ?>

            <div>
                <label>Status:</label>
                <select name="state" onchange="this.form.submit()">
                    <option value="">-- Wszystkie --</option>
                    <?php foreach ($states as $item): ?>
                        <option value="<?= htmlspecialchars($item['status']) ?>" <?= ($selected_state == $item['status']) ? 'selected' : '' ?>>
                             <?= htmlspecialchars($item['status']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

	    <div>
	       <label>Sortowanie:</label>
    		    <select name="sort" onchange="this.form.submit()">
			<option value="">-- Wszystkie --</option>
        		<option value="name_asc" <?= ($_GET['sort'] ?? '') == 'name_asc' ? 'selected' : '' ?>>Za nazwa gry (A-Z)</option>
			<option value="name_desc" <?= ($_GET['sort'] ?? '') == 'name_desc' ? 'selected' : '' ?>>Za nazwa gry (Z-A)</option>
			<option value="surname_asc" <?= ($_GET['sort'] ?? '') == 'surname_asc' ? 'selected' : '' ?>>Za nazwiskiem klienta (A-Z)</option>
			<option value="surname_desc" <?= ($_GET['sort'] ?? '') == 'surname_desc' ? 'selected' : '' ?>>Za nazwiskiem klienta (Z-A)</option>
	       		<option value="data_asc" <?= ($_GET['sort'] ?? '') == 'data_asc' ? 'selected' : '' ?>>Najpierw wczesniejsze</option>
	       		<option value="data_desc" <?= ($_GET['sort'] ?? '') == 'data_desc' ? 'selected' : '' ?>>Najpierw nowsze</option>
    		    </select>
	    </div>
        
            <?php if($selected_state || $search || $sort_key): ?>
                <a href="?section=orders" style="color: red; text-decoration: none;">Zresetowac</a>
            <?php endif; ?>
        
            <noscript><button type="submit">Zastosowac</button></noscript>
        </form>
   </div>
        <table border="1" cellpadding="10" cellspacing="0">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Data</th>
                    <th>Klient</th>
		    <th>Gry</th>
		    <th>Suma</th>
                    <th>Status</th>
                    <th>Akcja</th>
                </tr>
            </thead>
            <tbody>
            <?php foreach($grouped_orders as $order): ?>
                <tr>
                    <td><?= $order['id'] ?></td>
                    <td><?= $order['data'] ?></td>
                    <td>
                        <?= htmlspecialchars($order['imie']) ?> <?= htmlspecialchars($order['nazwisko']) ?>
                    </td>
                    <td>
            		<?php foreach ($order['games'] as $game): ?>
                	    <div> <?= htmlspecialchars($game['nazwa']) ?> (<?= $game['ilosc'] ?> szt.)</div>
            		<?php endforeach; ?>
        	    </td>
		    <td><?= $order['suma'] ?></td>
                    
                    <form method="post" action="?section=orders">
                        <input type="hidden" name="action" value="update_order_status">
                        <input type="hidden" name="id" value="<?= $order['id'] ?>">
                        
                        <td>
                            <select name="status">
                                <?php 
                                $order_statuses = ['nieoplacone', 'oplacone', 'zrealizowane', 'anulowane'];
                                foreach($order_statuses as $st): 
                                ?>
                                    <option value="<?= $st ?>" <?= $order['status'] == $st ? 'selected' : '' ?>>
                                        <?= ucfirst($st) ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </td>
                        <td>
                            <button type="submit" class="btn">Zmienic status</button>
                        </td>
                    </form>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    <?php endif; ?>

    <?php if ($section == 'dyst'): ?>
        
        <div class="form-box">
            <h3><?= $edit_id ? 'Redagowac dystrybutora' : 'Dodac nowego dystrybutora' ?></h3>
            <form method="post" action="?section=dyst">
                <input type="hidden" name="action" value="save_dyst">
                <?php if($edit_id): ?>
                    <input type="hidden" name="id" value="<?= $edit_data['id'] ?>">
                <?php endif; ?>

                <label>Nazwa:</label><br>
                <input type="text" name="nazwa" value="<?= $edit_data['nazwa'] ?? '' ?>" required style="width:50%"><br><br>

		<label>Mail:</label><br>
                <input type="text" name="mail" value="<?= $edit_data['mail'] ?? '' ?>" required style="width:50%"><br><br>

                <button type="submit" class="btn">Zatwierdz</button>
                <a href="?section=dyst" class="btn" style="background:#777">Zresetuj</a>
            </form>
        </div>

	</div>

    <h3>Kierowanie dystrybutorami</h3>

    <form method="get" style="margin: 20px 0;">
	<input type="hidden" name="section" value="dyst">
        <input type="text" name="search" placeholder="Wyszukaj dystrybutora..." value="<?= htmlspecialchars($search) ?>">
        <button type="submit">Wyszukaj</button>
        <?php if($search): ?><a href="?section=dyst">Zresetuj</a><?php endif; ?>
    </form>

   <div class="filters" style="background: #f4f4f4; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
       <form method="get" action="admin.cgi" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
	    <input type="hidden" name="section" value="dyst">
        
            <?php if($search): ?>
                <input type="hidden" name="search" value="<?= htmlspecialchars($search) ?>">
            <?php endif; ?>

	    <div>
	       <label>Sortowanie:</label>
    		    <select name="sort" onchange="this.form.submit()">
			<option value="">-- Wszystkie --</option>
        		<option value="name_asc" <?= ($_GET['sort'] ?? '') == 'name_asc' ? 'selected' : '' ?>>Za nazwa (A-Z)</option>
			<option value="name_desc" <?= ($_GET['sort'] ?? '') == 'name_desc' ? 'selected' : '' ?>>Za nazwa (Z-A)</option>
    		    </select>
	    </div>
        
            <?php if($search || $sort_key): ?>
                <a href="?section=dyst" style="color: red; text-decoration: none;">Zresetowac</a>
            <?php endif; ?>
        
            <noscript><button type="submit">Zastosowac</button></noscript>
        </form>
   </div>

        <table border="1" cellpadding="10" cellspacing="0">
	    <thead>
               <tr><th>ID</th><th>Nazwa</th><th>Mail</th><th>Gry</th><th>Akcja</th></tr>
            </thead>
	    <tbody>
	       <?php foreach($data_list as $row): ?>
               <tr>
                    <td><?= $row['id'] ?></td>
                    <td><?= htmlspecialchars($row['nazwa']) ?></td>
		    <td><?= htmlspecialchars($row['email']) ?></td>
		    <td>
			<?php 
            		if ($row['lista_gier']) {
                	    $games_array = explode('|||', $row['lista_gier']);

                	    foreach ($games_array as $game) {
                    		echo '<div style="margin-bottom: 4px;"> ' . htmlspecialchars($game) . '</div>';
                	    }
            		} else {
                	    echo '<span style="color:gray">Brak gier</span>';
            		}	
            		?>
		    </td>
                    <td>
                        <a href="?section=dyst&edit=<?= $row['id'] ?>" class="btn">Edytowac</a>
                    
                        <form method="post" style="display:inline" onsubmit="return confirm('Usunac?');">
                            <input type="hidden" name="action" value="delete_dyst">
                            <input type="hidden" name="id" value="<?= $row['id'] ?>">
                            <button type="submit" class="btn btn-danger">Usunac</button>
                        </form>
                   </td>
                </tr>
                <?php endforeach; ?>
	    </tbody>
        </table>
    <?php endif; ?>

</main>
</body>
</html>
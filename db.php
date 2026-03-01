<?php

$host = 'lkdb';
$db   = 'mrbd'; 
$user = '';          
$pass = '';       
$charset = 'utf8';

$dsn = "pgsql:host=$host;port=5432;dbname=$db;options='--client_encoding=$charset'";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION, 
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,       
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    throw new \PDOException($e->getMessage(), (int)$e->getCode());
}
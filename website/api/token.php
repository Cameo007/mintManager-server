<?php
header('Content-Type: text/html; charset=utf-8');

require '../vendor/autoload.php';

$mintManagerPath = '/var/www/mintManager';

function saveToken($username, $token) {
    $tokens = json_decode(file_get_contents("$mintManagerPath/tokens.json"), true);
    $data = array(
        'username' => $username,
        'token' => $token,
        'time' => time(),
    );
    array_push($tokens, $data);
    file_put_contents("$mintManagerPath/tokens.json", json_encode($tokens));
    echo $token;
}

$username = $_GET['username'];
$password = $_GET['password'];

function generateToken() {
    $length = 75;
    return substr(str_shuffle(str_repeat($x='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-.:,;<>+*#', ceil($length/strlen($x)) )),1,$length);
}

$passwordHash = json_decode(file_get_contents('./loginData.json'), true)['data'][0][$username][0]['passwordHash'];
if ($passwordHash == hash('sha512', $password)) {
    saveToken($username, generateToken());
} else {
    echo 'ERROR: Password';
}
?>

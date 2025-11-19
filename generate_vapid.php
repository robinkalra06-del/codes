<?php

function generateBase64Url($length) {
    return rtrim(strtr(base64_encode(random_bytes($length)), '+/', '-_'), '=');
}

$publicKey  = generateBase64Url(65);  // 65 bytes for P-256 public key
$privateKey = generateBase64Url(32);  // 32 bytes private key

echo "============================\n";
echo "PUBLIC KEY:\n$publicKey\n\n";
echo "PRIVATE KEY:\n$privateKey\n";
echo "============================\n";

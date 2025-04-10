<?php
$conn = new mysqli("localhost", "root", "", "vulndb");

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    // ❌ VULNERABLE SQL (NO PREPARED STATEMENTS)
    $sql = "SELECT * FROM users WHERE username = '$username'";
    $result = $conn->query($sql);
    $row = $result->fetch_assoc();

    if ($row && password_verify($password, $row['password'])) {
        echo "Login successful! Welcome, " . $row['username'];
    } else {
        echo "Invalid credentials!";
    }
}
?>

<form method="POST">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <input type="submit" value="Login">
</form>


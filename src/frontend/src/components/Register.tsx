import React, { useState } from "react";
import { TextField, Button, Typography, Container } from "@mui/material";
import { useNavigate } from "react-router-dom";
import APIService from "../services/APIService";

function Register() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username || !password) {
      setMessage("Please enter both username and password.");
      return;
    }

    try {
      const data = await APIService.request("/register", "POST", { username, password });

      if (data.updateRequired) {
        setMessage(data.message);
      } else {
        localStorage.setItem("accessToken", data.token);
        setMessage("Registration successful");
        navigate("/login");
      }
    } catch (error) {
      setMessage("Error registering user. Please try again later.");
    }
  };

  const goToHomePage = () => {
    navigate("/");
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4, p: 4, bgcolor: '#f0f0f0', borderRadius: 4 }}>
      <Typography variant="h4" component="h2" align="center" gutterBottom>
        Register
      </Typography>
      <form onSubmit={handleRegister}>
        <div>
          <TextField
            label="Username"
            variant="outlined"
            fullWidth
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
          />
        </div>
        <div>
          <TextField
            label="Password"
            type="password"
            variant="outlined"
            fullWidth
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </div>
        <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
          Register
        </Button>
      </form>
      {message && (
        <Typography color="error" align="center" sx={{ mt: 2 }}>
          {message}
        </Typography>
      )}
      <Button
        onClick={goToHomePage}
        variant="outlined"
        color="primary"
        fullWidth
        sx={{ mt: 2 }}
      >
        Go to Home Page
      </Button>
    </Container>
  );
}

export default Register;

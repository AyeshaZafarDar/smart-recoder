import React, { useState, useEffect } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
  Button,
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Divider,
  Snackbar,
  Alert,
} from "@mui/material";
import { createTheme, ThemeProvider, styled } from "@mui/material/styles";
import APIService from "../services/APIService";

const theme = createTheme({
  palette: {
    primary: {
      main: "#3f51b5",
    },
    secondary: {
      main: "#f50057",
    },
  },
});

const WelcomeBox = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(8),
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
}));

const ActionButton = styled(Button)(({ theme }) => ({
  margin: theme.spacing(1, 0),
}));

const Home: React.FC = () => {
  const [username, setUsername] = useState<string>("");
  const [openSnackbar, setOpenSnackbar] = useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("accessToken");
      if (token) {
        try {
          const response = await APIService.request("/user", "GET", null, token, true);
          if (response.updateRequired) {
            setOpenSnackbar(true);
          } else {
            setUsername(response.username);
          }
        } catch (error) {
          console.error("Error fetching user:", error);
        }
      }
    };

    fetchUser();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    setUsername("");
    navigate("/login");
  };

  return (
    <ThemeProvider theme={theme}>
      <Container component="main" maxWidth="xs">
        <Paper elevation={6} sx={{ padding: 2, marginTop: 4 }}>
          <WelcomeBox>
            <Typography component="h1" variant="h5" sx={{ mb: 2 }}>
              Home
            </Typography>
            {username ? (
              <div>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  Welcome, {username}!
                </Typography>
                <Grid container spacing={2} justifyContent="center">
                  <Grid item>
                    <ActionButton
                      variant="contained"
                      color="primary"
                      onClick={handleLogout}
                    >
                      Logout
                    </ActionButton>
                  </Grid>
                </Grid>
              </div>
            ) : (
              <Grid container spacing={2} justifyContent="center">
                <Grid item>
                  <Button
                    component={RouterLink}
                    to="/login"
                    variant="contained"
                    color="primary"
                    sx={{ mb: 1 }}
                  >
                    Login
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    component={RouterLink}
                    to="/register"
                    variant="outlined"
                    color="primary"
                    sx={{ mb: 1 }}
                  >
                    Register
                  </Button>
                </Grid>
              </Grid>
            )}
          </WelcomeBox>
          <Divider sx={{ my: 2 }} />
        </Paper>
        <Snackbar open={openSnackbar} autoHideDuration={6000}>
          <Alert severity="warning" sx={{ width: '100%' }}>
            Please update your client application.
          </Alert>
        </Snackbar>
      </Container>
    </ThemeProvider>
  );
};

export default Home;

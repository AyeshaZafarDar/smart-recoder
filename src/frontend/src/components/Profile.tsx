import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Typography, Container, Box, Avatar, Paper, Snackbar, Alert } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import APIService from "../services/APIService";
import AudioRecorder from "./AudioRecorder";

const Profile: React.FC = () => {
  const [user, setUser] = useState<{ id: number, username: string, motto: string }>({ id: 0, username: "", motto: "" });
  const [openSnackbar, setOpenSnackbar] = useState<boolean>(false);
  const navigate = useNavigate();
  const [refresh, setRefresh] = useState<boolean>(false);

  const fetchUser = async () => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      try {
        const response = await APIService.request("/user", "GET", null, token, true);
        if (response.updateRequired) {
          setOpenSnackbar(true);
        } else {
          setUser(response);
        }
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    } else {
      navigate("/"); // Redirect to Home page if no token (not logged in)
    }
  };

  useEffect(() => {
    fetchUser();
  }, [refresh]); // Fetch user data when refresh state changes

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    navigate("/");
  };

  const doRefresh = () => {
    setRefresh(!refresh);
  };

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      fetchUser(); // Fetch user data again after login or registration
    }
  }, [navigate]); // Reload user data when navigating (login or registration)

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, borderRadius: 4, mt: 4 }}>
        <Box textAlign="center">
          <Avatar sx={{ width: 100, height: 100, margin: "auto", mb: 2 }}>
            <AccountCircleIcon style={{ width: 80, height: 80 }} />
          </Avatar>
          <Box mt={2}>
            <Typography variant="h6" gutterBottom>{user.username}</Typography>
          </Box>
          <Box mt={6} mb={8}>
            <Typography variant="h5">{user.motto || "My motto goes here!"}</Typography>
          </Box>
          <Box display="flex" justifyContent="space-between" mt={4}>
            <AudioRecorder doRefresh={doRefresh} />
            <Button variant="contained" color="secondary" onClick={handleLogout}>Logout</Button>
          </Box>
        </Box>
      </Paper>
      <Snackbar open={openSnackbar} autoHideDuration={6000}>
        <Alert severity="warning" sx={{ width: '100%' }}>
          Please update your client application.
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Profile;

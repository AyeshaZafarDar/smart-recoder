///home/dev/Downloads/jotpsych-fullstack-swe-challenge-2-main/src/frontend/src/App.tsx
import { Route, Routes } from "react-router-dom";
import Register from "./components/Register";
import Login from "./components/Login";
import Home from "./components/Home";
import Profile from './components/Profile';
function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route path="/profile" element={<Profile />} />
    </Routes>
  );
}

export default App;

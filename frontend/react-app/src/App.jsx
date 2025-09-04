import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./Home";
import Preferences from "./Preferences";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/preferences" element={<Preferences />} />
      </Routes>
    </Router>
  );
}

export default App;

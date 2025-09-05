import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./Home";
import Preferences from "./Preferences";
import NewsLetters from "./NewsLetters";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/preferences" element={<Preferences />} />
        <Route path="/newsletters" element={<NewsLetters />} />
      </Routes>
    </Router>
  );
}

export default App;

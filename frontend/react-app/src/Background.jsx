import "./App.css";
import NavBar from "./NavBar";

function Wrapper({ children }) {
  return (
    <div className="hero-container">
      <NavBar />
      <div className="hero-content">{children}</div>
    </div>
  );
}

export default Wrapper;
